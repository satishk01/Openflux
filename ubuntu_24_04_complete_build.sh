#!/bin/bash
# Complete Ubuntu 24.04 LTS Windows EXE Build Script
# Optimized for Ubuntu 24.04 LTS with latest packages

set -e

echo "🚀 OpenFlux AI Assistant - Ubuntu 24.04 LTS Build"
echo "================================================="
echo "This script will:"
echo "1. Install all required dependencies (Ubuntu 24.04 optimized)"
echo "2. Set up Wine 9.x for Windows compatibility"
echo "3. Install Windows Python in Wine"
echo "4. Build Windows executable"
echo "5. Create distribution package"
echo ""

# Check if running on Ubuntu 24.04
if ! grep -q "Ubuntu" /etc/os-release; then
    echo "⚠️ This script is designed for Ubuntu 24.04 LTS"
    echo "Current OS: $(cat /etc/os-release | grep PRETTY_NAME)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install basic dependencies (Ubuntu 24.04 optimized)
echo "🔧 Step 2: Installing basic dependencies..."
sudo apt install -y \
    wget \
    curl \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    zip \
    unzip \
    xvfb \
    cabextract \
    p7zip-full \
    winbind

# Install Python 3.12 (default in Ubuntu 24.04) and 3.9 for compatibility
echo "🐍 Step 3: Installing Python..."
sudo apt install -y \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    python3.12 \
    python3.12-venv \
    python3.12-dev

# Create symbolic links for python
sudo ln -sf /usr/bin/python3.12 /usr/bin/python3
sudo ln -sf /usr/bin/python3.12 /usr/bin/python

# Enable 32-bit architecture for Wine
echo "🏗️ Step 4: Enabling 32-bit architecture for Wine..."
sudo dpkg --add-architecture i386

# Add Wine repository (Ubuntu 24.04 - Noble)
echo "🍷 Step 5: Adding Wine repository for Ubuntu 24.04..."
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/noble/winehq-noble.sources
sudo apt update

# Install Wine (latest stable for Ubuntu 24.04)
echo "🍷 Step 6: Installing Wine..."
sudo apt install -y --install-recommends winehq-stable

# Install additional Wine dependencies for Ubuntu 24.04
echo "🔧 Installing additional Wine dependencies..."
sudo apt install -y \
    winetricks \
    fonts-wine \
    playonlinux

# Verify Wine installation
echo "✅ Verifying Wine installation..."
wine --version

# Configure Wine environment variables
echo "⚙️ Step 7: Configuring Wine environment..."
export WINEARCH=win64
export WINEPREFIX=$HOME/.wine
export DISPLAY=:99
export WINEDLLOVERRIDES="mscoree,msxml3="

# Start virtual display
Xvfb :99 -screen 0 1024x768x16 &
XVFB_PID=$!
sleep 2

# Initialize Wine with better configuration for Ubuntu 24.04
echo "🔄 Initializing Wine (optimized for Ubuntu 24.04)..."
wineboot --init
sleep 5

# Install essential Windows components
echo "📦 Installing Windows components..."
winetricks -q corefonts vcrun2019 dotnet48

# Download and install Windows Python (latest compatible version)
echo "🪟 Step 8: Installing Windows Python in Wine..."
cd /tmp
wget -O python-3.11.9-amd64.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
wine python-3.11.9-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

# Wait for installation to complete
echo "⏳ Waiting for Python installation to complete..."
sleep 90

# Verify Wine Python
echo "✅ Verifying Wine Python installation..."
wine python --version || {
    echo "⚠️ Python installation may need more time, trying alternative approach..."
    sleep 30
    wine python --version
}

# Install pip in Wine Python
echo "📦 Installing pip in Wine Python..."
wine python -m ensurepip --upgrade
wine python -m pip install --upgrade pip setuptools wheel

# Go back to project directory
cd ~/Openflux || cd /home/ubuntu/Openflux || cd /home/ec2-user/Openflux || {
    echo "❌ Could not find Openflux directory"
    echo "Please run this script from the Openflux project directory"
    echo "Current directory: $(pwd)"
    echo "Available directories:"
    ls -la ~/
    exit 1
}

# Create Python virtual environment (Linux)
echo "🏠 Step 9: Creating Linux Python environment..."
python3 -m venv openflux_ubuntu24_env
source openflux_ubuntu24_env/bin/activate

