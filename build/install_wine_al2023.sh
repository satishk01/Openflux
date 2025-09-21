#!/bin/bash
# Install Wine on Amazon Linux 2023

echo "🍷 Installing Wine on Amazon Linux 2023..."

# Check OS version
echo "Checking OS version..."
cat /etc/os-release

# For Amazon Linux 2023, Wine should be available directly
echo "Installing Wine..."
sudo yum install -y wine

# Verify installation
if command -v wine &> /dev/null; then
    echo "✅ Wine installed successfully"
    wine --version
    
    # Configure Wine
    echo "⚙️ Configuring Wine..."
    export WINEARCH=win64
    export WINEPREFIX=$HOME/.wine
    
    # Initialize Wine prefix
    echo "Initializing Wine prefix..."
    wineboot --init
    
    echo "✅ Wine setup complete"
else
    echo "❌ Wine installation failed"
    echo "Trying alternative approaches..."
    
    # Try installing from Fedora repository (compatible)
    echo "Trying Fedora Wine repository..."
    sudo dnf config-manager --add-repo https://dl.winehq.org/wine-builds/fedora/38/winehq.repo
    sudo dnf install -y winehq-stable
    
    if command -v wine &> /dev/null; then
        echo "✅ Wine installed from WineHQ repository"
    else
        echo "❌ All Wine installation methods failed"
        echo "You may need to install Wine manually or use a different approach"
    fi
fi