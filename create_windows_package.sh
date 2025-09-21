#!/bin/bash
# Create complete Windows build package

echo "📦 Creating Windows 11 build package..."

# Run the Python script to create Windows build files
python3 build_windows_complete.py

# Create a complete package for Windows transfer
echo "📁 Creating transfer package..."

# Create package directory
mkdir -p windows_build_package

# Copy all necessary files
cp -r services windows_build_package/
cp -r components windows_build_package/
cp app.py windows_build_package/
cp startup.py windows_build_package/
cp requirements.txt windows_build_package/
cp requirements_windows.txt windows_build_package/
cp openflux_windows11.spec windows_build_package/
cp build_windows11.bat windows_build_package/
cp version_info.txt windows_build_package/

# Copy optional directories if they exist
[ -d "styles" ] && cp -r styles windows_build_package/
[ -d "templates" ] && cp -r templates windows_build_package/
[ -d "engines" ] && cp -r engines windows_build_package/
[ -d "assets" ] && cp -r assets windows_build_package/

# Create instructions file
cat > windows_build_package/WINDOWS_BUILD_INSTRUCTIONS.txt << 'EOF'
OpenFlux AI Assistant - Windows 11 Build Instructions
====================================================

PREREQUISITES:
1. Windows 10 or Windows 11 (64-bit)
2. Python 3.9+ installed from python.org
3. Internet connection

QUICK BUILD:
1. Extract all files to a folder
2. Double-click: build_windows11.bat
3. Wait for build to complete
4. Find executable in: dist\OpenFlux_AI_Assistant.exe

MANUAL BUILD:
1. Open Command Prompt in this folder
2. Run: python -m venv openflux_env
3. Run: openflux_env\Scripts\activate
4. Run: pip install -r requirements_windows.txt
5. Run: pyinstaller openflux_windows11.spec --clean --noconfirm

TESTING:
1. Run: dist\OpenFlux_AI_Assistant.exe
2. Enter your AWS credentials when prompted
3. Test all features

TROUBLESHOOTING:
- If Windows shows security warning: Click "More info" → "Run anyway"
- If build fails: Make sure Python 3.9+ is installed
- If antivirus blocks: Add exception for the executable
- If startup fails: Try running as administrator

The executable will be compatible with Windows 10 and Windows 11.
EOF

# Create archive
echo "🗜️ Creating archive..."
tar -czf openflux_windows11_build_package.tar.gz windows_build_package/

# Create zip for Windows users
if command -v zip &> /dev/null; then
    zip -r openflux_windows11_build_package.zip windows_build_package/
fi

echo "✅ Windows build package created!"
echo ""
echo "📦 Package contents:"
echo "   - openflux_windows11_build_package.tar.gz (Linux/Mac)"
echo "   - openflux_windows11_build_package.zip (Windows)"
echo ""
echo "📋 Transfer to Windows 11 machine:"
echo "1. Download: openflux_windows11_build_package.zip"
echo "2. Extract all files"
echo "3. Run: build_windows11.bat"
echo ""
echo "🎯 Result: OpenFlux_AI_Assistant.exe (Windows 11 compatible)"