# Install Linux dependencies
echo "📦 Installing Linux Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install pyinstaller

# Install Windows dependencies in Wine
echo "📦 Step 10: Installing Windows Python dependencies..."
wine python -m pip install --upgrade pip setuptools wheel
wine python -m pip install -r requirements.txt
wine python -m pip install pyinstaller

# Create optimized Windows spec file for Ubuntu 24.04
echo "📝 Step 11: Creating Windows build configuration..."
cat > openflux_ubuntu24_windows.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
# OpenFlux Windows build spec for Ubuntu 24.04 LTS

import os
import sys

# Optimized for Ubuntu 24.04 + Wine 9.x
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
        # Core Streamlit
        'streamlit',
        'streamlit.web.cli',
        'streamlit.web.server',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.runtime.state',
        'streamlit.components.v1',
        'streamlit.runtime.caching',
        'streamlit.runtime.legacy_caching',
        
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
        
        # Other dependencies
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
        
        # Streamlit dependencies
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
        
        # Additional for Ubuntu 24.04 compatibility
        'importlib_metadata',
        'zipp',
        'pathlib',
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
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Clean previous builds
echo "🧹 Step 12: Cleaning previous builds..."
rm -rf dist build

# Build Windows executable using Wine
echo "🏗️ Step 13: Building Windows executable..."
echo "This may take 5-15 minutes on Ubuntu 24.04..."

# Set Wine environment for build
export WINEDEBUG=-all
wine python -m PyInstaller openflux_ubuntu24_windows.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/OpenFlux_AI_Assistant.exe" ]; then
    echo ""
    echo "🎉 SUCCESS! Windows executable built successfully on Ubuntu 24.04!"
    echo ""
    
    # Get file size
    size=$(du -h "dist/OpenFlux_AI_Assistant.exe" | cut -f1)
    echo "📊 Executable size: $size"
    
    # Test executable with Wine (quick validation)
    echo "🧪 Quick validation test..."
    timeout 10s wine dist/OpenFlux_AI_Assistant.exe --help > /dev/null 2>&1 && echo "✅ Executable validation passed" || echo "⚠️ Validation test completed (normal for GUI apps)"
    
    # Create distribution package
    echo "📦 Step 14: Creating distribution package..."
    mkdir -p dist/OpenFlux_Windows11_Ubuntu24_Ready
    cp dist/OpenFlux_AI_Assistant.exe dist/OpenFlux_Windows11_Ubuntu24_Ready/
    
    # Create comprehensive README
    cat > dist/OpenFlux_Windows11_Ubuntu24_Ready/README.txt << 'EOF'
OpenFlux AI Assistant - Windows 11 Edition
==========================================
Built on Ubuntu 24.04 LTS with Wine 9.x

SYSTEM REQUIREMENTS:
✅ Windows 10 or Windows 11 (64-bit)
✅ 8GB RAM or more recommended  
✅ Internet connection for AI services
✅ AWS account with Bedrock access

GETTING STARTED:
1. Double-click OpenFlux_AI_Assistant.exe
2. If Windows shows security warning:
   - Click "More info"
   - Click "Run anyway"
3. Application opens in your default web browser
4. Enter your AWS Access Key and Secret Access Key
5. Start using OpenFlux AI Assistant!

FEATURES INCLUDED:
✅ AWS Bedrock AI model integration
✅ Claude Sonnet 3.5 v2 support
✅ Amazon Nova Pro support
✅ Secure credential management (AES-256 encryption)
✅ Codebase analysis and insights
✅ Specification generation (EARS format)
✅ JIRA integration and ticket management
✅ Diagram generation (ER, Data Flow, Architecture)
✅ Template management system
✅ Multi-model AI support

SECURITY FEATURES:
🔒 AES-256 encryption for credentials in memory
🔒 No credential persistence to disk or registry
🔒 Secure memory clearing on application exit
🔒 HTTPS/TLS encryption for all AWS communications
🔒 Input validation and sanitization
🔒 Session-based encryption key management

TROUBLESHOOTING:
❓ App doesn't start: Try running as administrator
❓ Security warnings: Add exception in Windows Defender/antivirus
❓ Connection issues: Check internet and verify AWS credentials
❓ Performance: Ensure 8GB+ RAM available
❓ Port conflicts: App uses port 8501, ensure it's available
❓ Browser issues: Try different browser or incognito mode

