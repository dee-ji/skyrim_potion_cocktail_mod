from __future__ import annotations

import sqlite3

import pytest

from tools.import_skyrim_bridge import apply_bridge_export


def test_import_skyrim_bridge_sample(tmp_path):
    payload = {
        "schema_version": 1,
        "character": "Dragonborn",
        "inventory": [
            {"name": "Blue Mountain Flower", "quantity": 3},
            {"name": "Wheat", "quantity": 2},
        ],
        "known_effects": [
            {"ingredient": "Blue Mountain Flower", "effects": ["Restore Health"]},
            {"ingredient": "Wheat", "effects": ["Restore Health", "Fortify Health"]},
        ],
    }

    summary = apply_bridge_export(payload, tmp_path, "replace")

    assert summary["character"] == "Dragonborn"
    assert summary["inventory_items"] == 2
    assert summary["known_effects_marked"] == 3

    with sqlite3.connect(tmp_path / "skyrim_alchemy.db") as conn:
        inventory = dict(
            conn.execute(
                """
                SELECT i.name, ci.quantity
                FROM character_inventory ci
                JOIN ingredients i ON i.id = ci.ingredient_id
                """
            ).fetchall()
        )
        known_count = conn.execute(
            "SELECT COUNT(*) FROM character_known_effects"
        ).fetchone()[0]

    assert inventory == {"Blue Mountain Flower": 3, "Wheat": 2}
    assert known_count == 3


def test_import_skyrim_bridge_rejects_unknown_ingredient(tmp_path):
    payload = {
        "schema_version": 1,
        "character": "Dragonborn",
        "inventory": [{"name": "Not A Skyrim Ingredient", "quantity": 1}],
    }

    with pytest.raises(ValueError, match="Unknown ingredients"):
        apply_bridge_export(payload, tmp_path, "replace")


def test_import_skyrim_bridge_rejects_wrong_effect_for_ingredient(tmp_path):
    payload = {
        "schema_version": 1,
        "character": "Dragonborn",
        "known_effects": [
            {"ingredient": "Blue Mountain Flower", "effects": ["Waterbreathing"]}
        ],
    }

    with pytest.raises(ValueError, match="does not have effect"):
        apply_bridge_export(payload, tmp_path, "replace")
