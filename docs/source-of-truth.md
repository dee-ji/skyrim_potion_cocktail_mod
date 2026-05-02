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

## Current Import Strategy

Phase 0 imports the authoritative baseline into `shared/` with:

```sh
uv run python tools/import_source_baseline.py
```

By default, the importer reads from the sibling source repo at `../skyrim_potion_cocktail_app`. Pass `--source /path/to/source/repo` to use a different checkout.

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

Phase 1 vendors the source app runtime into `companion_app/runtime/app` with:

```sh
uv run python tools/sync_companion_runtime.py
```

The sync excludes generated caches and SQLite database files. It writes `companion_app/runtime-manifest.json` with the source commit, dirty state, synced files, sizes, and hashes.

Validate the synced runtime with:

```sh
uv run python tools/validate_companion_runtime.py
```
