#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_RUNTIME_FILES = {
    "companion_app/runtime/app/app_factory.py",
    "companion_app/runtime/app/config.py",
    "companion_app/runtime/app/data/ingredients.json",
    "companion_app/runtime/app/db.py",
    "companion_app/runtime/app/main.py",
    "companion_app/runtime/app/rarity.py",
    "companion_app/runtime/app/static/index.html",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_manifest(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "companion_app/runtime-manifest.json"

    if not manifest_path.is_file():
        return [f"Missing runtime manifest: {manifest_path.relative_to(root)}"]

    manifest = load_json(manifest_path)
    for key in ("schema_version", "synced_at", "source_repo", "source_commit", "files"):
        if key not in manifest:
            errors.append(f"Runtime manifest missing key: {key}")

    files = manifest.get("files", [])
    if not isinstance(files, list) or not files:
        errors.append("Runtime manifest files must be a non-empty list")
        return errors

    destinations: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            errors.append("Runtime manifest file entry is not an object")
            continue

        destination = item.get("destination")
        expected_hash = item.get("sha256")
        if not isinstance(destination, str) or not isinstance(expected_hash, str):
            errors.append(
                f"Runtime manifest file entry is missing destination or sha256: {item}"
            )
            continue

        destinations.add(destination)
        destination_path = root / destination
        if not destination_path.is_file():
            errors.append(f"Runtime file is missing: {destination}")
            continue

        actual_hash = sha256(destination_path)
        if actual_hash != expected_hash:
            errors.append(
                f"Hash mismatch for {destination}: expected {expected_hash}, got {actual_hash}"
            )

    missing_required = sorted(REQUIRED_RUNTIME_FILES - destinations)
    if missing_required:
        errors.append(f"Runtime manifest is missing required files: {missing_required}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the synced companion app runtime."
    )
    parser.add_argument(
        "--root", type=Path, default=repo_root(), help="Delivery repo root."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    errors = validate_manifest(root)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Companion runtime validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
