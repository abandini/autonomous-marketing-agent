#!/usr/bin/env python3
"""
Competitive Intelligence Demo

This script demonstrates the capabilities of the Competitive Intelligence module
by setting up a sample competitive landscape and running analysis.
"""

import sys
import os
import logging
import datetime
import json
from pprint import pprint

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.competitive_intelligence import (
    CompetitorMonitor, 
    CompetitiveIntelligenceManager,
    PatternRecognizer,
    CrossTeamDistributor,
    CompetitiveInsight
)
from core.competitive_intelligence.monitoring import CompetitorProfile, MarketPositionData

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("competitive_intelligence_demo")

def create_sample_competitors():
    """Create sample competitor profiles for demonstration"""
    competitors = [
        CompetitorProfile(
            id="comp_acme",
            name="Acme Corporation",
            website="https://www.acmecorp.example",
            industry="Marketing Technology",
            size="large",
            main_products=["Acme Marketing Cloud", "Acme Analytics Suite", "Acme Campaign Manager"],
            target_markets=["Enterprise", "Mid-Market"],
            pricing_tiers={"basic": 500, "pro": 2000, "enterprise": 5000},
            last_updated=datetime.datetime.now(),
            social_profiles={"twitter": "@acmecorp", "linkedin": "acme-corporation"},
            key_strengths=["AI Integration", "Analytics Capabilities", "Enterprise Scale"],
            key_weaknesses=["High Price Point", "Complex Implementation"]
        ),
        CompetitorProfile(
            id="comp_globex",
            name="Globex Marketing",
            website="https://www.globexmarketing.example",
            industry="Marketing Automation",
            size="medium",
            main_products=["Globex Automation Platform", "Globex Customer Insights", "Globex Journey Mapper"],
            target_markets=["Mid-Market", "SMB"],
            pricing_tiers={"starter": 200, "business": 1000, "premium": 3000},
            last_updated=datetime.datetime.now(),
            social_profiles={"twitter": "@globexmktg", "linkedin": "globex-marketing"},
            key_strengths=["User Friendly", "Customer Journey Focus", "Quick Implementation"],
            key_weaknesses=["Limited Enterprise Features", "Data Integration Challenges"]
        ),
        CompetitorProfile(
            id="comp_initech",
            name="Initech Solutions",
            website="https://www.initech.example",
            industry="Traditional Marketing Services",
            size="large",
            main_products=["Initech Marketing Suite", "Initech Campaign Builder", "Initech Analytics"],
            target_markets=["Enterprise"],
            pricing_tiers={"standard": 1000, "professional": 3500, "custom": 10000},
            last_updated=datetime.datetime.now(),
            social_profiles={"twitter": "@initech", "linkedin": "initech-solutions"},
            key_strengths=["Established Brand", "Enterprise Relationships", "Comprehensive Services"],
            key_weaknesses=["Legacy Systems", "Slow Innovation", "High Costs"]
        ),
        CompetitorProfile(
            id="comp_umbrella",
            name="Umbrella Marketing Technologies",
            website="https://www.umbrella-tech.example",
            industry="AI Marketing",
            size="small",
            main_products=["Umbrella AI Platform", "Umbrella Predictive Analytics", "Umbrella Content Generator"],
            target_markets=["Enterprise", "Mid-Market", "SMB"],
            pricing_tiers={"basic": 300, "advanced": 1200, "unlimited": 4000},
            last_updated=datetime.datetime.now(),
            social_profiles={"twitter": "@umbrella_tech", "linkedin": "umbrella-technologies"},
            key_strengths=["Cutting-edge AI", "Innovative Features", "Flexible Pricing"],
            key_weaknesses=["New Market Entrant", "Limited Track Record", "Small Support Team"]
        )
    ]
    
    return competitors

