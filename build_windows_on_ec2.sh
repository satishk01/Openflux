#!/bin/bash
# Build Windows executable on EC2 using Docker

set -e

echo "🚀 Building Windows Executable on EC2 using Docker"
echo "================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    sudo yum update -y
    sudo yum install -y docker
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker ec2-user
    
    echo "⚠️ Docker installed. Please log out and log back in, then run this script again."
    echo "Or run: newgrp docker"
    exit 0
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "🔄 Starting Docker..."
    sudo systemctl start docker
fi

echo "✅ Docker is ready"

# Create Dockerfile for Windows build
echo "📝 Creating Dockerfile..."
cat > Dockerfile.windows << 'EOF'
# Use Ubuntu as base (better Wine support than Amazon Linux)
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV WINEARCH=win64
ENV WINEPREFIX=/root/.wine

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    software-properties-common \
    gnupg2 \
    ca-certificates \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Add Wine repository and install Wine
RUN wget -nc https://dl.winehq.org/wine-builds/winehq.key && \
    apt-key add winehq.key && \
    add-apt-repository 'deb https://dl.winehq.org/wine-builds/ubuntu/ jammy main' && \
    apt-get update && \
    apt-get install -y --install-recommends winehq-stable && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.9
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic links
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.9 /usr/bin/python

# Initialize Wine
RUN xvfb-run -a winecfg

# Download and install Windows Python in Wine
RUN cd /tmp && \
    wget https://www.python.org/ftp/python/3.9.18/python-3.9.18-amd64.exe && \
    xvfb-run -a wine python-3.9.18-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 && \
    rm python-3.9.18-amd64.exe

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install Linux Python dependencies (for building)
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install pyinstaller

# Install Windows Python dependencies
RUN xvfb-run -a wine python -m pip install --upgrade pip setuptools wheel && \
    xvfb-run -a wine python -m pip install -r requirements.txt && \
    xvfb-run -a wine python -m pip install pyinstaller

# Create the build script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🏗️ Building Windows executable..."\n\
\n\
# Create Windows spec file\n\
cat > openflux_windows_docker.spec << "SPEC_EOF"\n\
# -*- mode: python ; coding: utf-8 -*-\n\
\n\
a = Analysis(\n\
    ["startup.py"],\n\
    pathex=["."],\n\
    binaries=[],\n\
    datas=[\n\
        ("app.py", "."),\n\
        ("services", "services"),\n\
        ("components", "components"),\n\
    ],\n\
    hiddenimports=[\n\
        "streamlit",\n\
        "streamlit.web.cli",\n\
        "boto3",\n\
        "botocore",\n\
        "cryptography",\n\
        "cryptography.fernet",\n\
        "services.credentials_manager",\n\
        "components.credentials_ui",\n\
        "jira",\n\
        "pandas",\n\
        "plotly",\n\
        "yaml",\n\
        "markdown",\n\
        "PIL",\n\
        "requests",\n\
        "pydantic",\n\
    ],\n\
    hookspath=[],\n\
    hooksconfig={},\n\
    runtime_hooks=[],\n\
    excludes=[\n\
        "tkinter",\n\
        "matplotlib",\n\
        "scipy",\n\
        "test",\n\
        "unittest",\n\
    ],\n\
    win_no_prefer_redirects=False,\n\
    win_private_assemblies=False,\n\
    cipher=None,\n\
    noarchive=False,\n\
)\n\
\n\
pyz = PYZ(a.pure, a.zipped_data, cipher=None)\n\
\n\
exe = EXE(\n\
    pyz,\n\
    a.scripts,\n\
    a.binaries,\n\
    a.zipfiles,\n\
    a.datas,\n\
    [],\n\
    name="OpenFlux_AI_Assistant",\n\
    debug=False,\n\
    bootloader_ignore_signals=False,\n\
    strip=False,\n\
    upx=True,\n\
    upx_exclude=[],\n\
    runtime_tmpdir=None,\n\
    console=False,\n\
    disable_windowed_traceback=False,\n\
    target_arch=None,\n\
    codesign_identity=None,\n\
    entitlements_file=None,\n\
)\n\
SPEC_EOF\n\
\n\
# Build with Wine Python\n\
echo "🔨 Running PyInstaller with Wine..."\n\
xvfb-run -a wine python -m PyInstaller openflux_windows_docker.spec --clean --noconfirm\n\
\n\
# Check if build succeeded\n\
if [ -f "dist/OpenFlux_AI_Assistant.exe" ]; then\n\
    echo "✅ Windows executable built successfully!"\n\
    ls -lh dist/OpenFlux_AI_Assistant.exe\n\
