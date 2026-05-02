#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def configure_companion_runtime(state_dir: Path | None) -> Path:
    root = repo_root()
    sys.path.insert(0, str(root))

    from companion_app.launcher import configure_runtime, default_state_dir

    return configure_runtime((state_dir or default_state_dir()).expanduser())


def load_export(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Bridge export must be a JSON object")
    return payload


def normalized_name(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Expected a string")
    value = value.strip()
    if not value:
        raise ValueError("Expected a non-empty string")
    return value


def validate_payload(
    payload: dict[str, Any],
) -> tuple[str, Counter[str], dict[str, set[str]]]:
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported or missing schema_version; expected 1")

    character = normalized_name(payload.get("character"))
    if len(character) > 80:
        raise ValueError("character must be 80 characters or fewer")

    inventory: Counter[str] = Counter()
    for index, item in enumerate(payload.get("inventory", [])):
        if not isinstance(item, dict):
            raise ValueError(f"inventory[{index}] must be an object")
        name = normalized_name(item.get("name"))
        quantity = item.get("quantity")
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError(f"inventory[{index}].quantity must be an integer >= 0")
        inventory[name] += quantity

    known_effects: dict[str, set[str]] = defaultdict(set)
    for index, item in enumerate(payload.get("known_effects", [])):
        if not isinstance(item, dict):
            raise ValueError(f"known_effects[{index}] must be an object")
        ingredient = normalized_name(item.get("ingredient"))
        effects = item.get("effects")
        if not isinstance(effects, list) or not effects:
            raise ValueError(f"known_effects[{index}].effects must be a non-empty list")
        for effect in effects:
            known_effects[ingredient].add(normalized_name(effect))

    return character, inventory, known_effects


def ensure_character(conn: Any, name: str) -> int:
    row = conn.execute("SELECT id FROM characters WHERE name=?", (name,)).fetchone()
    if row:
        return int(row["id"])

    cursor = conn.execute("INSERT INTO characters(name) VALUES (?)", (name,))
    return int(cursor.lastrowid)


def validate_against_database(
    conn: Any, inventory: Counter[str], known_effects: dict[str, set[str]]
) -> list[str]:
    errors: list[str] = []
    ingredient_names = set(inventory) | set(known_effects)
    if ingredient_names:
        placeholders = ",".join("?" for _ in ingredient_names)
        known_ingredients = {
            row["name"]
            for row in conn.execute(
                f"SELECT name FROM ingredients WHERE name IN ({placeholders})",
                tuple(ingredient_names),
            ).fetchall()
        }
        missing = sorted(ingredient_names - known_ingredients)
        if missing:
            errors.append("Unknown ingredients: " + ", ".join(missing))

    for ingredient, effects in sorted(known_effects.items()):
        row = conn.execute(
            "SELECT id FROM ingredients WHERE name=?", (ingredient,)
        ).fetchone()
        if not row:
            continue
        placeholders = ",".join("?" for _ in effects)
        known = {
            effect_row["name"]
            for effect_row in conn.execute(
                f"""
                SELECT e.name
                FROM effects e
                JOIN ingredient_effects ie ON ie.effect_id = e.id
                WHERE ie.ingredient_id = ? AND e.name IN ({placeholders})
                """,
                (row["id"], *effects),
            ).fetchall()
        }
        missing_effects = sorted(effects - known)
        if missing_effects:
            errors.append(
                f"{ingredient} does not have effect(s): " + ", ".join(missing_effects)
            )

    return errors


def apply_bridge_export(
    payload: dict[str, Any], state_dir: Path | None, inventory_mode: str
) -> dict[str, int | str]:
    db_path = configure_companion_runtime(state_dir)

    from app.db import db, init_db
    from app.services import (
        get_ingredient_id_or_404,
        upsert_inventory_quantity,
        validate_ingredient_effects,
    )

    init_db()
    character, inventory, known_effects = validate_payload(payload)

    with db() as conn:
        errors = validate_against_database(conn, inventory, known_effects)
        if errors:
            raise ValueError("; ".join(errors))

        character_id = ensure_character(conn, character)

        if inventory_mode == "replace":
            conn.execute(
                "DELETE FROM character_inventory WHERE character_id=?", (character_id,)
            )

        for ingredient_name, quantity in sorted(inventory.items()):
            upsert_inventory_quantity(conn, character_id, ingredient_name, quantity)

        marked = 0
        for ingredient_name, effects in sorted(known_effects.items()):
            ingredient_id = get_ingredient_id_or_404(conn, ingredient_name)
            effect_rows = validate_ingredient_effects(
                conn, ingredient_id, sorted(effects)
            )
            before_changes = conn.total_changes
            for effect in effect_rows:
                conn.execute(
                    "INSERT OR IGNORE INTO character_known_effects(character_id, ingredient_id, effect_id) VALUES (?, ?, ?)",
                    (character_id, ingredient_id, effect["id"]),
                )
            marked += conn.total_changes - before_changes

    return {
        "character": character,
        "character_id": character_id,
        "inventory_items": len(inventory),
        "known_effect_groups": len(known_effects),
        "known_effects_marked": marked,
        "database": str(db_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a Skyrim bridge JSON export into the companion app database."
    )
    parser.add_argument(
        "export", type=Path, help="Path to a Skyrim bridge JSON export."
    )
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=None,
        help="Companion app state directory. Defaults to the launcher state directory.",
    )
    parser.add_argument(
        "--inventory-mode",
        choices=("replace", "merge"),
        default="replace",
        help="Use replace to make companion inventory match the export, or merge to upsert exported quantities only.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

    try:
        summary = apply_bridge_export(
            load_export(args.export), args.state_dir, args.inventory_mode
        )
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print("Skyrim bridge import completed.")
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
