#!/usr/bin/env python3
"""
Operator Dashboard Server

This script provides a Flask-based server for the GAMS Operator Dashboard.
It serves the frontend files and provides API endpoints for the dashboard.
"""

import os
import sys
import json
from flask import Flask, send_from_directory, send_file, jsonify, request
from flask_cors import CORS

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the operator interface
try:
    from core.operator.operator_api import app as api_app
    OPERATOR_API_AVAILABLE = True
except ImportError:
    print("Operator API not available, using mock server")
    OPERATOR_API_AVAILABLE = False
    api_app = None

# Create the Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Serve static files from the frontend directory
@app.route('/')
def index():
    """Serve the operator dashboard HTML."""
    return send_file('operator_dashboard.html')

@app.route('/test_gams_control.html')
def test_gams_control():
    """Serve the test GAMS control HTML page."""
    return send_file('test_gams_control.html')

@app.route('/operator_dashboard_fixed.js')
def operator_dashboard_fixed():
    """Serve the fixed JavaScript file."""
    return send_file('operator_dashboard_fixed.js')

@app.route('/test_fixed_gams_control.html')
def test_fixed_gams_control():
    """Serve the test fixed GAMS control HTML page."""
    return send_file('test_fixed_gams_control.html')

@app.route('/fixed_dashboard')
def fixed_dashboard():
    """Serve the fixed operator dashboard HTML page."""
    return send_file('fixed_operator_dashboard.html')

@app.route('/simple_gams_test')
def simple_gams_test():
    """Serve the simple GAMS test HTML page."""
    return send_file('simple_gams_test.html')

@app.route('/test')
def test_page():
    """Serve the test GAMS control page."""
    return send_from_directory('.', 'test_gams_control.html')

@app.route('/competitive-intelligence')
def competitive_intelligence():
    """Serve the competitive intelligence dashboard."""
    return send_from_directory('../examples/demo_output', 'index.html')

@app.route('/competitive-intelligence/<path:path>')
def serve_competitive_intelligence_static(path):
    """Serve static files for the competitive intelligence dashboard."""
    return send_from_directory('../examples/demo_output', path)

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('.', path)

# Import the operator API routes
if OPERATOR_API_AVAILABLE:
    # We'll use the Flask app from operator_api directly
    from core.operator.operator_api import app as api_app
    
    # Define API routes that match the ones in operator_api.py
    @app.route('/api/operator/approvals/pending', methods=['GET'])
    def api_get_pending_approvals():
        from core.operator.operator_api import get_pending_approvals
        return get_pending_approvals()
        
    @app.route('/api/operator/approvals/<approval_id>', methods=['POST'])
    def api_process_approval(approval_id):
        from core.operator.operator_api import process_approval
        return process_approval(approval_id)
    
    @app.route('/api/operator/approvals/<approval_id>/modify', methods=['POST'])
    def api_modify_approval(approval_id):
        from core.operator.operator_api import modify_approval
        return modify_approval(approval_id)
        
    @app.route('/api/operator/strategy', methods=['GET'])
    def api_get_strategy():
        from core.operator.operator_api import get_strategy
        return get_strategy()
        
    # Financial endpoints are implemented directly below, no need for these proxy functions
        
    # Financial endpoints are implemented directly below, no need for these proxy functions
        
    @app.route('/api/operator/experiments/active', methods=['GET'])
    def api_get_active_experiments():
        from core.operator.operator_api import get_active_experiments
        return get_active_experiments()
    
    @app.route('/api/operator/experiments/<experiment_id>/<action>', methods=['POST'])
    def api_process_experiment(experiment_id, action):
        from core.operator.operator_api import process_experiment
        return process_experiment(experiment_id, action)
        
    @app.route('/api/operator/compliance/issues', methods=['GET'])
    def api_get_compliance_issues():
        from core.operator.operator_api import get_compliance_issues
        return get_compliance_issues()
    
    @app.route('/api/operator/compliance/issues/<issue_id>/resolve', methods=['POST'])
    def api_resolve_compliance_issue(issue_id):
        from core.operator.operator_api import resolve_compliance_issue
        return resolve_compliance_issue(issue_id)
        
    @app.route('/api/operator/strategy/revenue-targets', methods=['POST'])
    def api_update_revenue_targets():
        from core.operator.operator_api import update_revenue_targets
        return update_revenue_targets()
        
    @app.route('/api/operator/strategy/channel-mix', methods=['POST'])
    def api_update_channel_mix():
        from core.operator.operator_api import update_channel_mix
        return update_channel_mix()
    
    # Competitive Intelligence endpoints
    @app.route('/api/operator/competitive-intelligence/data', methods=['GET'])
    def api_get_competitive_intelligence():
        from core.competitive_intelligence.manager import CompetitiveIntelligenceManager
        manager = CompetitiveIntelligenceManager()
        return jsonify(manager.export_intelligence_data())
    
    @app.route('/api/operator/competitive-intelligence/competitors', methods=['GET'])
    def api_get_competitors():
        from core.competitive_intelligence.manager import CompetitiveIntelligenceManager
        manager = CompetitiveIntelligenceManager()
        return jsonify(manager.get_all_competitors())
    
    @app.route('/api/operator/competitive-intelligence/insights', methods=['GET'])
    def api_get_insights():
        from core.competitive_intelligence.manager import CompetitiveIntelligenceManager
        manager = CompetitiveIntelligenceManager()
        return jsonify(manager.get_all_insights())
        
    # System control endpoint is implemented directly in the mock section below
