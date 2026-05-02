#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_dist_dir() -> Path:
    return repo_root() / "dist" / "SkyrimPotionCocktails"


def copy_if_exists(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Required release file is missing: {source}")
    shutil.copy2(source, destination)


def stage_release_files(dist_dir: Path) -> None:
    packaging_dir = repo_root() / "companion_app" / "packaging"
    copy_if_exists(packaging_dir / "PLAYER_README.md", dist_dir / "README.md")
    copy_if_exists(
        packaging_dir / "RELEASE_NOTES_TEMPLATE.md",
        dist_dir / "RELEASE_NOTES_TEMPLATE.md",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy player-facing release files into the companion distribution folder."
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
    dist_dir = args.dist_dir.expanduser().resolve()
    if not dist_dir.is_dir():
        raise SystemExit(f"Distribution folder does not exist: {dist_dir}")

    stage_release_files(dist_dir)
    print(f"Staged release files in: {dist_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
