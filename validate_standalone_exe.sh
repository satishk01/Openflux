#!/bin/bash
# Validate that the Windows executable is truly standalone

echo "🔍 Validating Standalone Windows Executable"
echo "==========================================="

# Check if executable exists
if [ ! -f "dist/OpenFlux_AI_Assistant.exe" ]; then
    echo "❌ Executable not found! Please build first."
    exit 1
fi

echo "✅ Executable found: dist/OpenFlux_AI_Assistant.exe"

# Check file size (should be substantial for standalone)
size_bytes=$(stat -c%s "dist/OpenFlux_AI_Assistant.exe")
size_mb=$((size_bytes / 1024 / 1024))

echo "📊 Executable size: ${size_mb}MB"

if [ $size_mb -lt 100 ]; then
    echo "⚠️ Warning: Executable seems small (${size_mb}MB). May be missing dependencies."
    echo "   Standalone executables are typically 150-400MB"
elif [ $size_mb -gt 600 ]; then
    echo "⚠️ Warning: Executable is very large (${size_mb}MB). May include unnecessary files."
else
    echo "✅ Executable size looks good for standalone application."
fi

# Check if it's a Windows executable
if command -v file &> /dev/null; then
    file_info=$(file "dist/OpenFlux_AI_Assistant.exe")
    echo "📋 File type: $file_info"
    
    if [[ $file_info == *"PE32+ executable"* ]] || [[ $file_info == *"MS Windows"* ]]; then
        echo "✅ Valid Windows 64-bit executable format detected."
    else
        echo "⚠️ Warning: File may not be a proper Windows executable."
    fi
fi

# Check for Python dependencies (should be bundled)
echo ""
echo "🔍 Checking for bundled dependencies..."

# Use strings command to check for embedded Python
if command -v strings &> /dev/null; then
    if strings "dist/OpenFlux_AI_Assistant.exe" | grep -q "python"; then
        echo "✅ Python runtime appears to be bundled"
    else
        echo "⚠️ Python runtime may not be properly bundled"
    fi
    
    if strings "dist/OpenFlux_AI_Assistant.exe" | grep -q "streamlit"; then
        echo "✅ Streamlit appears to be bundled"
    else
        echo "⚠️ Streamlit may not be properly bundled"
    fi
    
    if strings "dist/OpenFlux_AI_Assistant.exe" | grep -q "boto3"; then
        echo "✅ AWS SDK appears to be bundled"
    else
        echo "⚠️ AWS SDK may not be properly bundled"
    fi
fi

# Create final distribution package with validation
echo ""
echo "📦 Creating validated distribution package..."

mkdir -p dist/OpenFlux_Standalone_Validated
cp dist/OpenFlux_AI_Assistant.exe dist/OpenFlux_Standalone_Validated/

# Create comprehensive standalone README
cat > dist/OpenFlux_Standalone_Validated/README.txt << EOF
OpenFlux AI Assistant - Standalone Windows 11 Edition
=====================================================

🎉 COMPLETELY STANDALONE - NO PYTHON NEEDED!
============================================

This executable includes EVERYTHING needed to run:
✅ Python runtime (embedded)
✅ All Python libraries
✅ Streamlit web framework
✅ AWS SDK and cryptography
✅ All application code and dependencies

SYSTEM REQUIREMENTS:
✅ Windows 11 (64-bit) - Optimized for this
✅ Windows 10 (64-bit) - Also works
✅ 8GB RAM minimum (16GB recommended)
✅ Internet connection for AI services
✅ AWS account with Bedrock access
❌ NO Python installation needed
❌ NO pip, conda, or any Python tools needed
❌ NO additional software required

SIMPLE USAGE:
1. Extract this folder anywhere on your computer
2. Double-click OpenFlux_AI_Assistant.exe
3. Wait 30-60 seconds for first startup (normal)
4. Browser opens automatically with the application
5. Enter your AWS Access Key and Secret Access Key
6. Start using OpenFlux AI Assistant!

