#!/bin/bash
# Quick build script for OpenFlux AI Assistant

set -e

echo "🚀 Quick Build - OpenFlux AI Assistant"

# Activate virtual environment
source openflux_build_env/bin/activate

# Clean previous builds
rm -rf dist build *.spec

# Create a simple spec file directly
cat > openflux_simple.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

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
        'boto3',
        'botocore',
        'cryptography',
        'cryptography.fernet',
        'services.credentials_manager',
        'components.credentials_ui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Build the executable
echo "🏗️ Building executable..."
pyinstaller openflux_simple.spec --clean --noconfirm

# Check if successful
if [ -f "dist/OpenFlux_AI_Assistant" ]; then
    echo "✅ Build successful!"
    chmod +x "dist/OpenFlux_AI_Assistant"
    
    size=$(du -h "dist/OpenFlux_AI_Assistant" | cut -f1)
    echo "📊 Executable size: $size"
    
    echo ""
    echo "🎉 Build completed!"
    echo "📁 Executable: ./dist/OpenFlux_AI_Assistant"
    echo ""
    echo "🧪 To test: ./dist/OpenFlux_AI_Assistant"
else
    echo "❌ Build failed!"
    exit 1
fi

# Cleanup
rm -f openflux_simple.spec