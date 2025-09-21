#!/usr/bin/env python3
"""
Complete Windows build script for OpenFlux AI Assistant
This script creates all necessary files for Windows build
"""

import os
import sys
from pathlib import Path

def create_windows_spec():
    """Create optimized Windows PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for OpenFlux AI Assistant (Windows 11 Compatible)

import os
import sys
from pathlib import Path

# Get the application directory
app_dir = Path.cwd()

# Define data files to include
datas = [
    ('app.py', '.'),
    ('services', 'services'),
    ('components', 'components'),
]

# Check if optional directories exist and add them
optional_dirs = ['styles', 'templates', 'engines', 'assets']
for dir_name in optional_dirs:
    if (app_dir / dir_name).exists():
        datas.append((dir_name, dir_name))

# Hidden imports for modules that PyInstaller might miss
hiddenimports = [
    # Streamlit core
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.script_runner',
    'streamlit.runtime.state',
    'streamlit.components.v1',
    'streamlit.runtime.caching',
    'streamlit.runtime.legacy_caching',
    
    # AWS and Boto3
    'boto3',
    'botocore',
    'botocore.auth',
    'botocore.awsrequest',
    'botocore.endpoint',
    'botocore.httpsession',
    'botocore.client',
    'botocore.session',
    
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
    
    # Additional dependencies
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
    'validators',
    'watchdog',
    'gitpython',
    'protobuf',
]

# Modules to exclude to reduce size
excludes = [
    'tkinter',
    'matplotlib',
    'scipy',
    'IPython',
    'jupyter',
    'notebook',
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
]

block_cipher = None

a = Analysis(
    ['startup.py'],
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
    console=False,  # Set to False for Windows GUI app
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if Path('assets/icon.ico').exists() else None,
    version='version_info.txt' if Path('version_info.txt').exists() else None,
)
'''
    
    with open('openflux_windows11.spec', 'w') as f:
        f.write(spec_content)
    print("✅ Created openflux_windows11.spec")

def create_version_info():
    """Create Windows version info file"""
    version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'OpenFlux AI'),
        StringStruct(u'FileDescription', u'OpenFlux AI Assistant'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'OpenFlux_AI_Assistant'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2024 OpenFlux AI'),
        StringStruct(u'OriginalFilename', u'OpenFlux_AI_Assistant.exe'),
        StringStruct(u'ProductName', u'OpenFlux AI Assistant'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w') as f:
        f.write(version_info)
    print("✅ Created version_info.txt")

def create_windows_build_script():
    """Create comprehensive Windows build script"""
    build_script = '''@echo off
REM OpenFlux AI Assistant - Windows 11 Build Script
REM Run this script on a Windows 11 machine

echo 🚀 OpenFlux AI Assistant - Windows 11 Build
echo ============================================

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.9+ from python.org
    echo 📥 Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: app.py not found. Please run this script from the project root directory.
    pause
    exit /b 1
)

echo ✅ Project files found

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv openflux_windows_env
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo 📁 Activating virtual environment...
call openflux_windows_env\\Scripts\\activate.bat

REM Upgrade pip
echo 📈 Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Install PyInstaller
echo 🔧 Installing PyInstaller...
pip install pyinstaller==6.16.0
if %errorlevel% neq 0 (
    echo ❌ Failed to install PyInstaller
    pause
    exit /b 1
)

REM Create assets directory
if not exist "assets" mkdir assets

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Build the executable
echo 🏗️ Building Windows executable...
pyinstaller openflux_windows11.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo ❌ Build failed!
    echo 💡 Common solutions:
    echo    - Make sure all dependencies are installed
    echo    - Check that startup.py and app.py exist
    echo    - Try running: pip install --upgrade pyinstaller
    pause
    exit /b 1
)

REM Check if build was successful
if exist "dist\\OpenFlux_AI_Assistant.exe" (
    echo ✅ Build successful!
    
    REM Get file size
    for %%A in ("dist\\OpenFlux_AI_Assistant.exe") do (
        set size=%%~zA
        set /a sizeMB=!size!/1024/1024
    )
    
    echo 📊 Executable size: %sizeMB% MB
    echo 📁 Location: dist\\OpenFlux_AI_Assistant.exe
    
    REM Create distribution folder
    echo 📦 Creating distribution package...
    if not exist "dist\\OpenFlux_Portable" mkdir "dist\\OpenFlux_Portable"
    copy "dist\\OpenFlux_AI_Assistant.exe" "dist\\OpenFlux_Portable\\"
    
    REM Create user README
    echo Creating user documentation...
    (
        echo OpenFlux AI Assistant - Windows 11 Edition
        echo ==========================================
        echo.
        echo SYSTEM REQUIREMENTS:
        echo - Windows 10 or Windows 11 ^(64-bit^)
        echo - 8GB RAM or more recommended
        echo - Internet connection for AI services
        echo - AWS account with Bedrock access
        echo.
        echo GETTING STARTED:
        echo 1. Double-click OpenFlux_AI_Assistant.exe
        echo 2. If Windows shows a security warning, click "More info" then "Run anyway"
        echo 3. The application will open in your default web browser
        echo 4. Enter your AWS Access Key and Secret Access Key when prompted
        echo 5. Start using OpenFlux AI Assistant!
        echo.
        echo SECURITY NOTES:
        echo - Your AWS credentials are encrypted and stored only in memory
        echo - Credentials are never saved to disk
        echo - All data is cleared when you close the application
        echo.
        echo TROUBLESHOOTING:
        echo - If the app doesn't start, try running as administrator
        echo - Make sure your AWS credentials have Bedrock access permissions
        echo - Check your internet connection
        echo - Verify your antivirus isn't blocking the application
        echo.
        echo Version: 1.0.0
        echo Compatible with: Windows 10, Windows 11
    ) > "dist\\OpenFlux_Portable\\README.txt"
    
    REM Create ZIP package
    echo 📦 Creating ZIP package...
    powershell -command "Compress-Archive -Path 'dist\\OpenFlux_Portable\\*' -DestinationPath 'dist\\OpenFlux_AI_Assistant_Windows11.zip' -Force"
    
    echo.
    echo 🎉 Build completed successfully!
    echo.
    echo 📋 Files created:
    echo    - dist\\OpenFlux_AI_Assistant.exe ^(main executable^)
    echo    - dist\\OpenFlux_Portable\\ ^(distribution folder^)
    echo    - dist\\OpenFlux_AI_Assistant_Windows11.zip ^(distribution package^)
    echo.
    echo 🧪 To test:
    echo    dist\\OpenFlux_AI_Assistant.exe
    echo.
    echo 📤 Ready for distribution!
    
) else (
    echo ❌ Build failed! Executable not found.
    echo 💡 Check the output above for error details.
)

echo.
echo Press any key to exit...
pause >nul
'''
    
    with open('build_windows11.bat', 'w') as f:
        f.write(build_script)
    print("✅ Created build_windows11.bat")

def create_requirements_windows():
    """Create Windows-specific requirements file"""
    requirements = '''# OpenFlux AI Assistant - Windows Requirements
streamlit>=1.28.0
boto3>=1.34.0
botocore>=1.34.0
requests>=2.31.0
jira>=3.5.0
python-dotenv>=1.0.0
pydantic>=2.5.0
pandas>=2.1.0
plotly>=5.17.0
mermaid-py>=0.3.0
markdown>=3.5.0
PyYAML>=6.0.1
cryptography>=41.0.0
python-multipart>=0.0.6
aiofiles>=23.2.1
httpx>=0.25.0
pillow>=10.1.0
watchdog>=3.0.0
pyinstaller>=6.16.0

# Windows-specific packages
pywin32>=306
pywin32-ctypes>=0.2.0
'''
    
    with open('requirements_windows.txt', 'w') as f:
        f.write(requirements)
    print("✅ Created requirements_windows.txt")

def create_github_actions():
    """Create GitHub Actions workflow for automated Windows builds"""
    workflow = '''name: Build Windows Executable

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip setuptools wheel
        pip install -r requirements_windows.txt
    
    - name: Create build files
      run: |
        python build_windows_complete.py
    
    - name: Build executable
      run: |
        pyinstaller openflux_windows11.spec --clean --noconfirm
    
    - name: Create distribution package
      run: |
        mkdir dist/OpenFlux_Portable
        copy dist/OpenFlux_AI_Assistant.exe dist/OpenFlux_Portable/
        echo "OpenFlux AI Assistant - Windows 11 Edition" > dist/OpenFlux_Portable/README.txt
    
    - name: Upload executable
      uses: actions/upload-artifact@v3
      with:
        name: OpenFlux-Windows11-Executable
        path: dist/OpenFlux_Portable/
        retention-days: 30
    
    - name: Create release (on tag)
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: |
          dist/OpenFlux_AI_Assistant.exe
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'''
    
    os.makedirs('.github/workflows', exist_ok=True)
    with open('.github/workflows/build-windows.yml', 'w') as f:
        f.write(workflow)
    print("✅ Created .github/workflows/build-windows.yml")

def main():
    """Main function to create all Windows build files"""
    print("🚀 Creating Windows 11 build configuration...")
    print("=" * 50)
    
    create_windows_spec()
    create_version_info()
    create_windows_build_script()
    create_requirements_windows()
    create_github_actions()
    
    print("\n🎉 Windows 11 build files created successfully!")
    print("\n📋 Next steps:")
    print("1. Transfer all files to a Windows 11 machine")
    print("2. Run: build_windows11.bat")
    print("3. Or use GitHub Actions for automated builds")
    print("\n📁 Files created:")
    print("   - openflux_windows11.spec (PyInstaller config)")
    print("   - build_windows11.bat (Windows build script)")
    print("   - requirements_windows.txt (Windows dependencies)")
    print("   - version_info.txt (Windows version info)")
    print("   - .github/workflows/build-windows.yml (GitHub Actions)")

if __name__ == "__main__":
    main()