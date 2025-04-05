#!/usr/bin/env python3
"""
Simple HTTP server for the GAMS frontend dashboard.
This server provides both static file serving and a basic API for the dashboard.
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
import random
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import threading

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import GAMS components, but provide mock data if they're not available
try:
    from core.background_execution.process_orchestrator import ProcessOrchestrator
    from core.background_execution.task_scheduler import TaskScheduler
    from core.background_execution.event_manager import EventManager
    from core.background_execution.recovery_manager import RecoveryManager
    GAMS_AVAILABLE = True
except ImportError:
    print("GAMS components not available, using mock data")
    GAMS_AVAILABLE = False

# Try to import Google Analytics integration
try:
    from core.integrations.analytics_integration_manager import AnalyticsIntegrationManager
    GA_AVAILABLE = True
except ImportError:
    print("Google Analytics integration not available, using mock data")
    GA_AVAILABLE = False

# Port for the server
PORT = 8000

# Mock data for when GAMS components aren't available
MOCK_TASKS = [
    {
        "id": "task_website_update_123",
        "type": "Website Update",
        "schedule_type": "once",
        "schedule_value": (datetime.now() + timedelta(days=1)).isoformat(),
        "priority": 2,
        "status": "scheduled",
        "params": {"repository_name": "marketing-website"}
    },
    {
        "id": "task_content_analysis_456",
        "type": "Content Analysis",
        "schedule_type": "interval",
        "schedule_value": 86400,  # Daily
        "priority": 5,
        "status": "running",
        "params": {"content_ids": ["content_1", "content_2"]}
    },
    {
        "id": "task_report_generation_789",
        "type": "Report Generation",
        "schedule_type": "cron",
        "schedule_value": "0 8 * * 1",  # Mondays at 8am
        "priority": 8,
        "status": "idle",
        "params": {"report_type": "weekly", "format": "pdf"}
    }
]

MOCK_EVENTS = [
    {
        "id": "event_1",
        "name": "website_update_completed",
        "data": {"repository_name": "marketing-website", "status": "success"},
        "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat()
    },
    {
        "id": "event_2",
        "name": "traffic_spike",
        "data": {"page_url": "blog/new-product-launch", "spike_percentage": 150},
        "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat()
    },
    {
        "id": "event_3",
        "name": "content_generated",
        "data": {"content_count": 5, "content_type": "article"},
        "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()
    },
    {
        "id": "event_4",
        "name": "content_performance_change",
        "data": {"content_id": "product-page-3", "change": -25},
        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat()
    },
    {
        "id": "event_5",
        "name": "system_backup",
        "data": {"backup_type": "daily", "status": "completed"},
        "timestamp": (datetime.now() - timedelta(hours=6)).isoformat()
    }
]

MOCK_SYSTEM_STATUS = {
    "process_orchestrator": {"status": "healthy", "active_processes": 5},
    "task_scheduler": {"status": "healthy", "scheduled_tasks": 12},
    "event_manager": {"status": "healthy", "events_today": 24},
    "recovery_manager": {"status": "healthy", "recovery_actions": 0},
    "last_updated": datetime.now().isoformat()
}

MOCK_PERFORMANCE_DATA = {
    "website_traffic": [1200, 1900, 3000, 5000, 4000, 6000],
    "conversions": [50, 90, 150, 250, 200, 350],
    "bounce_rate": [65, 58, 52, 48, 50, 45],
    "avg_session_duration": [120, 145, 160, 175, 165, 180],
    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
}

# Global variables for the GAMS components
orchestrator = None
task_scheduler = None
event_manager = None
recovery_manager = None
analytics_manager = None


class GAMSHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for the GAMS frontend."""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        self.directory = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        # API endpoints
        if self.path.startswith('/api/'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Route to the appropriate API handler
            if self.path == '/api/tasks':
                self.wfile.write(json.dumps(self.get_tasks()).encode())
            elif self.path == '/api/events':
                self.wfile.write(json.dumps(self.get_events()).encode())
            elif self.path == '/api/system-status':
                self.wfile.write(json.dumps(self.get_system_status()).encode())
            elif self.path == '/api/performance-data':
                self.wfile.write(json.dumps(self.get_performance_data()).encode())
            elif self.path == '/api/analytics/sync':
                self.wfile.write(json.dumps(self.sync_analytics_data()).encode())
            else:
                self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
        else:
            # Serve static files
            return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Route to the appropriate API handler
        if self.path == '/api/schedule-task':
            result = self.schedule_task(data)
            self.wfile.write(json.dumps(result).encode())
        elif self.path == '/api/update-website':
            result = self.update_website(data)
            self.wfile.write(json.dumps(result).encode())
        elif self.path == '/api/analytics/sync':
            result = self.sync_analytics_data()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
    
    def get_tasks(self):
        """Get the list of scheduled tasks."""
        if GAMS_AVAILABLE and task_scheduler:
            # Get real tasks from the Task Scheduler
            tasks = task_scheduler.get_all_tasks()
            return tasks
        else:
            # Return mock data
            return MOCK_TASKS
    
    def get_events(self):
        """Get the list of recent events."""
        if GAMS_AVAILABLE and event_manager:
            # Get real events from the Event Manager
            events = event_manager.get_events_history()
            return events
        else:
            # Return mock data
            return MOCK_EVENTS
    
    def get_system_status(self):
        """Get the current system status."""
        if GAMS_AVAILABLE and orchestrator:
            # Get real system status
            status = {
                "process_orchestrator": {"status": "healthy", "active_processes": len(orchestrator.processes)},
                "task_scheduler": {"status": "healthy", "scheduled_tasks": len(task_scheduler.tasks)},
                "event_manager": {"status": "healthy", "events_today": len(event_manager.get_events_history())},
                "recovery_manager": {"status": "healthy", "recovery_actions": 0},
                "last_updated": datetime.now().isoformat()
            }
            return status
        else:
            # Return mock data
            return MOCK_SYSTEM_STATUS
    
    def get_performance_data(self):
        """Get performance data for charts."""
        # If Google Analytics integration is available, use it
        if GA_AVAILABLE and analytics_manager:
            try:
                # Get dashboard data from the analytics manager
                dashboard_data = analytics_manager.get_analytics_data_for_dashboard()
                return dashboard_data["website_traffic"]
            except Exception as e:
                print(f"Error getting analytics data: {e}")
                # Fall back to mock data
                return MOCK_PERFORMANCE_DATA
        else:
            # Fall back to mock data
            return MOCK_PERFORMANCE_DATA
    
    def schedule_task(self, data):
        """Schedule a new task."""
        if GAMS_AVAILABLE and task_scheduler:
            # Schedule a real task
            task_id = f"task_{data['type']}_{int(time.time())}"
            
            # Convert schedule value based on type
            schedule_value = data['schedule_value']
            if data['schedule_type'] == 'once':
                schedule_value = datetime.fromisoformat(schedule_value)
            elif data['schedule_type'] == 'interval':
                schedule_value = int(schedule_value)
            
            # Schedule the task
            task_scheduler.schedule_task(
                task_id=task_id,
                task_func=lambda: print(f"Running task {task_id}"),
                schedule_type=data['schedule_type'],
                schedule_value=schedule_value,
                priority=int(data['priority']),
                params=data.get('params', {})
            )
            
            return {"status": "success", "task_id": task_id}
        else:
            # Simulate task scheduling
            task_id = f"task_{data['type']}_{int(time.time())}"
            MOCK_TASKS.append({
                "id": task_id,
                "type": data['type'],
                "schedule_type": data['schedule_type'],
                "schedule_value": data['schedule_value'],
                "priority": int(data['priority']),
                "status": "scheduled",
                "params": data.get('params', {})
            })
            return {"status": "success", "task_id": task_id}
    
    def update_website(self, data):
        """Schedule a website update."""
        if GAMS_AVAILABLE and orchestrator:
            # Schedule a real website update
            process = orchestrator.schedule_website_update(
                repository_name=data.get('repository_name'),
                schedule_type=data['schedule_type'],
                schedule_value=data['schedule_value']
            )
            return {"status": "success", "process_id": process['id']}
        else:
            # Simulate website update
            process_id = f"website_update_{data.get('repository_name', 'all')}_{int(time.time())}"
            return {"status": "success", "process_id": process_id}
            
    def sync_analytics_data(self):
        """Sync analytics data from Google Analytics."""
        if GA_AVAILABLE and analytics_manager:
            try:
                # Sync data from Google Analytics
                sync_results = analytics_manager.sync_google_analytics_data()
                return {
                    "status": "success",
                    "message": f"Successfully synced data from Google Analytics",
                    "details": sync_results
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error syncing data from Google Analytics: {str(e)}"
                }
        else:
            return {
                "status": "error",
                "message": "Google Analytics integration not available"
            }


def initialize_gams():
    """Initialize the GAMS components if available."""
    global orchestrator, task_scheduler, event_manager, recovery_manager, analytics_manager
    
    if not GAMS_AVAILABLE:
        # Even if GAMS is not available, try to initialize Google Analytics
        if GA_AVAILABLE:
            try:
                analytics_manager = AnalyticsIntegrationManager()
                print("Google Analytics integration initialized successfully")
            except Exception as e:
                print(f"Error initializing Google Analytics integration: {e}")
        return
    
    try:
        # Create configuration
        config = {
            'process_orchestrator': {
                'scheduler_interval': 5,
                'max_concurrent_processes': 5
            },
            'task_scheduler': {
                'max_concurrent_tasks': 10,
                'default_priority': 5
            },
            'event_manager': {
                'max_events_history': 100
            },
            'recovery_manager': {
                'health_check_interval': 10,
                'max_recovery_attempts': 3
            }
        }
        
        # Create the components
        task_scheduler = TaskScheduler(config.get('task_scheduler', {}))
        event_manager = EventManager(config.get('event_manager', {}))
        recovery_manager = RecoveryManager(config.get('recovery_manager', {}))
        
        # Create the ProcessOrchestrator
        orchestrator = ProcessOrchestrator(
            config=config,
            task_scheduler=task_scheduler,
            event_manager=event_manager,
            recovery_manager=recovery_manager
        )
        
        # Initialize Google Analytics integration if available
        if GA_AVAILABLE:
            try:
                analytics_manager = AnalyticsIntegrationManager()
                print("Google Analytics integration initialized successfully")
                
                # Schedule periodic sync of Google Analytics data
                if task_scheduler:
                    task_scheduler.schedule_task(
                        task_id="google_analytics_sync",
                        task_func=lambda: analytics_manager.sync_google_analytics_data(),
                        schedule_type="interval",
                        schedule_value=3600,  # Sync every hour
                        priority=5
                    )
                    print("Scheduled periodic Google Analytics data sync")
            except Exception as e:
                print(f"Error initializing Google Analytics integration: {e}")
        
        print("GAMS components initialized successfully")
    except Exception as e:
        print(f"Error initializing GAMS components: {e}")


def run_server():
    """Run the HTTP server."""
    # Initialize GAMS components
    initialize_gams()
    
    # Create and start the server
    handler = GAMSHTTPRequestHandler
    httpd = socketserver.ThreadingTCPServer(("", PORT), handler)
    
    print(f"Serving GAMS dashboard at http://localhost:{PORT}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
