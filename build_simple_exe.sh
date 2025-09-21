#!/bin/bash
# Simple executable build - works on any platform

set -e

echo "🚀 Simple Executable Build"
echo "========================="

# Activate virtual environment
source openflux_build_env/bin/activate

# Clean previous builds
rm -rf dist build *.spec

# Create a minimal, working spec file
cat > simple_openflux.spec << 'EOF'
# Simple PyInstaller spec
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
        'boto3',
        'cryptography.fernet',
        'services.credentials_manager',
        'components.credentials_ui',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=True,
)
EOF

# Build the executable
echo "🔨 Building executable..."
pyinstaller simple_openflux.spec --clean --noconfirm

# Check result
if [ -f "dist/OpenFlux_AI_Assistant" ]; then
    echo "✅ Build successful!"
    
    # For Windows compatibility, add .exe extension
    cp "dist/OpenFlux_AI_Assistant" "dist/OpenFlux_AI_Assistant.exe"
    
    echo "📊 Files created:"
    ls -lh dist/OpenFlux_AI_Assistant*
    
    # Create simple package
    mkdir -p dist/OpenFlux_Package
    cp dist/OpenFlux_AI_Assistant.exe dist/OpenFlux_Package/
    
    echo "OpenFlux AI Assistant" > dist/OpenFlux_Package/README.txt
    echo "Run: OpenFlux_AI_Assistant.exe" >> dist/OpenFlux_Package/README.txt
    
    cd dist
    zip -r OpenFlux_Simple.zip OpenFlux_Package/
    cd ..
    
    echo ""
    echo "🎉 Simple build completed!"
    echo "📁 Download: dist/OpenFlux_Simple.zip"
    echo ""
    echo "📥 Download command:"
    echo "scp -i your-key.pem ec2-user@$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):~/Openflux/dist/OpenFlux_Simple.zip ./"
    
else
    echo "❌ Build failed!"
    exit 1
fi

rm -f simple_openflux.spec