#!/bin/bash
# Start GAMS Operator Dashboard with API Server
# This script starts the API server and opens the enhanced dashboard

# Configuration
API_PORT=5050
API_SERVER_SCRIPT="api_simulator.py"
DASHBOARD_PATH="frontend/enhanced_operator_dashboard.html"
PROJECT_DIR=$(dirname "$0")

# Function to check if a port is in use
check_port() {
    nc -z localhost $1 >/dev/null 2>&1
    return $?
}

# Function to display status messages
status_message() {
    echo -e "\033[1;34m[GAMS Dashboard]\033[0m $1"
}

# Change to project directory
cd "$PROJECT_DIR" || { echo "Error: Could not change to project directory"; exit 1; }

# Check if API server script exists
if [ ! -f "$API_SERVER_SCRIPT" ]; then
    status_message "Error: API server script not found at $API_SERVER_SCRIPT"
    exit 1
fi

# Check if dashboard file exists
if [ ! -f "$DASHBOARD_PATH" ]; then
    status_message "Error: Dashboard file not found at $DASHBOARD_PATH"
    exit 1
fi

# Check if port is already in use
if check_port $API_PORT; then
    status_message "Warning: Port $API_PORT is already in use. The API server might already be running."
else
    # Make API server script executable
    chmod +x "$API_SERVER_SCRIPT"
    
    # Start API server in background
    status_message "Starting API server on port $API_PORT..."
    python "$API_SERVER_SCRIPT" &
    API_PID=$!
    
    # Wait for API server to start
    status_message "Waiting for API server to start..."
    for i in {1..10}; do
        if check_port $API_PORT; then
            break
        fi
        sleep 1
    done
    
    if ! check_port $API_PORT; then
        status_message "Error: API server failed to start within the timeout period"
        kill $API_PID 2>/dev/null
        exit 1
    fi
    
    status_message "API server started successfully (PID: $API_PID)"
fi

# Open dashboard in browser
status_message "Opening dashboard in browser..."
open "$DASHBOARD_PATH"

status_message "Dashboard is now running!"
status_message "API Server: http://localhost:$API_PORT"
status_message "Dashboard: file://$PWD/$DASHBOARD_PATH"
status_message ""
status_message "Press Ctrl+C to stop the API server and exit"

# Trap Ctrl+C to clean up
trap 'status_message "Stopping API server..."; kill $API_PID 2>/dev/null; status_message "Exited."; exit 0' INT

# Keep script running until Ctrl+C
if [ -n "$API_PID" ]; then
    wait $API_PID
fi
