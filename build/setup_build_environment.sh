#!/bin/bash
# Setup build environment on Amazon Linux 2 for Windows executable generation

set -e  # Exit on any error

echo "🚀 Setting up OpenFlux build environment on Amazon Linux 2..."

# Update system packages
echo "📦 Updating system packages..."
sudo yum update -y

# Install required system packages
echo "🔧 Installing system dependencies..."
sudo yum install -y \
    git \
    wget \
    curl \
    gcc \
    gcc-c++ \
    make \
    zlib-devel \
    openssl-devel \
    libffi-devel \
    sqlite-devel \
    bzip2-devel \
    readline-devel \
    xz-devel

# Install Python 3.9 if not already installed
echo "🐍 Setting up Python 3.9..."
if ! command -v python3.9 &> /dev/null; then
    # Install Python 3.9 from source
    cd /tmp
    wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
    tar xzf Python-3.9.18.tgz
    cd Python-3.9.18
    ./configure --enable-optimizations --with-ensurepip=install
    make -j$(nproc)
    sudo make altinstall
    cd ~
else
    echo "✅ Python 3.9 already installed"
fi

# Create virtual environment
echo "🏠 Creating virtual environment..."
python3.9 -m venv openflux_build_env
source openflux_build_env/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Wine for Windows cross-compilation
echo "🍷 Installing Wine..."
sudo yum install -y epel-release
sudo yum install -y wine

# Configure Wine
echo "⚙️ Configuring Wine..."
export WINEARCH=win64
export WINEPREFIX=$HOME/.wine
winecfg &
sleep 5
pkill winecfg || true

# Download and install Windows Python in Wine
echo "🪟 Installing Windows Python in Wine..."
cd /tmp
wget https://www.python.org/ftp/python/3.9.18/python-3.9.18-amd64.exe
wine python-3.9.18-amd64.exe /quiet InstallAllUsers=1 PrependPath=1

# Wait for installation to complete
sleep 30

# Verify Wine Python installation
echo "✅ Verifying Wine Python installation..."
wine python --version

# Install pip in Wine Python
echo "📦 Installing pip in Wine Python..."
wine python -m ensurepip --upgrade
wine python -m pip install --upgrade pip setuptools wheel

echo "🎉 Build environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Activate the virtual environment: source openflux_build_env/bin/activate"
echo "2. Install Python dependencies: pip install -r requirements.txt"
echo "3. Run the build script: ./build/build_executable.sh"
echo ""
echo "🔍 Environment details:"
echo "- Python (Linux): $(python3.9 --version)"
echo "- Wine Python: $(wine python --version 2>/dev/null || echo 'Not accessible')"
echo "- Wine version: $(wine --version)"
echo "- Virtual environment: openflux_build_env"