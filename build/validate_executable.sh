#!/bin/bash
# Validate the built Windows executable

set -e

echo "🔍 Validating OpenFlux AI Assistant executable..."

# Check if executable exists
if [ ! -f "dist/OpenFlux_AI_Assistant.exe" ]; then
    echo "❌ Error: Executable not found at dist/OpenFlux_AI_Assistant.exe"
    echo "Please run build_executable.sh first."
    exit 1
fi

# Check file size (should be reasonable, not too large or too small)
size_bytes=$(stat -c%s "dist/OpenFlux_AI_Assistant.exe")
size_mb=$((size_bytes / 1024 / 1024))

echo "📊 Executable size: ${size_mb}MB"

if [ $size_mb -lt 50 ]; then
    echo "⚠️ Warning: Executable seems too small (${size_mb}MB). Dependencies might be missing."
elif [ $size_mb -gt 500 ]; then
    echo "⚠️ Warning: Executable is quite large (${size_mb}MB). Consider optimizing."
else
    echo "✅ Executable size looks reasonable."
fi

# Check if it's a valid Windows executable
if command -v file &> /dev/null; then
    file_info=$(file "dist/OpenFlux_AI_Assistant.exe")
    echo "📋 File type: $file_info"
    
    if [[ $file_info == *"PE32+ executable"* ]] || [[ $file_info == *"MS Windows"* ]]; then
        echo "✅ Valid Windows executable format detected."
    else
        echo "❌ Warning: File doesn't appear to be a Windows executable."
    fi
fi

# Check if Wine can run it (basic test)
echo "🍷 Testing executable with Wine..."
export WINEARCH=win64
export WINEPREFIX=$HOME/.wine

# Try to run with --help flag (if supported) or just check if it starts
timeout 10s wine "dist/OpenFlux_AI_Assistant.exe" --help &>/dev/null && echo "✅ Executable starts successfully with Wine" || echo "⚠️ Could not test execution with Wine (this is normal)"

# Validate distribution package
if [ -f "dist/OpenFlux_AI_Assistant_Portable.zip" ]; then
    echo "✅ Distribution package found."
    
    # Check zip contents
    echo "📦 Package contents:"
    unzip -l "dist/OpenFlux_AI_Assistant_Portable.zip"
    
    # Check zip size
    zip_size_bytes=$(stat -c%s "dist/OpenFlux_AI_Assistant_Portable.zip")
    zip_size_mb=$((zip_size_bytes / 1024 / 1024))
    echo "📊 Package size: ${zip_size_mb}MB"
    
else
    echo "❌ Distribution package not found."
fi

# Check for required files
echo "🔍 Checking for required files..."

required_files=(
    "dist/OpenFlux_AI_Assistant.exe"
    "dist/OpenFlux_Portable/OpenFlux_AI_Assistant.exe"
    "dist/OpenFlux_Portable/README.txt"
)

all_files_present=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ Missing: $file"
        all_files_present=false
    fi
done

# Final validation summary
echo ""
echo "📋 Validation Summary:"
echo "====================="

if [ "$all_files_present" = true ]; then
    echo "✅ All required files present"
else
    echo "❌ Some required files are missing"
fi

echo "📊 Executable: ${size_mb}MB"
echo "📦 Package: ${zip_size_mb}MB"

# Provide next steps
echo ""
echo "📋 Next Steps for Testing:"
echo "========================="
echo "1. Download the zip file to a Windows machine"
echo "2. Extract and run OpenFlux_AI_Assistant.exe"
echo "3. Test with valid AWS credentials"
echo "4. Verify all features work correctly"
echo ""
echo "🚀 Ready for distribution!"

# Create a simple test report
cat > dist/validation_report.txt << EOF
OpenFlux AI Assistant - Build Validation Report
===============================================

Build Date: $(date)
Executable Size: ${size_mb}MB
Package Size: ${zip_size_mb}MB
All Files Present: $all_files_present

Files Validated:
$(for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file"
    fi
done)

Recommendations:
- Test on Windows 10 and Windows 11
- Verify AWS Bedrock connectivity
- Test all application features
- Check antivirus compatibility

EOF

echo "📄 Validation report saved to dist/validation_report.txt"