# Skyrim Potion Cocktails

Skyrim Potion Cocktails is a hybrid delivery project for Skyrim PC players:

1. a local Windows companion app for tracking alchemy knowledge, inventory, and discovery-focused potion recipes
2. a narrow Skyrim-side bridge that can export in-game data into the companion app

The companion app is the primary product. The in-game mod layer should stay small and data-oriented.

## Current Status

- Phase 0 baseline import is implemented.
- Phase 1 companion app launcher, vendored runtime, validation, and PyInstaller build scaffold are implemented.
- Phase 2 bridge exchange format and companion-side JSON importer are implemented.
- The Skyrim-side Papyrus exporter is currently a source scaffold, not a production-ready compiled plugin.

## Requirements

Development requirements:

- Python `3.11+`
- `uv`

Windows release-build requirements:

- Windows 10/11
- `uv`
- PyInstaller via the build extra

Future Skyrim bridge requirements:

- Skyrim Special Edition / Anniversary Edition on PC
- SKSE if the plugin writes files from inside Skyrim
- a JSON-capable Papyrus utility such as PapyrusUtil or JContainers, unless the bridge moves to an external helper

## Source App Relationship

This repo vendors the current companion runtime and shared data baseline. Users, packagers, and Skyrim mod developers do not need the original Skyrim Potion Cocktails app repo installed.

Maintainers may explicitly refresh vendored files from the source app, but normal launch and build commands use only committed files in this repo.

## Install For Development

From the repo root:

```sh
uv sync
```

Run the full companion preflight:

```sh
uv run python tools/build_companion.py --skip-pyinstaller
```

Short form:

```sh
make companion-check
```

Run tests:

```sh
uv run pytest -q
```

## Run The Companion App

Start the local app:

```sh
uv run python companion_app/launcher.py
```

Then open:

```text
http://127.0.0.1:8765/
```

Useful launcher options:

```sh
uv run python companion_app/launcher.py --no-browser
uv run python companion_app/launcher.py --port 8766
uv run python companion_app/launcher.py --state-dir /path/to/state
uv run python companion_app/launcher.py --check
```

## Companion App Usage

1. Create or select a character.
2. Track ingredient inventory for that character.
3. Mark known effects you already discovered in Skyrim.
4. Use direct recipe checking for specific ingredient combinations.
5. Use the inventory discovery optimizer to find recipes that reveal useful unknown effects.
6. Click `Created` after crafting a potion to consume tracked inventory and mark discovered effects.
7. Reopen the app later; state persists in the local SQLite database.

Default state locations:

- Windows: `%LOCALAPPDATA%\Skyrim Potion Cocktails\skyrim_alchemy.db`
- macOS: `~/Library/Application Support/Skyrim Potion Cocktails/skyrim_alchemy.db`
- Linux: `$XDG_DATA_HOME/skyrim-potion-cocktails/skyrim_alchemy.db`, or `~/.local/share/skyrim-potion-cocktails/skyrim_alchemy.db`

## Build A Windows Companion Release

Install build dependencies:

```sh
uv sync --extra build
```

Build:

```sh
uv run python tools/build_companion.py
```

Expected output:

```text
dist/SkyrimPotionCocktails/
```

The build also stages `README.md`, `RELEASE_NOTES_TEMPLATE.md`, and `SHA256SUMS.txt` into the dist folder.

Run the generated executable on Windows:

```powershell
dist\SkyrimPotionCocktails\SkyrimPotionCocktails.exe
```

Before publishing, test the generated folder on a clean Windows machine or VM:

1. Launch `SkyrimPotionCocktails.exe`.
2. Confirm the browser opens at `http://127.0.0.1:8765/`.
3. Create a character.
4. Add inventory.
5. Mark known effects.
6. Close and reopen the app.
7. Confirm state persisted under `%LOCALAPPDATA%\Skyrim Potion Cocktails\`.
8. Zip the `dist\SkyrimPotionCocktails\` folder for distribution.

See `docs/nexus-packaging.md` for Nexus packaging notes.

## Skyrim Bridge Workflow

The bridge imports a Skyrim-side JSON export into the companion database.

Base-game Skyrim ingredient Form IDs are mapped in:

```text
skyrim_mod/data/ingredient-form-map.json
```

Validate the mapping with:

```sh
uv run python tools/validate_skyrim_mapping.py
```

Test with the sample export:

```sh
uv run python tools/import_skyrim_bridge.py shared/exchange/examples/skyrim-bridge-export.json --state-dir /tmp/spc-bridge-test
```

Import into the default companion database:

```sh
uv run python tools/import_skyrim_bridge.py path/to/skyrim-bridge-export.json
```

Inventory import defaults to replacing the companion inventory for that character. To upsert exported quantities without clearing other entries:

```sh
uv run python tools/import_skyrim_bridge.py path/to/skyrim-bridge-export.json --inventory-mode merge
```

The exchange format is documented in `docs/skyrim-bridge.md` and `shared/exchange/skyrim-bridge.schema.json`.

## Maintainer Source Refresh

Only maintainers with the original source app checkout need this.

```sh
uv run python tools/build_companion.py --refresh-source --skip-pyinstaller --source /path/to/skyrim_potion_cocktail_app
```

Or:

```sh
SKYRIM_POTION_SOURCE_APP=/path/to/skyrim_potion_cocktail_app make source-refresh
```

This updates:

- `shared/data/ingredients.json`
- `shared/domain/rarity.py`
- `shared/source_docs/`
- `shared/manifests/source-baseline.json`
- `companion_app/runtime/app/`
- `companion_app/runtime-manifest.json`

Do not manually recreate ingredient, rarity, or discovery-scoring data.

## Production Readiness Checklist

Companion app:

- build and smoke-test PyInstaller output on Windows
- verify persistence across app upgrades
- add a player-facing README into the release archive
- add versioned release notes
- record archive hashes for Nexus uploads
- test antivirus behavior against the PyInstaller build
- test blocked-port handling and alternate `--port`
- decide whether to keep console output visible or ship a windowed launcher

Skyrim bridge:

- choose PapyrusUtil, JContainers, or an external helper for JSON writing
- map Skyrim ingredient forms to canonical companion ingredient names
- compile Papyrus scripts and document Creation Kit setup
- export inventory to the bridge schema from an actual save
- decide whether known-effect export is feasible and reliable
- add an MCM or in-game configuration only if needed
- document SKSE and utility dependencies clearly for Nexus users
- package Skyrim plugin files separately from the companion app unless a combined archive is intentionally chosen

## Project Layout

```text
companion_app/
  launcher.py
  runtime/
  packaging/
docs/
  implementation-plan.md
  nexus-packaging.md
  skyrim-bridge.md
  source-of-truth.md
shared/
  data/
  domain/
  exchange/
  manifests/
skyrim_mod/
  README.md
  source/scripts/
tools/
  build_companion.py
  import_skyrim_bridge.py
  validate_shared_baseline.py
  validate_companion_runtime.py
```
