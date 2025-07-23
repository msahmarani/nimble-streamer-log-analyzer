#!/usr/bin/env python3
"""
Linux Web GUI Launcher for Nimble Streamer Log Analyzer
Modified for Oracle Linux 10 deployment with external access support
"""

import os
import sys
import socket
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def get_vm_ip():
    """Get the VM's IP address for external access."""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def find_available_port(start_port=8050, max_attempts=10):
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    return None

def main():
    """Main function to start the web GUI with Linux optimizations."""
    
    print("🐧 Nimble Streamer Log Analyzer - Oracle Linux 10")
    print("=" * 55)
    
    # Check if we're in a virtual environment
    if not os.environ.get('VIRTUAL_ENV'):
        print("⚠️  Warning: Not running in virtual environment")
        print("   Consider running: source .venv/bin/activate")
        print()
    
    # Get network information
    vm_ip = get_vm_ip()
    port = find_available_port()
    
    if not port:
        print("❌ No available ports found!")
        return 1
    
    print(f"🌐 VM IP Address: {vm_ip}")
    print(f"🔌 Using Port: {port}")
    print()
    
    # Import and configure the web application
    try:
        from web_gui import app
        
        print("🚀 Starting Nimble Streamer Log Analyzer...")
        print("📍 Access URLs:")
        print(f"   Local:    http://localhost:{port}")
        print(f"   Network:  http://{vm_ip}:{port}")
        print()
        print("🛑 Press Ctrl+C to stop the server")
        print("🔥 Make sure port {port} is open in firewall!")
        print()
        
        # Start the server with external access
        app.run_server(
            host='0.0.0.0',  # Accept connections from any IP
            port=port,
            debug=False,
            dev_tools_ui=False,
            dev_tools_props_check=False,
            use_reloader=False,
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        return 0
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
