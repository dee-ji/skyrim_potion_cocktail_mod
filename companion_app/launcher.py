#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import webbrowser
from pathlib import Path


APP_NAME = "Skyrim Potion Cocktails"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def companion_root() -> Path:
    return Path(__file__).resolve().parent


def runtime_root() -> Path:
    return companion_root() / "runtime"


def default_state_dir() -> Path:
    override = os.environ.get("SKYRIM_POTION_COCKTAILS_STATE_DIR")
    if override:
        return Path(override).expanduser()

    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return Path(base) / "Skyrim Potion Cocktails"

    if sys.platform == "darwin":
        return (
            Path.home() / "Library" / "Application Support" / "Skyrim Potion Cocktails"
        )

    return (
        Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        / "skyrim-potion-cocktails"
    )


def configure_runtime(state_dir: Path) -> Path:
    sys.dont_write_bytecode = True

    runtime = runtime_root()
    app_dir = runtime / "app"
    if not app_dir.is_dir():
        raise FileNotFoundError(
            f"Companion runtime is missing at {app_dir}. Run tools/sync_companion_runtime.py first."
        )

    sys.path.insert(0, str(runtime))
    state_dir.mkdir(parents=True, exist_ok=True)

    db_path = state_dir / "skyrim_alchemy.db"
    os.environ.setdefault("SKYRIM_ALCHEMY_DB", str(db_path))
    return db_path


def import_app() -> object:
    from app.app_factory import create_app

    return create_app()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"Launch {APP_NAME}.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Local host to bind.")
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help="Local port to bind."
    )
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=None,
        help="Directory for the SQLite user database.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the browser automatically.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that the companion runtime can be imported without starting the server.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state_dir = args.state_dir.expanduser() if args.state_dir else default_state_dir()
    db_path = configure_runtime(state_dir)
    app = import_app()

    if args.check:
        print(f"{APP_NAME} runtime import succeeded.")
        print(f"Database path: {db_path}")
        return 0

    try:
        import uvicorn
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing dependency: uvicorn. Install companion app dependencies before launching."
        ) from exc

    url = f"http://{args.host}:{args.port}/"
    if not args.no_browser:
        webbrowser.open(url)

    print(f"{APP_NAME} running at {url}")
    print(f"Database path: {db_path}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
