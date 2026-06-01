# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['67mango.py'],
    pathex=[],
    binaries=[],
    datas=[('1.png', '.'), ('2.png', '.'), ('3.png', '.')],
    hiddenimports=[],
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
    name='Water Whack-a-Mole',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='Water Whack-a-Mole',
)
app = BUNDLE(
    coll,
    name='Water Whack-a-Mole.app',
    icon=None,
    bundle_identifier=None,
)
