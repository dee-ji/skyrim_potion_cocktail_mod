# Skyrim Potion Cocktails

Skyrim Potion Cocktails is a local companion app for Skyrim PC players. It helps track alchemy ingredient inventory, known effects, and discovery-focused potion recipes.

## Install

1. Extract the archive to a folder outside `Program Files`, such as `C:\Games\Tools\SkyrimPotionCocktails`.
2. Run `SkyrimPotionCocktails.exe`.
3. Your browser should open to `http://127.0.0.1:8765/`.

If the browser does not open, manually visit:

```text
http://127.0.0.1:8765/
```

## Use

1. Create or select a character.
2. Add the ingredients you have in Skyrim to character inventory.
3. Mark known effects you already discovered.
4. Use the inventory discovery optimizer to find useful recipes.
5. After crafting a potion, click `Created` so the app updates inventory and known effects.

## Saved Data

The app stores character data at:

```text
%LOCALAPPDATA%\Skyrim Potion Cocktails\skyrim_alchemy.db
```

This file is not inside the extracted app folder, so it should survive app upgrades.

## Upgrade

1. Close the app.
2. Replace the extracted app folder with the new version.
3. Run `SkyrimPotionCocktails.exe` again.

Your saved data should remain in `%LOCALAPPDATA%\Skyrim Potion Cocktails\`.

## Uninstall

Delete the extracted app folder.

To remove saved companion-app state too, delete:

```text
%LOCALAPPDATA%\Skyrim Potion Cocktails\
```

## Troubleshooting

- If port `8765` is already in use, run from PowerShell with `--port 8766`.
- If Windows Defender or antivirus flags the executable, check the release notes and archive hash from the download page.
- If character data appears missing after upgrading, confirm `skyrim_alchemy.db` still exists under `%LOCALAPPDATA%\Skyrim Potion Cocktails\`.

