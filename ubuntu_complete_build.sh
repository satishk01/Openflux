#!/bin/bash
# Complete Ubuntu 20.04 Windows EXE Build Script
# This script sets up everything from scratch on Ubuntu 20.04

set -e

echo "🚀 OpenFlux AI Assistant - Complete Ubuntu 20.04 Build"
echo "======================================================"
echo "This script will:"
echo "1. Install all required dependencies"
echo "2. Set up Wine for Windows compatibility"
echo "3. Install Windows Python in Wine"
echo "4. Build Windows executable"
echo "5. Create distribution package"
echo ""

# Check if running on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
    echo "⚠️ This script is designed for Ubuntu 20.04"
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

# Install basic dependencies
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
    xvfb

# Install Python 3.9
echo "🐍 Step 3: Installing Python 3.9..."
sudo apt install -y \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    python3-pip

# Create symbolic links for python
sudo ln -sf /usr/bin/python3.9 /usr/bin/python3
sudo ln -sf /usr/bin/python3.9 /usr/bin/python

# Enable 32-bit architecture for Wine
echo "🏗️ Step 4: Enabling 32-bit architecture for Wine..."
sudo dpkg --add-architecture i386

# Add Wine repository
echo "🍷 Step 5: Adding Wine repository..."
wget -nc https://dl.winehq.org/wine-builds/winehq.key
sudo apt-key add winehq.key
sudo add-apt-repository 'deb https://dl.winehq.org/wine-builds/ubuntu/ focal main'
sudo apt update

# Install Wine
echo "🍷 Step 6: Installing Wine..."
sudo apt install -y --install-recommends winehq-stable

# Verify Wine installation
echo "✅ Verifying Wine installation..."
wine --version

# Configure Wine
echo "⚙️ Step 7: Configuring Wine..."
export WINEARCH=win64
export WINEPREFIX=$HOME/.wine
export DISPLAY=:99

# Start virtual display
Xvfb :99 -screen 0 1024x768x16 &
XVFB_PID=$!

# Initialize Wine
echo "🔄 Initializing Wine (this may take a few minutes)..."
winecfg &
sleep 10
pkill winecfg || true

# Download and install Windows Python
echo "🪟 Step 8: Installing Windows Python in Wine..."
cd /tmp
wget -O python-3.9.18-amd64.exe https://www.python.org/ftp/python/3.9.18/python-3.9.18-amd64.exe
wine python-3.9.18-amd64.exe /quiet InstallAllUsers=1 PrependPath=1

# Wait for installation to complete
echo "⏳ Waiting for Python installation to complete..."
sleep 60

# Verify Wine Python
echo "✅ Verifying Wine Python installation..."
wine python --version

# Install pip in Wine Python
echo "📦 Installing pip in Wine Python..."
wine python -m ensurepip --upgrade
wine python -m pip install --upgrade pip setuptools wheel

# Go back to project directory
cd ~/Openflux || cd /home/ubuntu/Openflux || cd /home/ec2-user/Openflux || {
    echo "❌ Could not find Openflux directory"
    echo "Please run this script from the Openflux project directory"
    exit 1
}

# Create Python virtual environment (Linux)
echo "🏠 Step 9: Creating Linux Python environment..."
python3.9 -m venv openflux_ubuntu_env
source openflux_ubuntu_env/bin/activate

# Install Linux dependencies
echo "📦 Installing Linux Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install pyinstaller

# Install Windows dependencies in Wine
echo "📦 Step 10: Installing Windows Python dependencies..."
wine python -m pip install -r requirements.txt
wine python -m pip install pyinstaller

# Create optimized Windows spec file
echo "📝 Step 11: Creating Windows build configuration..."
cat > openflux_ubuntu_windows.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
# OpenFlux Windows build spec for Ubuntu

