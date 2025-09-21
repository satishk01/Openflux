# OpenFlux AI Assistant - Windows Executable Build Guide

This guide provides step-by-step instructions for building a Windows executable of the OpenFlux AI Assistant on Amazon Linux 2.

## 📋 Prerequisites

- Amazon Linux 2 EC2 instance (t3.medium or larger recommended)
- At least 8GB RAM and 20GB free disk space
- Internet connection for downloading dependencies
- SSH access to the EC2 instance

## 🚀 Quick Start

### Step 1: Connect to Your EC2 Instance

```bash
ssh -i your-key.pem ec2-user@your-ec2-instance-ip
```

### Step 2: Clone the Repository

```bash
git clone <your-repository-url>
cd openflux-streamlit-app
```

### Step 3: Set Up Build Environment

```bash
# Make the setup script executable
chmod +x build/setup_build_environment.sh

# Run the setup script (this will take 10-15 minutes)
./build/setup_build_environment.sh
```

### Step 4: Build the Executable

```bash
# Make the build script executable
chmod +x build/build_executable.sh

# Run the build process (this will take 15-20 minutes)
./build/build_executable.sh
```

### Step 5: Validate the Build

```bash
# Make the validation script executable
chmod +x build/validate_executable.sh

# Validate the built executable
./build/validate_executable.sh
```

### Step 6: Download the Executable

The build process creates a distribution package at:
```
dist/OpenFlux_AI_Assistant_Portable.zip
```

Download this file to your local machine using SCP:

```bash
# From your local machine
scp -i your-key.pem ec2-user@your-ec2-instance-ip:~/openflux-streamlit-app/dist/OpenFlux_AI_Assistant_Portable.zip ./
```

## 📖 Detailed Instructions

### Environment Setup Details

The `setup_build_environment.sh` script performs the following:

1. **System Updates**: Updates all system packages
2. **Dependencies**: Installs build tools (gcc, make, etc.)
3. **Python 3.9**: Installs Python 3.9 from source
4. **Virtual Environment**: Creates isolated Python environment
5. **Wine Installation**: Installs Wine for Windows cross-compilation
6. **Windows Python**: Installs Python 3.9 in Wine environment

### Build Process Details

The `build_executable.sh` script:

1. **Dependency Installation**: Installs all Python packages
2. **Asset Preparation**: Sets up icons and resources
3. **PyInstaller Setup**: Installs PyInstaller in Wine
4. **Executable Creation**: Builds the Windows executable
5. **Package Creation**: Creates distribution package with documentation

### Build Configuration

The build uses `build/openflux.spec` which configures:

- **Hidden Imports**: Ensures all required modules are included
- **Data Files**: Includes styles, templates, and components
- **Exclusions**: Removes unnecessary modules to reduce size
- **Windows Settings**: Configures for Windows compatibility

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Wine Configuration Issues

**Problem**: Wine fails to configure or install Windows Python

**Solution**:
```bash
# Reset Wine configuration
rm -rf ~/.wine
export WINEARCH=win64
export WINEPREFIX=$HOME/.wine
winecfg
```

#### 2. Python Installation Fails

**Problem**: Python 3.9 compilation fails

**Solution**:
```bash
# Install additional dependencies
sudo yum install -y ncurses-devel gdbm-devel tk-devel uuid-devel

# Retry Python installation
cd /tmp
wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
tar xzf Python-3.9.18.tgz
cd Python-3.9.18
./configure --enable-optimizations --with-ensurepip=install
make -j$(nproc)
sudo make altinstall
```

#### 3. PyInstaller Build Fails

**Problem**: PyInstaller cannot find modules or fails to build

**Solution**:
```bash
# Clean previous builds
rm -rf build dist *.spec

# Reinstall PyInstaller
wine python -m pip uninstall pyinstaller
wine python -m pip install pyinstaller==5.13.2

# Retry build
./build/build_executable.sh
```

#### 4. Executable Too Large

**Problem**: Generated executable is over 500MB

**Solution**:
- Review the `excludes` list in `build/openflux.spec`
- Add more modules to exclude unnecessary dependencies
- Use UPX compression (already enabled in spec file)

