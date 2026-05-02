#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


FORBIDDEN_PARTS = {
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}
FORBIDDEN_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".db",
    ".sqlite",
    ".sqlite3",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_dist_dir() -> Path:
    return repo_root() / "dist" / "SkyrimPotionCocktails"


def expected_executable_name() -> str:
    return (
        "SkyrimPotionCocktails.exe"
        if sys.platform == "win32"
        else "SkyrimPotionCocktails"
    )


def find_internal_root(dist_dir: Path) -> Path:
    internal = dist_dir / "_internal"
    return internal if internal.is_dir() else dist_dir


def inspect_dist(dist_dir: Path) -> list[str]:
    errors: list[str] = []

    if not dist_dir.is_dir():
        return [f"Distribution folder does not exist: {dist_dir}"]

    executable = dist_dir / expected_executable_name()
    if not executable.is_file():
        errors.append(f"Missing executable: {executable}")

    internal_root = find_internal_root(dist_dir)
    required_paths = [
        internal_root / "app" / "data" / "ingredients.json",
        internal_root / "app" / "static" / "index.html",
    ]
    for path in required_paths:
        if not path.is_file():
            errors.append(f"Missing bundled runtime asset: {path}")

    for path in dist_dir.rglob("*"):
        relative_parts = set(path.relative_to(dist_dir).parts)
        if relative_parts & FORBIDDEN_PARTS:
            errors.append(f"Forbidden build artifact included: {path}")
        if path.is_file() and path.suffix in FORBIDDEN_SUFFIXES:
            errors.append(f"Forbidden local/runtime state file included: {path}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect the PyInstaller companion app distribution."
    )
    parser.add_argument(
        "--dist-dir",
        type=Path,
        default=default_dist_dir(),
        help="Path to dist/SkyrimPotionCocktails.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors = inspect_dist(args.dist_dir.expanduser().resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Companion distribution inspection passed: {args.dist_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
