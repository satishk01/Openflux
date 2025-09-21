# OpenFlux AI Assistant - Complete Deployment Steps

## 🚀 Step-by-Step Deployment Guide

Follow these exact steps to deploy your code to EC2 and build the Windows executable.

### Phase 1: EC2 Setup and Code Deployment

#### 1. Launch EC2 Instance
```bash
# Launch Amazon Linux 2 instance (t3.medium or larger)
# Ensure you have SSH key pair configured
# Security group should allow SSH (port 22)
```

#### 2. Connect to EC2 Instance
```bash
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

#### 3. Upload Your Code
Option A - Using Git (Recommended):
```bash
# On EC2 instance
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

Option B - Using SCP:
```bash
# From your local machine
scp -i your-key.pem -r /path/to/your/openflux-code ec2-user@your-ec2-ip:~/
ssh -i your-key.pem ec2-user@your-ec2-ip
cd openflux-code
```

### Phase 2: Build Environment Setup

#### 4. Make Scripts Executable
```bash
chmod +x build/setup_build_environment.sh
chmod +x build/build_executable.sh
chmod +x build/validate_executable.sh
```

#### 5. Run Environment Setup
```bash
# This takes 10-15 minutes
./build/setup_build_environment.sh
```

**Expected Output:**
- System packages updated
- Python 3.9 installed
- Virtual environment created
- Wine installed and configured
- Windows Python installed in Wine

#### 6. Verify Environment
```bash
# Check installations
python3.9 --version          # Should show Python 3.9.18
wine python --version        # Should show Python 3.9.18
wine --version              # Should show Wine version

# Activate virtual environment
source openflux_build_env/bin/activate
pip --version               # Should show pip in virtual env
```

### Phase 3: Build the Executable

#### 7. Build the Windows Executable
```bash
# Ensure you're in the project root directory
pwd  # Should show /home/ec2-user/your-project-name

# Run the build (takes 15-20 minutes)
./build/build_executable.sh
```

**Build Process Steps:**
1. Installs Python dependencies
2. Sets up Wine environment
3. Installs PyInstaller in Wine
4. Builds Windows executable
5. Creates distribution package

**Expected Output:**
```
🏗️ Building OpenFlux AI Assistant Windows Executable...
📦 Installing Python dependencies...
🎨 Setting up assets...
🧹 Cleaning previous builds...
📦 Installing PyInstaller in Wine Python...
📦 Installing dependencies in Wine Python...
🚀 Creating Windows executable...
✅ Build successful!
📊 Executable size: XXXmb
📦 Creating distribution package...
🎉 Build completed successfully!
```

#### 8. Validate the Build
```bash
./build/validate_executable.sh
```

**Validation Checks:**
- Executable file exists and has reasonable size
- Distribution package created
- All required files present
- Basic functionality test

### Phase 4: Download and Test

#### 9. Download the Executable
```bash
# Check the files created
ls -la dist/
# You should see:
# - OpenFlux_AI_Assistant.exe
# - OpenFlux_Portable/ (folder)
# - OpenFlux_AI_Assistant_Portable.zip
# - validation_report.txt
```

#### 10. Download to Your Local Machine
```bash
# From your local machine (new terminal)
scp -i your-key.pem ec2-user@your-ec2-ip:~/your-project/dist/OpenFlux_AI_Assistant_Portable.zip ./
```

#### 11. Test on Windows
1. Extract `OpenFlux_AI_Assistant_Portable.zip`
2. Run `OpenFlux_AI_Assistant.exe`
3. Enter your AWS credentials when prompted
4. Test all functionality

### Phase 5: Troubleshooting

#### Common Issues and Solutions

**Issue 1: Wine Installation Fails**
```bash
# Solution: Install EPEL repository first
sudo yum install -y epel-release
sudo yum clean all
sudo yum install -y wine
```

**Issue 2: Python Compilation Fails**
```bash
# Solution: Install additional development tools
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel libffi-devel bzip2-devel
```

**Issue 3: PyInstaller Build Fails**
```bash
# Solution: Clean and retry
rm -rf build dist *.spec
wine python -m pip install --upgrade pyinstaller
./build/build_executable.sh
```

**Issue 4: Executable Too Large**
```bash
# Check size
ls -lh dist/OpenFlux_AI_Assistant.exe

# If over 500MB, optimize by editing build/openflux.spec
# Add more modules to the 'excludes' list
```

**Issue 5: Missing Dependencies**
```bash
# Add missing modules to hiddenimports in build/openflux.spec
# Common missing modules:
# - 'altair'
# - 'plotly.validators'
# - 'streamlit.components.v1.html'
```

### Phase 6: Distribution

#### 12. Prepare for Distribution
The build creates:
- `OpenFlux_AI_Assistant_Portable.zip` - Ready for distribution
- Contains executable + user documentation
- Size typically 150-300MB

#### 13. User Instructions
Provide users with:
1. The ZIP file
2. AWS credentials setup guide
3. System requirements (Windows 10/11, 8GB RAM)
4. Support contact information

### Build Specifications

**Environment:**
- Amazon Linux 2
- Python 3.9.18
- Wine for Windows cross-compilation
- PyInstaller 5.13.2

**Output:**
- Windows 64-bit executable
- Single-file deployment
- No installation required
- Includes all dependencies

**Features:**
- AWS credentials input UI
- Encrypted credential storage
- All original OpenFlux functionality
- Streamlit web interface

### Performance Notes

**Build Time:** 30-45 minutes total
- Environment setup: 10-15 minutes
- Executable build: 15-20 minutes
- Validation: 2-3 minutes

**Resource Usage:**
- Minimum: t3.medium (2 vCPU, 4GB RAM)
- Recommended: t3.large (2 vCPU, 8GB RAM)
- Disk space: 20GB free space required

**Final Executable:**
- Size: 150-300MB
- Startup time: 10-15 seconds
- Memory usage: 200-500MB during operation

### Security Checklist

- [ ] No credentials embedded in executable
- [ ] User credentials encrypted in memory only
- [ ] No credential persistence to disk
- [ ] HTTPS/TLS for all AWS communications
- [ ] Secure memory clearing on exit

### Success Criteria

✅ **Build Successful When:**
- Executable file created without errors
- Size between 100-400MB
- Validation script passes all checks
- Test run on Windows works
- All application features functional

🎉 **Ready for Production When:**
- Tested on Windows 10 and 11
- AWS connectivity verified
- All UI components working
- File operations functional
- Error handling working properly

---

**Total Time Investment:** 1-2 hours
**Skill Level Required:** Intermediate (Linux command line)
**Success Rate:** High (following exact steps)