else:
    # Mock API endpoints if the real API is not available
    @app.route('/api/operator/competitive-intelligence/data', methods=['GET'])
    def get_competitive_intelligence():
        """Get competitive intelligence data."""
        try:
            # Mock data for competitive intelligence
            data = {
                "insights": [
                    {
                        "id": "ins-001",
                        "title": "Competitor A launching new product",
                        "description": "Competitor A is preparing to launch a new product that directly competes with our flagship offering.",
                        "priority": "high",
                        "category": "product",
                        "timestamp": "2023-04-15T10:30:00Z"
                    },
                    {
                        "id": "ins-002",
                        "title": "Market share shift detected",
                        "description": "Our market share has decreased by 2.5% in the last quarter, while Competitor B has gained 3.1%.",
                        "priority": "high",
                        "category": "market",
                        "timestamp": "2023-04-10T14:45:00Z"
                    },
                    {
                        "id": "ins-003",
                        "title": "Competitor C price reduction",
                        "description": "Competitor C has reduced prices by 15% on their premium tier services.",
                        "priority": "medium",
                        "category": "pricing",
                        "timestamp": "2023-04-05T09:15:00Z"
                    }
                ],
                "competitors": [
                    {
                        "id": "comp-001",
                        "name": "Acme Corporation",
                        "website": "https://www.acme.example.com",
                        "industry": "Technology",
                        "size": "Enterprise",
                        "main_products": ["Product A", "Product B", "Product C"],
                        "strengths": ["Strong brand recognition", "Extensive distribution network", "High R&D budget"],
                        "weaknesses": ["Slow to innovate", "High pricing", "Poor customer service"]
                    },
                    {
                        "id": "comp-002",
                        "name": "Globex Marketing",
                        "website": "https://www.globex.example.com",
                        "industry": "Marketing",
                        "size": "Mid-size",
                        "main_products": ["Marketing Suite", "Analytics Platform", "Campaign Manager"],
                        "strengths": ["Innovative features", "Strong customer loyalty", "Competitive pricing"],
                        "weaknesses": ["Limited market reach", "Small sales team", "Platform stability issues"]
                    },
                    {
                        "id": "comp-003",
                        "name": "Initech Solutions",
                        "website": "https://www.initech.example.com",
                        "industry": "Technology",
                        "size": "Startup",
                        "main_products": ["Cloud Platform", "AI Assistant", "Developer Tools"],
                        "strengths": ["Cutting-edge technology", "Agile development", "Strong technical team"],
                        "weaknesses": ["Limited funding", "Small customer base", "Unproven track record"]
                    }
                ],
                "recommendations": [
                    {
                        "id": "rec-001",
                        "title": "Launch counter-marketing campaign",
                        "description": "Develop a targeted marketing campaign highlighting our advantages over Competitor A's new product.",
                        "urgency": "high",
                        "impact": "high",
                        "implementation_time": "2 weeks"
                    },
                    {
                        "id": "rec-002",
                        "title": "Revise pricing strategy",
                        "description": "Adjust our pricing tiers to better compete with Competitor C's recent price reductions.",
                        "urgency": "medium",
                        "impact": "high",
                        "implementation_time": "1 month"
                    },
                    {
                        "id": "rec-003",
                        "title": "Enhance product features",
                        "description": "Accelerate development of key features to address the market share loss to Competitor B.",
                        "urgency": "medium",
                        "impact": "high",
                        "implementation_time": "3 months"
                    }
                ],
                "events": [
                    {
                        "id": "evt-001",
                        "title": "Competitor A product announcement",
                        "description": "Competitor A announced their new product at industry conference.",
                        "date": "2023-03-15",
                        "category": "product",
                        "significance": "high"
                    },
                    {
                        "id": "evt-002",
                        "title": "Competitor B marketing campaign",
                        "description": "Competitor B launched major marketing campaign across digital channels.",
                        "date": "2023-02-28",
                        "category": "marketing",
                        "significance": "medium"
                    },
                    {
                        "id": "evt-003",
                        "title": "Competitor C price change",
                        "description": "Competitor C announced 15% price reduction on premium services.",
                        "date": "2023-04-01",
                        "category": "pricing",
                        "significance": "high"
                    }
                ]
            }
            
            return jsonify(data)
        except Exception as e:
            app.logger.error(f"Error getting competitive intelligence data: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to get competitive intelligence data: {str(e)}"
            }), 500
    
    @app.route('/api/operator/competitive-intelligence/competitors', methods=['GET'])
    def get_competitors():
        """Get competitor data."""
        try:
            # Mock data for competitors
            data = [
                {
                    "id": "comp-001",
                    "name": "Acme Corporation",
                    "website": "https://www.acme.example.com",
                    "industry": "Technology",
                    "size": "Enterprise",
                    "main_products": ["Product A", "Product B", "Product C"],
                    "strengths": ["Strong brand recognition", "Extensive distribution network", "High R&D budget"],
                    "weaknesses": ["Slow to innovate", "High pricing", "Poor customer service"]
                },
                {
                    "id": "comp-002",
                    "name": "Globex Marketing",
                    "website": "https://www.globex.example.com",
                    "industry": "Marketing",
                    "size": "Mid-size",
                    "main_products": ["Marketing Suite", "Analytics Platform", "Campaign Manager"],
                    "strengths": ["Innovative features", "Strong customer loyalty", "Competitive pricing"],
                    "weaknesses": ["Limited market reach", "Small sales team", "Platform stability issues"]
                },
                {
                    "id": "comp-003",
                    "name": "Initech Solutions",
                    "website": "https://www.initech.example.com",
                    "industry": "Technology",
                    "size": "Startup",
                    "main_products": ["Cloud Platform", "AI Assistant", "Developer Tools"],
                    "strengths": ["Cutting-edge technology", "Agile development", "Strong technical team"],
                    "weaknesses": ["Limited funding", "Small customer base", "Unproven track record"]
                }
            ]
            
            return jsonify(data)
        except Exception as e:
            app.logger.error(f"Error getting competitors: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to get competitors: {str(e)}"
            }), 500
    
    @app.route('/api/operator/competitive-intelligence/insights', methods=['GET'])
    def get_insights():
        """Get competitive insights."""
        try:
            # Mock data for insights
            data = [
                {
                    "id": "ins-001",
                    "title": "Competitor A launching new product",
                    "description": "Competitor A is preparing to launch a new product that directly competes with our flagship offering.",
                    "priority": "high",
                    "category": "product",
                    "timestamp": "2023-04-15T10:30:00Z"
                },
                {
                    "id": "ins-002",
                    "title": "Market share shift detected",
                    "description": "Our market share has decreased by 2.5% in the last quarter, while Competitor B has gained 3.1%.",
                    "priority": "high",
                    "category": "market",
                    "timestamp": "2023-04-10T14:45:00Z"
                },
                {
                    "id": "ins-003",
                    "title": "Competitor C price reduction",
                    "description": "Competitor C has reduced prices by 15% on their premium tier services.",
                    "priority": "medium",
                    "category": "pricing",
                    "timestamp": "2023-04-05T09:15:00Z"
                }
            ]
            
            return jsonify(data)
        except Exception as e:
            app.logger.error(f"Error getting insights: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to get insights: {str(e)}"
            }), 500
    
    @app.route('/api/operator/approvals/pending', methods=['GET'])
    def get_pending_approvals():
        """Get pending approvals."""
        mock_approvals = [
            {
                'id': 'experiment_20250401123456',
                'type': 'experiment',
                'data': {
                    'name': 'A/B Test: Homepage Hero Section',
                    'description': 'Testing 3 variations of hero messaging for conversion rate',
                    'budget': 1500,
                    'duration_days': 14
                },
                'description': 'Testing 3 variations of hero messaging for conversion rate',
                'urgency': 'normal',
                'status': 'pending',
                'created_at': '2025-04-01T12:34:56Z'
            },
            {
                'id': 'budget_20250402091234',
                'type': 'budget',
                'data': {
                    'campaign': 'Facebook Ad Campaign',
                    'current_budget': 5000,
                    'requested_budget': 7500,
                    'increase_amount': 2500,
                    'reason': 'Strong performance, ROAS of 3.2'
                },
                'description': 'Facebook Ad Campaign - $2,500 increase',
                'urgency': 'high',
                'status': 'pending',
                'created_at': '2025-04-02T09:12:34Z'
            },
            {
                'id': 'content_20250403151617',
                'type': 'content',
                'data': {
                    'title': '10 Ways to Optimize Your Marketing',
                    'word_count': 2500,
                    'content_type': 'blog',
                    'target_keywords': ['marketing optimization', 'marketing strategy', 'marketing ROI']
                },
                'description': '2,500 word article on marketing optimization strategies',
                'urgency': 'normal',
                'status': 'pending',
                'created_at': '2025-04-03T15:16:17Z'
            }
        ]
        return jsonify(mock_approvals)

    @app.route('/api/operator/strategy', methods=['GET'])
    def get_strategy():
        """Get strategy settings."""
        mock_strategy = {
            'revenue_targets': {
                'monthly': 50000,
                'quarterly': 150000,
                'annual': 600000
            },
            'channel_mix': {
                'organic': 0.3,
                'paid': 0.4,
                'email': 0.15,
                'affiliate': 0.15
            },
            'affiliate_partners': [
                {
                    'name': 'Marketing Pro Blog',
                    'commission_rate': 0.15,
                    'status': 'active',
                    'monthly_revenue': 3250
                },
                {
                    'name': 'Digital Marketing Academy',
                    'commission_rate': 0.2,
                    'status': 'active',
                    'monthly_revenue': 5120
                }
            ]
        }
        return jsonify(mock_strategy)

    @app.route('/api/operator/financial/summary', methods=['GET'])
    def get_financial_summary():
        """Get financial summary."""
        try:
            mock_financial = {
                'revenue': 125000,
                'expenses': 75000,
                'profit': 50000,
                'profit_margin': 0.4,
                'revenue_growth': 0.12,
                'expense_growth': 0.08,
                'profit_growth': 0.18,
                'vs_target': 12.5,
                'revenueByChannel': {
                    'organic': 45000,
                    'paid': 35000,
                    'email': 25000,
                    'affiliate': 20000
                },
                'kpis': {
                    'cac': 42.50,
                    'ltv': 215.75,
                    'conversion_rate': 3.2,
                    'churn_rate': 2.1,
                    'roas': 3.8
                }
            }
            return jsonify(mock_financial)
        except Exception as e:
            app.logger.error(f"Error getting financial summary: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to get financial summary: {str(e)}"
            }), 500
        
    @app.route('/api/operator/financial/historical', methods=['GET'])
    def get_financial_historical():
        """Get historical financial data."""
        try:
            # Generate mock data for the past 12 months
            today = datetime.now()
            mock_data = []
            for i in range(12):
                month = today.replace(month=today.month - i, day=1)
                mock_data.append({
                    'period': month.strftime('%b %Y'),
                    'revenue': 100000 + (i * 5000),
                    'expenses': 60000 + (i * 2000),
                    'profit': 40000 + (i * 3000)
                })
            return jsonify(mock_data)
        except Exception as e:
            app.logger.error(f"Error getting historical financial data: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to get historical financial data: {str(e)}"
            }), 500

    @app.route('/api/operator/experiments/active', methods=['GET'])
    def get_active_experiments():
        """Get active experiments."""
        mock_experiments = [
            {
                'id': 'exp_001',
                'name': 'Homepage Hero Test',
                'type': 'a_b_test',
                'status': 'active',
                'startDate': '2025-03-15T00:00:00Z',
                'endDate': '2025-04-15T00:00:00Z',
                'budget': 5000,
                'spendToDate': 3250,
                'description': 'Testing three variations of the homepage hero section to improve conversion rates.',
                'hypothesis': 'A more benefit-focused headline will increase conversion rates by at least 15%.',
                'results': 'Variant B is showing a 22% improvement in conversion rate over the control.',
                'metrics': {
                    'conversionRate': 4.5,
                    'roi': 185,
                    'clickThroughRate': {
                        'control': 3.2,
                        'variant': 4.1,
                        'difference': 28.1
                    },
                    'timeOnPage': {
                        'control': 45,
                        'variant': 62,
                        'difference': 37.8
                    },
                    'revenue': {
                        'control': 9500,
                        'variant': 12500,
                        'difference': 31.6
                    }
                }
            },
            {
                'id': 'exp_002',
                'name': 'Pricing Page Layout',
                'type': 'multivariate_test',
                'status': 'active',
                'startDate': '2025-03-20T00:00:00Z',
                'endDate': '2025-04-20T00:00:00Z',
                'budget': 4500,
                'spendToDate': 2800,
                'description': 'Testing different layouts and pricing structures to optimize conversion.',
                'hypothesis': 'Featuring the annual plan more prominently will increase annual subscription sign-ups by 20%.',
                'results': 'Results are mixed. Annual plan sign-ups have increased but overall conversion rate is down slightly.',
                'metrics': {
                    'conversionRate': 3.2,
                    'roi': 112,
                    'annualPlanSignups': {
                        'control': 22,
                        'variant': 31,
                        'difference': 40.9
                    },
                    'overallConversion': {
                        'control': 3.5,
                        'variant': 3.2,
                        'difference': -8.6
                    }
                }
            },
            {
                'id': 'exp_003',
                'name': 'Email Subject Line Test',
                'type': 'a_b_test',
                'status': 'pending_review',
                'startDate': '2025-04-10T00:00:00Z',
                'endDate': None,
                'budget': 2000,
                'spendToDate': 0,
                'description': 'Testing personalized vs. benefit-focused subject lines in the monthly newsletter.',
                'hypothesis': 'Personalized subject lines will increase open rates by at least 10%.',
                'results': None,
                'metrics': None
            }
        ]
        return jsonify(mock_experiments)
        
    @app.route('/api/operator/experiments/<experiment_id>/<action>', methods=['POST'])
    def process_experiment(experiment_id, action):
        """Process an experiment action (approve/reject)."""
        if action not in ['approve', 'reject']:
            return jsonify({
                'status': 'error',
                'message': f"Invalid action: {action}. Must be 'approve' or 'reject'."
            }), 400
            
        data = request.json
        return jsonify({
            'status': 'success',
            'experiment': {
                'id': experiment_id,
                'status': 'active' if action == 'approve' else 'rejected',
                'operator_id': data.get('operator_id', 'unknown'),
                'processed_at': '2025-04-04T23:15:00Z',
                'notes': data.get('notes', '')
            }
        })

    @app.route('/api/operator/compliance/issues', methods=['GET'])
    def get_compliance_issues():
        """Get compliance issues."""
        mock_issues = [
            {
                'id': 'compliance_gdpr_20250403121314',
                'type': 'gdpr',
                'title': 'GDPR Violation in Email Campaign',
                'description': 'The new product launch email campaign is missing required GDPR compliance elements.',
                'details': {
                    'content_type': 'email',
                    'campaign': 'New Product Launch',
                    'issues': ['Missing unsubscribe link', 'No clear privacy policy link']
                },
                'priority': 'high',
                'status': 'open',
                'created_at': '2025-04-03T12:13:14Z',
                'due_by': '2025-04-10T12:13:14Z',
                'regulation': 'GDPR Article 7',
                'potential_penalty': '€20,000',
                'affected_users': 4850
            },
            {
                'id': 'compliance_affiliate_20250402151617',
                'type': 'affiliate_disclosure',
                'title': 'Missing Affiliate Disclosure',
                'description': 'Blog post contains affiliate links without proper disclosure.',
                'details': {
                    'content_type': 'blog',
                    'url': '/blog/best-marketing-tools',
                    'issues': ['Missing affiliate disclosure']
                },
                'priority': 'medium',
                'status': 'open',
                'created_at': '2025-04-02T15:16:17Z',
                'due_by': '2025-04-09T15:16:17Z',
                'regulation': 'FTC Disclosure Guidelines',
                'potential_penalty': '$10,000',
                'affected_users': 1250
            },
            {
                'id': 'compliance_accessibility_20250404091011',
                'type': 'accessibility',
                'title': 'Website Accessibility Issues',
                'description': 'Several pages have accessibility issues that need to be addressed.',
                'details': {
                    'content_type': 'website',
                    'pages': ['/pricing', '/features', '/contact'],
                    'issues': ['Low contrast text', 'Missing alt tags', 'Non-keyboard navigable elements']
                },
                'priority': 'medium',
                'status': 'open',
                'created_at': '2025-04-04T09:10:11Z',
                'due_by': '2025-04-18T09:10:11Z',
                'regulation': 'ADA Compliance',
                'potential_penalty': '$25,000',
                'affected_users': 'All users'
            }
        ]
        return jsonify(mock_issues)
        
    @app.route('/api/operator/compliance/issues/<issue_id>/resolve', methods=['POST'])
    def resolve_compliance_issue(issue_id):
        """Resolve a compliance issue."""
        data = request.json
        return jsonify({
            'status': 'success',
            'issue': {
                'id': issue_id,
                'status': 'resolved',
                'resolution': data.get('resolution', 'operator_resolved'),
                'resolved_by': data.get('operator_id', 'unknown'),
                'resolved_at': '2025-04-04T23:15:00Z',
                'notes': data.get('notes', '')
            }
        })

    # Mock POST endpoints
    @app.route('/api/operator/approvals/<approval_id>', methods=['POST'])
    def process_approval(approval_id):
        """Process an approval."""
        try:
            data = request.json
            return jsonify({
                'status': 'success',
                'approval': {
                    'id': approval_id,
                    'status': data.get('status', 'pending'),
                    'operator_id': data.get('operator_id', 'unknown'),
                    'processed_at': '2025-04-04T23:15:00Z',
                    'notes': data.get('notes', '')
                }
            })
        except Exception as e:
            app.logger.error(f"Error processing approval: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to process approval: {str(e)}"
            }), 500
        
    @app.route('/api/operator/approvals/<approval_id>/modify', methods=['POST'])
    def modify_approval(approval_id):
        """Request modification for an approval."""
        try:
            data = request.json
            return jsonify({
                'status': 'success',
                'approval': {
                    'id': approval_id,
                    'status': 'modification_requested',
                    'operator_id': data.get('operator_id', 'unknown'),
                    'processed_at': '2025-04-04T23:15:00Z',
                    'reason': data.get('reason', ''),
                    'suggestions': data.get('suggestions', ''),
                    'priority': data.get('priority', 'medium')
                }
            })
        except Exception as e:
            app.logger.error(f"Error modifying approval: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to modify approval: {str(e)}"
            }), 500

    @app.route('/api/operator/strategy/revenue-targets', methods=['POST'])
    def update_revenue_targets():
        """Update revenue targets."""
        try:
            data = request.json
            return jsonify({
                'status': 'success',
                'targets': {
                    'monthly': float(data.get('monthlyTarget', 0)),
                    'quarterly': float(data.get('quarterlyTarget', 0)),
                    'annual': float(data.get('annualTarget', 0))
                }
            })
        except Exception as e:
            app.logger.error(f"Error updating revenue targets: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to update revenue targets: {str(e)}"
            }), 500

    @app.route('/api/operator/strategy/channel-mix', methods=['POST'])
    def update_channel_mix():
        """Update channel mix."""
        try:
            data = request.json
            return jsonify({
                'status': 'success',
                'channel_mix': {
                    'organic': float(data.get('organicAllocation', 0)) / 100,
                    'paid': float(data.get('paidAllocation', 0)) / 100,
                    'email': float(data.get('emailAllocation', 0)) / 100,
                    'affiliate': float(data.get('affiliateAllocation', 0)) / 100
                }
            })
        except Exception as e:
            app.logger.error(f"Error updating channel mix: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f"Failed to update channel mix: {str(e)}"
            }), 500
        


@app.route('/api/operator/system/control', methods=['POST'])
def system_control():
    """Start or stop the GAMS system."""
    try:
        print(f"DEBUG: Received system control request")
        print(f"DEBUG: Request data: {request.data}")
        print(f"DEBUG: Request headers: {request.headers}")
        print(f"DEBUG: Request content type: {request.content_type}")
        
        app.logger.info(f"Received system control request: {request.data}")
        
        # Check if the request has JSON data
        if not request.is_json:
            print(f"DEBUG: Request is not JSON. Content-Type: {request.content_type}")
            return jsonify({
                'status': 'error',
                'message': f"Did not attempt to load JSON data because the request Content-Type was not 'application/json'."
            }), 415
            
        data = request.json
        print(f"DEBUG: Parsed JSON data: {data}")
        app.logger.info(f"Parsed JSON data: {data}")
        
        if not data:
            app.logger.error("No JSON data provided in request")
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
            
        action = data.get('action', '').lower()
        app.logger.info(f"Requested action: {action}")
        
        if action not in ['start', 'stop']:
            app.logger.error(f"Invalid action: {action}. Must be 'start' or 'stop'.")
            return jsonify({
                'status': 'error',
                'message': f"Invalid action: {action}. Must be 'start' or 'stop'."
            }), 400
            
        # In a real implementation, this would start or stop the actual GAMS system
        # For now, we'll just return a success response with the current system state
        
        system_status = {
            'running': action == 'start',
            'status': 'running' if action == 'start' else 'stopped',
            'start_time': '2025-04-04T23:19:30Z' if action == 'start' else None,
            'uptime': '0 minutes' if action == 'start' else '0',
            'operator_id': data.get('operator_id', 'unknown'),
            'action_time': '2025-04-04T23:19:30Z'
        }
        
        return jsonify({
            'status': 'success',
            'message': f"GAMS system {'started' if action == 'start' else 'stopped'} successfully",
            'system_status': system_status
        })
    except Exception as e:
        app.logger.error(f"Error controlling GAMS system: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Failed to control GAMS: {str(e)}"
        }), 500

def run_server(host='0.0.0.0', port=5011, debug=True):
    """Run the Flask server.
    
    Args:
        host (str): Host to run the server on. Default is '0.0.0.0' to allow external connections.
        port (int): Port to run the server on. Default is 5011.
        debug (bool): Whether to run in debug mode. Default is True.
    """
    print(f"Starting Operator Dashboard server at http://localhost:{port}")
    print(f"Dashboard will be available at: http://localhost:{port}/")
    print(f"API endpoints will be available at: http://localhost:{port}/api/operator/...")
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    import argparse
    import datetime
    
    parser = argparse.ArgumentParser(description='Run the GAMS Operator Dashboard server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5011, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, debug=args.debug)
