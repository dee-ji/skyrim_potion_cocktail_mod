# Implementation Plan

## Purpose

This plan breaks the remaining work into small, testable phases. Each phase should leave the repo in a working state before the next phase starts.

The companion app remains the primary product. The Skyrim-side mod layer should stay narrow and should not reimplement rarity, discovery scoring, recipe ranking, or the companion UI.

## Ground Rules

- Keep the repo independently runnable from committed files.
- Use `uv` for Python commands.
- Preserve ingredient, effect, source, rarity, inventory, known-effect, and discovery-scoring semantics.
- Do not manually recreate source data from memory.
- Document intentional divergences in `docs/divergences.md`.
- Keep Skyrim-specific code isolated under `skyrim_mod/`.
- Prefer inventory-only bridge functionality before attempting known-effect automation.

## Completed Foundation

### Phase 0: Baseline Import And Audit

Status: complete enough for current development.

Delivered:

- committed shared baseline under `shared/`
- source baseline manifest under `shared/manifests/source-baseline.json`
- source refresh command requiring explicit `--source`
- newline-stable hash validation
- `tools/validate_shared_baseline.py`

Verification:

```sh
uv run python tools/validate_shared_baseline.py
```

### Phase 1: Companion App Foundation

Status: complete enough for packaging work.

Delivered:

- committed companion runtime under `companion_app/runtime/`
- local launcher at `companion_app/launcher.py`
- runtime manifest under `companion_app/runtime-manifest.json`
- PyInstaller spec scaffold
- maintainer build/preflight command

Verification:

```sh
uv run python tools/build_companion.py --skip-pyinstaller
uv run python companion_app/launcher.py --check
```

### Phase 2: Bridge Foundation

Status: complete enough for Skyrim-side export work.

Delivered:

- JSON exchange schema under `shared/exchange/skyrim-bridge.schema.json`
- sample bridge export
- companion-side bridge importer at `tools/import_skyrim_bridge.py`
- Papyrus scaffold under `skyrim_mod/source/scripts/`
- bridge tests

Verification:

```sh
uv run pytest -q
make bridge-import-example
```

## Buildable Phases

### Phase 3: Windows Companion Build

Goal: produce a working Windows companion app folder from PyInstaller.

Status: in progress. The frozen-app runtime path, PyInstaller data layout, post-build distribution inspection, and Windows build checklist have been added. A local PyInstaller one-folder build passed import and API smoke tests; Windows remains the required acceptance environment for this phase.

Scope:

1. Build the PyInstaller one-folder app on Windows.
2. Fix PyInstaller spec issues only.
3. Verify the generated executable launches the local web app.
4. Confirm no source app checkout is required.

Do not include:

- Skyrim plugin work
- bridge UI changes
- installer creation
- broad frontend redesign

Deliverables:

- working `dist/SkyrimPotionCocktails/` folder
- any required PyInstaller spec updates
- short build notes if Windows-specific adjustments are discovered
- `tools/inspect_companion_dist.py` passes after PyInstaller

Verification:

```powershell
uv sync --extra build
uv run python tools/build_companion.py
dist\SkyrimPotionCocktails\SkyrimPotionCocktails.exe
```

Manual checks:

