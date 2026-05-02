#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


REQUIRED_INGREDIENT_KEYS = {"name", "source", "effects"}
REQUIRED_RARITY_KEYS = {"rarity", "rarity_label", "rarity_rank", "rarity_note"}
VALID_RARITY_TIERS = {"common", "uncommon", "rare", "very_rare"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_rarity_module(path: Path) -> ModuleType:
    sys.dont_write_bytecode = True

    spec = importlib.util.spec_from_file_location("shared_rarity", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load rarity module from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_manifest(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "shared/manifests/source-baseline.json"

    if not manifest_path.is_file():
        return [f"Missing manifest: {manifest_path.relative_to(root)}"]

    manifest = load_json(manifest_path)
    for key in (
        "schema_version",
        "imported_at",
        "source_repo",
        "source_commit",
        "imports",
    ):
        if key not in manifest:
            errors.append(f"Manifest missing key: {key}")

    imports = manifest.get("imports", [])
    if not isinstance(imports, list) or not imports:
        errors.append("Manifest imports must be a non-empty list")
        return errors

    for item in imports:
        if not isinstance(item, dict):
            errors.append("Manifest import entry is not an object")
            continue

        destination = item.get("destination")
        expected_hash = item.get("sha256")
        if not isinstance(destination, str) or not isinstance(expected_hash, str):
            errors.append(
                f"Manifest import entry is missing destination or sha256: {item}"
            )
            continue

        destination_path = root / destination
        if not destination_path.is_file():
            errors.append(f"Imported file is missing: {destination}")
            continue

        actual_hash = sha256(destination_path)
        if actual_hash != expected_hash:
            errors.append(
                f"Hash mismatch for {destination}: expected {expected_hash}, got {actual_hash}"
            )

    return errors


def validate_ingredients(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    ingredients_path = root / "shared/data/ingredients.json"

    if not ingredients_path.is_file():
        return [
            f"Missing ingredients data: {ingredients_path.relative_to(root)}"
        ], warnings

    ingredients = load_json(ingredients_path)
    if not isinstance(ingredients, list):
        return ["Ingredients data must be a list"], warnings

    names: set[str] = set()
    duplicate_names: set[str] = set()

    for index, ingredient in enumerate(ingredients):
        if not isinstance(ingredient, dict):
            errors.append(f"Ingredient #{index} must be an object")
            continue

        missing_keys = REQUIRED_INGREDIENT_KEYS - ingredient.keys()
        if missing_keys:
            errors.append(f"Ingredient #{index} missing keys: {sorted(missing_keys)}")

        name = ingredient.get("name")
        source = ingredient.get("source")
        effects = ingredient.get("effects")

        if not isinstance(name, str) or not name.strip():
            errors.append(f"Ingredient #{index} has invalid name")
        elif name in names:
            duplicate_names.add(name)
        else:
            names.add(name)

        if not isinstance(source, str) or not source.strip():
            errors.append(f"Ingredient #{index} has invalid source")

        if not isinstance(effects, list) or len(effects) != 4:
            errors.append(f"Ingredient #{index} must have exactly 4 ordered effects")
        elif any(
            not isinstance(effect, str) or not effect.strip() for effect in effects
        ):
            errors.append(f"Ingredient #{index} has invalid effect names")

    if duplicate_names:
        errors.append(f"Duplicate ingredient names: {sorted(duplicate_names)}")

    if len(ingredients) < 1:
        errors.append("Ingredients data is empty")
    elif len(ingredients) != 189:
        warnings.append(
            f"Expected 189 ingredients from current handoff; found {len(ingredients)}"
        )

    return errors, warnings


def validate_rarity(root: Path) -> list[str]:
    errors: list[str] = []
    ingredients = load_json(root / "shared/data/ingredients.json")
    ingredient_names = {
        item["name"]
        for item in ingredients
        if isinstance(item, dict) and "name" in item
    }
    rarity = load_rarity_module(root / "shared/domain/rarity.py")

    for name in (
        "RARITY_ORDER",
        "RARITY_LABELS",
        "RARITY_BY_NAME",
        "rarity_for_ingredient",
    ):
        if not hasattr(rarity, name):
            errors.append(f"rarity.py missing {name}")

    if errors:
        return errors

    rarity_order = rarity.RARITY_ORDER
    rarity_labels = rarity.RARITY_LABELS
    rarity_by_name = rarity.RARITY_BY_NAME

    if set(rarity_order) != VALID_RARITY_TIERS:
        errors.append(f"RARITY_ORDER tiers changed: {sorted(rarity_order)}")
    if set(rarity_labels) != VALID_RARITY_TIERS:
        errors.append(f"RARITY_LABELS tiers changed: {sorted(rarity_labels)}")

    unknown_rarity_names = sorted(set(rarity_by_name) - ingredient_names)
    if unknown_rarity_names:
        errors.append(
            f"RARITY_BY_NAME contains names missing from ingredients data: {unknown_rarity_names}"
        )

    invalid_tiers = sorted(
        {tier for tier in rarity_by_name.values() if tier not in VALID_RARITY_TIERS}
    )
    if invalid_tiers:
        errors.append(f"RARITY_BY_NAME contains invalid tiers: {invalid_tiers}")

    for ingredient_name in sorted(ingredient_names):
        value = rarity.rarity_for_ingredient(ingredient_name)
        if not isinstance(value, dict):
            errors.append(
                f"rarity_for_ingredient({ingredient_name!r}) did not return an object"
            )
            continue

        missing_keys = REQUIRED_RARITY_KEYS - value.keys()
        if missing_keys:
            errors.append(
                f"rarity_for_ingredient({ingredient_name!r}) missing keys: {sorted(missing_keys)}"
            )
            continue

        if value["rarity"] not in VALID_RARITY_TIERS:
            errors.append(
                f"rarity_for_ingredient({ingredient_name!r}) returned invalid tier: {value['rarity']}"
            )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate imported shared baseline assets."
    )
    parser.add_argument(
        "--root", type=Path, default=repo_root(), help="Delivery repo root."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()

    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(validate_manifest(root))
    ingredient_errors, ingredient_warnings = validate_ingredients(root)
    errors.extend(ingredient_errors)
    warnings.extend(ingredient_warnings)

    if not ingredient_errors:
        errors.extend(validate_rarity(root))

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Shared baseline validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
