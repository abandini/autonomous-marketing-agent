#!/usr/bin/env python3
"""
Revenue Knowledge Integration Demo

This script demonstrates the integration between the Revenue Optimization Framework
and the Knowledge Graph, showing how revenue strategies and performance metrics
can be stored and retrieved from the centralized knowledge repository.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.knowledge_graph.knowledge_graph import MarketingKnowledgeGraph
from core.revenue.revenue_optimization_framework import RevenueOptimizationFramework
from core.revenue.revenue_goal_manager import GoalPeriod
from core.revenue.revenue_strategy_manager import StrategyType
from core.revenue.revenue_graph_initializer import RevenueGraphInitializer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def setup_knowledge_graph():
    """Initialize and set up the knowledge graph with basic structure."""
    kg_storage_dir = "data/knowledge_graph"
    if not os.path.exists(kg_storage_dir):
        os.makedirs(kg_storage_dir)
        
    kg_file_path = os.path.join(kg_storage_dir, "marketing_knowledge_graph.json")
    
    kg_config = {
        "persistence_path": kg_file_path,
        "load_on_init": True
    }
    
    kg = MarketingKnowledgeGraph(config=kg_config)
    
    # Initialize the knowledge graph with revenue-specific structure
    initializer = RevenueGraphInitializer(knowledge_graph=kg)
    await initializer.initialize_revenue_structure()
    
    # Create basic categories if they don't exist (for backward compatibility)
    categories = [
        {"id": "metrics", "name": "Metrics", "description": "Performance metrics"},
        {"id": "goals", "name": "Goals", "description": "Business and marketing goals"},
        {"id": "strategies", "name": "Strategies", "description": "Marketing and revenue strategies"}
    ]
    
    for category in categories:
        if not kg.has_node(category["id"]):
            kg.add_node(category["id"], {
                "type": "category",
                "name": category["name"],
                "description": category["description"]
            })
        
    # Connect channels to the campaigns category
    for category in categories:
        if category["type"] == "channel":
            kg.add_edge("campaigns", category["id"], {"type": "contains"})
            
    logger.info("Knowledge graph initialized with basic structure")
    return kg

async def demo_revenue_goal_integration(framework: RevenueOptimizationFramework):
    """Demonstrate revenue goal integration with knowledge graph."""
    logger.info("\n=== REVENUE GOAL INTEGRATION DEMO ===")
    
    # Create revenue goals
    goals = [
        {
            "name": "Q3 Email Revenue Target",
            "target_value": 50000.0,
            "period": GoalPeriod.QUARTERLY,
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=90),
            "channel": "Email Marketing"
        },
        {
            "name": "Monthly Social Media Revenue",
            "target_value": 15000.0,
            "period": GoalPeriod.MONTHLY,
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=30),
            "channel": "Social Media"
        },
        {
            "name": "New Customer Acquisition Revenue",
            "target_value": 25000.0,
            "period": GoalPeriod.QUARTERLY,
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=90),
            "segment": "New Customers"
        }
    ]
    
    # Set goals using the framework
    goal_ids = []
    for goal_data in goals:
        # Create a goal and store it in the knowledge graph
        goal = await framework.set_revenue_goal(**goal_data)
        
        # Handle both dictionary and RevenueGoal object formats
        if hasattr(goal, 'to_dict'):
            goal_dict = goal.to_dict()
            logger.info(f"Created goal: {goal_dict['name']} with ID: {goal_dict['id']}")
        else:
            logger.info(f"Created goal: {goal.name} with ID: {goal.id}")
        
        goal_ids.append(goal.id if hasattr(goal, 'id') else goal['id'])
        
    # Retrieve goals from knowledge graph
    kg_goals = await framework.get_goals_from_knowledge_graph()
    logger.info(f"Retrieved {len(kg_goals)} goals from knowledge graph")
    
    # Display goal information
    for goal in kg_goals:
        logger.info(f"Goal from KG: {goal['name']} - Target: ${goal['target_value']}")
        
    return [g["id"] for g in kg_goals]

async def demo_revenue_strategy_integration(framework: RevenueOptimizationFramework, goal_ids: List[str]):
    """Demonstrate revenue strategy integration with knowledge graph."""
    logger.info("\n=== REVENUE STRATEGY INTEGRATION DEMO ===")
    
    # Create revenue strategies
    strategies = [
        {
            "name": "Email Upsell Campaign",
            "strategy_type": StrategyType.MONETIZATION,
            "description": "Targeted email campaign to upsell existing customers",
            "target_channels": ["Email Marketing"],
            "target_segments": ["Returning Customers"],
            "goals": [goal_ids[0]] if goal_ids else []
        },
        {
            "name": "Social Media Acquisition",
            "strategy_type": StrategyType.ACQUISITION,
            "description": "Social media campaign to acquire new customers",
            "target_channels": ["Social Media"],
            "target_segments": ["New Customers"],
            "goals": [goal_ids[2]] if len(goal_ids) > 2 else []
        },
        {
            "name": "Affiliate Commission Optimization",
            "strategy_type": StrategyType.PRICING,
            "description": "Optimize affiliate commission structure for better ROI",
            "target_channels": ["Affiliate Marketing"],
            "target_segments": [],
            "goals": []
        }
    ]
    
    # Create strategies using the framework
    strategy_ids = []
    for strategy_data in strategies:
        strategy = await framework.create_revenue_strategy(**strategy_data)
        
        # Handle both dictionary and RevenueStrategy object formats
        if hasattr(strategy, 'to_dict'):
            strategy_dict = strategy.to_dict()
            logger.info(f"Created strategy: {strategy_dict['name']} with ID: {strategy_dict['id']}")
            strategy_ids.append(strategy_dict['id'])
        else:
            logger.info(f"Created strategy: {strategy['name']} with ID: {strategy['id']}")
            strategy_ids.append(strategy['id'])
        
    # Retrieve strategies from knowledge graph
    kg_strategies = await framework.get_strategies_from_knowledge_graph()
    logger.info(f"Retrieved {len(kg_strategies)} strategies from knowledge graph")
    
    # Display strategy information
    for strategy in kg_strategies:
        logger.info(f"Strategy from KG: {strategy['name']} - Type: {strategy['strategy_type']}")
        
    # Get strategies for a specific goal
    if goal_ids:
        goal_strategies = await framework.get_strategies_for_goal(goal_ids[0])
        logger.info(f"Found {len(goal_strategies)} strategies for goal {goal_ids[0]}")
        
    return [s["id"] for s in kg_strategies]

async def demo_performance_metrics_integration(framework: RevenueOptimizationFramework):
    """Demonstrate performance metrics integration with knowledge graph."""
    logger.info("\n=== PERFORMANCE METRICS INTEGRATION DEMO ===")
    
    # Record performance metrics for different channels
    metrics_data = [
        {
            "metrics": {
                "revenue": 12500.0,
                "conversions": 250,
                "cost": 2500.0,
                "ctr": 0.025,
                "conversion_rate": 0.035
            },
            "source": "Email Marketing"
        },
        {
            "metrics": {
                "revenue": 8750.0,
                "conversions": 175,
                "cost": 3500.0,
                "ctr": 0.018,
                "conversion_rate": 0.022
            },
            "source": "Social Media"
        },
        {
            "metrics": {
                "revenue": 15000.0,
                "conversions": 120,
                "cost": 5000.0,
                "ctr": 0.032,
                "conversion_rate": 0.028
            },
            "source": "Search Marketing"
        },
        {
            "metrics": {
                "revenue": 9500.0,
                "conversions": 95,
                "cost": 2850.0,
                "ctr": 0.021,
                "conversion_rate": 0.019
            },
            "source": "Affiliate Marketing"
        }
    ]
    
    # Record metrics using the framework
    for data in metrics_data:
        result = await framework.record_performance_metrics(**data)
        logger.info(f"Recorded metrics for {data['source']}")
        
    # Analyze channel performance using knowledge graph
    performance_analysis = await framework.analyze_channel_performance_from_knowledge_graph()
    
    if performance_analysis.get("status") == "success":
        logger.info("Channel performance analysis from knowledge graph:")
        for channel, metrics in performance_analysis.get("channel_performance", {}).items():
            roi = metrics.get("roi", 0)
            logger.info(f"Channel: {channel} - Revenue: ${metrics.get('revenue', 0):.2f} - ROI: {roi:.2f}%")
    else:
        logger.info(f"Analysis status: {performance_analysis.get('status')}")
        
    return performance_analysis

async def main():
    """Run the revenue knowledge integration demo."""
    logger.info("Starting Revenue Knowledge Integration Demo")
    
    # Setup knowledge graph
    kg = await setup_knowledge_graph()
    
    # Initialize Revenue Optimization Framework with knowledge graph
    framework = RevenueOptimizationFramework(
        storage_dir="data/revenue",
        knowledge_graph=kg
    )
    
    # Run demo components
    goal_ids = await demo_revenue_goal_integration(framework)
    strategy_ids = await demo_revenue_strategy_integration(framework, goal_ids)
    performance_analysis = await demo_performance_metrics_integration(framework)
    
    logger.info("\n=== DEMO COMPLETE ===")
    logger.info("The Revenue Optimization Framework has been successfully integrated with the Knowledge Graph")
    logger.info("This integration enables centralized storage and retrieval of revenue-related information")
    
if __name__ == "__main__":
    asyncio.run(main())
