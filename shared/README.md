# Shared Baseline

This directory contains imported or exported assets from the authoritative Skyrim Potion Cocktails source app.

Do not edit imported domain files directly unless the divergence is intentional and recorded in `docs/divergences.md`.

## Import

From the repo root:

```sh
python3 tools/import_source_baseline.py
```

The default source path is `../skyrim_potion_cocktail_app`. Use `--source /path/to/source/repo` if the source app lives elsewhere.

## Validate

```sh
python3 tools/validate_shared_baseline.py
```

Validation checks the import manifest, ingredient data shape, uniqueness of ingredient names, four ordered effects per ingredient, and rarity tier consistency.

