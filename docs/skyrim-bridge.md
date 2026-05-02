# Skyrim Bridge

Phase 2 starts with a file-based bridge between Skyrim and the companion app.

The first supported bridge direction is:

```text
Skyrim inventory / known effects -> JSON file -> companion app database
```

Discovery scoring, rarity behavior, recipe ranking, and potion recommendations stay in the companion app. The Skyrim-side integration should only collect data and write it to the agreed exchange format.

## Exchange File

The exchange format is documented in `shared/exchange/skyrim-bridge.schema.json`.

Minimal example:

```json
{
  "schema_version": 1,
  "character": "Dragonborn",
  "inventory": [
    {
      "name": "Blue Mountain Flower",
      "quantity": 3
    }
  ],
  "known_effects": [
    {
      "ingredient": "Blue Mountain Flower",
      "effects": ["Restore Health"]
    }
  ]
}
```

Ingredient and effect names must match the committed companion baseline exactly.

## Companion Import

Import an export file into the default companion database:

```sh
uv run python tools/import_skyrim_bridge.py path/to/skyrim-bridge-export.json
```

Use a separate state directory for testing:

```sh
uv run python tools/import_skyrim_bridge.py shared/exchange/examples/skyrim-bridge-export.json --state-dir /tmp/spc-bridge-test
```

Inventory import defaults to `replace`, meaning the exported inventory becomes the companion inventory for that character. Use `--inventory-mode merge` to only upsert exported quantities.

## Skyrim-Side Scope

The initial Skyrim mod should stay thin:

- collect ingredient inventory counts
- optionally collect known ingredient effects if the modding stack can access them reliably
- write a JSON file matching the exchange schema
- avoid implementing discovery scoring or rarity ranking in Papyrus

## Tooling Assumption

Plain Papyrus cannot safely write structured JSON by itself. The first practical implementation should use SKSE plus a JSON-capable Papyrus utility such as PapyrusUtil or JContainers, or a small external helper launched outside Skyrim.

This is documented as a tooling requirement, not a domain divergence. The domain rules remain in the companion app.

