# Packaging

Phase 1 targets a Windows-friendly companion-app archive suitable for Nexus distribution.

## Initial Build Target

Use PyInstaller to create a one-folder distribution containing:

- the companion launcher executable
- the vendored FastAPI runtime under `runtime/app`
- static frontend assets
- ingredient data

The SQLite user database should not be bundled. It is created in the user's application data directory by `companion_app/launcher.py`.

## Maintainer Flow

From the repo root:

```sh
uv run python tools/build_companion.py
```

Use `uv run python tools/build_companion.py --skip-pyinstaller` to run the preflight checks without producing a packaged build.

The default build flow is independent of the original source app checkout. To intentionally refresh the vendored runtime and shared baseline before building:

```sh
uv run python tools/build_companion.py --refresh-source --source /path/to/skyrim_potion_cocktail_app
```
