"""
Revenue Optimization Framework Integration Example.

This script demonstrates how to use the Revenue Optimization Framework
with the Marketing Orchestrator and Knowledge Graph.
"""

import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import core components
from core.orchestrator.orchestrator import MarketingOrchestrator
from core.knowledge_graph.knowledge_graph import MarketingKnowledgeGraph
from core.revenue.revenue_optimization_framework import RevenueOptimizationFramework
from core.revenue.orchestrator_integration import RevenueOrchestratorIntegration
from core.revenue.revenue_goal_manager import GoalPeriod, GoalStatus
from core.revenue.forecast_models import ForecastingMethod, ScenarioType, TimeGranularity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample data
SAMPLE_CUSTOMER_JOURNEYS = {
    "customer1": {
        "touchpoints": [
            {
                "channel": "organic_search",
                "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
                "page": "/blog/seo-tips",
                "weight": 0.3
            },
            {
                "channel": "email",
                "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
                "campaign": "newsletter_weekly",
                "weight": 0.2
            },
            {
                "channel": "social_media",
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                "platform": "twitter",
                "weight": 0.5
            }
        ],
        "conversions": [
            {
                "timestamp": datetime.now().isoformat(),
                "value": 120.0,
                "product": "premium_subscription",
                "attribution_model": "linear"
            }
        ]
    },
    "customer2": {
        "touchpoints": [
            {
                "channel": "paid_search",
                "timestamp": (datetime.now() - timedelta(days=7)).isoformat(),
                "campaign": "product_launch",
                "weight": 0.6
            },
            {
                "channel": "referral",
                "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
                "source": "partner_website",
                "weight": 0.4
            }
        ],
        "conversions": [
            {
                "timestamp": datetime.now().isoformat(),
                "value": 250.0,
                "product": "annual_plan",
                "attribution_model": "first_touch"
            }
        ]
    }
}

SAMPLE_HISTORICAL_REVENUE = [
    {"timestamp": (datetime.now() - timedelta(days=180)).isoformat(), "value": 10000.0},
    {"timestamp": (datetime.now() - timedelta(days=150)).isoformat(), "value": 12000.0},
    {"timestamp": (datetime.now() - timedelta(days=120)).isoformat(), "value": 15000.0},
    {"timestamp": (datetime.now() - timedelta(days=90)).isoformat(), "value": 18000.0},
    {"timestamp": (datetime.now() - timedelta(days=60)).isoformat(), "value": 22000.0},
    {"timestamp": (datetime.now() - timedelta(days=30)).isoformat(), "value": 25000.0}
]

SAMPLE_CONTENT_DATA = {
    "content_items": [
        {
            "id": "content1",
            "title": "10 SEO Tips for 2023",
            "url": "https://example.com/blog/seo-tips-2023",
            "keywords": ["seo", "tips", "2023"]
        },
        {
            "id": "content2",
            "title": "Guide to Content Marketing",
            "url": "https://example.com/blog/content-marketing-guide",
            "keywords": ["content marketing", "guide"]
        },
        {
            "id": "content3",
            "title": "Email Marketing Best Practices",
            "url": "https://example.com/blog/email-marketing",
            "keywords": ["email marketing", "best practices"]
        }
    ],
    "analytics": {
        "content1": {
            "views": 5000,
            "conversions": 50,
            "revenue": 2500.0
        },
        "content2": {
            "views": 3000,
            "conversions": 30,
            "revenue": 1500.0
        },
        "content3": {
            "views": 2000,
            "conversions": 10,
            "revenue": 500.0
        }
    }
}

SAMPLE_ANALYTICS_DATA = {
    "metrics": {
        "total_revenue": 30000.0,
        "conversion_rate": 2.5,
        "average_order_value": 120.0,
        "customer_acquisition_cost": 50.0,
        "revenue_per_visitor": 3.0
    },
    "reports": [
        {
            "title": "Revenue by Channel",
            "data": {
                "series": [
                    {"channel": "organic_search", "value": 10000.0},
                    {"channel": "paid_search", "value": 8000.0},
                    {"channel": "social_media", "value": 6000.0},
                    {"channel": "email", "value": 4000.0},
                    {"channel": "referral", "value": 2000.0}
                ]
            }
        },
        {
            "title": "Monthly Revenue Trend",
            "data": {
                "series": SAMPLE_HISTORICAL_REVENUE
            }
        }
    ]
}

