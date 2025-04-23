#!/usr/bin/env python3
"""
GAMS API Simulator

This script creates a simple Flask server to simulate the backend API endpoints
for testing the GAMS Operator Dashboard.
"""

from flask import Flask, jsonify, request, send_from_directory
# Removed CORS dependency for compatibility
import os
import json
import random
from datetime import datetime, timedelta
import uuid
import time

app = Flask(__name__)
# Adding CORS headers manually
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

# Simulated data storage
data = {
    "system_status": "stopped",
    "start_time": None,
    "metrics": {
        "page_views": random.randint(1000, 10000),
        "conversions": random.randint(50, 500),
        "revenue": round(random.uniform(1000, 10000), 2),
        "engagement_rate": round(random.uniform(0.1, 0.5), 2)
    },
    "content_performance": [
        {
            "url": "/homepage",
            "page_views": random.randint(500, 2000),
            "bounce_rate": round(random.uniform(0.2, 0.6), 2),
            "avg_time_on_page": round(random.uniform(30, 180), 1),
            "conversion_rate": round(random.uniform(0.01, 0.1), 3),
            "engagement_rate": round(random.uniform(0.1, 0.5), 2)
        },
        {
            "url": "/products",
            "page_views": random.randint(300, 1500),
            "bounce_rate": round(random.uniform(0.2, 0.6), 2),
            "avg_time_on_page": round(random.uniform(30, 180), 1),
            "conversion_rate": round(random.uniform(0.01, 0.1), 3),
            "engagement_rate": round(random.uniform(0.1, 0.5), 2)
        },
        {
            "url": "/blog",
            "page_views": random.randint(200, 1000),
            "bounce_rate": round(random.uniform(0.2, 0.6), 2),
            "avg_time_on_page": round(random.uniform(30, 180), 1),
            "conversion_rate": round(random.uniform(0.01, 0.1), 3),
            "engagement_rate": round(random.uniform(0.1, 0.5), 2)
        },
        {
            "url": "/contact",
            "page_views": random.randint(100, 500),
            "bounce_rate": round(random.uniform(0.2, 0.6), 2),
            "avg_time_on_page": round(random.uniform(30, 180), 1),
            "conversion_rate": round(random.uniform(0.01, 0.1), 3),
            "engagement_rate": round(random.uniform(0.1, 0.5), 2)
        }
    ],
    "recommendations": [
        {
            "id": str(uuid.uuid4()),
            "type": "content",
            "title": "Optimize homepage call-to-action",
            "description": "The main CTA on the homepage has a low click-through rate. Consider testing alternative copy and design.",
            "impact": "high",
            "effort": "medium"
        },
        {
            "id": str(uuid.uuid4()),
            "type": "seo",
            "title": "Improve blog post meta descriptions",
            "description": "Several blog posts have generic meta descriptions. Update them to improve CTR from search results.",
            "impact": "medium",
            "effort": "low"
        },
        {
            "id": str(uuid.uuid4()),
            "type": "conversion",
            "title": "Simplify checkout process",
            "description": "Users are abandoning carts during the checkout process. Reduce the number of steps required.",
            "impact": "high",
            "effort": "high"
        }
    ],
    "cycles": [
        {
            "id": str(uuid.uuid4()),
            "name": "Q2 Growth Initiative",
            "current_phase": "website_optimization",
            "start_time": (datetime.now() - timedelta(days=5)).isoformat(),
            "last_phase_change": (datetime.now() - timedelta(days=2)).isoformat(),
            "status": "active"
        }
    ],
    "goals": [
        {
            "id": str(uuid.uuid4()),
            "name": "Increase Conversion Rate",
            "type": "conversion",
            "target": "Improve conversion rate by 15%",
            "status": "active",
            "metrics": {
                "conversion_rate": 0.032,
                "target_rate": 0.035,
                "progress": 0.65
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Boost Organic Traffic",
            "type": "traffic",
            "target": "Increase organic traffic by 25%",
            "status": "at_risk",
            "metrics": {
                "organic_sessions": 12500,
                "target_sessions": 15000,
                "progress": 0.42
            }
        }
    ],
    "campaigns": [
        {
            "id": str(uuid.uuid4()),
            "name": "Summer Product Launch",
            "type": "multi-channel",
            "status": "active",
            "goal_id": None,  # Will be set to a real goal ID
            "metrics": {
                "impressions": 45000,
                "clicks": 3200,
                "conversions": 128,
                "revenue": 12800.00,
                "roi": 3.2
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Email Re-engagement",
            "type": "email",
            "status": "paused",
            "goal_id": None,  # Will be set to a real goal ID
            "metrics": {
                "sent": 10000,
                "opens": 2200,
                "clicks": 450,
                "conversions": 28,
                "revenue": 1400.00
            }
        }
    ],
    "approvals": [
        {
            "id": str(uuid.uuid4()),
            "type": "content",
            "title": "New Blog Post: '10 Tips for SEO Success'",
            "status": "pending",
            "created_at": (datetime.now() - timedelta(hours=6)).isoformat(),
            "description": "A new blog post focusing on SEO best practices."
        },
        {
            "id": str(uuid.uuid4()),
            "type": "campaign",
            "title": "Holiday Promotion Email Sequence",
            "status": "pending",
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "description": "A series of 3 emails promoting holiday specials."
        }
    ]
}

# Link campaigns to goals
data["campaigns"][0]["goal_id"] = data["goals"][0]["id"]
data["campaigns"][1]["goal_id"] = data["goals"][1]["id"]

# System control endpoints
@app.route('/api/operator/control/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": data["system_status"],
        "start_time": data["start_time"],
        "uptime": calculate_uptime() if data["start_time"] else 0,
        "version": "1.0.0"
    })

@app.route('/api/operator/control/start', methods=['POST'])
def start_system():
    data["system_status"] = "running"
    data["start_time"] = datetime.now().isoformat()
    return jsonify({"status": "success", "message": "GAMS system started successfully"})

@app.route('/api/operator/control/stop', methods=['POST'])
def stop_system():
    data["system_status"] = "stopped"
    return jsonify({"status": "success", "message": "GAMS system stopped successfully"})

# Analytics endpoints
@app.route('/api/operator/analytics/metrics', methods=['GET'])
def get_metrics():
    # Simulate changing metrics
    data["metrics"]["page_views"] += random.randint(-100, 200)
    data["metrics"]["conversions"] += random.randint(-5, 15)
    data["metrics"]["revenue"] += round(random.uniform(-100, 300), 2)
    data["metrics"]["engagement_rate"] = round(min(0.5, max(0.1, data["metrics"]["engagement_rate"] + random.uniform(-0.02, 0.02))), 2)
    
    return jsonify({
        "metrics": data["metrics"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/operator/analytics/content', methods=['GET'])
def get_content_performance():
    # Simulate changing content performance
    for content in data["content_performance"]:
        content["page_views"] += random.randint(-20, 50)
        content["bounce_rate"] = round(min(0.8, max(0.1, content["bounce_rate"] + random.uniform(-0.05, 0.05))), 2)
        content["avg_time_on_page"] = round(min(300, max(10, content["avg_time_on_page"] + random.uniform(-10, 10))), 1)
        content["conversion_rate"] = round(min(0.2, max(0.005, content["conversion_rate"] + random.uniform(-0.005, 0.005))), 3)
        content["engagement_rate"] = round(min(0.6, max(0.05, content["engagement_rate"] + random.uniform(-0.02, 0.02))), 2)
    
    return jsonify({
        "content": data["content_performance"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/operator/analytics/recommendations', methods=['GET'])
def get_recommendations():
    return jsonify({
        "recommendations": data["recommendations"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/operator/analytics/report', methods=['GET'])
def get_performance_report():
    start_date = request.args.get('start_date', default=None)
    end_date = request.args.get('end_date', default=None)
    
    # Generate simulated report data
    report_data = {
        "summary": {
            "period": f"{start_date} to {end_date}" if start_date and end_date else "Last 30 days",
            "total_page_views": random.randint(10000, 50000),
            "total_conversions": random.randint(500, 2000),
            "total_revenue": round(random.uniform(10000, 50000), 2),
            "avg_engagement_rate": round(random.uniform(0.1, 0.4), 2)
        },
        "traffic": {
            "total": random.randint(10000, 50000),
            "sources": {
                "organic": round(random.uniform(0.3, 0.5), 2),
                "direct": round(random.uniform(0.1, 0.3), 2),
                "referral": round(random.uniform(0.1, 0.2), 2),
                "social": round(random.uniform(0.05, 0.15), 2),
                "email": round(random.uniform(0.05, 0.1), 2),
                "other": round(random.uniform(0.01, 0.05), 2)
            }
        },
        "conversions": {
            "total": random.randint(500, 2000),
            "rate": round(random.uniform(0.01, 0.05), 3),
            "by_source": {
                "organic": round(random.uniform(0.01, 0.04), 3),
                "direct": round(random.uniform(0.02, 0.06), 3),
                "referral": round(random.uniform(0.015, 0.05), 3),
                "social": round(random.uniform(0.01, 0.03), 3),
                "email": round(random.uniform(0.03, 0.08), 3)
            }
        },
        "engagement": {
            "avg_time_on_site": round(random.uniform(120, 300), 1),
            "pages_per_session": round(random.uniform(1.5, 4.0), 1),
            "bounce_rate": round(random.uniform(0.3, 0.6), 2)
        },
        "revenue": {
            "total": round(random.uniform(10000, 50000), 2),
            "average_order_value": round(random.uniform(50, 150), 2),
            "by_channel": {
                "organic": round(random.uniform(2000, 10000), 2),
                "direct": round(random.uniform(3000, 15000), 2),
                "referral": round(random.uniform(1000, 5000), 2),
                "social": round(random.uniform(500, 3000), 2),
                "email": round(random.uniform(1500, 8000), 2)
            }
        },
        "time_series": {
            "dates": [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)],
            "page_views": [random.randint(300, 1500) for _ in range(30)],
            "conversions": [random.randint(10, 60) for _ in range(30)],
            "revenue": [round(random.uniform(300, 1500), 2) for _ in range(30)]
        }
    }
    
    return jsonify({
        "report": report_data,
        "timestamp": datetime.now().isoformat()
    })

# Orchestrator endpoints
@app.route('/api/operator/orchestrator/cycles', methods=['GET'])
def get_cycles():
    return jsonify({
        "cycles": data["cycles"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/operator/orchestrator/cycles/<cycle_id>', methods=['GET'])
def get_cycle_details(cycle_id):
    cycle = next((c for c in data["cycles"] if c["id"] == cycle_id), None)
    if not cycle:
        return jsonify({"status": "error", "message": "Cycle not found"}), 404
    
    # Add more detailed information for the specific cycle
    cycle_details = cycle.copy()
    cycle_details["phases"] = [
        "website_optimization",
        "multi_channel_marketing",
        "data_learning",
        "content_refinement",
        "revenue_optimization",
        "system_expansion"
    ]
    cycle_details["current_phase_index"] = cycle_details["phases"].index(cycle["current_phase"])
    cycle_details["tasks"] = [
        {
            "id": str(uuid.uuid4()),
            "name": "Analyze website performance",
            "status": "completed",
            "completion_date": (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Identify optimization opportunities",
            "status": "in_progress",
            "start_date": (datetime.now() - timedelta(hours=12)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Implement A/B testing",
            "status": "pending",
            "due_date": (datetime.now() + timedelta(days=2)).isoformat()
        }
    ]
    
    return jsonify({
        "cycle": cycle_details,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/operator/orchestrator/cycles/<cycle_id>/advance', methods=['POST'])
def advance_cycle_phase(cycle_id):
    cycle = next((c for c in data["cycles"] if c["id"] == cycle_id), None)
    if not cycle:
        return jsonify({"status": "error", "message": "Cycle not found"}), 404
    
    phases = [
        "website_optimization",
        "multi_channel_marketing",
        "data_learning",
        "content_refinement",
        "revenue_optimization",
        "system_expansion"
    ]
    
    current_index = phases.index(cycle["current_phase"])
    if current_index < len(phases) - 1:
        cycle["current_phase"] = phases[current_index + 1]
        cycle["last_phase_change"] = datetime.now().isoformat()
        return jsonify({"status": "success", "message": f"Advanced to {cycle['current_phase']}"})
    else:
        return jsonify({"status": "error", "message": "Already at the final phase"}), 400

@app.route('/api/operator/orchestrator/goals', methods=['GET'])
def get_goals():
    return jsonify({
        "goals": data["goals"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/operator/orchestrator/goals/<goal_id>', methods=['GET'])
def get_goal_details(goal_id):
    goal = next((g for g in data["goals"] if g["id"] == goal_id), None)
    if not goal:
        return jsonify({"status": "error", "message": "Goal not found"}), 404
    
    # Add more detailed information for the specific goal
    goal_details = goal.copy()
    goal_details["campaigns"] = [c for c in data["campaigns"] if c["goal_id"] == goal_id]
    goal_details["created_at"] = (datetime.now() - timedelta(days=10)).isoformat()
    goal_details["target_date"] = (datetime.now() + timedelta(days=20)).isoformat()
    goal_details["history"] = [
        {
            "date": (datetime.now() - timedelta(days=8)).isoformat(),
            "value": goal["metrics"].get("progress", 0) * 0.5
        },
        {
            "date": (datetime.now() - timedelta(days=4)).isoformat(),
            "value": goal["metrics"].get("progress", 0) * 0.8
        },
        {
            "date": datetime.now().isoformat(),
            "value": goal["metrics"].get("progress", 0)
        }
    ]
    
    return jsonify({
        "goal": goal_details,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/operator/orchestrator/campaigns', methods=['GET'])
def get_campaigns():
    return jsonify({
        "campaigns": data["campaigns"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/operator/orchestrator/campaigns/<campaign_id>', methods=['GET'])
def get_campaign_details(campaign_id):
    campaign = next((c for c in data["campaigns"] if c["id"] == campaign_id), None)
    if not campaign:
        return jsonify({"status": "error", "message": "Campaign not found"}), 404
    
    # Add more detailed information for the specific campaign
    campaign_details = campaign.copy()
    campaign_details["created_at"] = (datetime.now() - timedelta(days=5)).isoformat()
    campaign_details["start_date"] = (datetime.now() - timedelta(days=3)).isoformat()
    campaign_details["end_date"] = (datetime.now() + timedelta(days=25)).isoformat()
    campaign_details["channels"] = ["email", "social", "search"]
    campaign_details["budget"] = 5000.00
    campaign_details["spend"] = 2100.00
    campaign_details["history"] = [
        {
            "date": (datetime.now() - timedelta(days=3)).isoformat(),
            "metrics": {
                "impressions": 15000,
                "clicks": 1200,
                "conversions": 48,
                "revenue": 4800.00
            }
        },
        {
            "date": (datetime.now() - timedelta(days=2)).isoformat(),
            "metrics": {
                "impressions": 30000,
                "clicks": 2100,
                "conversions": 84,
                "revenue": 8400.00
            }
        },
        {
            "date": datetime.now().isoformat(),
            "metrics": campaign["metrics"]
        }
    ]
    
    return jsonify({
        "campaign": campaign_details,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/operator/orchestrator/campaigns/<campaign_id>/status', methods=['POST'])
def update_campaign_status(campaign_id):
    campaign = next((c for c in data["campaigns"] if c["id"] == campaign_id), None)
    if not campaign:
        return jsonify({"status": "error", "message": "Campaign not found"}), 404
    
    request_data = request.get_json()
    if not request_data or "status" not in request_data:
        return jsonify({"status": "error", "message": "Status not provided"}), 400
    
    new_status = request_data["status"]
    if new_status not in ["active", "paused", "completed", "cancelled"]:
        return jsonify({"status": "error", "message": "Invalid status"}), 400
    
    campaign["status"] = new_status
    return jsonify({
        "status": "success",
        "message": f"Campaign status updated to {new_status}",
        "campaign": campaign
    })

# Approvals endpoints
@app.route('/api/operator/approvals', methods=['GET'])
def get_approvals():
    return jsonify({
        "approvals": data["approvals"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/operator/approvals/<approval_id>', methods=['GET'])
def get_approval_details(approval_id):
    approval = next((a for a in data["approvals"] if a["id"] == approval_id), None)
    if not approval:
        return jsonify({"status": "error", "message": "Approval not found"}), 404
    
    # Add more detailed information for the specific approval
    approval_details = approval.copy()
    approval_details["content"] = "This is the detailed content that needs approval."
    approval_details["requested_by"] = "GAMS System"
    approval_details["urgency"] = "medium"
    
    return jsonify({
        "approval": approval_details,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/operator/approvals/<approval_id>/action', methods=['POST'])
def process_approval(approval_id):
    approval = next((a for a in data["approvals"] if a["id"] == approval_id), None)
    if not approval:
        return jsonify({"status": "error", "message": "Approval not found"}), 404
    
    request_data = request.get_json()
    if not request_data or "action" not in request_data:
        return jsonify({"status": "error", "message": "Action not provided"}), 400
    
    action = request_data["action"]
    if action not in ["approve", "reject"]:
        return jsonify({"status": "error", "message": "Invalid action"}), 400
    
    approval["status"] = "approved" if action == "approve" else "rejected"
    
    # Remove from pending approvals list
    data["approvals"] = [a for a in data["approvals"] if a["id"] != approval_id]
    
    return jsonify({
        "status": "success",
        "message": f"Approval {action}d successfully"
    })

# Helper functions
def calculate_uptime():
    if not data["start_time"]:
        return 0
    
    start_time = datetime.fromisoformat(data["start_time"])
    now = datetime.now()
    delta = now - start_time
    return int(delta.total_seconds())

# Serve static files
@app.route('/', defaults={'path': 'enhanced_operator_dashboard.html'})
@app.route('/<path:path>')
def serve_static(path):
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    return app.send_static_file(path)

if __name__ == '__main__':
    # Set the static folder to the frontend directory
    app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    app.run(debug=True, port=5050)