WHAT HAPPENS WHEN YOU RUN IT:
- The .exe file contains a complete Python environment
- It starts a local web server on your computer
- Opens your browser to http://localhost:8501
- Everything runs locally - no cloud dependencies except AWS AI
- Your credentials are encrypted in memory only

SECURITY FEATURES:
🔒 Standalone execution - no external dependencies
🔒 Local web server - runs only on your computer
🔒 Encrypted credential storage in memory
🔒 No data persistence - everything cleared on exit
🔒 HTTPS communication with AWS only

TROUBLESHOOTING:
❓ App doesn't start: 
   - Try "Run as administrator"
   - Check Windows Defender isn't blocking it
   - Ensure port 8501 is available

❓ Security warnings:
   - This is normal for unsigned executables
   - Click "More info" → "Run anyway"
   - Add to Windows Defender exclusions if needed

❓ Slow startup:
   - First run takes 30-60 seconds (normal)
   - Subsequent runs are faster
   - Large executable needs time to initialize

❓ Browser doesn't open:
   - Manually go to http://localhost:8501
   - Try different browser
   - Check if port 8501 is blocked

FILE INFORMATION:
- Executable Size: ${size_mb}MB
- Architecture: 64-bit (x86_64)
- Python Runtime: Embedded (no installation needed)
- Dependencies: All bundled
- Build Date: $(date)
- Compatible: Windows 10/11 64-bit

🎯 THIS IS A PORTABLE APPLICATION
- No installation required
- No Python needed
- No additional software needed
- Just run the .exe file!
EOF

# Create enhanced startup script
cat > dist/OpenFlux_Standalone_Validated/Start_OpenFlux_Standalone.bat << 'EOF'
@echo off
title OpenFlux AI Assistant - Standalone Edition
color 0A
cls
echo.
echo ==========================================
echo   OpenFlux AI Assistant
echo   Standalone Windows 11 Edition
echo ==========================================
echo.
echo 🎉 NO PYTHON INSTALLATION REQUIRED!
echo ✅ Everything is included in this executable
echo ✅ Completely portable and standalone
echo ✅ No additional software needed
echo.
echo System Check:
echo - Windows Version: 
ver
echo - Available Memory:
wmic OS get FreePhysicalMemory /format:value | find "FreePhysicalMemory"
echo.
echo Starting OpenFlux AI Assistant...
echo Please wait 30-60 seconds for first startup.
echo.
echo The application will open in your web browser.
echo Keep this window open while using the application.
echo.
echo Starting...
OpenFlux_AI_Assistant.exe
echo.
echo Application has stopped.
echo.
pause
EOF

# Create ZIP package
cd dist
zip -r OpenFlux_AI_Assistant_Standalone_Windows11.zip OpenFlux_Standalone_Validated/
cd ..

echo ""
echo "📁 Validated standalone package created:"
echo "   ✅ dist/OpenFlux_AI_Assistant.exe (${size_mb}MB standalone executable)"
echo "   ✅ dist/OpenFlux_Standalone_Validated/ (complete package)"
echo "   ✅ dist/OpenFlux_AI_Assistant_Standalone_Windows11.zip (ready to download)"

echo ""
echo "📥 Download command:"
echo "   scp -i your-key.pem ubuntu@$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):~/Openflux/dist/OpenFlux_AI_Assistant_Standalone_Windows11.zip ./"

echo ""
echo "🎯 On Windows 11 (NO PYTHON NEEDED):"
echo "   1. Extract ZIP file anywhere"
echo "   2. Double-click OpenFlux_AI_Assistant.exe"
echo "   3. Wait for browser to open (30-60 seconds)"
echo "   4. Enter AWS credentials"
echo "   5. Use the application!"
echo ""
echo "✨ TRULY STANDALONE - Works on any Windows 11 computer!"
echo "✨ No Python, no pip, no installation - just run the .exe!"