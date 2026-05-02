# Skyrim Potion Cocktails Mod

This repository is the hybrid delivery project for Skyrim Potion Cocktails.

## Goal

Build two delivery paths from the same product baseline:

1. a Windows companion app for Skyrim PC players
2. a later in-game Skyrim mod integration layer

## Phase Order

### Phase 1: Companion App

The first milestone is a packaged local app that:

- reuses the existing Skyrim Potion Cocktails logic and dataset
- runs locally for PC users
- is suitable for Nexus distribution
- does not require players to host the FastAPI app manually

### Phase 2: In-Game Mod

The second milestone is a smaller Skyrim-side integration layer that may use:

- Creation Kit
- Papyrus
- SkyUI / MCM
- optional SKSE-dependent features if needed later

This phase should start narrow and should not assume full parity with the browser UI.

## Relationship To The Source App

This repo does not replace the source app repo.

The source app repo remains the current authority for:

- ingredient data
- rarity metadata
- discovery-scoring semantics
- inventory and known-effect behavior

## Initial Layout

- `docs/`
  - planning and handoff notes
- `companion_app/`
  - future packaging and launcher work
- `shared/`
  - future exported data or shared-core assets
- `skyrim_mod/`
  - future Creation Kit / Papyrus / Skyrim integration work

## Immediate Next Goal

Deliver a first companion-app milestone before starting in-game integration.

## Companion App Development

Refresh the source baseline and synced companion runtime:

```sh
uv run python tools/build_companion.py --skip-pyinstaller
```

Launch the local companion app after installing dependencies:

```sh
uv run python companion_app/launcher.py
```

See `companion_app/README.md` and `docs/nexus-packaging.md` for runtime and packaging details.
