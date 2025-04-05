#!/usr/bin/env python3
"""
Test script for the GAMS control API endpoint
"""
import requests
import json
import sys

def test_gams_control(action):
    """Test the GAMS control API endpoint"""
    url = "http://localhost:5001/api/operator/system/control"
    headers = {"Content-Type": "application/json"}
    data = {"action": action}
    
    print(f"Sending {action} request to {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data)}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        try:
            print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    action = "start"
    if len(sys.argv) > 1:
        action = sys.argv[1]
    
    if action not in ["start", "stop"]:
        print(f"Invalid action: {action}. Must be 'start' or 'stop'.")
        sys.exit(1)
    
    test_gams_control(action)