def create_sample_market_positions(ci_manager):
    """Create sample market position data for competitors"""
    positions = [
        MarketPositionData(
            competitor_id="comp_acme",
            competitor_name="Acme Corporation",
            price_position=0.8,  # High price position
            quality_position=0.9,  # High quality
            innovation_position=0.7,  # Good innovation
            market_share=0.28,
            customer_sentiment=0.7,  # Positive sentiment
            share_of_voice=0.32,
            target_segments=["Enterprise", "Mid-Market"],
            unique_selling_points=["Brand recognition", "Product breadth", "Enterprise relationships"],
            timestamp=datetime.datetime.now()
        ),
        MarketPositionData(
            competitor_id="comp_globex",
            competitor_name="Globex Marketing",
            price_position=0.6,  # Medium-high price
            quality_position=0.8,  # Good quality
            innovation_position=0.9,  # High innovation
            market_share=0.15,
            customer_sentiment=0.8,  # Very positive sentiment
            share_of_voice=0.18,
            target_segments=["Mid-Market", "SMB"],
            unique_selling_points=["User experience", "Modern architecture", "Quick implementation"],
            timestamp=datetime.datetime.now()
        ),
        MarketPositionData(
            competitor_id="comp_initech",
            competitor_name="Initech Solutions",
            price_position=0.9,  # Very high price
            quality_position=0.7,  # Good quality
            innovation_position=0.4,  # Lower innovation
            market_share=0.22,
            customer_sentiment=0.3,  # Somewhat negative sentiment
            share_of_voice=0.25,
            target_segments=["Enterprise"],
            unique_selling_points=["Stability", "Comprehensive features", "Industry expertise"],
            timestamp=datetime.datetime.now()
        ),
        MarketPositionData(
            competitor_id="comp_umbrella",
            competitor_name="Umbrella Marketing Technologies",
            price_position=0.4,  # Lower price
            quality_position=0.6,  # Decent quality
            innovation_position=0.9,  # High innovation
            market_share=0.08,
            customer_sentiment=0.6,  # Positive sentiment
            share_of_voice=0.12,
            target_segments=["Enterprise", "Mid-Market", "SMB"],
            unique_selling_points=["Cutting-edge technology", "Agile development", "Competitive pricing"],
            timestamp=datetime.datetime.now()
        )
    ]
    
    # Add positions to the position analyzer's position_data dictionary
    for position in positions:
        ci_manager.position_analyzer.position_data[position.competitor_id] = position
        
    return positions

def create_sample_events(ci_manager):
    """Create sample competitive events"""
    
    # Acme events
    acme_events = [
        {
            "competitor_id": "comp_acme",
            "event_type": "product_launch",
            "title": "Acme Launches AI-Powered Marketing Assistant",
            "description": "Acme Corporation announced the release of their new AI-powered marketing assistant, designed to automate campaign optimization and content creation.",
            "date": datetime.datetime.now() - datetime.timedelta(days=45),
            "impact_level": "high"
        },
        {
            "competitor_id": "comp_acme",
            "event_type": "price_change",
            "title": "Acme Increases Enterprise Pricing by 12%",
            "description": "Acme Corporation has increased pricing for their Enterprise tier by 12%, citing increased development costs and expanded feature set.",
            "date": datetime.datetime.now() - datetime.timedelta(days=90),
            "impact_level": "medium"
        }
    ]
    
    # Globex events
    globex_events = [
        {
            "competitor_id": "comp_globex",
            "event_type": "partnership",
            "title": "Globex Partners with Major CRM Provider",
            "description": "Globex Marketing announced a strategic partnership with a leading CRM provider to enhance their data integration capabilities.",
            "date": datetime.datetime.now() - datetime.timedelta(days=30),
            "impact_level": "medium"
        },
        {
            "competitor_id": "comp_globex",
            "event_type": "marketing_campaign",
            "title": "Globex Launches 'Future of Marketing' Campaign",
            "description": "Globex Marketing initiated a major marketing campaign focused on their vision for the future of marketing automation.",
            "date": datetime.datetime.now() - datetime.timedelta(days=15),
            "impact_level": "low"
        }
    ]
    
    # Initech events
    initech_events = [
        {
            "competitor_id": "comp_initech",
            "event_type": "executive_change",
            "title": "Initech Appoints New Chief Technology Officer",
            "description": "Initech Solutions has appointed a new CTO with a background in AI and machine learning, signaling a potential shift in technology strategy.",
            "date": datetime.datetime.now() - datetime.timedelta(days=60),
            "impact_level": "medium"
        }
    ]
    
    # Umbrella events
    umbrella_events = [
        {
            "competitor_id": "comp_umbrella",
            "event_type": "funding",
            "title": "Umbrella Secures $50M Series C Funding",
            "description": "Umbrella Marketing Technologies has secured $50 million in Series C funding to accelerate product development and market expansion.",
            "date": datetime.datetime.now() - datetime.timedelta(days=20),
            "impact_level": "high"
        },
        {
            "competitor_id": "comp_umbrella",
            "event_type": "product_launch",
            "title": "Umbrella Releases Predictive Content Optimization Tool",
            "description": "Umbrella has launched a new predictive content optimization tool that uses machine learning to improve content performance.",
            "date": datetime.datetime.now() - datetime.timedelta(days=10),
            "impact_level": "medium"
        }
    ]
    
    # Combine all events
    all_events = acme_events + globex_events + initech_events + umbrella_events
    
    # Record events
    for event_data in all_events:
        # Create event ID
        event_id = f"event_{event_data['competitor_id']}_{event_data['event_type']}_{hash(event_data['title']) % 10000}"
        
        # Create event object
        from core.competitive_intelligence.knowledge_repository import CompetitiveEvent
        event = CompetitiveEvent(
            event_id=event_id,
            competitor_id=event_data["competitor_id"],
            event_type=event_data["event_type"],
            title=event_data["title"],
            description=event_data["description"],
            date=event_data["date"],
            impact_level=event_data["impact_level"],
            sources=["news", "company_website"],
            tags=[event_data["event_type"], event_data["competitor_id"]]
        )
        
        # Record the event
        ci_manager.record_competitor_event(event)
        
    return all_events

