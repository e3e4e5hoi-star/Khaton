from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("khaton") + collect_submodules("studio")

analysis = Analysis(
    ["khaton_studio.py"],
    pathex=["."],
    binaries=[],
    datas=[("studio/assets", "studio/assets")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="KhatonStudio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
