# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for OpenFlux AI Assistant

import os
import sys
from pathlib import Path

# Get the application directory
app_dir = Path(__file__).parent.parent

# Define data files to include
datas = [
    (str(app_dir / 'app.py'), '.'),
    (str(app_dir / 'styles'), 'styles'),
    (str(app_dir / 'templates'), 'templates'),
    (str(app_dir / 'components'), 'components'),
    (str(app_dir / 'services'), 'services'),
    (str(app_dir / 'engines'), 'engines'),
]

# Hidden imports for modules that PyInstaller might miss
hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.script_runner',
    'streamlit.runtime.state',
    'streamlit.components.v1',
    'boto3',
    'botocore',
    'botocore.auth',
    'botocore.awsrequest',
    'botocore.endpoint',
    'botocore.httpsession',
    'cryptography',
    'cryptography.fernet',
    'jira',
    'pandas',
    'plotly',
    'plotly.graph_objects',
    'plotly.express',
    'yaml',
    'markdown',
    'PIL',
    'PIL.Image',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'pydantic',
    'pydantic.dataclasses',
    'pydantic.json',
    'typing_extensions',
    'services.credentials_manager',
    'components.credentials_ui',
    'components.chat_interface',
]

# Modules to exclude to reduce size
excludes = [
    'tkinter',
    'matplotlib',
    'scipy',
    'numpy.distutils',
    'distutils',
    'setuptools',
    'pip',
    'wheel',
    'pytest',
    'test',
    'unittest',
    'doctest',
    'pdb',
    'pydoc',
    'sqlite3',
    'xml',
    'xmlrpc',
    'email',
    'calendar',
    'turtle',
    'curses',
]

block_cipher = None

a = Analysis(
    ['../startup.py'],
    pathex=[str(app_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OpenFlux_AI_Assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(app_dir / 'assets' / 'icon.ico') if (app_dir / 'assets' / 'icon.ico').exists() else None,
)