- browser opens to `http://127.0.0.1:8765/`
- character creation works
- inventory updates work
- known effects can be marked
- closing and reopening preserves state in `%LOCALAPPDATA%\Skyrim Potion Cocktails\`

Exit criteria:

- a Windows user can run the generated executable without installing Python
- no source app checkout is needed

### Phase 4: Companion Release Polish

Goal: make the Windows companion build suitable for a first private release archive.

Status: in progress. Player README, release notes template, release staging, distribution inspection updates, and checksum generation have been added.

Scope:

1. Add player-facing release README content for the packaged folder.
2. Add version metadata and release notes template.
3. Add archive/checksum helper or documented checksum command.
4. Document blocked-port, browser-open, antivirus, uninstall, and state-reset troubleshooting.

Do not include:

- Skyrim plugin work
- installer technology
- MCM/SkyUI work

Deliverables:

- release README template
- release notes template
- checksum/version documentation
- updated Nexus packaging docs

Verification:

```sh
uv run python tools/build_companion.py --skip-pyinstaller
```

Manual checks:

- package docs explain install, launch, upgrade, uninstall, and state location
- release artifact excludes `.venv`, local databases, caches, and maintainer-only source paths

Exit criteria:

- the companion app can be zipped and shared with a tester with clear instructions

### Phase 5: Skyrim Inventory Mapping

Goal: define the mapping between Skyrim ingredient forms and companion ingredient names.

Scope:

1. Add a data file for Skyrim form/editor IDs mapped to canonical ingredient names.
2. Cover base Skyrim first.
3. Add validation that every mapped companion name exists in `shared/data/ingredients.json`.
4. Document unsupported DLC/Creation ingredients as explicit gaps.

Do not include:

- Papyrus export logic
- known-effect export
- MCM/SkyUI UI

Deliverables:

- mapping file under `skyrim_mod/`
- validation script or test
- documented coverage status

Verification:

```sh
uv run pytest -q
```

Manual checks:

- spot-check several common ingredients against Creation Kit / UESP naming
- verify all mapped companion names are exact canonical names

Exit criteria:

- base-game inventory export has a reliable name mapping target

### Phase 6: Skyrim Inventory Export Prototype

Goal: export ingredient inventory from Skyrim to the bridge JSON format.

Scope:

1. Choose JSON writer mechanism: PapyrusUtil, JContainers, or external helper.
2. Implement inventory collection for mapped ingredients.
3. Write `bridge-export.json` matching `shared/exchange/skyrim-bridge.schema.json`.
4. Keep the export trigger simple, such as console-started quest function or minimal spell/power.

Do not include:

- known-effect export
- discovery/ranking logic
- polished MCM
- broad DLC/Creation coverage unless mapping already exists

Deliverables:

- Papyrus source update
- dependency note for chosen JSON writer
- example output from a real save

Verification:

```sh
uv run python tools/import_skyrim_bridge.py path/to/bridge-export.json --state-dir /tmp/spc-real-export-test
```

Manual checks:

- export file is created from a real Skyrim SE/AE save
- companion importer accepts it without hand editing
- imported inventory appears for the expected character

Exit criteria:

- a real Skyrim inventory can be moved into the companion app

### Phase 7: Bridge Usability

Goal: make the bridge usable by a player without developer-only steps.

Scope:

1. Add a simple in-game export trigger.
2. Add clear export file location conventions.
3. Add companion-side import instructions for Windows users.
4. Add error messages or troubleshooting for missing dependencies/export file.

Do not include:

- full MCM unless needed
- known-effect export unless inventory export is stable
- recipe lookup inside Skyrim

Deliverables:

- updated Skyrim mod README
- bridge workflow documentation
- packaging notes for scripts/plugin/dependencies

Verification:

- export from Skyrim
- import into companion app
- repeat after inventory changes

Exit criteria:

- a tester can follow documented steps without hand-editing JSON

### Phase 8: Known-Effects Investigation

Goal: decide whether known-effect export is reliable enough to ship.

Scope:

1. Research/test whether the Skyrim scripting stack can read known alchemy effects reliably.
2. Prototype known-effect export if feasible.
3. Import known effects with existing `tools/import_skyrim_bridge.py`.
4. Document limitations if Skyrim does not expose enough data safely.

Do not include:

- blocking inventory bridge release on known effects
- reimplementing discovery scoring in Skyrim

Deliverables:

- feasibility note
- prototype or explicit non-go decision
- importer/test updates only if the export shape changes

Verification:

```sh
uv run pytest -q
```

Manual checks:

- compare exported known effects against an actual character's alchemy knowledge

Exit criteria:

- known-effect export is either shippable or explicitly deferred

### Phase 9: First Nexus Candidate

Goal: assemble a first release candidate for Skyrim PC users.

Scope:

1. Decide one archive vs separate companion/mod archives.
2. Build Windows companion artifact.
3. Package Skyrim bridge files and dependency notes.
4. Add screenshots and final player instructions.
5. Record artifact hashes.

Do not include:

- new feature work
- broad UI redesign
- unplanned mod scope expansion

Deliverables:

- release candidate archive(s)
- release notes
- checksums
- final install/uninstall docs

Verification:

- clean Windows companion app test
- clean Skyrim bridge test on Skyrim SE/AE
- import exported inventory into companion app

Exit criteria:

- ready for private tester distribution or Nexus draft upload

## Backlog After First Candidate

- DLC and Creation ingredient mapping expansion
- optional MCM settings page
- one-click companion import from default bridge export location
- installer or self-contained updater
- companion UI polish for bridge import status
- optional recipe lookup helper inside Skyrim
