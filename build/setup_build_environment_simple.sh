#!/bin/bash
# Simplified setup script for Amazon Linux 2 build environment
# Use this if the main setup script encounters package conflicts

set -e  # Exit on any error

echo "🚀 Setting up OpenFlux build environment (Simple Version)..."

# Update system packages
echo "📦 Updating system packages..."
sudo yum update -y

# Install essential build tools only
echo "🔧 Installing essential build dependencies..."
sudo yum groupinstall -y "Development Tools"

# Install Python development packages
echo "🐍 Installing Python development packages..."
sudo yum install -y \
    openssl-devel \
    libffi-devel \
    bzip2-devel \
    readline-devel \
    sqlite-devel \
    xz-devel \
    zlib-devel

# Check if Python 3.9 is available in repos
echo "🔍 Checking for Python 3.9..."
if yum list available | grep -q python39; then
    echo "Installing Python 3.9 from repository..."
    sudo yum install -y python39 python39-pip python39-devel
    PYTHON_CMD="python3.9"
else
    echo "Python 3.9 not available in repos, will compile from source..."
    
    # Install Python 3.9 from source
    echo "📥 Downloading Python 3.9.18..."
    cd /tmp
    wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
    tar xzf Python-3.9.18.tgz
    cd Python-3.9.18
    
    echo "🔨 Compiling Python 3.9.18..."
    ./configure --enable-optimizations --with-ensurepip=install
    make -j$(nproc)
    sudo make altinstall
    
    PYTHON_CMD="python3.9"
    cd ~
fi

# Verify Python installation
echo "✅ Verifying Python installation..."
$PYTHON_CMD --version

# Create virtual environment
echo "🏠 Creating virtual environment..."
$PYTHON_CMD -m venv openflux_build_env
source openflux_build_env/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Wine (try multiple approaches)
echo "🍷 Installing Wine..."
if ! command -v wine &> /dev/null; then
    # Try EPEL first
    sudo yum install -y epel-release || echo "EPEL already installed"
    
    # Clean cache
    sudo yum clean all
    
    # Try to install Wine
    if sudo yum install -y wine; then
        echo "✅ Wine installed successfully"
    else
        echo "⚠️ Wine installation failed, trying alternative..."
        
        # Try with skip-broken
        sudo yum install -y --skip-broken wine || {
            echo "❌ Wine installation failed completely"
            echo "You may need to install Wine manually or use a different approach"
            echo "Continuing without Wine - you can install it later"
        }
    fi
else
    echo "✅ Wine already installed"
fi

# Configure Wine if available
if command -v wine &> /dev/null; then
    echo "⚙️ Configuring Wine..."
    export WINEARCH=win64
    export WINEPREFIX=$HOME/.wine
    
    # Initialize Wine (this may take a while)
    echo "Initializing Wine prefix..."
    wineboot --init
    
    # Download and install Windows Python in Wine
    echo "🪟 Installing Windows Python in Wine..."
    cd /tmp
    
    if [ ! -f "python-3.9.18-amd64.exe" ]; then
        wget https://www.python.org/ftp/python/3.9.18/python-3.9.18-amd64.exe
    fi
    
    # Install Python silently
    wine python-3.9.18-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 &
    
    # Wait for installation
    echo "Waiting for Windows Python installation to complete..."
    sleep 60
    
    # Kill any remaining processes
    pkill -f python-3.9.18-amd64.exe || true
    
    # Verify Wine Python installation
    echo "✅ Verifying Wine Python installation..."
    wine python --version || echo "⚠️ Wine Python verification failed"
    
    # Install pip in Wine Python
    echo "📦 Installing pip in Wine Python..."
    wine python -m ensurepip --upgrade || echo "⚠️ Wine pip installation failed"
    wine python -m pip install --upgrade pip setuptools wheel || echo "⚠️ Wine pip upgrade failed"
else
    echo "⚠️ Wine not available - you'll need to install it manually for Windows builds"
fi

echo "🎉 Build environment setup complete!"
echo ""
echo "📋 Summary:"
echo "- Python (Linux): $($PYTHON_CMD --version)"
if command -v wine &> /dev/null; then
    echo "- Wine Python: $(wine python --version 2>/dev/null || echo 'Not accessible')"
    echo "- Wine version: $(wine --version)"
else
    echo "- Wine: Not installed"
fi
echo "- Virtual environment: openflux_build_env"
echo ""
echo "📋 Next steps:"
echo "1. Activate the virtual environment: source openflux_build_env/bin/activate"
echo "2. Install Python dependencies: pip install -r requirements.txt"
echo "3. Run the build script: ./build/build_executable.sh"