#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FORM_ID_PATTERN = re.compile(r"^[0-9A-F]{8}$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_mapping(root: Path) -> list[str]:
    errors: list[str] = []
    ingredients = load_json(root / "shared/data/ingredients.json")
    mapping = load_json(root / "skyrim_mod/data/ingredient-form-map.json")

    base_names = {item["name"] for item in ingredients if item["source"] == "Skyrim"}
    all_sources = {item["source"] for item in ingredients}
    mappings = mapping.get("mappings", [])
    deferred_sources = set(mapping.get("deferred_sources", []))

    if mapping.get("schema_version") != 1:
        errors.append("Mapping schema_version must be 1")
    if mapping.get("plugin") != "Skyrim.esm":
        errors.append("Phase 5 mapping plugin must be Skyrim.esm")
    if not isinstance(mappings, list) or not mappings:
        errors.append("Mapping must contain a non-empty mappings list")
        return errors

    mapped_names: set[str] = set()
    form_ids: set[str] = set()
    for index, item in enumerate(mappings):
        if not isinstance(item, dict):
            errors.append(f"mappings[{index}] must be an object")
            continue
        if set(item) != {"form_id", "editor_id", "name"}:
            errors.append(
                f"mappings[{index}] must contain form_id, editor_id, and name"
            )
            continue

        form_id = item["form_id"]
        name = item["name"]
        editor_id = item["editor_id"]

        if not isinstance(form_id, str) or not FORM_ID_PATTERN.match(form_id):
            errors.append(f"Invalid form_id for {name!r}: {form_id!r}")
        elif form_id in form_ids:
            errors.append(f"Duplicate form_id: {form_id}")
        form_ids.add(form_id)

        if not isinstance(name, str) or not name:
            errors.append(f"Invalid mapped name at index {index}")
        elif name in mapped_names:
            errors.append(f"Duplicate mapped name: {name}")
        mapped_names.add(name)

        if editor_id is not None and not isinstance(editor_id, str):
            errors.append(f"editor_id must be null or string for {name!r}")

    missing = sorted(base_names - mapped_names)
    extra = sorted(mapped_names - base_names)
    if missing:
        errors.append("Missing base Skyrim mappings: " + ", ".join(missing))
    if extra:
        errors.append("Mappings not in base Skyrim source set: " + ", ".join(extra))

    undocumented_deferred = sorted(all_sources - {"Skyrim"} - deferred_sources)
    if undocumented_deferred:
        errors.append(
            "Deferred sources not documented: " + ", ".join(undocumented_deferred)
        )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Skyrim ingredient form mapping."
    )
    parser.add_argument(
        "--root", type=Path, default=repo_root(), help="Repository root."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors = validate_mapping(args.root.expanduser().resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Skyrim ingredient mapping validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
