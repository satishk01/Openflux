# Windows Build Instructions

Since Wine is not available on Amazon Linux 2023, here are alternative approaches to create a Windows executable:

## Option 1: Build on Windows Machine (Recommended)

### Prerequisites
- Windows 10 or Windows 11
- Python 3.9+ installed
- Git (optional, for cloning)

### Steps

1. **Transfer your code to Windows machine:**
   ```cmd
   # Option A: Download as ZIP from your repository
   # Option B: Use SCP to transfer from EC2
   scp -i your-key.pem -r ec2-user@your-ec2-ip:~/your-project ./
   ```

2. **Install Python dependencies:**
   ```cmd
   cd your-project
   pip install -r requirements.txt
   pip install pyinstaller==5.13.2
   ```

3. **Build the executable:**
   ```cmd
   pyinstaller build/openflux.spec --clean --noconfirm
   ```

4. **Test the executable:**
   ```cmd
   dist\OpenFlux_AI_Assistant.exe
   ```

## Option 2: Use GitHub Actions (Automated)

Create `.github/workflows/build-windows.yml`:

```yaml
name: Build Windows Executable

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller==5.13.2
    
    - name: Build executable
      run: |
        pyinstaller build/openflux.spec --clean --noconfirm
    
    - name: Upload executable
      uses: actions/upload-artifact@v3
      with:
        name: OpenFlux-Windows-Executable
        path: dist/OpenFlux_AI_Assistant.exe
```

## Option 3: Use Docker with Windows Container

```dockerfile
# Use Windows Server Core with Python
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Install Python
RUN powershell -Command \
    Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.9.18/python-3.9.18-amd64.exe -OutFile python-installer.exe; \
    Start-Process python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; \
    Remove-Item python-installer.exe

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies and build
RUN pip install -r requirements.txt && \
    pip install pyinstaller==5.13.2 && \
    pyinstaller build/openflux.spec --clean --noconfirm
```

## Option 4: Cross-Compilation with PyInstaller Bootloader

This is more complex but possible:

1. **Download Windows PyInstaller bootloader:**
   ```bash
   # On your Linux machine
   wget https://github.com/pyinstaller/pyinstaller/releases/download/v5.13.2/PyInstaller-5.13.2.tar.gz
   tar -xzf PyInstaller-5.13.2.tar.gz
   ```

2. **Modify the spec file for cross-compilation:**
   ```python
   # Add to openflux.spec
   import sys
   sys.platform = 'win32'
   ```

3. **Build with specific bootloader:**
   ```bash
   pyinstaller --bootloader-ignore-signals \
               --target-arch=x86_64 \
               build/openflux.spec
   ```

## Recommended Approach

**For immediate results:** Use **Option 1** (Windows machine build)

**For automation:** Use **Option 2** (GitHub Actions)

The Linux executable created on your EC2 instance can serve as a reference and testing platform, while the Windows executable should be built natively on Windows for best compatibility.

## File Transfer Commands

To transfer your project from EC2 to Windows:

```bash
# Create a zip of your project (on EC2)
tar -czf openflux-project.tar.gz .

# Download to Windows (from Windows machine)
scp -i your-key.pem ec2-user@your-ec2-ip:~/your-project/openflux-project.tar.gz ./

# Or use WinSCP GUI tool for easier file transfer
```

## Testing

Once you have the Windows executable:

1. Test on Windows 10 and Windows 11
2. Verify AWS credentials input works
3. Test all application features
4. Check antivirus compatibility
5. Validate file size and startup time