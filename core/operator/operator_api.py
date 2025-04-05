"""
Operator API Module

This module provides a Flask-based API server for the Operator Interface,
allowing the dashboard to interact with the operator interface functionality.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Union
from flask import Flask, request, jsonify, send_from_directory

from core.operator.operator_interface import OperatorInterface, ApprovalStatus, ApprovalType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Operator Interface
operator_interface = OperatorInterface(config_path='config/operator_config.json')

# Mock data for demonstration (would be replaced with real data in production)
mock_data = {
    'active_experiments': [
        {
            'id': 'exp_001',
            'name': 'Homepage Hero Test',
            'type': 'a_b_test',
            'status': 'active',
            'start_date': '2025-03-15T00:00:00Z',
            'end_date': '2025-04-15T00:00:00Z',
            'performing_well': True,
            'metrics': {
                'conversion_rate': 0.045,
                'revenue': 12500
            }
        },
        {
            'id': 'exp_002',
            'name': 'Pricing Page Layout',
            'type': 'multivariate_test',
            'status': 'active',
            'start_date': '2025-03-20T00:00:00Z',
            'end_date': '2025-04-20T00:00:00Z',
            'performing_well': False,
            'metrics': {
                'conversion_rate': 0.032,
                'revenue': 8750
            }
        },
        {
            'id': 'exp_003',
            'name': 'Email Subject Line Test',
            'type': 'a_b_test',
            'status': 'active',
            'start_date': '2025-03-25T00:00:00Z',
            'end_date': '2025-04-10T00:00:00Z',
            'performing_well': True,
            'metrics': {
                'open_rate': 0.28,
                'click_rate': 0.045
            }
        }
    ],
    'financial_summary': {
        'revenue': {
            'total': 42580,
            'by_channel': {
                'organic': 12500,
                'paid': 18750,
                'affiliate': 7500,
                'email': 3830
            }
        },
        'expenses': {
            'total': 21290,
            'by_category': {
                'advertising': 15000,
                'content': 4500,
                'tools': 1000,
                'other': 790
            }
        },
        'profit': 21290,
        'profit_margin': 0.5,
        'vs_target': 12.5,
        'key_metrics': {
            'cac': 28.5,
            'ltv': 175,
            'conversion_rate': 0.035,
            'roas': 2.8
        }
    }
}

# API Routes

@app.route('/')
def index():
    """Serve the operator dashboard."""
    return send_from_directory('../frontend', 'operator_dashboard.html')

@app.route('/operator_dashboard.js')
def dashboard_js():
    """Serve the operator dashboard JavaScript."""
    return send_from_directory('../frontend', 'operator_dashboard.js')

# Approval Routes

@app.route('/api/operator/approvals/pending', methods=['GET'])
def get_pending_approvals():
    """Get all pending approvals."""
    # In a real implementation, this would use the operator_interface
    # For demo purposes, we'll return mock data
    
    # Get actual pending approvals from the operator interface
    pending_approvals = operator_interface.get_pending_approvals()
    
    # If no real approvals exist, provide mock data for demonstration
    if not pending_approvals:
        pending_approvals = [
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
            },
            {
                'id': 'pricing_20250404081234',
                'type': 'pricing',
                'data': {
                    'product': 'Premium Plan',
                    'current_price': 99.99,
                    'proposed_price': 79.99,
                    'discount_percentage': 20,
                    'reason': 'Competitive pressure and conversion optimization'
                },
                'description': '20% discount on Premium Plan',
                'urgency': 'critical',
                'status': 'pending',
                'created_at': '2025-04-04T08:12:34Z'
            },
            {
                'id': 'compliance_20250403121314',
                'type': 'compliance',
                'data': {
                    'content_type': 'email',
                    'campaign': 'New Product Launch',
                    'issues': ['GDPR compliance check required']
                },
                'description': 'Review new email marketing flow for GDPR compliance',
                'urgency': 'normal',
                'status': 'pending',
                'created_at': '2025-04-03T12:13:14Z'
            }
        ]
    
    return jsonify(pending_approvals)

@app.route('/api/operator/approvals/<approval_id>', methods=['POST'])
def process_approval(approval_id):
    """Process an approval request."""
    data = request.json
    
    status_str = data.get('status', 'pending')
    status_map = {
        'approved': ApprovalStatus.APPROVED,
        'rejected': ApprovalStatus.REJECTED,
        'modified': ApprovalStatus.MODIFIED
    }
    
    status = status_map.get(status_str, ApprovalStatus.PENDING)
    operator_id = data.get('operator_id', 'unknown')
    comments = data.get('comments', '')
    modified_data = data.get('modified_data')
    
    # Process the approval using the operator interface
    result = operator_interface.process_approval(
        approval_id=approval_id,
        status=status,
        operator_id=operator_id,
        comments=comments,
        modified_data=modified_data
    )
    
    if result:
        return jsonify({'status': 'success', 'approval': result})
    else:
        return jsonify({'status': 'error', 'message': 'Approval not found'}), 404

# Strategy Routes

@app.route('/api/operator/strategy', methods=['GET'])
def get_strategy():
    """Get current strategy settings."""
    # In a real implementation, this would use the operator_interface
    # For demo purposes, we'll return mock data
    
    strategy = {
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
            },
            {
                'name': 'SEO Experts Network',
                'commission_rate': 0.12,
                'status': 'pending',
                'monthly_revenue': 0
            }
        ]
    }
    
    return jsonify(strategy)

@app.route('/api/operator/strategy/revenue-targets', methods=['POST'])
def update_revenue_targets():
    """Update revenue targets."""
    data = request.json
    
    # Convert string values to numbers
    targets = {
        'monthly': float(data.get('monthlyTarget', 0)),
        'quarterly': float(data.get('quarterlyTarget', 0)),
        'annual': float(data.get('annualTarget', 0))
    }
    
    # Update targets using the operator interface
    result = operator_interface.define_revenue_targets(targets)
    
    return jsonify({'status': 'success', 'targets': result})

@app.route('/api/operator/strategy/channel-mix', methods=['POST'])
def update_channel_mix():
    """Update channel mix."""
    data = request.json
    
    # Convert percentage strings to decimal values
    channel_mix = {
        'organic': float(data.get('organicAllocation', 0)) / 100,
        'paid': float(data.get('paidAllocation', 0)) / 100,
        'email': float(data.get('emailAllocation', 0)) / 100,
        'affiliate': float(data.get('affiliateAllocation', 0)) / 100
    }
    
    # Update channel mix using the operator interface
    result = operator_interface.define_channel_mix(channel_mix)
    
    return jsonify({'status': 'success', 'channel_mix': result})

# Compliance Routes

@app.route('/api/operator/compliance/issues', methods=['GET'])
def get_compliance_issues():
    """Get compliance issues."""
    # In a real implementation, this would use the operator_interface
    # For demo purposes, we'll return mock data
    
    issues = [
        {
            'id': 'compliance_gdpr_20250403121314',
            'type': 'gdpr',
            'details': {
                'content_type': 'email',
                'campaign': 'New Product Launch',
                'issues': ['Missing unsubscribe link', 'No clear privacy policy link']
            },
            'status': 'open',
            'created_at': '2025-04-03T12:13:14Z'
        },
        {
            'id': 'compliance_affiliate_20250402151617',
            'type': 'affiliate_disclosure',
            'details': {
                'content_type': 'blog',
                'url': '/blog/best-marketing-tools',
                'issues': ['Missing affiliate disclosure']
            },
            'status': 'open',
            'created_at': '2025-04-02T15:16:17Z'
        }
    ]
    
    return jsonify(issues)

@app.route('/api/operator/compliance/settings', methods=['POST'])
def update_compliance_settings():
    """Update compliance settings."""
    data = request.json
    
    # Update compliance settings using the operator interface
    result = operator_interface.configure_compliance_settings(data)
    
    return jsonify({'status': 'success', 'settings': result})

# Financial Routes

@app.route('/api/operator/financial/summary', methods=['GET'])
def get_financial_summary():
    """Get financial summary."""
    # In a real implementation, this would use the operator_interface
    # For demo purposes, we'll return mock data
    
    return jsonify(mock_data['financial_summary'])

# Experiment Routes

@app.route('/api/operator/experiments/active', methods=['GET'])
def get_active_experiments():
    """Get active experiments."""
    # In a real implementation, this would use the operator_interface
    # For demo purposes, we'll return mock data
    
    return jsonify(mock_data['active_experiments'])

def start_api_server(host='0.0.0.0', port=5000, debug=False):
    """Start the API server."""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_api_server(debug=True)
