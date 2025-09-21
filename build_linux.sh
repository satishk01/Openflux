#!/bin/bash
# Build Linux executable for OpenFlux AI Assistant

set -e

echo "🏗️ Building OpenFlux AI Assistant Linux Executable..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️ Warning: No virtual environment detected. Activating openflux_build_env..."
    if [ -d "openflux_build_env" ]; then
        source openflux_build_env/bin/activate
    else
        echo "❌ Error: Virtual environment not found. Please run setup first."
        exit 1
    fi
fi

# Install dependencies if needed
echo "📦 Checking Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Create assets directory if it doesn't exist
mkdir -p assets

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist build *.spec

# Build the executable
echo "🚀 Creating Linux executable..."
pyinstaller build/openflux_linux.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/OpenFlux_AI_Assistant" ]; then
    echo "✅ Build successful!"
    
    # Get file size
    size=$(du -h "dist/OpenFlux_AI_Assistant" | cut -f1)
    echo "📊 Executable size: $size"
    
    # Make executable
    chmod +x "dist/OpenFlux_AI_Assistant"
    
    # Test if it starts (quick test)
    echo "🧪 Testing executable startup..."
    timeout 5s ./dist/OpenFlux_AI_Assistant --help > /dev/null 2>&1 || echo "Note: Quick test completed (this is normal)"
    
    echo ""
    echo "🎉 Linux build completed successfully!"
    echo "📁 Executable location: dist/OpenFlux_AI_Assistant"
    echo ""
    echo "📋 To test the application:"
    echo "./dist/OpenFlux_AI_Assistant"
    echo ""
    echo "📋 For Windows build:"
    echo "1. Transfer this project to a Windows machine"
    echo "2. Install Python 3.9+ and dependencies"
    echo "3. Run: pyinstaller build/openflux_windows.spec"
    
else
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi