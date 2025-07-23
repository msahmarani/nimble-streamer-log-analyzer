#!/bin/bash
# Setup script for Oracle Linux 10
# Run this script on your VM to set up the Nimble Streamer Log Analyzer

echo "🐧 Setting up Nimble Streamer Log Analyzer on Oracle Linux 10"
echo "============================================================="

# Update system packages
echo "📦 Updating system packages..."
sudo dnf update -y

# Install Python 3.11+ and development tools
echo "🐍 Installing Python and development tools..."
sudo dnf install -y python3 python3-pip python3-venv python3-devel
sudo dnf install -y gcc gcc-c++ make git

# Install system dependencies for Python packages
echo "🔧 Installing system dependencies..."
sudo dnf install -y sqlite sqlite-devel
sudo dnf install -y libjpeg-turbo-devel zlib-devel freetype-devel
sudo dnf install -y libpng-devel

# Create virtual environment
echo "🌐 Creating Python virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Install maxminddb for offline database support (optional)
echo "🗄️ Installing maxminddb for offline databases..."
pip install maxminddb>=2.2.0

# Create ipinfo_data directory for optional databases
echo "📁 Creating IPinfo data directory..."
mkdir -p ipinfo_data

# IPinfo Lite API Information
echo "🌍 IPinfo Integration Setup"
echo "=================================="
echo "✅ IPinfo Lite API: FREE & UNLIMITED"
echo "   - No token required"
echo "   - Country, continent, and ASN data"
echo "   - No daily/monthly limits"
echo ""
echo "📋 API Endpoint: https://api.ipinfo.io/lite/{ip}"
echo "📋 Example: https://api.ipinfo.io/lite/8.8.8.8"
echo ""
echo "� Optional: Enhanced IPinfo with Token"
echo "   - Get free token at: https://ipinfo.io/signup"
echo "   - City-level accuracy + ISP data"
echo "   - 50,000 requests/month free"
echo ""
echo "✅ Your analyzer will use IPinfo Lite API by default!"
echo "✅ Add token in web interface for enhanced features."

# Set executable permissions
echo "🔐 Setting executable permissions..."
chmod +x start_web_gui_linux.sh

# Check Python version
echo "✅ Setup verification:"
echo "Python version: $(python3 --version)"
echo "Pip version: $(pip --version)"

# Test import of key modules
echo "🧪 Testing key module imports..."
python3 -c "import dash; print('✅ Dash imported successfully')" 2>/dev/null || echo "❌ Dash import failed"
python3 -c "import pandas; print('✅ Pandas imported successfully')" 2>/dev/null || echo "❌ Pandas import failed"
python3 -c "import sqlite3; print('✅ SQLite3 imported successfully')" 2>/dev/null || echo "❌ SQLite3 import failed"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Run: source .venv/bin/activate"
echo "2. Run: ./start_web_gui_linux.sh"
echo "3. Access: http://your-vm-ip:8050"
echo ""
echo "🔥 For external access, make sure to:"
echo "   - Open port 8050 in firewall"
echo "   - Use 0.0.0.0 as host in web_gui.py"
