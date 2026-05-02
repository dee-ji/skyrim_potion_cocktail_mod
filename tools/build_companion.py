#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run(command: list[str], root: Path) -> None:
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=root, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the companion app distribution."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Path to the source app repo. Only used with --refresh-source.",
    )
    parser.add_argument(
        "--refresh-source",
        action="store_true",
        help="Refresh vendored shared/runtime files from the source app before building.",
    )
    parser.add_argument(
        "--skip-pyinstaller",
        action="store_true",
        help="Run validation and launcher checks without producing a packaged build.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()

    if args.refresh_source:
        if args.source is None:
            raise SystemExit("--refresh-source requires --source /path/to/source-app")

        source = args.source.expanduser().resolve()
        run(
            [
                sys.executable,
                "tools/import_source_baseline.py",
                "--source",
                str(source),
            ],
            root,
        )
        run(
            [
                sys.executable,
                "tools/sync_companion_runtime.py",
                "--source",
                str(source),
            ],
            root,
        )

    run([sys.executable, "tools/validate_shared_baseline.py"], root)
    run([sys.executable, "tools/validate_companion_runtime.py"], root)
    check_state_dir = (
        Path(tempfile.gettempdir()) / "skyrim-potion-cocktails-build-check"
    )
    run(
        [
            sys.executable,
            "companion_app/launcher.py",
            "--check",
            "--state-dir",
            str(check_state_dir),
        ],
        root,
    )

    if args.skip_pyinstaller:
        print("Skipped PyInstaller build.")
        return 0

    pyinstaller = shutil.which("pyinstaller")
    if pyinstaller is None:
        raise SystemExit(
            "PyInstaller is not installed. Install the build extra, then rerun: "
            "uv sync --extra build"
        )

    run([pyinstaller, "companion_app/packaging/skyrim-potion-cocktails.spec"], root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
