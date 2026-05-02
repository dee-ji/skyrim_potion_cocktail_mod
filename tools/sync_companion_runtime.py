#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path


RUNTIME_SOURCE_DIR = "app"
RUNTIME_DESTINATION_DIR = "companion_app/runtime/app"
IGNORED_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "skyrim_alchemy.db",
}
IGNORED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".db",
    ".sqlite",
    ".sqlite3",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_git(source_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=source_root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_ignore(path: Path) -> bool:
    return path.name in IGNORED_NAMES or path.suffix in IGNORED_SUFFIXES


def sync_runtime(source_root: Path, destination_root: Path) -> list[dict[str, object]]:
    source_dir = source_root / RUNTIME_SOURCE_DIR
    destination_dir = destination_root / RUNTIME_DESTINATION_DIR

    if not source_dir.is_dir():
        raise NotADirectoryError(
            f"Source runtime directory does not exist: {source_dir}"
        )

    if destination_dir.exists():
        shutil.rmtree(destination_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)

    files: list[dict[str, object]] = []
    for source_path in sorted(source_dir.rglob("*")):
        if any(
            should_ignore(part) for part in source_path.relative_to(source_dir).parents
        ):
            continue
        if should_ignore(source_path):
            continue
        if not source_path.is_file():
            continue

        relative_path = source_path.relative_to(source_dir)
        destination_path = destination_dir / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)

        files.append(
            {
                "source": str(Path(RUNTIME_SOURCE_DIR) / relative_path),
                "destination": str(Path(RUNTIME_DESTINATION_DIR) / relative_path),
                "sha256": sha256(destination_path),
                "size_bytes": destination_path.stat().st_size,
            }
        )

    return files


def build_manifest(
    source_root: Path, files: list[dict[str, object]]
) -> dict[str, object]:
    status = run_git(source_root, "status", "--short")

    return {
        "schema_version": 1,
        "synced_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_repo": str(source_root),
        "source_commit": run_git(source_root, "rev-parse", "HEAD"),
        "source_dirty": bool(status),
        "source_status": status.splitlines(),
        "runtime_source": RUNTIME_SOURCE_DIR,
        "runtime_destination": RUNTIME_DESTINATION_DIR,
        "files": files,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync the source app runtime into companion_app/runtime."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=repo_root().parent / "skyrim_potion_cocktail_app",
        help="Path to the source app repo. Defaults to ../skyrim_potion_cocktail_app.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = args.source.expanduser().resolve()
    destination_root = repo_root()

    files = sync_runtime(source_root, destination_root)
    manifest = build_manifest(source_root, files)

    manifest_path = destination_root / "companion_app/runtime-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Synced {len(files)} runtime files from {source_root}")
    print(f"Manifest: {manifest_path.relative_to(destination_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