async def main():
    """Run the Revenue Optimization Framework integration example."""
    logger.info("Starting Revenue Optimization Framework integration example")
    
    # Create data directories
    os.makedirs("data/revenue", exist_ok=True)
    os.makedirs("data/knowledge_graph", exist_ok=True)
    
    # Initialize core components
    orchestrator = MarketingOrchestrator()
    knowledge_graph = MarketingKnowledgeGraph()
    
    # Initialize Revenue Optimization Framework integration
    revenue_integration = RevenueOrchestratorIntegration(
        orchestrator=orchestrator,
        knowledge_graph=knowledge_graph,
        config={
            "storage_dir": "data/revenue"
        }
    )
    
    # Step 1: Set revenue goals
    logger.info("Step 1: Setting revenue goals")
    
    # Monthly revenue goal
    monthly_goal = await revenue_integration.revenue_framework.set_revenue_goal(
        name="Monthly Revenue Target",
        target_value=30000.0,
        period=GoalPeriod.MONTHLY,
        start_date=datetime.now().isoformat(),
        end_date=(datetime.now() + timedelta(days=30)).isoformat()
    )
    
    # Quarterly revenue goal
    quarterly_goal = await revenue_integration.revenue_framework.set_revenue_goal(
        name="Quarterly Revenue Target",
        target_value=100000.0,
        period=GoalPeriod.QUARTERLY,
        start_date=datetime.now().isoformat(),
        end_date=(datetime.now() + timedelta(days=90)).isoformat()
    )
    
    # Channel-specific goal
    channel_goal = await revenue_integration.revenue_framework.set_revenue_goal(
        name="Organic Search Revenue",
        target_value=15000.0,
        period=GoalPeriod.MONTHLY,
        start_date=datetime.now().isoformat(),
        end_date=(datetime.now() + timedelta(days=30)).isoformat(),
        channel="organic_search"
    )
    
    logger.info(f"Created goals: {monthly_goal['id']}, {quarterly_goal['id']}, {channel_goal['id']}")
    
    # Step 2: Record customer journeys and conversions
    logger.info("Step 2: Recording customer journeys and conversions")
    
    for customer_id, journey in SAMPLE_CUSTOMER_JOURNEYS.items():
        # Record touchpoints
        for touchpoint in journey["touchpoints"]:
            await revenue_integration.revenue_framework.attribution_agent.record_touchpoint(
                customer_id=customer_id,
                channel=touchpoint["channel"],
                timestamp=touchpoint["timestamp"],
                metadata={k: v for k, v in touchpoint.items() if k not in ["channel", "timestamp", "weight"]}
            )
        
        # Record conversions
        for conversion in journey["conversions"]:
            await revenue_integration.revenue_framework.attribution_agent.record_conversion(
                customer_id=customer_id,
                value=conversion["value"],
                timestamp=conversion["timestamp"],
                metadata={k: v for k, v in conversion.items() if k not in ["value", "timestamp"]}
            )
    
    # Step 3: Load historical data and generate forecasts
    logger.info("Step 3: Loading historical data and generating forecasts")
    
    # Load historical revenue data
    await revenue_integration.revenue_framework.forecasting_engine.load_historical_data(
        data=SAMPLE_HISTORICAL_REVENUE
    )
    
    # Generate revenue forecast
    forecast = await revenue_integration.revenue_framework.forecast_revenue(
        periods=12,
        granularity=TimeGranularity.MONTHLY,
        method=ForecastingMethod.ARIMA
    )
    
    logger.info(f"Generated forecast: {forecast['id']}")
    
    # Generate scenario forecasts
    optimistic_forecast = await revenue_integration.revenue_framework.forecast_revenue(
        periods=12,
        granularity=TimeGranularity.MONTHLY,
        method=ForecastingMethod.ARIMA,
        scenario_type=ScenarioType.OPTIMISTIC
    )
    
    pessimistic_forecast = await revenue_integration.revenue_framework.forecast_revenue(
        periods=12,
        granularity=TimeGranularity.MONTHLY,
        method=ForecastingMethod.ARIMA,
        scenario_type=ScenarioType.PESSIMISTIC
    )
    
    logger.info(f"Generated scenario forecasts: optimistic={optimistic_forecast['id']}, pessimistic={pessimistic_forecast['id']}")
    
    # Step 4: Analyze channel performance
    logger.info("Step 4: Analyzing channel performance")
    
    channel_analysis = await revenue_integration.revenue_framework.analyze_channel_performance()
    
    logger.info(f"Channel analysis: {json.dumps(channel_analysis, indent=2)}")
    
    # Step 5: Optimize revenue allocation
    logger.info("Step 5: Optimizing revenue allocation")
    
    allocation = await revenue_integration.revenue_framework.optimize_revenue_allocation(
        budget=10000.0,
        forecast_id=forecast["id"]
    )
    
    logger.info(f"Optimized allocation: {json.dumps(allocation, indent=2)}")
    
    # Step 6: Synchronize with knowledge graph
    logger.info("Step 6: Synchronizing with knowledge graph")
    
    sync_results = await revenue_integration.sync_with_knowledge_graph()
    
    logger.info(f"Sync results: {json.dumps(sync_results, indent=2)}")
    
    # Step 7: Integrate with SEO Content Generator
    logger.info("Step 7: Integrating with SEO Content Generator")
    
    content_integration = await revenue_integration.integrate_with_seo_content_generator(
        content_data=SAMPLE_CONTENT_DATA
    )
    
    logger.info(f"Content integration: {json.dumps(content_integration, indent=2)}")
    
    # Step 8: Integrate with Analytics Engine
    logger.info("Step 8: Integrating with Analytics Engine")
    
    analytics_integration = await revenue_integration.integrate_with_analytics_engine(
        analytics_data=SAMPLE_ANALYTICS_DATA
    )
    
    logger.info(f"Analytics integration: {json.dumps(analytics_integration, indent=2)}")
    
    # Step 9: Generate revenue report
    logger.info("Step 9: Generating revenue report")
    
    report = await revenue_integration.revenue_framework.generate_revenue_report(
        start_date=(datetime.now() - timedelta(days=30)).isoformat(),
        end_date=datetime.now().isoformat(),
        include_forecasts=True,
        include_goals=True,
        include_attribution=True
    )
    
    logger.info(f"Revenue report: {json.dumps(report, indent=2)}")
    
    # Step 10: Get revenue insights from knowledge graph
    logger.info("Step 10: Getting revenue insights from knowledge graph")
    
    insights = revenue_integration.revenue_kg.get_revenue_insights()
    
    logger.info(f"Revenue insights: {json.dumps(insights, indent=2)}")
    
    logger.info("Revenue Optimization Framework integration example completed successfully")

if __name__ == "__main__":
    asyncio.run(main())
