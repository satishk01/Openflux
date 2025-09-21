"""
Startup script for OpenFlux AI Assistant executable
Handles Streamlit server initialization and browser launching
"""
import sys
import os
import subprocess
import webbrowser
import time
import socket
from pathlib import Path
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openflux.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def find_free_port(start_port=8501, max_attempts=10):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def wait_for_server(port, timeout=30):
    """Wait for Streamlit server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result == 0:
                    return True
        except:
            pass
        time.sleep(0.5)
    return False

def open_browser(port):
    """Open the application in the default browser"""
    url = f"http://localhost:{port}"
    try:
        webbrowser.open(url)
        logger.info(f"Opened browser to {url}")
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        print(f"Please open your browser and go to: {url}")

def cleanup_on_exit():
    """Cleanup function to run on exit"""
    logger.info("Application shutting down...")
    # Any cleanup code here

def main():
    """Main startup function"""
    try:
        logger.info("Starting OpenFlux AI Assistant...")
        
        # Set up environment
        if getattr(sys, 'frozen', False):
            # Running as executable
            app_dir = Path(sys._MEIPASS)
            os.chdir(app_dir)
        else:
            # Running as script
            app_dir = Path(__file__).parent
        
        logger.info(f"Application directory: {app_dir}")
        
        # Find available port
        port = find_free_port()
        if not port:
            logger.error("Could not find available port")
            input("Press Enter to exit...")
            return
        
        logger.info(f"Using port: {port}")
        
        # Prepare Streamlit command
        streamlit_cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.address", "localhost",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--server.fileWatcherType", "none",
            "--theme.base", "dark"
        ]
        
        logger.info("Starting Streamlit server...")
        
        # Start Streamlit server
        process = subprocess.Popen(
            streamlit_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to be ready
        if wait_for_server(port):
            logger.info("Server is ready")
            
            # Open browser after a short delay
            threading.Timer(1.0, lambda: open_browser(port)).start()
            
            print(f"""
🤖 OpenFlux AI Assistant is starting...

🌐 Opening in your browser: http://localhost:{port}

📋 Instructions:
1. The application will open in your default web browser
2. Enter your AWS Access Key and Secret Access Key when prompted
3. Start using OpenFlux AI Assistant!

🔒 Security: Your credentials are encrypted and never stored on disk

⚠️  Keep this window open while using the application
    Close this window to shut down OpenFlux AI Assistant
""")
            
            # Wait for process to complete
            try:
                process.wait()
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                process.terminate()
                
        else:
            logger.error("Server failed to start within timeout")
            process.terminate()
            print("❌ Failed to start the application. Please check the logs.")
            input("Press Enter to exit...")
            
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        print(f"❌ Application startup failed: {e}")
        input("Press Enter to exit...")
    
    finally:
        cleanup_on_exit()

if __name__ == "__main__":
    main()