def main():
    """Main demo function"""
    logger.info("Starting Competitive Intelligence Demo")
    
    # Create output directory for results
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the CI manager
    ci_manager = CompetitiveIntelligenceManager(storage_dir=output_dir)
    
    # Add sample competitors
    logger.info("Adding sample competitors")
    competitors = create_sample_competitors()
    for competitor in competitors:
        ci_manager.add_competitor(competitor)
        
    # Add market positions
    logger.info("Adding market positions")
    create_sample_market_positions(ci_manager)
    
    # Add sample events
    logger.info("Adding sample competitive events")
    create_sample_events(ci_manager)
    
    # Start the CI system
    logger.info("Starting Competitive Intelligence system")
    start_result = ci_manager.start_system()
    print("\nSystem Start Result:")
    pprint(start_result)
    
    # Get system status
    status = ci_manager.get_system_status()
    print("\nSystem Status:")
    pprint(status)
    
    # Get competitor intelligence
    print("\nCompetitor Intelligence for Acme Corporation:")
    acme_intel = ci_manager.get_competitor_intelligence("comp_acme")
    
    # Save intelligence to file
    with open(os.path.join(output_dir, "acme_intelligence.json"), "w") as f:
        json.dump(acme_intel, f, indent=2, default=str)
        
    # Print key insights
    print("\nKey Insights:")
    for insight in acme_intel.get("key_insights", []):
        print(f"- {insight['title']} (Priority: {insight['priority']:.2f})")
        
    # Get upcoming actions
    print("\nUpcoming Predicted Actions:")
    for action in acme_intel.get("upcoming_actions", []):
        print(f"- {action['description']} (Probability: {action['probability']:.2f})")
        
    # Get market trends
    print("\nMarket Trends:")
    trends = ci_manager.get_market_trends(min_importance=0.6)
    
    # Save trends to file
    with open(os.path.join(output_dir, "market_trends.json"), "w") as f:
        json.dump(trends, f, indent=2, default=str)
        
    # Print trends by category
    for category, category_trends in trends.get("trends_by_category", {}).items():
        print(f"\n{category.title()} Trends:")
        for trend in category_trends:
            print(f"- {trend['name']} (Importance: {trend['strategic_importance']:.2f})")
            
    # Generate strategic recommendations
    print("\nStrategic Recommendations:")
    recommendations = ci_manager.generate_strategic_recommendations()
    
    # Save recommendations to file
    with open(os.path.join(output_dir, "strategic_recommendations.json"), "w") as f:
        json.dump(recommendations, f, indent=2, default=str)
        
    # Print top recommendations
    for i, rec in enumerate(recommendations.get("recommendations", [])[:3]):
        print(f"\n{i+1}. {rec['trigger']}")
        print(f"   Urgency: {rec['urgency']}")
        print(f"   Description: {rec['description']}")
        print("   Actions:")
        for action in rec.get("actions", [])[:2]:
            print(f"   - {action}")
            
    # Export intelligence data
    logger.info("Exporting intelligence data")
    export_result = ci_manager.export_intelligence_data(output_dir)
    print("\nExport Result:")
    pprint(export_result)
    
    # Stop the CI system
    logger.info("Stopping Competitive Intelligence system")
    stop_result = ci_manager.stop_system()
    print("\nSystem Stop Result:")
    pprint(stop_result)
    
    logger.info("Competitive Intelligence Demo completed")
    print(f"\nResults saved to: {output_dir}")

if __name__ == "__main__":
    main()
