# Nexus Packaging

This document describes the intended Phase 1 companion-app package for Nexus distribution.

## Package Contents

The Windows archive should contain the PyInstaller `SkyrimPotionCocktails` folder, including:

- `SkyrimPotionCocktails.exe`
- bundled Python dependencies
- `runtime/app` with the synced FastAPI app, static UI, ingredient data, and rarity metadata
- a short player README

Do not include local SQLite databases, source app virtual environments, build caches, or developer-only state.

## Player Install

1. Extract the archive to a folder outside `Program Files`, such as a modding tools folder.
2. Run `SkyrimPotionCocktails.exe`.
3. The app opens in the default browser at `http://127.0.0.1:8765/`.

The companion app is independent of the Skyrim install folder for Phase 1.

## Player State

The app creates its SQLite database at:

```text
%LOCALAPPDATA%\Skyrim Potion Cocktails\skyrim_alchemy.db
```

This file contains character inventory, known effects, and created recipe history. It should persist across app upgrades.

## Uninstall

Delete the extracted companion-app folder.

To remove saved companion-app state too, delete:

```text
%LOCALAPPDATA%\Skyrim Potion Cocktails\
```

## Troubleshooting

- If the browser does not open, manually visit `http://127.0.0.1:8765/`.
- If port `8765` is already in use, launch from a terminal with `--port <number>`.
- If antivirus software flags the executable, document the exact build version, PyInstaller version, and archive hash before release.
- If character data appears missing after an upgrade, check that the database still exists under `%LOCALAPPDATA%\Skyrim Potion Cocktails\`.

## Maintainer Build

From the repo root:

```sh
uv run python tools/build_companion.py
```

This build uses the vendored runtime and shared baseline committed in this repo. It does not require the original Skyrim Potion Cocktails app checkout.

For a preflight without producing a PyInstaller build:

```sh
uv run python tools/build_companion.py --skip-pyinstaller
```