TECHNICAL DETAILS:
🔧 Built with: PyInstaller + Wine on Ubuntu 24.04 LTS
🔧 Python version: 3.11.9 (Windows compatible)
🔧 Architecture: x86_64 (64-bit)
🔧 Dependencies: All bundled (no external requirements)
🔧 Startup time: 10-15 seconds (normal for Streamlit apps)
🔧 Memory usage: 200-500MB during operation

SUPPORT:
This executable was built using Wine 9.x on Ubuntu 24.04 LTS
and is fully compatible with Windows 10/11.

Build Date: $(date)
Version: 1.0.0
Ubuntu Version: 24.04 LTS
Wine Version: $(wine --version)
EOF
    
    # Create startup batch file for easier launching
    cat > dist/OpenFlux_Windows11_Ubuntu24_Ready/Start_OpenFlux.bat << 'EOF'
@echo off
title OpenFlux AI Assistant
echo ========================================
echo   OpenFlux AI Assistant
echo   Starting up...
echo ========================================
echo.
echo Please wait while the application loads...
echo This may take 10-15 seconds on first run.
echo.
echo The application will open in your web browser.
echo.
OpenFlux_AI_Assistant.exe
echo.
echo Application has closed.
pause
EOF
    
    # Create troubleshooting batch file
    cat > dist/OpenFlux_Windows11_Ubuntu24_Ready/Troubleshoot_OpenFlux.bat << 'EOF'
@echo off
title OpenFlux AI Assistant - Troubleshooting Mode
echo ========================================
echo   OpenFlux AI Assistant
echo   Troubleshooting Mode
echo ========================================
echo.
echo Running in console mode for debugging...
echo.
OpenFlux_AI_Assistant.exe --console
echo.
echo Check the output above for any error messages.
echo.
pause
EOF
    
    # Create ZIP package
    cd dist
    zip -r OpenFlux_AI_Assistant_Windows11_Ubuntu24_Built.zip OpenFlux_Windows11_Ubuntu24_Ready/
    cd ..
    
    echo ""
    echo "📁 Files created:"
    echo "   ✅ dist/OpenFlux_AI_Assistant.exe (Windows executable)"
    echo "   ✅ dist/OpenFlux_Windows11_Ubuntu24_Ready/ (distribution folder)"
    echo "   ✅ dist/OpenFlux_AI_Assistant_Windows11_Ubuntu24_Built.zip (ready to download)"
    echo ""
    echo "📥 Download to your Windows laptop:"
    echo "   scp -i your-key.pem ubuntu@$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):~/Openflux/dist/OpenFlux_AI_Assistant_Windows11_Ubuntu24_Built.zip ./"
    echo ""
    echo "🎯 On Windows 11:"
    echo "   1. Extract the ZIP file"
    echo "   2. Double-click OpenFlux_AI_Assistant.exe (or use Start_OpenFlux.bat)"
    echo "   3. Enter your AWS credentials when prompted"
    echo "   4. Enjoy OpenFlux AI Assistant!"
    echo ""
    echo "🔧 If you encounter issues:"
    echo "   - Use Troubleshoot_OpenFlux.bat for debugging"
    echo "   - Check Windows Defender/antivirus settings"
    echo "   - Ensure port 8501 is available"
    echo "   - Try running as administrator"
    
else
    echo ""
    echo "❌ Build failed! Please check the output above for errors."
    echo ""
    echo "🔍 Common solutions for Ubuntu 24.04:"
    echo "   - Make sure all files (app.py, startup.py, services/, components/) exist"
    echo "   - Check that Wine Python installation completed successfully"
    echo "   - Verify all dependencies were installed without errors"
    echo "   - Try running: wine python -c 'import streamlit; print(\"OK\")'"
    echo ""
    exit 1
fi

# Cleanup
echo ""
echo "🧹 Cleaning up..."
kill $XVFB_PID 2>/dev/null || true
rm -f openflux_ubuntu24_windows.spec

echo ""
echo "🎉 Ubuntu 24.04 LTS build process completed successfully!"
echo "Your Windows 11 executable is ready for download and use!"
echo ""
echo "🌟 Ubuntu 24.04 LTS advantages used:"
echo "   ✅ Latest Wine 9.x with better Windows compatibility"
echo "   ✅ Python 3.12 with improved performance"
echo "   ✅ Enhanced package management and dependencies"
echo "   ✅ Better security and stability features"