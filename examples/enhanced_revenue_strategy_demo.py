"""
Enhanced Revenue Strategy Management Demo

This script demonstrates the enhanced revenue strategy management capabilities
with knowledge graph integration, including strategy creation, evaluation,
optimization, and performance monitoring.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledge_graph import MarketingKnowledgeGraph
from core.revenue.revenue_optimization_framework import RevenueOptimizationFramework
from core.revenue.revenue_strategy_manager import StrategyType
from core.revenue.revenue_strategy_manager_ext import EnhancedRevenueStrategyManager
from core.revenue.revenue_performance_monitor import RevenuePerformanceMonitor
from core.revenue.revenue_knowledge_integration import RevenueKnowledgeIntegration
from core.revenue.revenue_graph_initializer import RevenueGraphInitializer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def setup_knowledge_graph():
    """Initialize and set up the knowledge graph with revenue structure."""
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
    
    # Save the knowledge graph
    kg.save()
        
    logger.info("Knowledge graph initialized with comprehensive revenue structure")
    return kg

async def create_and_evaluate_strategies(knowledge_integration):
    """Create and evaluate revenue strategies."""
    # Create the enhanced strategy manager
    strategy_manager = EnhancedRevenueStrategyManager(
        storage_dir="data/revenue",
        knowledge_integration=knowledge_integration
    )
    
    # Create acquisition strategy
    acquisition_strategy = await strategy_manager.create_strategy(
        name="Social Media Acquisition Campaign",
        strategy_type=StrategyType.ACQUISITION,
        description="Strategy to acquire new customers through social media advertising",
        target_channels=["social_media", "display"],
        target_segments=["new_customers", "young_professionals"],
        revenue_model="cpa",
        metrics={
            "budget": 5000,
            "duration_days": 30,
            "platforms": ["instagram", "facebook", "linkedin"]
        },
        actions=[
            {
                "name": "Create ad creatives",
                "description": "Design ad creatives for social media platforms",
                "type": "creative"
            },
            {
                "name": "Set up targeting",
                "description": "Configure audience targeting for each platform",
                "type": "targeting"
            }
        ]
    )
    
    logger.info(f"Created acquisition strategy: {acquisition_strategy.name} (ID: {acquisition_strategy.id})")
    
    # Create monetization strategy
    monetization_strategy = await strategy_manager.create_strategy(
        name="Email Upsell Campaign",
        strategy_type=StrategyType.MONETIZATION,
        description="Strategy to increase revenue from existing customers through email marketing",
        target_channels=["email"],
        target_segments=["existing_customers", "high_value"],
        revenue_model="upsell",
        metrics={
            "budget": 2000,
            "duration_days": 45,
            "email_frequency": "weekly"
        },
        actions=[
            {
                "name": "Segment email list",
                "description": "Segment email list based on purchase history",
                "type": "segmentation"
            },
            {
                "name": "Create email templates",
                "description": "Design email templates for upsell campaign",
                "type": "creative"
            }
        ]
    )
    
    logger.info(f"Created monetization strategy: {monetization_strategy.name} (ID: {monetization_strategy.id})")
    
    # Create retention strategy
    retention_strategy = await strategy_manager.create_strategy(
        name="Customer Loyalty Program",
        strategy_type=StrategyType.RETENTION,
        description="Strategy to improve customer retention through a loyalty program",
        target_channels=["email", "mobile_app"],
        target_segments=["existing_customers", "at_risk"],
        revenue_model="loyalty",
        metrics={
            "budget": 3000,
            "duration_days": 90,
            "rewards": ["discounts", "exclusive_content", "early_access"]
        },
        actions=[
            {
                "name": "Design loyalty program",
                "description": "Design loyalty program structure and rewards",
                "type": "program_design"
            },
            {
                "name": "Implement tracking",
                "description": "Implement tracking system for loyalty points",
                "type": "technical"
            },
            {
                "name": "Create communication plan",
                "description": "Create communication plan for loyalty program",
                "type": "communication"
            }
        ]
    )
    
    logger.info(f"Created retention strategy: {retention_strategy.name} (ID: {retention_strategy.id})")
    
    # Update strategy metrics
    await strategy_manager.update_strategy_metrics(
        strategy_id=acquisition_strategy.id,
        metrics={
            "impressions": 250000,
            "clicks": 7500,
            "conversions": 375,
            "revenue": 18750,
            "cost": 5000,
            "conversion_rate": 0.05
        }
    )
    
    await strategy_manager.update_strategy_metrics(
        strategy_id=monetization_strategy.id,
        metrics={
            "emails_sent": 10000,
            "open_rate": 0.25,
            "click_rate": 0.08,
            "conversions": 200,
            "revenue": 15000,
            "cost": 2000,
            "conversion_rate": 0.02
        }
    )
    
    await strategy_manager.update_strategy_metrics(
        strategy_id=retention_strategy.id,
        metrics={
            "participants": 1500,
            "retention_rate": 0.85,
            "revenue": 30000,
            "cost": 3000,
            "conversion_rate": 0.03
        }
    )
    
    logger.info("Updated metrics for all strategies")
    
    # Evaluate strategies
    acquisition_evaluation = await strategy_manager.evaluate_strategy(acquisition_strategy.id)
    logger.info(f"Acquisition strategy evaluation: {acquisition_evaluation['evaluation']['overall']} rating")
    
    monetization_evaluation = await strategy_manager.evaluate_strategy(monetization_strategy.id)
    logger.info(f"Monetization strategy evaluation: {monetization_evaluation['evaluation']['overall']} rating")
    
    retention_evaluation = await strategy_manager.evaluate_strategy(retention_strategy.id)
    logger.info(f"Retention strategy evaluation: {retention_evaluation['evaluation']['overall']} rating")
    
    # Generate recommendations
    acquisition_recommendations = await strategy_manager.generate_recommendations(acquisition_strategy.id)
    logger.info(f"Generated {len(acquisition_recommendations)} recommendations for acquisition strategy")
    
    # Optimize strategy
    optimization_plan = await strategy_manager.optimize_strategy(acquisition_strategy.id)
    logger.info(f"Created optimization plan for {optimization_plan['name']} with {len(optimization_plan['optimization_actions'])} actions")
    
    # Get strategies by performance
    top_strategies = await strategy_manager.get_strategies_by_performance(min_roi=50)
    logger.info(f"Found {len(top_strategies)} strategies with ROI > 50%")
    
    # Analyze strategies by channel
    channel_analysis = await strategy_manager.analyze_strategies_by_channel()
    logger.info(f"Completed channel analysis for {len(channel_analysis['channel_performance'])} channels")
    
    # Analyze strategies by segment
    segment_analysis = await strategy_manager.analyze_strategies_by_segment()
    logger.info(f"Completed segment analysis for {len(segment_analysis['segment_performance'])} segments")
    
    return strategy_manager

async def retrieve_from_knowledge_graph(knowledge_integration, strategy_manager):
    """Retrieve and display data from the knowledge graph."""
    # Get all strategies from knowledge graph
    strategies = await knowledge_integration.get_revenue_strategies()
    logger.info(f"Retrieved {len(strategies)} strategies from knowledge graph")
    
    if strategies:
        # Get first strategy ID
        strategy_id = strategies[0]["id"]
        
        # Get metrics for the strategy
        metrics = await knowledge_integration.get_strategy_metrics(strategy_id)
        if metrics:
            logger.info(f"Retrieved metrics for strategy {strategy_id}: ROI = {metrics.get('roi', 0):.1f}%")
        
        # Get recommendations for the strategy
        recommendations = await knowledge_integration.get_strategy_recommendations(strategy_id)
        if recommendations:
            logger.info(f"Retrieved {len(recommendations)} recommendations for strategy {strategy_id}")
        
        # Get evaluation for the strategy
        evaluation = await knowledge_integration.get_strategy_evaluation(strategy_id)
        if evaluation:
            logger.info(f"Retrieved evaluation for strategy {strategy_id}: {evaluation.get('evaluation', {}).get('overall', 'N/A')} rating")
        
        # Get optimization plan for the strategy
        optimization = await knowledge_integration.get_strategy_optimization(strategy_id)
        if optimization:
            logger.info(f"Retrieved optimization plan for strategy {strategy_id} with {len(optimization.get('optimization_actions', []))} actions")
    
    # Get strategies by channel
    channel_strategies = await knowledge_integration.get_strategies_by_channel("channel_social_media")
    logger.info(f"Retrieved {len(channel_strategies)} strategies for social media channel")
    
    # Get strategies by segment
    segment_strategies = await knowledge_integration.get_strategies_by_segment("segment_existing_customers")
    logger.info(f"Retrieved {len(segment_strategies)} strategies for existing customers segment")
    
    # Analyze revenue performance by channel
    channel_analysis = await knowledge_integration.analyze_revenue_performance_by_channel()
    logger.info(f"Channel performance analysis: {len(channel_analysis['channels'])} channels, Total Revenue: ${channel_analysis['total_revenue']:.2f}, ROI: {channel_analysis['roi']:.2f}%")
    
    # Analyze revenue performance by segment
    segment_analysis = await knowledge_integration.analyze_revenue_performance_by_segment()
    logger.info(f"Segment performance analysis: {len(segment_analysis['segments'])} segments, Total Revenue: ${segment_analysis['total_revenue']:.2f}, ROI: {segment_analysis['roi']:.2f}%")

async def main():
    """Main function to run the demo."""
    try:
        logger.info("Starting Enhanced Revenue Strategy Management Demo")
        
        # Set up knowledge graph
        kg = await setup_knowledge_graph()
        
        # Create knowledge integration
        knowledge_integration = RevenueKnowledgeIntegration(knowledge_graph=kg)
        
        # Create and evaluate strategies
        strategy_manager = await create_and_evaluate_strategies(knowledge_integration)
        
        # Retrieve data from knowledge graph
        await retrieve_from_knowledge_graph(knowledge_integration, strategy_manager)
        
        logger.info("Enhanced Revenue Strategy Management Demo completed successfully")
        
    except Exception as e:
        logger.error(f"Error in demo: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
