.PHONY: companion-check companion-build companion-run shared-validate runtime-validate runtime-sync

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

runtime-sync:
	uv run python tools/sync_companion_runtime.py
