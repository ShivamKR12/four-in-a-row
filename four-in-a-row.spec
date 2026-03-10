# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['four-in-a-row.py'],
    pathex=[],
    binaries=[],
    datas=[('4row_arrow.png', '.'), ('4row_black.png', '.'), ('4row_board.png', '.'), ('4row_computerwinner.png', '.'), ('4row_humanwinner.png', '.'), ('4row_red.png', '.'), ('4row_tie.png', '.'), ('four-in-a-row.png', '.')],
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
    a.binaries,
    a.datas,
    [],
    name='four-in-a-row',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['four-in-a-row.ico'],
)
