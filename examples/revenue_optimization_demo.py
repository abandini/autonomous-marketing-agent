#!/usr/bin/env python3
"""
Revenue Optimization Demo

This script demonstrates how to use the Revenue Optimizer to
continuously optimize revenue through reinforcement learning.
"""

import os
import sys
import json
import time
import logging
import random
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.revenue_optimization.revenue_optimizer import RevenueOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample data sources for demonstration
def get_analytics_data():
    """
    Sample analytics data source.
    """
    return {
        'page_views': random.randint(1000, 5000),
        'unique_visitors': random.randint(800, 3000),
        'bounce_rate': random.uniform(0.2, 0.6),
        'conversion_rate': random.uniform(0.01, 0.05),
        'average_session_duration': random.uniform(60, 300),
        'top_pages': [
            {'url': '/product-1', 'views': random.randint(100, 500)},
            {'url': '/product-2', 'views': random.randint(100, 500)},
            {'url': '/blog/post-1', 'views': random.randint(50, 300)}
        ]
    }

def get_financial_data():
    """
    Sample financial data source.
    """
    return {
        'revenue': random.uniform(5000, 15000),
        'costs': random.uniform(2000, 8000),
        'profit': random.uniform(1000, 7000),
        'profit_margin': random.uniform(0.1, 0.5),
        'average_order_value': random.uniform(50, 150),
        'customer_acquisition_cost': random.uniform(10, 50),
        'lifetime_value': random.uniform(200, 1000)
    }

def get_marketing_data():
    """
    Sample marketing data source.
    """
    return {
        'email_campaigns': {
            'open_rate': random.uniform(0.1, 0.4),
            'click_rate': random.uniform(0.01, 0.1),
            'conversion_rate': random.uniform(0.005, 0.03)
        },
        'social_media': {
            'engagement_rate': random.uniform(0.01, 0.05),
            'followers_growth': random.uniform(-0.01, 0.05),
            'click_through_rate': random.uniform(0.005, 0.02)
        },
        'ad_campaigns': {
            'impressions': random.randint(10000, 50000),
            'clicks': random.randint(100, 1000),
            'ctr': random.uniform(0.01, 0.05),
            'cpc': random.uniform(0.5, 2.0),
            'conversions': random.randint(10, 100),
            'conversion_rate': random.uniform(0.01, 0.1),
            'roas': random.uniform(1.0, 5.0)
        }
    }

# Sample action handlers for demonstration
def handle_content_action(action, experiment_id):
    """
    Sample content action handler.
    """
    logger.info(f"Handling content action: {action}, experiment: {experiment_id}")
    return {
        'status': 'success',
        'message': f"Content action executed successfully",
        'action_type': 'content',
        'experiment_id': experiment_id
    }

def handle_pricing_action(action, experiment_id):
    """
    Sample pricing action handler.
    """
    logger.info(f"Handling pricing action: {action}, experiment: {experiment_id}")
    return {
        'status': 'success',
        'message': f"Pricing action executed successfully",
        'action_type': 'pricing',
        'experiment_id': experiment_id
    }

def handle_advertising_action(action, experiment_id):
    """
    Sample advertising action handler.
    """
    logger.info(f"Handling advertising action: {action}, experiment: {experiment_id}")
    return {
        'status': 'success',
        'message': f"Advertising action executed successfully",
        'action_type': 'advertising',
        'experiment_id': experiment_id
    }

def main():
    """
    Main function to demonstrate the Revenue Optimizer.
    """
    # Initialize the Revenue Optimizer
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'revenue_optimization_config.json'))
    optimizer = RevenueOptimizer(config_path)
    
    # Register data sources
    optimizer.register_data_source('analytics', get_analytics_data)
    optimizer.register_data_source('financial', get_financial_data)
    optimizer.register_data_source('marketing', get_marketing_data)
    
    # Register action handlers
    optimizer.register_action_handler('content', handle_content_action)
    optimizer.register_action_handler('pricing', handle_pricing_action)
    optimizer.register_action_handler('advertising', handle_advertising_action)
    
    # Start the optimization process
    optimizer.start()
    
    try:
        # Run for a while to demonstrate
        logger.info("Revenue Optimizer is running. Press Ctrl+C to stop.")
        
        # Periodically check the status
        for i in range(5):
            time.sleep(10)  # Wait for 10 seconds
            
            # Get optimization status
            status = optimizer.get_optimization_status()
            logger.info(f"Optimization Status: {json.dumps(status, indent=2)}")
            
            # Get revenue insights
            insights = optimizer.get_revenue_insights()
            logger.info(f"Revenue Insights: {json.dumps(insights, indent=2)}")
            
            # Demonstrate manual optimization
            if i == 2:
                manual_action = {
                    'content_type': 'blog',
                    'pricing': 1.1,
                    'ad_spend': 1.5
                }
                result = optimizer.manual_optimization(manual_action)
                logger.info(f"Manual Optimization Result: {json.dumps(result, indent=2)}")
        
    except KeyboardInterrupt:
        logger.info("Stopping the Revenue Optimizer...")
    finally:
        # Stop the optimization process
        optimizer.stop()
        logger.info("Revenue Optimizer stopped.")

if __name__ == "__main__":
    main()
