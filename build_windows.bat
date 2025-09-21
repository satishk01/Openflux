@echo off
REM Build Windows executable for OpenFlux AI Assistant

echo 🏗️ Building OpenFlux AI Assistant Windows Executable...

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: app.py not found. Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Create assets directory if it doesn't exist
if not exist "assets" mkdir assets

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del *.spec

REM Build the executable
echo 🚀 Creating Windows executable...
pyinstaller build/openflux_windows.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

REM Check if build was successful
if exist "dist\OpenFlux_AI_Assistant.exe" (
    echo ✅ Build successful!
    
    REM Get file size
    for %%A in ("dist\OpenFlux_AI_Assistant.exe") do echo 📊 Executable size: %%~zA bytes
    
    echo.
    echo 🎉 Windows build completed successfully!
    echo 📁 Executable location: dist\OpenFlux_AI_Assistant.exe
    echo.
    echo 📋 To test the application:
    echo dist\OpenFlux_AI_Assistant.exe
    echo.
    echo 📋 Distribution ready!
    
) else (
    echo ❌ Build failed! Executable not found.
    pause
    exit /b 1
)

pause