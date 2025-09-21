#!/bin/bash
# Fix curl package conflicts on Amazon Linux

echo "🔧 Fixing curl package conflicts..."

# Option 1: Remove conflicting packages and reinstall
echo "Attempting to resolve curl conflicts..."

# Check current curl installation
echo "Current curl packages:"
rpm -qa | grep curl

# Try to resolve conflicts by allowing erasure
sudo yum install -y --allowerasing curl

# If that fails, try removing curl-minimal and installing curl
if [ $? -ne 0 ]; then
    echo "Trying alternative approach..."
    sudo yum remove -y curl-minimal
    sudo yum install -y curl
fi

# Verify curl is working
if command -v curl &> /dev/null; then
    echo "✅ Curl is now available"
    curl --version
else
    echo "❌ Curl installation failed"
    echo "You can continue without curl - wget is available as alternative"
fi

echo "✅ Curl conflict resolution complete"