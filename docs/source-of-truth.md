# Source Of Truth

Until this repo has an explicit shared export pipeline, the authoritative domain baseline is the main Skyrim Potion Cocktails app repo.

## Authoritative Assets

- ingredient list, source labels, ordered effects
- rarity tiers and rarity notes
- discovery scoring intent
- inventory semantics
- known-effect semantics

## Authoritative Files In The Source App Repo

- `app/data/ingredients.json`
- `app/rarity.py`
- `AGENTS.md`
- `docs/handoff.md`
- `docs/discovery-scoring.md`

## Rule For Divergence

If this repo intentionally differs from the source app:

- document the exact difference
- explain why the divergence is necessary
- state whether the cause is UX, packaging, Skyrim engine limits, or modding-tool limits

## Current Committed Baseline

This repo commits the current shared baseline and companion runtime so users, packagers, and future Skyrim mod work do not require the original source app checkout.

The source app remains the authority for domain evolution, but it is not a runtime dependency of this repo.

## Maintainer Import Strategy

When intentionally refreshing from the source app, import the authoritative baseline into `shared/` with:

```sh
uv run python tools/import_source_baseline.py --source /path/to/skyrim_potion_cocktail_app
```

You can also set `SKYRIM_POTION_SOURCE_APP=/path/to/skyrim_potion_cocktail_app`.

The import writes:

- `shared/data/ingredients.json`
- `shared/domain/rarity.py`
- `shared/source_docs/AGENTS.md`
- `shared/source_docs/handoff.md`
- `shared/source_docs/discovery-scoring.md`
- `shared/manifests/source-baseline.json`

Validate the imported baseline with:

```sh
uv run python tools/validate_shared_baseline.py
```

## Companion Runtime Sync

Phase 1 vendors the source app runtime into `companion_app/runtime/app`. When intentionally refreshing it, run:

```sh
uv run python tools/sync_companion_runtime.py --source /path/to/skyrim_potion_cocktail_app
```

The sync excludes generated caches and SQLite database files. It writes `companion_app/runtime-manifest.json` with the source commit, dirty state, synced files, sizes, and hashes.

Validate the synced runtime with:

```sh
uv run python tools/validate_companion_runtime.py
```