import os
import sys

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
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.runtime.state',
        'streamlit.components.v1',
        
        # AWS
        'boto3',
        'botocore',
        'botocore.auth',
        'botocore.awsrequest',
        'botocore.endpoint',
        'botocore.httpsession',
        
        # Cryptography
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
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
echo "This may take 5-10 minutes..."

wine python -m PyInstaller openflux_ubuntu_windows.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/OpenFlux_AI_Assistant.exe" ]; then
    echo ""
    echo "🎉 SUCCESS! Windows executable built successfully!"
    echo ""
    
    # Get file size
    size=$(du -h "dist/OpenFlux_AI_Assistant.exe" | cut -f1)
    echo "📊 Executable size: $size"
    
    # Create distribution package
    echo "📦 Step 14: Creating distribution package..."
    mkdir -p dist/OpenFlux_Windows11_Ready
    cp dist/OpenFlux_AI_Assistant.exe dist/OpenFlux_Windows11_Ready/
    
    # Create comprehensive README
    cat > dist/OpenFlux_Windows11_Ready/README.txt << 'EOF'
OpenFlux AI Assistant - Windows 11 Edition
==========================================
Built on Ubuntu 20.04 with Wine

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
✅ Secure credential management
✅ Codebase analysis
✅ Spec generation
✅ JIRA integration
✅ Diagram generation

SECURITY NOTES:
🔒 Your AWS credentials are encrypted in memory only
🔒 Credentials are never saved to disk
🔒 All data cleared when you close the application
🔒 HTTPS/TLS encryption for all AWS communications

TROUBLESHOOTING:
❓ App doesn't start: Try running as administrator
❓ Security warnings: Add exception in Windows Defender
❓ Connection issues: Check internet and AWS credentials
❓ Performance: Ensure 8GB+ RAM available

SUPPORT:
This executable was built using Wine on Ubuntu 20.04
and should be fully compatible with Windows 10/11.

Build Date: $(date)
Version: 1.0.0
EOF
    
    # Create startup batch file for easier launching
    cat > dist/OpenFlux_Windows11_Ready/Start_OpenFlux.bat << 'EOF'
@echo off
echo Starting OpenFlux AI Assistant...
echo Please wait while the application loads...
OpenFlux_AI_Assistant.exe
EOF
    
    # Create ZIP package
    cd dist
    zip -r OpenFlux_AI_Assistant_Windows11_Ubuntu_Built.zip OpenFlux_Windows11_Ready/
    cd ..
    
    echo ""
    echo "📁 Files created:"
    echo "   ✅ dist/OpenFlux_AI_Assistant.exe (Windows executable)"
    echo "   ✅ dist/OpenFlux_Windows11_Ready/ (distribution folder)"
    echo "   ✅ dist/OpenFlux_AI_Assistant_Windows11_Ubuntu_Built.zip (ready to download)"
    echo ""
    echo "📥 Download to your Windows laptop:"
    echo "   scp -i your-key.pem ubuntu@$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):~/Openflux/dist/OpenFlux_AI_Assistant_Windows11_Ubuntu_Built.zip ./"
    echo ""
    echo "🎯 On Windows 11:"
    echo "   1. Extract the ZIP file"
    echo "   2. Double-click OpenFlux_AI_Assistant.exe"
    echo "   3. Enter your AWS credentials"
    echo "   4. Enjoy OpenFlux AI Assistant!"
    
else
    echo ""
    echo "❌ Build failed! Please check the output above for errors."
    echo ""
    echo "🔍 Common solutions:"
    echo "   - Make sure all files (app.py, startup.py, services/, components/) exist"
    echo "   - Check that Wine Python installation completed successfully"
    echo "   - Verify all dependencies were installed"
    echo ""
    exit 1
fi

# Cleanup
echo ""
echo "🧹 Cleaning up..."
kill $XVFB_PID 2>/dev/null || true
rm -f openflux_ubuntu_windows.spec

echo ""
echo "🎉 Ubuntu 20.04 build process completed successfully!"
echo "Your Windows 11 executable is ready for download and use!"