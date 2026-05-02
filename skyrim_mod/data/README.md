# Skyrim Data Mapping

`ingredient-form-map.json` maps base-game Skyrim ingredient Form IDs to the canonical companion-app ingredient names.

Current coverage:

- `Skyrim.esm` base-game ingredients: complete for the 91 ingredients whose source is `Skyrim` in `shared/data/ingredients.json`
- DLC, Creation Club, `_ResourcePack.esl`, and Creation-specific ingredients: deferred
- quest-only variants: deferred or intentionally excluded

The first inventory bridge should use this file to translate in-game inventory forms into companion-app ingredient names before writing `shared/exchange/skyrim-bridge.schema.json`.

## Notes

- `Salt Pile` maps to the standard `00034CDF` item, not the Black-Briar quest variant.
- `Void Salts` maps to the standard `0003AD60` item, not Fine-Cut Void Salts.
- `Bone Meal` maps to the standard `00034CDD` item, not Berit's Ashes.
- `Jarrin Root` is not part of the companion baseline and is not mapped.
