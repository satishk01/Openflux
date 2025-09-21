#!/bin/bash
# Quick Windows build using cross-compilation (no Docker needed)

set -e

echo "🚀 Quick Windows Build on EC2 (Cross-compilation)"
echo "================================================"

# Activate virtual environment
source openflux_build_env/bin/activate

# Install cross-compilation tools
echo "📦 Installing cross-compilation dependencies..."
pip install pyinstaller-hooks-contrib
pip install pefile
pip install pywin32-ctypes

# Create a Windows-targeted spec file
echo "📝 Creating Windows cross-compilation spec..."
cat > openflux_cross_windows.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
# Cross-compilation spec for Windows

import sys
import os

# Force Windows platform
import PyInstaller.utils.win32.versioninfo as vi

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
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.backends',
        'services.credentials_manager',
        'components.credentials_ui',
        'components.chat_interface',
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
        'altair',
        'numpy',
        'pyarrow',
        'tornado',
        'click',
        'toml',
        'watchdog',
        'gitpython',
        'protobuf',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
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
        'sqlite3',
        'xml.etree',
        'xmlrpc',
        'email',
        'calendar',
        'turtle',
        'curses',
        'readline',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

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
    console=False,
    disable_windowed_traceback=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist build

# Build the executable
echo "🔨 Building Windows executable (cross-compilation)..."
pyinstaller openflux_cross_windows.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/OpenFlux_AI_Assistant" ]; then
    echo "✅ Cross-compilation build completed!"
    
    # Rename to .exe for Windows
    mv "dist/OpenFlux_AI_Assistant" "dist/OpenFlux_AI_Assistant.exe"
    
    echo "📊 File details:"
    ls -lh dist/OpenFlux_AI_Assistant.exe
    
    echo ""
    echo "📦 Creating Windows distribution package..."
    
    # Create distribution folder
    mkdir -p dist/OpenFlux_Windows_Portable
    cp dist/OpenFlux_AI_Assistant.exe dist/OpenFlux_Windows_Portable/
    
    # Create README
    cat > dist/OpenFlux_Windows_Portable/README.txt << 'EOF'
OpenFlux AI Assistant - Windows Edition (Cross-compiled)
=======================================================

IMPORTANT: This executable was cross-compiled on Linux.
It should work on Windows 10/11, but if you encounter issues,
please use the Docker-built version instead.

GETTING STARTED:
1. Double-click OpenFlux_AI_Assistant.exe
2. If Windows shows a security warning, click "More info" then "Run anyway"
3. The application will open in your default web browser
4. Enter your AWS Access Key and Secret Access Key when prompted
5. Start using OpenFlux AI Assistant!

TROUBLESHOOTING:
- If the app doesn't start, try running as administrator
- If you get DLL errors, you may need the Docker-built version
- Make sure your antivirus isn't blocking the application

This is a cross-compiled version. For best compatibility,
use the Docker-built version if available.
EOF
    
    # Create ZIP package
    cd dist
    zip -r OpenFlux_AI_Assistant_Windows_CrossCompiled.zip OpenFlux_Windows_Portable/
    cd ..
    
    echo ""
    echo "🎉 Cross-compiled Windows executable ready!"
    echo ""
    echo "📁 Files created:"
    echo "   - dist/OpenFlux_AI_Assistant.exe"
    echo "   - dist/OpenFlux_AI_Assistant_Windows_CrossCompiled.zip"
    echo ""
    echo "📥 Download command for your Windows laptop:"
    echo "   scp -i your-key.pem ec2-user@$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):~/Openflux/dist/OpenFlux_AI_Assistant_Windows_CrossCompiled.zip ./"
    echo ""
    echo "⚠️ Note: This is cross-compiled. If it doesn't work on Windows,"
    echo "   use the Docker build method: ./build_windows_on_ec2.sh"
    
else
    echo "❌ Cross-compilation failed!"
    exit 1
fi

# Cleanup
rm -f openflux_cross_windows.spec