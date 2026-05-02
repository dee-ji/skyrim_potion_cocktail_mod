.PHONY: companion-check companion-build companion-run shared-validate runtime-validate skyrim-mapping-validate bridge-import-example source-refresh

companion-check:
	uv run python tools/build_companion.py --skip-pyinstaller

companion-build:
	uv run python tools/build_companion.py

companion-run:
	uv run python companion_app/launcher.py

shared-validate:
	uv run python tools/validate_shared_baseline.py

runtime-validate:
	uv run python tools/validate_companion_runtime.py

skyrim-mapping-validate:
	uv run python tools/validate_skyrim_mapping.py

bridge-import-example:
	uv run python tools/import_skyrim_bridge.py shared/exchange/examples/skyrim-bridge-export.json --state-dir /tmp/spc-bridge-test

source-refresh:
ifndef SKYRIM_POTION_SOURCE_APP
	$(error Set SKYRIM_POTION_SOURCE_APP=/path/to/skyrim_potion_cocktail_app)
endif
	uv run python tools/build_companion.py --refresh-source --skip-pyinstaller --source "$$SKYRIM_POTION_SOURCE_APP"
