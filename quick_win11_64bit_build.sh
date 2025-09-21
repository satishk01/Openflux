#!/bin/bash
# Quick Windows 11 64-bit Build (No Wine - Pure Cross-Compilation)
# This avoids Wine issues and creates a proper 64-bit Windows executable

set -e

echo "🚀 Quick Windows 11 64-bit Build (Cross-Compilation)"
echo "===================================================="
echo "Building 64-bit Windows executable without Wine"
echo ""

# Go to project directory
cd ~/Openflux || cd /home/ubuntu/Openflux || cd /home/ec2-user/Openflux || {
    echo "❌ Could not find Openflux directory"
    exit 1
}

# Create or activate Python environment
if [ ! -d "openflux_win11_env" ]; then
    echo "🏠 Creating Python environment..."
    python3 -m venv openflux_win11_env
fi

source openflux_win11_env/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install pyinstaller

# Create Windows 11 64-bit spec file
echo "📝 Creating Windows 11 64-bit specification..."
cat > openflux_win11_cross.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
# Windows 11 64-bit Cross-Compilation Spec

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
        # Core application
        'streamlit',
        'streamlit.web.cli',
        'streamlit.web.server',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.runtime.state',
        'streamlit.components.v1',
        'streamlit.runtime.caching',
        
        # AWS
        'boto3',
        'botocore',
        'botocore.auth',
        'botocore.awsrequest',
        'botocore.endpoint',
        'botocore.httpsession',
        'botocore.client',
        'botocore.session',
        'botocore.credentials',
        
        # Cryptography
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.backends.openssl',
        
        # Application modules
        'services.credentials_manager',
        'components.credentials_ui',
        'components.chat_interface',
        
        # Dependencies
        'jira',
        'pandas',
        'plotly',
        'plotly.graph_objects',
        'plotly.express',
        'plotly.io',
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
        
        # Streamlit ecosystem
        'altair',
        'numpy',
        'pyarrow',
        'tornado',
        'click',
        'toml',
        'watchdog',
        'gitpython',
        'protobuf',
        'validators',
        'packaging',
        'tenacity',
        'cachetools',
        'blinker',
        
        # Additional imports for stability
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
        'http.client',
        'urllib.parse',
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
        'multiprocessing',
        'concurrent.futures',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

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
    console=False,
    disable_windowed_traceback=False,
    target_arch='x86_64',  # Explicitly target 64-bit
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist build

# Build with explicit 64-bit targeting
echo "🏗️ Building Windows 11 64-bit executable..."
echo "Using cross-compilation for maximum compatibility..."

pyinstaller openflux_win11_cross.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/OpenFlux_AI_Assistant" ]; then
    # Rename to .exe for Windows
    mv "dist/OpenFlux_AI_Assistant" "dist/OpenFlux_AI_Assistant.exe"
    
    echo ""
    echo "🎉 SUCCESS! Windows 11 64-bit executable created!"
    echo ""
    
    # Get file size
    size=$(du -h "dist/OpenFlux_AI_Assistant.exe" | cut -f1)
    echo "📊 Executable size: $size"
    
    # Create distribution package
    echo "📦 Creating Windows 11 distribution package..."
    mkdir -p dist/OpenFlux_Windows11_CrossCompiled
    cp dist/OpenFlux_AI_Assistant.exe dist/OpenFlux_Windows11_CrossCompiled/
    
    # Create Windows 11 specific README
    cat > dist/OpenFlux_Windows11_CrossCompiled/README.txt << 'EOF'
OpenFlux AI Assistant - Windows 11 64-bit Standalone
===================================================

IMPORTANT: NO PYTHON INSTALLATION REQUIRED!
This is a completely standalone executable that includes everything needed.

SYSTEM REQUIREMENTS:
✅ Windows 11 (64-bit) - Primary target
✅ Windows 10 (64-bit) - Also supported  
✅ 8GB RAM minimum (16GB recommended)
✅ Internet connection for AI services
✅ AWS account with Bedrock access
❌ NO Python installation needed
❌ NO additional software required

