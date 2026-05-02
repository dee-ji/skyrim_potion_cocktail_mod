# Companion App

The companion app packages the current Skyrim Potion Cocktails FastAPI experience as a local app for Skyrim PC players.

## Runtime

The vendored runtime lives in `companion_app/runtime/app` and is synced from the authoritative source app with:

```sh
uv run python tools/sync_companion_runtime.py
```

The sync writes `companion_app/runtime-manifest.json`, including the source repo commit, dirty state, and hashes for every copied runtime file.

## Launch

Install the runtime dependencies from the repo root:

```sh
uv sync
```

Then launch:

```sh
uv run python companion_app/launcher.py
```

The app opens at `http://127.0.0.1:8765/` by default.

## User State

The launcher stores the SQLite database outside the vendored runtime:

- Windows: `%LOCALAPPDATA%\Skyrim Potion Cocktails\skyrim_alchemy.db`
- macOS: `~/Library/Application Support/Skyrim Potion Cocktails/skyrim_alchemy.db`
- Linux: `$XDG_DATA_HOME/skyrim-potion-cocktails/skyrim_alchemy.db`, or `~/.local/share/skyrim-potion-cocktails/skyrim_alchemy.db`

Override the state directory with:

```sh
uv run python companion_app/launcher.py --state-dir /path/to/state
```

## Development Checks

```sh
uv run python companion_app/launcher.py --check
uv run python tools/validate_shared_baseline.py
uv run python tools/validate_companion_runtime.py
```

## Packaging Direction

The first packaging target is a Windows-friendly build that launches the local app without requiring users to install Python manually. The initial packaging path is PyInstaller because the source app is already Python/FastAPI based.

Run the maintainer build flow with:

```sh
uv run python tools/build_companion.py
```

Use `--skip-pyinstaller` for a preflight check when PyInstaller is not installed.
