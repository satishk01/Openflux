#!/bin/bash
# Build Linux executable (can be used as reference for Windows build)

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

# Modify spec file for Linux build
echo "🔧 Configuring for Linux build..."
sed -i 's/console=False/console=True/' openflux.spec
sed -i 's/win_no_prefer_redirects=False//' openflux.spec
sed -i 's/win_private_assemblies=False//' openflux.spec

# Build the executable
echo "🚀 Creating Linux executable..."
pyinstaller openflux.spec --clean --noconfirm

# Check if build was successful
if [ -f "dist/OpenFlux_AI_Assistant" ]; then
    echo "✅ Build successful!"
    
    # Get file size
    size=$(du -h "dist/OpenFlux_AI_Assistant" | cut -f1)
    echo "📊 Executable size: $size"
    
    # Make executable
    chmod +x "dist/OpenFlux_AI_Assistant"
    
    # Create distribution package
    echo "📦 Creating distribution package..."
    mkdir -p dist/OpenFlux_Linux
    cp dist/OpenFlux_AI_Assistant dist/OpenFlux_Linux/
    
    # Create README for users
    cat > dist/OpenFlux_Linux/README.txt << EOF
OpenFlux AI Assistant - Linux Edition
====================================

Thank you for downloading OpenFlux AI Assistant!

SYSTEM REQUIREMENTS:
- Linux (Ubuntu 18.04+, CentOS 7+, Amazon Linux 2+)
- 8GB RAM or more recommended
- Internet connection for AI services
- AWS account with Bedrock access

GETTING STARTED:
1. Open terminal in this directory
2. Run: ./OpenFlux_AI_Assistant
3. The application will open in your default web browser
4. Enter your AWS Access Key and Secret Access Key when prompted
5. Start using OpenFlux AI Assistant!

SECURITY NOTES:
- Your AWS credentials are encrypted and stored only in memory
- Credentials are never saved to disk
- All data is cleared when you close the application

TROUBLESHOOTING:
- Make sure the file is executable: chmod +x OpenFlux_AI_Assistant
- Check that your AWS credentials have Bedrock access permissions
- Verify your internet connection is working
- Try running from terminal to see any error messages

For Windows version:
- Transfer this project to a Windows machine
- Install Python 3.9+ and dependencies
- Run: pyinstaller openflux.spec

Version: 1.0.0
Build Date: $(date)
EOF
    
    # Create tar package
    cd dist
    tar -czf "OpenFlux_AI_Assistant_Linux.tar.gz" OpenFlux_Linux/
    cd ..
    
    echo ""
    echo "🎉 Build completed successfully!"
    echo "📁 Files created:"
    echo "   - dist/OpenFlux_AI_Assistant (Linux executable)"
    echo "   - dist/OpenFlux_Linux/ (distribution folder)"
    echo "   - dist/OpenFlux_AI_Assistant_Linux.tar.gz (distribution package)"
    echo ""
    echo "📋 For Windows executable:"
    echo "1. Transfer this project to a Windows machine"
    echo "2. Install Python 3.9+ and pip"
    echo "3. Run: pip install -r requirements.txt"
    echo "4. Run: pip install pyinstaller"
    echo "5. Run: pyinstaller build/openflux.spec"
    echo ""
    echo "📋 Test the Linux executable:"
    echo "./dist/OpenFlux_AI_Assistant"
    
else
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi

# Cleanup
echo "🧹 Cleaning up build files..."
rm -f openflux.spec
rm -rf build/__pycache__

echo "✨ Build process complete!"