#!/usr/bin/env python3
"""
GAMS Dashboard Test Script

This script helps set up and test the enhanced GAMS Operator Dashboard by:
1. Starting the API simulator
2. Opening the dashboard in a browser
3. Providing test instructions

Usage:
    python test_dashboard.py
"""

import os
import sys
import webbrowser
import subprocess
import time
import threading
import http.client
import socket
from pathlib import Path

# Configuration
API_PORT = 5050
API_URL = f"http://localhost:{API_PORT}"
DASHBOARD_PATH = "frontend/enhanced_operator_dashboard.html"

def check_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_server(port, timeout=10):
    """Wait for server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = http.client.HTTPConnection("localhost", port, timeout=1)
            conn.request("GET", "/")
            response = conn.getresponse()
            if response.status == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def start_api_server():
    """Start the API simulator"""
    print("Starting API simulator...")
    
    # Check if port is already in use
    if check_port_in_use(API_PORT):
        print(f"Port {API_PORT} is already in use. The API server might already be running.")
        return None
    
    # Start the API server
    try:
        api_script = Path(__file__).parent / "api_simulator.py"
        if not api_script.exists():
            print(f"Error: API simulator script not found at {api_script}")
            return None
        
        # Make the script executable
        os.chmod(api_script, 0o755)
        
        # Start the API server as a subprocess
        process = subprocess.Popen([sys.executable, str(api_script)], 
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True)
        
        # Wait for the server to start
        if wait_for_server(API_PORT):
            print(f"API simulator started successfully on {API_URL}")
            return process
        else:
            print("Failed to start API simulator within the timeout period")
            process.terminate()
            return None
    except Exception as e:
        print(f"Error starting API simulator: {e}")
        return None

def open_dashboard():
    """Open the dashboard in a browser"""
    dashboard_path = Path(__file__).parent / DASHBOARD_PATH
    if not dashboard_path.exists():
        print(f"Error: Dashboard not found at {dashboard_path}")
        return False
    
    dashboard_url = f"file://{dashboard_path.absolute()}"
    print(f"Opening dashboard at {dashboard_url}")
    webbrowser.open(dashboard_url)
    return True

def print_test_instructions():
    """Print test instructions"""
    print("\n" + "="*80)
    print("GAMS DASHBOARD TEST INSTRUCTIONS")
    print("="*80)
    print("\nThe enhanced GAMS Operator Dashboard is now open in your browser.")
    print("The API simulator is running to provide test data.")
    print("\nTest the following features:")
    print("1. Dashboard Overview:")
    print("   - Check system status indicator")
    print("   - Test the Start/Stop GAMS button")
    print("   - Verify quick stats display")
    
    print("\n2. Analytics Features:")
    print("   - Navigate to the Analytics tab")
    print("   - Refresh metrics, content performance, and recommendations")
    print("   - Generate a performance report with a date range")
    
    print("\n3. Orchestrator Integration:")
    print("   - Navigate to the Orchestrator tab")
    print("   - View active improvement cycles")
    print("   - Check marketing goals and campaigns")
    print("   - Test the advance cycle phase functionality")
    
    print("\n4. Approvals and Settings:")
    print("   - Navigate through the remaining tabs")
    print("   - Verify all UI elements are displayed correctly")
    
    print("\nTo stop the test:")
    print("1. Close the browser tab with the dashboard")
    print("2. Press Ctrl+C in this terminal to stop the API server")
    print("="*80 + "\n")

def main():
    """Main function"""
    # Start the API server
    api_process = start_api_server()
    if not api_process:
        return
    
    # Give the server a moment to fully initialize
    time.sleep(1)
    
    # Open the dashboard
    if not open_dashboard():
        api_process.terminate()
        return
    
    # Print test instructions
    print_test_instructions()
    
    # Keep the script running until user interrupts
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping API server...")
        api_process.terminate()
        print("Test completed. Thank you for testing the GAMS Operator Dashboard!")

if __name__ == "__main__":
    main()