#### 5. Missing Dependencies

**Problem**: Executable fails to run due to missing modules

**Solution**:
- Add missing modules to `hiddenimports` in `build/openflux.spec`
- Test the executable with Wine to identify missing dependencies

### Build Environment Verification

Before building, verify your environment:

```bash
# Check Python versions
python3.9 --version
wine python --version

# Check Wine configuration
wine --version
winecfg

# Check virtual environment
source openflux_build_env/bin/activate
pip list | grep -E "(streamlit|boto3|pyinstaller)"
```

### Performance Optimization

For faster builds:

1. **Use Larger Instance**: t3.large or t3.xlarge for faster compilation
2. **Parallel Builds**: The scripts use `make -j$(nproc)` for parallel compilation
3. **Clean Builds**: Remove previous builds before starting new ones

## 📊 Build Specifications

### Target Configuration

- **Target OS**: Windows 10/11 (64-bit)
- **Python Version**: 3.9.18
- **Architecture**: x86_64
- **Executable Type**: Single-file executable

### Dependencies Included

- Streamlit web framework
- AWS Boto3 SDK
- Cryptography for credential encryption
- All UI components and services
- Required system libraries

### File Structure

```
dist/
├── OpenFlux_AI_Assistant.exe          # Main executable
├── OpenFlux_Portable/                 # Distribution folder
│   ├── OpenFlux_AI_Assistant.exe      # Executable copy
│   └── README.txt                     # User instructions
├── OpenFlux_AI_Assistant_Portable.zip # Distribution package
└── validation_report.txt              # Build validation report
```

## 🧪 Testing the Executable

### On Windows Machine

1. **Extract Package**: Unzip `OpenFlux_AI_Assistant_Portable.zip`
2. **Run Executable**: Double-click `OpenFlux_AI_Assistant.exe`
3. **Security Warning**: Click "More info" → "Run anyway" if Windows shows warning
4. **Browser Opens**: Application should open in default browser
5. **Enter Credentials**: Provide AWS Access Key and Secret Key
6. **Test Features**: Verify all functionality works

### Test Checklist

- [ ] Application starts without errors
- [ ] Credentials input form appears
- [ ] AWS connection test works
- [ ] AI model selection functions
- [ ] File upload and analysis works
- [ ] Spec generation completes
- [ ] All UI components render correctly
- [ ] Application closes cleanly

## 📦 Distribution

### For End Users

Provide users with:

1. **Executable Package**: `OpenFlux_AI_Assistant_Portable.zip`
2. **AWS Setup Guide**: Instructions for obtaining AWS credentials
3. **System Requirements**: Windows 10/11, 8GB RAM, internet connection
4. **Support Information**: Contact details for technical support

### AWS Credentials Setup for Users

Users will need:

1. **AWS Account**: With Bedrock access enabled
2. **IAM User**: With programmatic access
3. **Permissions**: Bedrock model access permissions
4. **Credentials**: Access Key ID and Secret Access Key

## 🔒 Security Considerations

### Build Security

- Build environment is isolated in virtual environment
- No credentials are embedded in executable
- All dependencies are from official sources

### Runtime Security

- User credentials are encrypted in memory
- No credential persistence to disk
- Secure credential clearing on exit
- HTTPS/TLS for all AWS communications

## 📈 Monitoring and Maintenance

### Build Monitoring

- Check build logs for warnings or errors
- Monitor executable size trends
- Validate all features after each build

### Updates and Maintenance

- Regularly update Python dependencies
- Monitor for security updates
- Test with latest AWS Bedrock models
- Update Wine and build tools periodically

## 🆘 Support and Resources

### Getting Help

1. **Check Logs**: Review build output for specific errors
2. **Validation Report**: Check `dist/validation_report.txt`
3. **Test Environment**: Verify setup with validation scripts
4. **Documentation**: Review this guide and troubleshooting section

### Additional Resources

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [Wine Documentation](https://wiki.winehq.org/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Build Time Estimate**: 30-45 minutes total
**Executable Size**: ~150-300MB
**Supported Windows**: Windows 10, Windows 11 (64-bit)