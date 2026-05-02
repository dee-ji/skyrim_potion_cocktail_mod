from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORM_ID_PATTERN = re.compile(r"^[0-9A-F]{8}$")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_base_skyrim_ingredient_mapping_is_complete():
    ingredients = load_json(ROOT / "shared/data/ingredients.json")
    base_names = {item["name"] for item in ingredients if item["source"] == "Skyrim"}
    mapping = load_json(ROOT / "skyrim_mod/data/ingredient-form-map.json")
    mapped_names = {item["name"] for item in mapping["mappings"]}

    assert len(base_names) == 91
    assert mapped_names == base_names


def test_skyrim_ingredient_mapping_shape_and_uniqueness():
    mapping = load_json(ROOT / "skyrim_mod/data/ingredient-form-map.json")

    assert mapping["schema_version"] == 1
    assert mapping["plugin"] == "Skyrim.esm"

    form_ids: set[str] = set()
    names: set[str] = set()
    for item in mapping["mappings"]:
        assert set(item) == {"form_id", "editor_id", "name"}
        assert FORM_ID_PATTERN.match(item["form_id"])
        assert item["form_id"] not in form_ids
        assert item["name"] not in names
        assert item["editor_id"] is None or isinstance(item["editor_id"], str)
        form_ids.add(item["form_id"])
        names.add(item["name"])


def test_deferred_sources_are_explicit():
    ingredients = load_json(ROOT / "shared/data/ingredients.json")
    mapping = load_json(ROOT / "skyrim_mod/data/ingredient-form-map.json")
    all_sources = {item["source"] for item in ingredients}
    deferred = set(mapping["deferred_sources"])

    assert "Skyrim" not in deferred
    assert all_sources - {"Skyrim"} <= deferred