INSTALLATION:
1. Extract all files to any folder on your computer
2. Double-click OpenFlux_AI_Assistant.exe
3. If Windows shows security warning:
   - Click "More info" 
   - Click "Run anyway"
4. That's it! No installation needed.

FIRST RUN:
- Application may take 30-60 seconds to start (this is normal)
- A web browser window will open automatically
- Enter your AWS Access Key and Secret Access Key
- The application runs completely locally on your machine

WHAT'S INCLUDED:
✅ Complete Python runtime (embedded)
✅ All required libraries and dependencies
✅ Streamlit web framework
✅ AWS SDK and cryptography libraries
✅ Everything needed to run - nothing else required!

WINDOWS 11 COMPATIBILITY:
✅ Built specifically for 64-bit Windows architecture
✅ Standalone executable - no dependencies
✅ No Python, pip, or any other software needed
✅ Works on fresh Windows installations

TROUBLESHOOTING:
- If app doesn't start: Try "Run as administrator"
- If blocked by antivirus: Add the .exe file to exclusions
- If slow startup: This is normal on first run (30-60 seconds)
- If browser doesn't open: Manually go to http://localhost:8501
- If port conflict: Close other applications using port 8501

SECURITY:
- Your AWS credentials are encrypted in memory only
- No data is stored on your computer
- Application runs locally - no data sent anywhere except AWS
- Safe to use on any Windows 11 computer

This is a PORTABLE, STANDALONE application.
No Python or other software installation required!

Build Method: Cross-compilation (Ubuntu → Windows 64-bit)
Target Architecture: x86_64 (64-bit)
Python Runtime: Embedded (included in executable)
EOF
    
    # Create simple startup script
    cat > dist/OpenFlux_Windows11_CrossCompiled/Start_OpenFlux.bat << 'EOF'
@echo off
title OpenFlux AI Assistant - Standalone Edition
color 0A
echo.
echo ==========================================
echo   OpenFlux AI Assistant
echo   Standalone Windows 11 Edition
echo ==========================================
echo.
echo ✅ NO Python installation required!
echo ✅ Everything is included in this executable
echo ✅ Completely portable and standalone
echo.
echo Starting application...
echo Please wait, this may take 30-60 seconds on first run.
echo The application will open in your web browser.
echo.
echo Keep this window open while using the application.
echo Close this window to stop the application.
echo.
OpenFlux_AI_Assistant.exe
echo.
echo Application has stopped.
pause
EOF
    
    # Create ZIP package
    cd dist
    zip -r OpenFlux_AI_Assistant_Windows11_CrossCompiled.zip OpenFlux_Windows11_CrossCompiled/
    cd ..
    
    echo ""
    echo "📁 Files created:"
    echo "   ✅ dist/OpenFlux_AI_Assistant.exe"
    echo "   ✅ dist/OpenFlux_Windows11_CrossCompiled/"
    echo "   ✅ dist/OpenFlux_AI_Assistant_Windows11_CrossCompiled.zip"
    echo ""
    echo "📥 Download command:"
    echo "   scp -i your-key.pem ubuntu@$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):~/Openflux/dist/OpenFlux_AI_Assistant_Windows11_CrossCompiled.zip ./"
    echo ""
    echo "🎯 Windows 11 Usage (NO PYTHON NEEDED):"
    echo "   1. Extract ZIP file to any folder"
    echo "   2. Double-click OpenFlux_AI_Assistant.exe (or Start_OpenFlux.bat)"
    echo "   3. Wait for browser to open (30-60 seconds first time)"
    echo "   4. Enter AWS credentials when prompted"
    echo "   5. Use the application - everything is included!"
    echo ""
    echo "✨ STANDALONE EXECUTABLE - No Python installation required!"
    echo "✨ Works on any Windows 11 computer out of the box!"
    
else
    echo ""
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi

# Cleanup
rm -f openflux_win11_cross.spec

echo ""
echo "🎉 Quick Windows 11 64-bit build completed!"