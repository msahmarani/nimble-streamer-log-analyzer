#!/bin/bash
# Linux launcher for Nimble Streamer Log Analyzer Web GUI
# Compatible with Oracle Linux 10

echo "🚀 Starting Nimble Streamer Log Analyzer Web GUI"
echo "================================================="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup_oracle_linux.sh first"
    exit 1
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source .venv/bin/activate

# Check if web_gui.py exists
if [ ! -f "web_gui.py" ]; then
    echo "❌ web_gui.py not found!"
    exit 1
fi

# Get VM IP address for external access
VM_IP=$(hostname -I | awk '{print $1}')
echo "🌐 VM IP Address: $VM_IP"

# Check if port 8050 is available
if netstat -tuln | grep -q ':8050 '; then
    echo "⚠️ Port 8050 is already in use"
    echo "Trying to find available port..."
    
    # Find available port starting from 8051
    for port in {8051..8060}; do
        if ! netstat -tuln | grep -q ":$port "; then
            echo "✅ Using port $port instead"
            export PORT=$port
            break
        fi
    done
fi

# Start the web application
echo "🌟 Starting web interface..."
echo "📍 Access URLs:"
echo "   Local:    http://localhost:${PORT:-8050}"
echo "   Network:  http://$VM_IP:${PORT:-8050}"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Run the application with external host binding
python3 -c "
import sys
sys.path.insert(0, '.')
from web_gui import app

# Configure for external access
app.run_server(
    host='0.0.0.0',  # Allow external connections
    port=${PORT:-8050},
    debug=False,
    dev_tools_hot_reload=False
)
"
