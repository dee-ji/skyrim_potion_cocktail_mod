# Skyrim Mod Integration

Phase 2 starts as a narrow bridge into the companion app.

## First Feature

Export Skyrim-side ingredient inventory, and later known effects, into the JSON format documented in `docs/skyrim-bridge.md`.

The companion app imports that file with:

```sh
uv run python tools/import_skyrim_bridge.py path/to/skyrim-bridge-export.json
```

## Scope Boundary

The Skyrim plugin should not reimplement:

- rarity tiers
- discovery scoring
- recipe ranking
- companion UI behavior

Those remain in the companion app. Skyrim-side code should collect and export data only.

## Inventory Mapping

Base-game ingredient Form IDs are mapped in:

```text
skyrim_mod/data/ingredient-form-map.json
```

This mapping covers the 91 companion ingredients whose source is `Skyrim`. DLC, Creation Club, `_ResourcePack.esl`, Creation-specific sources, and quest-only variants are deferred until the base-game bridge is working from a real save.

## Expected Tooling

The bridge likely needs SKSE plus a JSON-capable Papyrus utility such as PapyrusUtil or JContainers. If that changes, document the actual tooling in this directory before expanding implementation.

## Planned Structure

```text
skyrim_mod/
  README.md
  data/
  source/
    scripts/
  packaging/
```
