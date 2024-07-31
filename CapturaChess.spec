# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=['src/reconocimiento', 'src/interfaz', 'src/IA', 'src/baseDeDatos', ''],
    binaries=[],
    datas=[('src/_internal/resultados', './resultados'), ('src/_internal/icons', './icons'), ('src/_internal/fuentes', './fuentes'), ('D:/PoetryCache/virtualenvs/04-lagloriosa-mAynO3wB-py3.12/Lib/site-packages/ultralytics/cfg/default.yaml', './ultralytics/cfg')],
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
    name='CapturaChess',
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
    icon=['D:\\SecondoProg\\Proyectaso\\proyecto\\04-LaGloriosa\\src\\_internal\\icons\\icon.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CapturaChess',
)
