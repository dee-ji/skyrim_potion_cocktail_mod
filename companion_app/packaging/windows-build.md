# Windows Build Checklist

Use this checklist for Phase 3 Windows companion builds.

## Build

From the repo root on Windows:

```powershell
uv sync --extra build
uv run python tools/build_companion.py
```

Do not run PyInstaller directly unless you are debugging packaging internals. The build script passes the absolute path to:

```text
companion_app\packaging\skyrim-potion-cocktails.spec
```

Expected output:

```text
dist\SkyrimPotionCocktails\
```

The build command runs:

1. shared baseline validation
2. companion runtime validation
3. launcher import check
4. PyInstaller build
5. distribution inspection

## Smoke Test

Run:

```powershell
dist\SkyrimPotionCocktails\SkyrimPotionCocktails.exe
```

Then verify:

- browser opens to `http://127.0.0.1:8765/`
- a character can be created
- inventory can be updated
- known effects can be marked
- closing and reopening preserves state

State should be stored at:

```text
%LOCALAPPDATA%\Skyrim Potion Cocktails\skyrim_alchemy.db
```

## Failure Notes

- If the executable starts but the page cannot load ingredients, check that `dist\SkyrimPotionCocktails\_internal\app\data\ingredients.json` exists.
- If the browser does not open, manually visit `http://127.0.0.1:8765/`.
- If port `8765` is occupied, run the executable from PowerShell with `--port 8766`.
