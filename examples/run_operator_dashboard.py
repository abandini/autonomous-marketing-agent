"""
Run Operator Dashboard Demo

This script starts the operator dashboard server and provides instructions
for accessing the operator interface in a web browser.
"""

import os
import sys
import webbrowser
import time
from threading import Thread

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frontend.operator_server import run_server

def open_browser():
    """Open the browser after a short delay to ensure server is running."""
    time.sleep(2)  # Wait for server to start
    url = "http://localhost:5000"
    print(f"\nOpening dashboard in browser: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    print("Starting GAMS Operator Dashboard...")
    print("=" * 50)
    print("The dashboard provides a user-friendly interface for operators to:")
    print("  - Review and process approval requests")
    print("  - Update revenue targets and channel mix")
    print("  - Monitor compliance issues")
    print("  - Track financial performance")
    print("  - Oversee active experiments")
    print("=" * 50)
    
    # Start browser in a separate thread
    browser_thread = Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the server (this will block until terminated)
    try:
        run_server(host='localhost', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        print("Thank you for using the GAMS Operator Dashboard!")
