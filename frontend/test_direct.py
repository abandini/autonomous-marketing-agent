#!/usr/bin/env python3
import requests
import json
import time

def test_gams_control():
    """Test the GAMS control API directly."""
    url = "http://localhost:5001/api/operator/system/control"
    headers = {"Content-Type": "application/json"}
    
    # First try to start GAMS
    print("Testing START action...")
    data = {"action": "start"}
    response = requests.post(url, headers=headers, json=data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Wait a moment
    time.sleep(1)
    
    # Then try to stop GAMS
    print("\nTesting STOP action...")
    data = {"action": "stop"}
    response = requests.post(url, headers=headers, json=data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_gams_control()
