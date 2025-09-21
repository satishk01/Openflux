#!/bin/bash
# Build Windows executable for OpenFlux AI Assistant

set -e  # Exit on any error

echo "🏗️ Building OpenFlux AI Assistant Windows Executable..."

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
        echo "❌ Error: Virtual environment not found. Please run setup_build_environment.sh first."
        exit 1
    fi
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create assets directory and icon if they don't exist
echo "🎨 Setting up assets..."
mkdir -p assets
if [ ! -f "assets/icon.ico" ]; then
    echo "ℹ️ No icon found, executable will use default icon"
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/dist build/build *.spec

# Copy spec file to root directory
cp build/openflux.spec ./

# Build with PyInstaller using Wine for Windows target
echo "🔨 Building executable with PyInstaller..."
export WINEARCH=win64
export WINEPREFIX=$HOME/.wine

# Install PyInstaller in Wine Python
echo "📦 Installing PyInstaller in Wine Python..."
wine python -m pip install pyinstaller==5.13.2

# Install dependencies in Wine Python
echo "📦 Installing dependencies in Wine Python..."
wine python -m pip install -r requirements.txt

# Build the executable
echo "🚀 Creating Windows executable..."
wine python -m PyInstaller openflux.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/OpenFlux_AI_Assistant.exe" ]; then
    echo "✅ Build successful!"
    
    # Get file size
    size=$(du -h "dist/OpenFlux_AI_Assistant.exe" | cut -f1)
    echo "📊 Executable size: $size"
    
    # Create distribution package
    echo "📦 Creating distribution package..."
    mkdir -p dist/OpenFlux_Portable
    cp dist/OpenFlux_AI_Assistant.exe dist/OpenFlux_Portable/
    
    # Create README for users
    cat > dist/OpenFlux_Portable/README.txt << EOF
OpenFlux AI Assistant - Portable Edition
========================================

Thank you for downloading OpenFlux AI Assistant!

SYSTEM REQUIREMENTS:
- Windows 10 or Windows 11
- 8GB RAM or more recommended
- Internet connection for AI services
- AWS account with Bedrock access

GETTING STARTED:
1. Double-click OpenFlux_AI_Assistant.exe to start
2. The application will open in your default web browser
3. Enter your AWS Access Key and Secret Access Key when prompted
4. Start using OpenFlux AI Assistant!

SECURITY NOTES:
- Your AWS credentials are encrypted and stored only in memory
- Credentials are never saved to disk
- All data is cleared when you close the application

TROUBLESHOOTING:
- If Windows shows a security warning, click "More info" then "Run anyway"
- Make sure your AWS credentials have Bedrock access permissions
- Check that your internet connection is working
- Try running as administrator if you encounter file access issues

SUPPORT:
For help and documentation, visit the OpenFlux documentation or
contact your system administrator.

Version: 1.0.0
Build Date: $(date)
EOF
    
    # Create zip package
    cd dist
    zip -r "OpenFlux_AI_Assistant_Portable.zip" OpenFlux_Portable/
    cd ..
    
    echo ""
    echo "🎉 Build completed successfully!"
    echo "📁 Files created:"
    echo "   - dist/OpenFlux_AI_Assistant.exe (executable)"
    echo "   - dist/OpenFlux_Portable/ (distribution folder)"
    echo "   - dist/OpenFlux_AI_Assistant_Portable.zip (distribution package)"
    echo ""
    echo "📋 Next steps:"
    echo "1. Test the executable on a Windows machine"
    echo "2. Download the zip file to distribute to users"
    echo "3. Provide users with their AWS credentials setup instructions"
    
else
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi

# Cleanup
echo "🧹 Cleaning up build files..."
rm -f openflux.spec
rm -rf build/__pycache__

echo "✨ Build process complete!"