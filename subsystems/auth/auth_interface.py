"""
Authentication Interface for the Autonomous Marketing Agent.

This module provides a web interface for managing authentication credentials
for various marketing platforms and analytics services.
"""

import os
import json
import logging
from typing import Dict, Any, List
import secrets
from datetime import datetime

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn

from subsystems.auth.auth_manager import AuthManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Marketing Agent Authentication Interface")
security = HTTPBasic()

# Initialize templates
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

# Initialize static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize authentication manager
auth_manager = AuthManager()

# Admin credentials (should be stored securely in production)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "password")

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials."""
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Define platform information
PLATFORM_INFO = {
    "google_analytics": {
        "name": "Google Analytics",
        "description": "Web analytics service that tracks and reports website traffic",
        "fields": ["client_id", "client_secret", "refresh_token"],
        "oauth": True,
        "icon": "google.png"
    },
    "facebook": {
        "name": "Facebook",
        "description": "Social media platform for social networking",
        "fields": ["app_id", "app_secret", "access_token"],
        "oauth": True,
        "icon": "facebook.png"
    },
    "twitter": {
        "name": "Twitter",
        "description": "Social media platform for microblogging",
        "fields": ["api_key", "api_secret", "access_token", "access_token_secret"],
        "oauth": True,
        "icon": "twitter.png"
    },
    "linkedin": {
        "name": "LinkedIn",
        "description": "Social media platform for professional networking",
        "fields": ["client_id", "client_secret"],
        "oauth": True,
        "icon": "linkedin.png"
    },
    "instagram": {
        "name": "Instagram",
        "description": "Social media platform for photo and video sharing",
        "fields": ["username", "password"],
        "oauth": False,
        "icon": "instagram.png"
    },
    "google_ads": {
        "name": "Google Ads",
        "description": "Online advertising platform by Google",
        "fields": ["client_id", "client_secret", "developer_token", "refresh_token"],
        "oauth": True,
        "icon": "google-ads.png"
    },
    "mailchimp": {
        "name": "Mailchimp",
        "description": "Marketing automation platform for email marketing",
        "fields": ["api_key"],
        "oauth": False,
        "icon": "mailchimp.png"
    },
    "hubspot": {
        "name": "HubSpot",
        "description": "Marketing, sales, and customer service platform",
        "fields": ["api_key"],
        "oauth": False,
        "icon": "hubspot.png"
    },
    "semrush": {
        "name": "SEMrush",
        "description": "SEO and competitive analysis tool",
        "fields": ["api_key"],
        "oauth": False,
        "icon": "semrush.png"
    },
    "ahrefs": {
        "name": "Ahrefs",
        "description": "SEO and backlink analysis tool",
        "fields": ["api_key"],
        "oauth": False,
        "icon": "ahrefs.png"
    },
    "moz": {
        "name": "Moz",
        "description": "SEO software and tools",
        "fields": ["access_id", "secret_key"],
        "oauth": False,
        "icon": "moz.png"
    },
    "wordpress": {
        "name": "WordPress",
        "description": "Content management system for websites",
        "fields": ["url", "username", "password"],
        "oauth": False,
        "icon": "wordpress.png"
    }
}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, username: str = Depends(verify_credentials)):
    """Render the index page."""
    platforms = auth_manager.list_platforms()
    platform_data = []
    
    for platform_id in PLATFORM_INFO:
        platform_info = PLATFORM_INFO[platform_id]
        connected = platform_id in platforms
        
        platform_data.append({
            "id": platform_id,
            "name": platform_info["name"],
            "description": platform_info["description"],
            "connected": connected,
            "icon": platform_info.get("icon", "default.png")
        })
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "platforms": platform_data,
            "username": username,
            "title": "Marketing Agent - Platform Connections"
        }
    )

@app.get("/platform/{platform_id}", response_class=HTMLResponse)
async def platform_details(request: Request, platform_id: str, username: str = Depends(verify_credentials)):
    """Render the platform details page."""
    if platform_id not in PLATFORM_INFO:
        return RedirectResponse(url="/")
    
    platform_info = PLATFORM_INFO[platform_id]
    credentials = auth_manager.get_credentials(platform_id) or {}
    
    return templates.TemplateResponse(
        "platform.html",
        {
            "request": request,
            "platform_id": platform_id,
            "platform": platform_info,
            "credentials": credentials,
            "username": username,
            "title": f"Marketing Agent - {platform_info['name']} Connection"
        }
    )

@app.post("/platform/{platform_id}")
async def update_platform(
    platform_id: str,
    request: Request,
    username: str = Depends(verify_credentials)
):
    """Update platform credentials."""
    if platform_id not in PLATFORM_INFO:
        return RedirectResponse(url="/")
    
    form_data = await request.form()
    credentials = {}
    
    # Extract credentials from form
    for field in PLATFORM_INFO[platform_id]["fields"]:
        if field in form_data:
            credentials[field] = form_data[field]
    
    # Validate credentials
    validation = auth_manager.validate_credentials(platform_id, credentials)
    
    if validation["status"] == "success":
        # Add credentials
        auth_manager.add_credentials(platform_id, credentials)
        return RedirectResponse(url="/", status_code=303)
    else:
        # Return to form with error
        return templates.TemplateResponse(
            "platform.html",
            {
                "request": request,
                "platform_id": platform_id,
                "platform": PLATFORM_INFO[platform_id],
                "credentials": credentials,
                "error": validation["message"],
                "username": username,
                "title": f"Marketing Agent - {PLATFORM_INFO[platform_id]['name']} Connection"
            }
        )

@app.get("/remove/{platform_id}")
async def remove_platform(platform_id: str, username: str = Depends(verify_credentials)):
    """Remove platform credentials."""
    auth_manager.remove_credentials(platform_id)
    return RedirectResponse(url="/")

@app.get("/test/{platform_id}")
async def test_platform(platform_id: str, username: str = Depends(verify_credentials)):
    """Test platform connection."""
    result = auth_manager.authenticate(platform_id)
    
    if result["status"] == "success":
        return {"status": "success", "message": f"Successfully connected to {PLATFORM_INFO[platform_id]['name']}"}
    else:
        return {"status": "error", "message": result["message"]}

def create_template_files():
    """Create template files if they don't exist."""
    # Create index.html
    index_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .platform-card {
                transition: transform 0.3s;
                height: 100%;
            }
            .platform-card:hover {
                transform: translateY(-5px);
            }
            .connected {
                border-left: 5px solid #28a745;
            }
            .not-connected {
                border-left: 5px solid #dc3545;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">Marketing Agent</a>
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item">
                            <span class="nav-link">Welcome, {{ username }}</span>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h1>Platform Connections</h1>
            <p class="lead">Connect your marketing platforms and analytics services to enable the autonomous marketing agent.</p>
            
            <div class="row mt-4">
                {% for platform in platforms %}
                <div class="col-md-4 mb-4">
                    <div class="card platform-card {% if platform.connected %}connected{% else %}not-connected{% endif %}">
                        <div class="card-body">
                            <h5 class="card-title">{{ platform.name }}</h5>
                            <p class="card-text">{{ platform.description }}</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    {% if platform.connected %}
                                    <span class="badge bg-success">Connected</span>
                                    {% else %}
                                    <span class="badge bg-danger">Not Connected</span>
                                    {% endif %}
                                </div>
                                <a href="/platform/{{ platform.id }}" class="btn btn-primary">
                                    {% if platform.connected %}
                                    Edit Connection
                                    {% else %}
                                    Connect
                                    {% endif %}
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    # Create platform.html
    platform_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">Marketing Agent</a>
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item">
                            <span class="nav-link">Welcome, {{ username }}</span>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h1>{{ platform.name }} Connection</h1>
            <p class="lead">Enter your credentials to connect to {{ platform.name }}.</p>
            
            {% if error %}
            <div class="alert alert-danger">{{ error }}</div>
            {% endif %}
            
            <div class="card mt-4">
                <div class="card-body">
                    <form method="post" action="/platform/{{ platform_id }}">
                        {% for field in platform.fields %}
                        <div class="mb-3">
                            <label for="{{ field }}" class="form-label">{{ field|replace('_', ' ')|title }}</label>
                            <input type="{% if 'password' in field or 'secret' in field or 'key' in field %}password{% else %}text{% endif %}" 
                                   class="form-control" 
                                   id="{{ field }}" 
                                   name="{{ field }}" 
                                   value="{{ credentials[field] if field in credentials else '' }}">
                        </div>
                        {% endfor %}
                        
                        <div class="d-flex justify-content-between">
                            <a href="/" class="btn btn-secondary">Cancel</a>
                            <div>
                                {% if platform_id in credentials %}
                                <a href="/remove/{{ platform_id }}" class="btn btn-danger me-2">Remove Connection</a>
                                <a href="/test/{{ platform_id }}" class="btn btn-info me-2" id="test-connection">Test Connection</a>
                                {% endif %}
                                <button type="submit" class="btn btn-primary">Save Connection</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            document.getElementById('test-connection')?.addEventListener('click', function(e) {
                e.preventDefault();
                fetch(this.href)
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            alert('Success: ' + data.message);
                        } else {
                            alert('Error: ' + data.message);
                        }
                    });
            });
        </script>
    </body>
    </html>
    """
    
    # Write template files
    with open(os.path.join(templates_dir, "index.html"), "w") as f:
        f.write(index_html)
        
    with open(os.path.join(templates_dir, "platform.html"), "w") as f:
        f.write(platform_html)

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the authentication interface server."""
    # Create template files
    create_template_files()
    
    # Run server
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()
