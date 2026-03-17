# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

# Coleta metadados e arquivos do streamlit e dependências
datas = copy_metadata('streamlit')
datas += collect_data_files('streamlit', include_py_files=True)
datas += collect_data_files('altair')
datas += collect_data_files('pandas')
datas += collect_data_files('pyarrow')
datas += [('streamlit_app.py', '.'), ('processador.py', '.')]

# Módulos ocultos para resolver erros de importação (NumPy, Tkinter, LXML)
hiddenimports = collect_submodules('streamlit')
hiddenimports += [
    'tkinter', 
    'tkinter.filedialog', 
    'lxml.etree', 
    'openpyxl', 
    'numpy', 
    'pandas'
]

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ProcessadorXML',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False, # OBRIGATÓRIO: Mantido False para evitar erro de DLL
    console=False,
    icon='app_icon.ico',
)