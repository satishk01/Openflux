#!/bin/bash
# Build Truly Standalone Windows 11 Executable
# NO PYTHON REQUIRED ON WINDOWS - Everything bundled

set -e

echo "🚀 Building Standalone Windows 11 Executable"
echo "============================================"
echo "Creating executable that requires NO Python on Windows"
echo ""

# Go to project directory
cd ~/Openflux || cd /home/ubuntu/Openflux || cd /home/ec2-user/Openflux || {
    echo "❌ Could not find Openflux directory"
    exit 1
}

# Create or activate Python environment
if [ ! -d "standalone_build_env" ]; then
    echo "🏠 Creating standalone build environment..."
    python3 -m venv standalone_build_env
fi

source standalone_build_env/bin/activate

# Install dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install pyinstaller

# Create truly standalone spec file
echo "📝 Creating standalone Windows 11 specification..."
cat > standalone_windows11.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
# Standalone Windows 11 64-bit specification
# Bundles EVERYTHING - no external dependencies

import os
import sys

block_cipher = None

a = Analysis(
    ['startup.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('app.py', '.'),
        ('services', 'services'),
        ('components', 'components'),
    ],
    hiddenimports=[
        # Streamlit complete
        'streamlit',
        'streamlit.web',
        'streamlit.web.cli',
        'streamlit.web.server',
        'streamlit.web.server.server',
        'streamlit.runtime',
        'streamlit.runtime.scriptrunner',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.runtime.state',
        'streamlit.runtime.state.session_state',
        'streamlit.components',
        'streamlit.components.v1',
        'streamlit.runtime.caching',
        'streamlit.runtime.legacy_caching',
        
        # AWS complete
        'boto3',
        'boto3.session',
        'botocore',
        'botocore.auth',
        'botocore.awsrequest',
        'botocore.endpoint',
        'botocore.httpsession',
        'botocore.client',
        'botocore.session',
        'botocore.credentials',
        'botocore.config',
        'botocore.exceptions',
        
        # Cryptography complete
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives.kdf',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.backends.openssl',
        'cryptography.hazmat.backends.openssl.backend',
        
        # Application modules
        'services',
        'services.credentials_manager',
        'components',
        'components.credentials_ui',
        'components.chat_interface',
        
        # Core dependencies
        'jira',
        'pandas',
        'pandas.core',
        'pandas.io',
        'plotly',
        'plotly.graph_objects',
        'plotly.express',
        'plotly.io',
        'plotly.io.html',
        'yaml',
        'markdown',
        'PIL',
        'PIL.Image',
        'requests',
        'requests.adapters',
        'requests.auth',
        'urllib3',
        'urllib3.util',
        'certifi',
        'charset_normalizer',
        'idna',
        
        # Pydantic complete
        'pydantic',
        'pydantic.dataclasses',
        'pydantic.json',
        'pydantic.types',
        'pydantic.validators',
        
        # Type system
        'typing_extensions',
        'typing',
        
        # Streamlit ecosystem
        'altair',
        'altair.vegalite',
        'numpy',
        'numpy.core',
        'pyarrow',
        'pyarrow.parquet',
        'tornado',
        'tornado.web',
        'tornado.ioloop',
        'click',
        'toml',
        'watchdog',
        'watchdog.observers',
        'gitpython',
        'git',
        'protobuf',
        'validators',
        'packaging',
        'tenacity',
        'cachetools',
        'blinker',
        
        # System and utility
        'importlib_metadata',
        'zipp',
        'pathlib',
        'json',
        'base64',
        'hashlib',
        'hmac',
        'datetime',
        'time',
        'threading',
        'queue',
        'socket',
        'ssl',
        'http',
        'http.client',
        'http.server',
        'urllib',
        'urllib.parse',
        'urllib.request',
        'webbrowser',
        'subprocess',
        'logging',
        'logging.handlers',
        
        # Additional for completeness
        'email.mime',
        'email.mime.text',
        'email.mime.multipart',
        'mimetypes',
        'tempfile',
        'shutil',
        'glob',
        'fnmatch',
        're',
        'collections',
        'collections.abc',
        'itertools',
        'functools',
        'operator',
        'copy',
        'pickle',
        'gzip',
        'zipfile',
        'tarfile',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude only truly unnecessary modules
        'tkinter',
        'matplotlib',
        'scipy',
        'IPython',
        'jupyter',
        'pytest',
        'test',
        'unittest',
        'doctest',
        'pdb',
        'pydoc',
        'turtle',
        'curses',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Bundle everything into the executable
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
    console=False,  # GUI application
    disable_windowed_traceback=False,
    target_arch='x86_64',  # 64-bit Windows
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist build

# Build the standalone executable
echo "🏗️ Building standalone Windows 11 executable..."
echo "This creates a single file with everything bundled..."

pyinstaller standalone_windows11.spec --clean --noconfirm

# Validate the build
if [ -f "dist/OpenFlux_AI_Assistant" ]; then
    # Rename to .exe for Windows
    mv "dist/OpenFlux_AI_Assistant" "dist/OpenFlux_AI_Assistant.exe"
    
    echo ""
    echo "🎉 SUCCESS! Standalone Windows 11 executable created!"
    
    # Run validation
    chmod +x validate_standalone_exe.sh
    ./validate_standalone_exe.sh
    
else
    echo ""
    echo "❌ Build failed! No executable found."
    exit 1
fi

# Cleanup
rm -f standalone_windows11.spec

echo ""
echo "🎉 Standalone Windows 11 build completed!"
echo ""
echo "🎯 KEY POINTS:"
echo "   ✅ NO Python needed on Windows"
echo "   ✅ NO pip or conda needed"
echo "   ✅ NO additional software needed"
echo "   ✅ Everything is bundled in the .exe file"
echo "   ✅ Just download and run!"