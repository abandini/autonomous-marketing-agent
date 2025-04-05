#!/usr/bin/env python3
import requests
import json

def test_gams_control_api():
    """Test the GAMS control API endpoint."""
    url = "http://localhost:5001/api/operator/system/control"
    headers = {"Content-Type": "application/json"}
    data = {"action": "start"}
    
    print(f"Sending POST request to {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            print("Success! The API endpoint is working correctly.")
        else:
            print(f"Error: Received status code {response.status_code}")
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    test_gams_control_api()
