#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path


IMPORTS = (
    ("app/data/ingredients.json", "shared/data/ingredients.json"),
    ("app/rarity.py", "shared/domain/rarity.py"),
    ("AGENTS.md", "shared/source_docs/AGENTS.md"),
    ("docs/handoff.md", "shared/source_docs/handoff.md"),
    ("docs/discovery-scoring.md", "shared/source_docs/discovery-scoring.md"),
)
TEXT_HASH_SUFFIXES = {".html", ".json", ".md", ".py", ".toml", ".txt"}


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


def manifest_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    if path.suffix in TEXT_HASH_SUFFIXES or path.name == "Makefile":
        content = path.read_text(encoding="utf-8")
        normalized = content.replace("\r\n", "\n").replace("\r", "\n")
        digest.update(normalized.encode("utf-8"))
        return digest.hexdigest()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_imports(source_root: Path, destination_root: Path) -> list[dict[str, object]]:
    imported: list[dict[str, object]] = []

    for source_rel, destination_rel in IMPORTS:
        source_path = source_root / source_rel
        destination_path = destination_root / destination_rel

        if not source_path.is_file():
            raise FileNotFoundError(f"Required source file is missing: {source_path}")

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)

        imported.append(
            {
                "source": source_rel,
                "destination": destination_rel,
                "sha256": manifest_sha256(destination_path),
                "size_bytes": destination_path.stat().st_size,
            }
        )

    return imported


def build_manifest(
    source_root: Path, imported: list[dict[str, object]]
) -> dict[str, object]:
    status = run_git(source_root, "status", "--short")

    return {
        "schema_version": 1,
        "imported_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_repo": source_root.name,
        "source_commit": run_git(source_root, "rev-parse", "HEAD"),
        "source_dirty": bool(status),
        "source_status": status.splitlines(),
        "imports": imported,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import the authoritative Skyrim Potion Cocktails source baseline into shared/."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Path to the source app repo. Can also be set with SKYRIM_POTION_SOURCE_APP.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_arg = args.source or os.environ.get("SKYRIM_POTION_SOURCE_APP")
    if source_arg is None:
        raise SystemExit(
            "Source app path is required. Pass --source /path/to/source-app or set SKYRIM_POTION_SOURCE_APP."
        )

    source_root = Path(source_arg).expanduser().resolve()
    destination_root = repo_root()

    if not source_root.is_dir():
        raise NotADirectoryError(f"Source repo does not exist: {source_root}")

    imported = copy_imports(source_root, destination_root)
    manifest = build_manifest(source_root, imported)

    manifest_path = destination_root / "shared/manifests/source-baseline.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Imported {len(imported)} files from {source_root}")
    print(f"Manifest: {manifest_path.relative_to(destination_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
