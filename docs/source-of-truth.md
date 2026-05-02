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
