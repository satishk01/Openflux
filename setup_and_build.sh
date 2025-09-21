#!/bin/bash
# Complete setup and build script for OpenFlux AI Assistant

set -e

echo "🚀 OpenFlux AI Assistant - Complete Setup and Build"
echo "=================================================="

# Step 1: Activate virtual environment
echo "📁 Step 1: Activating virtual environment..."
if [ -d "openflux_build_env" ]; then
    source openflux_build_env/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Creating one..."
    python3.9 -m venv openflux_build_env
    source openflux_build_env/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Step 2: Install dependencies
echo ""
echo "📦 Step 2: Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Step 3: Create missing directories
echo ""
echo "📁 Step 3: Setting up directories..."
mkdir -p assets
mkdir -p styles
mkdir -p templates
mkdir -p engines
echo "✅ Directories created"

# Step 4: Build Linux executable
echo ""
echo "🏗️ Step 4: Building Linux executable..."
chmod +x build_linux.sh
./build_linux.sh

echo ""
echo "🎉 Setup and build completed successfully!"
echo ""
echo "📋 What's been created:"
echo "- ✅ Virtual environment: openflux_build_env"
echo "- ✅ All dependencies installed"
echo "- ✅ Linux executable: dist/OpenFlux_AI_Assistant"
echo ""
echo "📋 Next steps:"
echo "1. Test Linux executable: ./dist/OpenFlux_AI_Assistant"
echo "2. For Windows build: Transfer project to Windows machine and run build_windows.bat"
echo ""
echo "📋 Files ready for Windows transfer:"
echo "- All source code"
echo "- build/openflux_windows.spec"
echo "- build_windows.bat"
echo "- requirements.txt"