else\n\
    echo "❌ Build failed!"\n\
    exit 1\n\
fi\n\
' > /app/build_in_docker.sh && chmod +x /app/build_in_docker.sh

# Set the default command
CMD ["/app/build_in_docker.sh"]
EOF

echo "✅ Dockerfile created"

# Build Docker image
echo "🔨 Building Docker image (this may take 10-15 minutes)..."
docker build -f Dockerfile.windows -t openflux-windows-builder .

# Run the build
echo "🚀 Running Windows build in Docker..."
docker run --rm -v $(pwd)/dist:/app/dist openflux-windows-builder

# Check if build was successful
if [ -f "dist/OpenFlux_AI_Assistant.exe" ]; then
    echo ""
    echo "🎉 SUCCESS! Windows executable built on EC2!"
    echo ""
    echo "📊 File details:"
    ls -lh dist/OpenFlux_AI_Assistant.exe
    
    echo ""
    echo "📦 Creating distribution package..."
    
    # Create distribution folder
    mkdir -p dist/OpenFlux_Windows11_Portable
    cp dist/OpenFlux_AI_Assistant.exe dist/OpenFlux_Windows11_Portable/
    
    # Create README for Windows users
    cat > dist/OpenFlux_Windows11_Portable/README.txt << 'EOF'
OpenFlux AI Assistant - Windows 11 Edition
==========================================

SYSTEM REQUIREMENTS:
- Windows 10 or Windows 11 (64-bit)
- 8GB RAM or more recommended
- Internet connection for AI services
- AWS account with Bedrock access

GETTING STARTED:
1. Double-click OpenFlux_AI_Assistant.exe
2. If Windows shows a security warning, click "More info" then "Run anyway"
3. The application will open in your default web browser
4. Enter your AWS Access Key and Secret Access Key when prompted
5. Start using OpenFlux AI Assistant!

SECURITY NOTES:
- Your AWS credentials are encrypted and stored only in memory
- Credentials are never saved to disk
- All data is cleared when you close the application

TROUBLESHOOTING:
- If the app doesn't start, try running as administrator
- Make sure your AWS credentials have Bedrock access permissions
- Check your internet connection
- Verify your antivirus isn't blocking the application

Built on: $(date)
Compatible with: Windows 10, Windows 11 (64-bit)
EOF
    
    # Create ZIP package
    cd dist
    zip -r OpenFlux_AI_Assistant_Windows11.zip OpenFlux_Windows11_Portable/
    cd ..
    
    echo ""
    echo "📁 Files ready for download:"
    echo "   - dist/OpenFlux_AI_Assistant.exe (Windows executable)"
    echo "   - dist/OpenFlux_Windows11_Portable/ (distribution folder)"
    echo "   - dist/OpenFlux_AI_Assistant_Windows11.zip (ready to transfer)"
    echo ""
    echo "📥 To download to your Windows laptop:"
    echo "   scp -i your-key.pem ec2-user@$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):~/Openflux/dist/OpenFlux_AI_Assistant_Windows11.zip ./"
    echo ""
    echo "🎯 Then on Windows: Extract and run OpenFlux_AI_Assistant.exe"
    
else
    echo "❌ Build failed! Check the Docker output above for errors."
    exit 1
fi