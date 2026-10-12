# -*- mode: python ; coding: utf-8 -*-
# Uso: pyinstaller packaging/filepilot.spec --noconfirm
# Gera dist/FilePilot/FilePilot.exe em modo --onedir: as bibliotecas do PySide6
# ficam como arquivos separados na pasta (decisao da stack para a licenca LGPL).
from pathlib import Path

# SPECPATH e a pasta deste arquivo (packaging/); a raiz do repositorio fica acima.
project_root = str(Path(SPECPATH).parent)

a = Analysis(
    [str(Path(SPECPATH) / "entry.py")],
    pathex=[project_root],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FilePilot",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="FilePilot",
)
