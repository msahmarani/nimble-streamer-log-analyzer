"""
Simple Web GUI Launcher - Avoids threading issues
"""

import os
import sys

def main():
    """Simple launcher that avoids threading issues."""
    
    print("🚀 Simple Web GUI Launcher")
    print("=" * 40)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Set environment variable to avoid GUI threading issues
    os.environ['MPLBACKEND'] = 'Agg'  # Use non-interactive matplotlib backend
    
    try:
        # Import and run the web GUI
        from web_gui import app, find_available_port
        
        print("✅ Modules imported successfully")
        
        # Find available port
        port = find_available_port(8050)
        if port is None:
            print("❌ No available ports found")
            return
        
        print(f"🌐 Starting server on http://127.0.0.1:{port}")
        print("📝 Press Ctrl+C to stop the server")
        print("=" * 40)
        
        # Run with minimal configuration to avoid issues
        app.run(
            host='127.0.0.1',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Try running start_web_gui.bat instead")

if __name__ == "__main__":
    main()
