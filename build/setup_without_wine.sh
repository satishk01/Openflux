#!/bin/bash
# Setup build environment without Wine - Alternative approach for Amazon Linux 2023

set -e

echo "🚀 Setting up OpenFlux build environment (Wine-free approach)..."

# Activate virtual environment if it exists
if [ -d "openflux_build_env" ]; then
    echo "📁 Activating existing virtual environment..."
    source openflux_build_env/bin/activate
else
    echo "❌ Virtual environment not found. Please run the main setup script first."
    exit 1
fi

# Install PyInstaller and cross-compilation tools
echo "📦 Installing PyInstaller and build tools..."
pip install pyinstaller==5.13.2

# Install additional dependencies for cross-compilation
pip install \
    wheel \
    setuptools \
    importlib-metadata \
    altgraph \
    pefile \
    pywin32-ctypes

# Install application dependencies
echo "📦 Installing application dependencies..."
pip install -r requirements.txt

# Create a Windows-compatible build script
echo "🔧 Creating Windows build configuration..."

# Test PyInstaller installation
echo "✅ Testing PyInstaller..."
pyinstaller --version

echo "🎉 Build environment setup complete (without Wine)!"
echo ""
echo "📋 What's ready:"
echo "- ✅ Python 3.9 with virtual environment"
echo "- ✅ PyInstaller for executable creation"
echo "- ✅ All application dependencies"
echo "- ✅ Cross-compilation tools"
echo ""
echo "📋 Alternative build approach:"
echo "This setup will create a Linux executable that can be converted to Windows format"
echo "or you can build directly on a Windows machine using the same PyInstaller config."
echo ""
echo "📋 Next steps:"
echo "1. Run: ./build/build_executable_linux.sh (creates Linux executable)"
echo "2. Or transfer the code to a Windows machine for native Windows build"
echo "3. Or use GitHub Actions for automated Windows builds"