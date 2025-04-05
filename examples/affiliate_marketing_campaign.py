#!/usr/bin/env python3
"""
Example script demonstrating how to create and run an affiliate marketing campaign
with continuous improvement cycle integration.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path to allow imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.orchestrator.orchestrator import MarketingOrchestrator, ContinuousImprovementCycle
from core.agents.affiliate_agent.affiliate_agent import AffiliateAgent
from core.workflows.affiliate_marketing_workflow import AffiliateMarketingWorkflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_affiliate_campaign():
    """Run an example affiliate marketing campaign with continuous improvement."""
    
    # Initialize the orchestrator
    orchestrator = MarketingOrchestrator()
    
    # Initialize and register the affiliate agent
    affiliate_agent = AffiliateAgent(
        api_keys={
            "amazon": os.environ.get("AMAZON_AFFILIATE_KEY", "demo_key"),
            "clickbank": os.environ.get("CLICKBANK_AFFILIATE_KEY", "demo_key"),
            "shareasale": os.environ.get("SHAREASALE_AFFILIATE_KEY", "demo_key")
        }
    )
    orchestrator.register_agent("affiliate", affiliate_agent)
    
    # Initialize and register the affiliate marketing workflow
    affiliate_workflow = AffiliateMarketingWorkflow(orchestrator)
    
    # Load workflow configuration
    config_path = project_root / "config" / "workflows" / "affiliate_marketing_workflows.json"
    with open(config_path, 'r') as f:
        workflow_config = json.load(f)
    
    # Create a campaign
    campaign_id = orchestrator.create_campaign({
        "name": "Fitness Equipment Affiliate Campaign",
        "description": "Promote fitness equipment through affiliate marketing with continuous improvement",
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
        "budget": 1000,
        "goals": [
            {
                "name": "increase_affiliate_revenue",
                "description": "Increase affiliate revenue by 30% over 90 days",
                "target_value": 30,
                "current_value": 0,
                "unit": "percent",
                "deadline": (datetime.now() + timedelta(days=90)).isoformat()
            },
            {
                "name": "improve_conversion_rate",
                "description": "Improve affiliate link conversion rate to 5%",
                "target_value": 5,
                "current_value": 2.1,
                "unit": "percent",
                "deadline": (datetime.now() + timedelta(days=60)).isoformat()
            }
        ]
    })
    
    logger.info(f"Created campaign with ID: {campaign_id}")
    
    # Create a continuous improvement cycle for the campaign
    cycle_id = orchestrator.create_improvement_cycle(
        campaign_id=campaign_id,
        name="Affiliate Revenue Optimization Cycle",
        description="Continuous improvement cycle for optimizing affiliate revenue",
        goal_names=["increase_affiliate_revenue", "improve_conversion_rate"]
    )
    
    logger.info(f"Created improvement cycle with ID: {cycle_id}")
    
    # Start the improvement cycle with the website optimization phase
    start_result = await orchestrator.execute_workflow(
        "affiliate_continuous_improvement",
        {
            "cycle_id": cycle_id,
            "action": "start",
            "initial_phase": "website_optimization"
        }
    )
    
    logger.info(f"Started improvement cycle: {start_result}")
    
    # Execute product selection workflow
    product_selection_result = await orchestrator.execute_workflow(
        "affiliate_product_selection",
        {
            "campaign_id": campaign_id,
            "cycle_id": cycle_id,
            "niche": "fitness_equipment",
            "budget": 500,
            "platform_preference": "amazon",
            "count": 10
        }
    )
    
    logger.info(f"Product selection completed: {product_selection_result['status']}")
    
    if product_selection_result["status"] == "success":
        # Get selected product IDs
        product_ids = [product["id"] for product in 
                      product_selection_result.get("recommendations", {}).get("recommendations", [])]
        
        # Generate affiliate links
        link_generation_result = await orchestrator.execute_workflow(
            "affiliate_link_generation",
            {
                "campaign_id": campaign_id,
                "cycle_id": cycle_id,
                "product_ids": product_ids,
                "tracking_id": f"fitness-campaign-{campaign_id}",
                "utm_params": {
                    "source": "affiliate_campaign",
                    "medium": "website",
                    "campaign": f"fitness-{campaign_id}"
                }
            }
        )
        
        logger.info(f"Link generation completed: {link_generation_result['status']}")
        
        # Create A/B test for product pages
        ab_test_result = await orchestrator.execute_workflow(
            "affiliate_ab_testing",
            {
                "campaign_id": campaign_id,
                "cycle_id": cycle_id,
                "action": "create",
                "test_name": "Product Page Layout Test",
                "test_type": "landing_page",
                "variants": [
                    {
                        "id": "control",
                        "name": "Standard Layout",
                        "description": "Standard product page layout"
                    },
                    {
                        "id": "variant_a",
                        "name": "Benefits-focused Layout",
                        "description": "Layout focusing on product benefits"
                    },
                    {
                        "id": "variant_b",
                        "name": "Social Proof Layout",
                        "description": "Layout emphasizing customer reviews and testimonials"
                    }
                ],
                "duration_days": 14
            }
        )
        
        logger.info(f"A/B test creation completed: {ab_test_result['status']}")
        
        # Advance to the next phase (data learning & analysis)
        advance_result = await orchestrator.execute_workflow(
            "affiliate_continuous_improvement",
            {
                "cycle_id": cycle_id,
                "action": "advance"
            }
        )
        
        logger.info(f"Advanced to next phase: {advance_result}")
        
        # Simulate some time passing (in a real scenario, this would be days/weeks)
        logger.info("Simulating time passing...")
        
        # Simulate conversion analysis after collecting data
        conversion_analysis_result = await orchestrator.execute_workflow(
            "affiliate_conversion_analysis",
            {
                "campaign_id": campaign_id,
                "cycle_id": cycle_id,
                "product_id": product_ids[0] if product_ids else "sample_product_id",
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=14)).isoformat()
            }
        )
        
        logger.info(f"Conversion analysis completed: {conversion_analysis_result['status']}")
        
        # Track revenue
        revenue_tracking_result = await orchestrator.execute_workflow(
            "affiliate_revenue_tracking",
            {
                "campaign_id": campaign_id,
                "cycle_id": cycle_id,
                "product_ids": product_ids,
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "platforms": ["amazon", "clickbank"]
            }
        )
        
        logger.info(f"Revenue tracking completed: {revenue_tracking_result['status']}")
        
        # Advance to the next phase (content & offering refinement)
        advance_result = await orchestrator.execute_workflow(
            "affiliate_continuous_improvement",
            {
                "cycle_id": cycle_id,
                "action": "advance"
            }
        )
        
        logger.info(f"Advanced to next phase: {advance_result}")
        
        # Analyze A/B test results
        ab_analysis_result = await orchestrator.execute_workflow(
            "affiliate_ab_testing",
            {
                "campaign_id": campaign_id,
                "cycle_id": cycle_id,
                "action": "analyze",
                "test_id": ab_test_result.get("test_id", "sample_test_id"),
                "confidence_level": 0.95
            }
        )
        
        logger.info(f"A/B test analysis completed: {ab_analysis_result['status']}")
        
        # Apply an acceleration strategy based on the results
        acceleration_result = await orchestrator.execute_workflow(
            "affiliate_continuous_improvement",
            {
                "cycle_id": cycle_id,
                "action": "accelerate",
                "strategy_name": "conversion_boost"
            }
        )
        
        logger.info(f"Applied acceleration strategy: {acceleration_result}")
        
        # Advance to the next phase (revenue optimization)
        advance_result = await orchestrator.execute_workflow(
            "affiliate_continuous_improvement",
            {
                "cycle_id": cycle_id,
                "action": "advance"
            }
        )
        
        logger.info(f"Advanced to next phase: {advance_result}")
        
        # Optimize commissions
        commission_optimization_result = await orchestrator.execute_workflow(
            "affiliate_commission_optimization",
            {
                "campaign_id": campaign_id,
                "cycle_id": cycle_id,
                "platform": "amazon",
                "target_metric": "revenue",
                "optimization_strategy": "balanced"
            }
        )
        
        logger.info(f"Commission optimization completed: {commission_optimization_result['status']}")
        
        # Get the final cycle status
        status_result = await orchestrator.execute_workflow(
            "affiliate_continuous_improvement",
            {
                "cycle_id": cycle_id,
                "action": "status"
            }
        )
        
        logger.info(f"Final cycle status: {status_result}")
        
        # Get campaign metrics
        campaign_metrics = orchestrator.get_campaign_metrics(campaign_id)
        logger.info(f"Campaign metrics: {campaign_metrics}")
        
    else:
        logger.error("Product selection failed, cannot continue with the campaign")

if __name__ == "__main__":
    asyncio.run(run_affiliate_campaign())
