# AGENTS.md

## Purpose

This repository is the hybrid delivery repo for Skyrim Potion Cocktails:

- phase 1: a packaged PC companion app for Skyrim players
- phase 2: an optional in-game Skyrim mod integration layer

This repo is derived from the main Skyrim Potion Cocktails app repo and should preserve its domain rules unless a divergence is explicitly documented.

## Source Of Truth

The current authoritative domain baseline lives in the source app repo.

Treat the following as authoritative unless replaced by an explicit shared export or core package:

- `app/data/ingredients.json`
- `app/rarity.py`
- `AGENTS.md`
- `docs/handoff.md`
- `docs/discovery-scoring.md`

## Delivery Strategy

- Build the companion app first.
- Keep the in-game mod scope intentionally small at first.
- Do not attempt full UI parity inside Skyrim as an initial milestone.

## Priorities

- preserve ingredient/effect/source/rarity semantics
- preserve discovery-scoring intent
- keep packaging and distribution practical for Nexus users
- keep Skyrim-specific integration isolated from shared domain behavior

## Do Not Do

- do not silently redefine rarity
- do not silently redefine discovery priority
- do not manually rebuild the ingredient dataset from memory
- do not start with a full Papyrus/SkyUI rewrite of the entire app

## Working Guidance

- Prefer incremental milestones.
- Document divergences caused by Skyrim engine limitations.
- Keep the repo friendly to future packaging and Nexus release workflows.
