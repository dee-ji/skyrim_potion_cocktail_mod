# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


repo_root = Path(SPECPATH).parents[1]
companion_root = repo_root / "companion_app"


a = Analysis(
    [str(companion_root / "launcher.py")],
    pathex=[str(companion_root / "runtime")],
    binaries=[],
    datas=[
        (str(companion_root / "runtime" / "app" / "data"), "app/data"),
        (str(companion_root / "runtime" / "app" / "static"), "app/static"),
    ],
    hiddenimports=[
        "app.app_factory",
        "app.config",
        "app.db",
        "app.main",
        "app.rarity",
        "app.routes.characters",
        "app.routes.ingredients",
        "app.routes.pages",
        "app.schemas",
        "app.services",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SkyrimPotionCocktails",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SkyrimPotionCocktails",
)
