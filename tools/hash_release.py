#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


EXCLUDED_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path, output: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.resolve() == output.resolve():
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def write_checksums(root: Path, output: Path) -> None:
    lines = []
    for path in iter_files(root, output):
        relative = path.relative_to(root).as_posix()
        lines.append(f"{sha256(path)}  {relative}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate SHA-256 checksums for a release folder."
    )
    parser.add_argument("release_dir", type=Path, help="Release folder to hash.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output checksum file. Defaults to <release_dir>/SHA256SUMS.txt.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    release_dir = args.release_dir.expanduser().resolve()
    if not release_dir.is_dir():
        raise SystemExit(f"Release folder does not exist: {release_dir}")

    output = (
        args.output.expanduser().resolve()
        if args.output
        else release_dir / "SHA256SUMS.txt"
    )
    write_checksums(release_dir, output)
    print(f"Wrote checksums: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
