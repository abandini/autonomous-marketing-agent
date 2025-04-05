"""
Competitive Intelligence Manager

This module provides the main integration point for the Competitive Intelligence system,
bringing together all components and providing a unified interface.
"""

import logging
import json
import datetime
import os
import uuid
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field

from .monitoring import CompetitorMonitor, CompetitorProfile, MarketPositionData, MarketPositionAnalyzer, BenchmarkAlertSystem, CompetitiveAlert
from .pattern_recognizer import PatternRecognizer
from .predictive_modeler import PredictiveModeler
from .trend_analyzer import TrendAnalyzer
from .knowledge_repository import KnowledgeRepository, CompetitiveEvent, CompetitiveInsight
from .response import CountermeasureEngine
from .opportunity import OpportunityAnalyzer
from .wargaming import WarGamingSimulator
from .insights import CrossTeamDistributor, CompetitiveInsight
from .ai_analysis import SentimentAnalyzer

logger = logging.getLogger(__name__)

class CompetitiveIntelligenceManager:
    """
    Competitive Intelligence Manager
    
    Main integration point for the Competitive Intelligence system.
    Coordinates all components and provides a unified interface.
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize the Competitive Intelligence Manager"""
        logger.info("Initializing Competitive Intelligence Manager")
        
        # Initialize components
        self.competitor_monitor = CompetitorMonitor()
        self.position_analyzer = MarketPositionAnalyzer(self.competitor_monitor)
        self.alert_system = BenchmarkAlertSystem(self.competitor_monitor, self.position_analyzer)
        
        # Initialize analysis components
        self.pattern_recognizer = PatternRecognizer(self.competitor_monitor)
        self.predictive_modeler = PredictiveModeler(self.competitor_monitor, self.pattern_recognizer)
        self.trend_analyzer = TrendAnalyzer(self.competitor_monitor)
        self.knowledge_repository = KnowledgeRepository(storage_dir)
        
        # Initialize response components
        self.countermeasure_engine = CountermeasureEngine(self.competitor_monitor, self.position_analyzer, self.alert_system)
        self.opportunity_analyzer = OpportunityAnalyzer(self.competitor_monitor, self.position_analyzer)
        self.war_gaming_simulator = WarGamingSimulator(self.competitor_monitor, self.position_analyzer)
        
        # Initialize insight components
        self.insight_distributor = CrossTeamDistributor(self.competitor_monitor, self.alert_system, 
                                                      self.countermeasure_engine, self.opportunity_analyzer, 
                                                      self.war_gaming_simulator)
        self.sentiment_analyzer = SentimentAnalyzer(self.competitor_monitor)
        
        # System state
        self.is_running = False
        self.last_full_analysis = None
        self.analysis_frequency_days = 7  # Default to weekly analysis
        
    def start_system(self) -> Dict:
        """
        Start the Competitive Intelligence system
        
        Returns status information
        """
        logger.info("Starting Competitive Intelligence system")
        
        if self.is_running:
            return {
                "status": "already_running",
                "message": "Competitive Intelligence system is already running"
            }
            
        self.is_running = True
        
        # Run initial analysis if needed
        if not self.last_full_analysis:
            analysis_results = self.run_full_analysis()
            status_message = "System started with initial analysis"
        else:
            days_since_last = (datetime.datetime.now() - self.last_full_analysis).days
            if days_since_last >= self.analysis_frequency_days:
                analysis_results = self.run_full_analysis()
                status_message = "System started with fresh analysis"
            else:
                analysis_results = None
                status_message = "System started with existing analysis"
                
        return {
            "status": "running",
            "message": status_message,
            "last_analysis": self.last_full_analysis.isoformat() if self.last_full_analysis else None,
            "analysis_results": analysis_results
        }
        
    def stop_system(self) -> Dict:
        """
        Stop the Competitive Intelligence system
        
        Returns status information
        """
        logger.info("Stopping Competitive Intelligence system")
        
        if not self.is_running:
            return {
                "status": "already_stopped",
                "message": "Competitive Intelligence system is already stopped"
            }
            
        self.is_running = False
        
        return {
            "status": "stopped",
            "message": "Competitive Intelligence system stopped successfully"
        }
        
    def get_system_status(self) -> Dict:
        """
        Get the current status of the Competitive Intelligence system
        
        Returns status information
        """
        logger.info("Getting Competitive Intelligence system status")
        
        return {
            "is_running": self.is_running,
            "last_full_analysis": self.last_full_analysis.isoformat() if self.last_full_analysis else None,
            "analysis_frequency_days": self.analysis_frequency_days,
            "next_scheduled_analysis": (self.last_full_analysis + datetime.timedelta(days=self.analysis_frequency_days)).isoformat() if self.last_full_analysis else None,
            "component_status": {
                "competitor_monitor": {
                    "competitors_tracked": len(self.competitor_monitor.competitors)
                },
                "pattern_recognizer": {
                    "active_patterns": sum(len(patterns) for patterns in self.pattern_recognizer.competitor_patterns.values())
                },
                "predictive_modeler": {
                    "active_predictions": len([p for p in self.predictive_modeler.predictions.values() if p.status == "active"])
                },
                "trend_analyzer": {
                    "tracked_trends": len(self.trend_analyzer.trends)
                },
                "knowledge_repository": {
                    "events": len(self.knowledge_repository.events),
                    "insights": len(self.knowledge_repository.insights)
                }
            }
        }
        
    def run_full_analysis(self) -> Dict:
        """
        Run a full competitive intelligence analysis
        
        Returns analysis results
        """
        logger.info("Running full competitive intelligence analysis")
        
        if not self.is_running:
            logger.warning("Cannot run analysis while system is stopped")
            return {
                "status": "error",
                "message": "Cannot run analysis while system is stopped"
            }
            
        # Update last analysis timestamp
        self.last_full_analysis = datetime.datetime.now()
        
        # Run component analyses
        pattern_results = self.pattern_recognizer.run_pattern_detection()
        prediction_results = self.predictive_modeler.run_prediction_cycle()
        trend_results = self.trend_analyzer.run_trend_analysis()
        
        # Generate new insights
        new_insights = self._generate_insights_from_analysis(
            pattern_results, prediction_results, trend_results
        )
        
        # Distribute insights if needed
        if new_insights:
            # Add insights to the distributor's insights list
            self.insight_distributor.insights.extend(new_insights)
            # Call distribute_insights without arguments
            distribution_results = self.insight_distributor.distribute_insights()
        else:
            distribution_results = {"distributed_insights": 0}
            
        return {
            "status": "success",
            "timestamp": self.last_full_analysis.isoformat(),
            "pattern_results": pattern_results,
            "prediction_results": prediction_results,
            "trend_results": trend_results,
            "new_insights": len(new_insights),
            "distribution_results": distribution_results
        }
        
    def _generate_insights_from_analysis(self, pattern_results, prediction_results, trend_results) -> List[CompetitiveInsight]:
        """
        Generate insights from analysis results
        
        Parameters:
        - pattern_results: Results from pattern detection
        - prediction_results: Results from prediction cycle
        - trend_results: Results from trend analysis
        
        Returns list of new insights
        """
        logger.info("Generating insights from analysis results")
        
        new_insights = []
        
        # Generate insights from high-probability predictions
        high_prob_predictions = self.predictive_modeler.get_high_probability_predictions()
        for prediction in high_prob_predictions:
            # Skip if we already have an insight for this prediction
            existing = False
            for insight in self.knowledge_repository.insights.values():
                if prediction.prediction_id in insight.description:
                    existing = True
                    break
                    
            if existing:
                continue
                
            # Generate insight
            insight_id = f"insight_pred_{uuid.uuid4().hex[:8]}"
            
            # Get competitor name
            competitor_id = prediction.competitor_id
            profile = self.competitor_monitor.competitors.get(competitor_id)
            competitor_name = profile.name if profile else competitor_id
            
            # Create insight
            insight = CompetitiveInsight(
                id=insight_id,
                title=f"Predicted {prediction.action_type} from {competitor_name}",
                description=f"Prediction: {prediction.description}. Expected between {prediction.estimated_timing['min'].strftime('%Y-%m-%d')} and {prediction.estimated_timing['max'].strftime('%Y-%m-%d')}. Probability: {prediction.probability:.2f}",
                insight_type="prediction",
                source_type="analysis",
                source_id=prediction.prediction_id,
                related_competitors=[competitor_id],
                priority=int(prediction.probability * 5),
                created_at=datetime.datetime.now(),
                tags=["prediction", prediction.action_type]
            )
            
            # Add to repository
            self.knowledge_repository.add_insight(insight)
            new_insights.append(insight)
            
        # Generate insights from important trends
        important_trends = self.trend_analyzer.get_trends_by_importance(min_importance=0.7)
        for trend in important_trends:
            # Skip if we already have an insight for this trend
            existing = False
            for insight in self.knowledge_repository.insights.values():
                if trend.trend_id in insight.description:
                    existing = True
                    break
                    
            if existing:
                continue
                
            # Generate insight
            insight_id = f"insight_trend_{uuid.uuid4().hex[:8]}"
            
            # Create insight
            insight = CompetitiveInsight(
                id=insight_id,
                title=f"Important Market Trend: {trend.name}",
                description=f"{trend.description} This trend has strategic importance of {trend.strategic_importance:.2f} and is in {trend.status} status with adoption rate of {trend.adoption_rate:.2f}.",
                insight_type="market_trend",
                source_type="analysis",
                source_id=trend.trend_id,
                related_competitors=list(trend.competitor_positions.keys()),
                priority=int(trend.strategic_importance * 5),
                created_at=datetime.datetime.now(),
                tags=["trend", trend.category, trend.status]
            )
            
            # Add to repository
            self.knowledge_repository.add_insight(insight)
            new_insights.append(insight)
            
        # Generate insights from trend gaps
        trend_gaps = self.trend_analyzer.identify_trend_gaps()
        for gap in trend_gaps[:3]:  # Top 3 gaps only
            # Skip if we already have an insight for this gap
            existing = False
            for insight in self.knowledge_repository.insights.values():
                if (gap["trend_id"] in insight.description and
                    gap["competitor_id"] in insight.related_competitors):
                    existing = True
                    break
                    
            if existing:
                continue
                
            # Generate insight
            insight_id = f"insight_gap_{uuid.uuid4().hex[:8]}"
            
            # Create insight
            insight = CompetitiveInsight(
                id=insight_id,
                title=f"Competitive Gap: {gap['competitor_name']} in {gap['trend_name']}",
                description=f"{gap['competitor_name']} is lagging in adoption of {gap['trend_name']} with a position of {gap['competitor_position']:.2f} compared to average {gap['average_position']:.2f} and leader position of {gap['leader_position']:.2f}.",
                insight_type="competitive_gap",
                source_type="analysis",
                source_id=gap["trend_id"],
                related_competitors=[gap["competitor_id"]],
                priority=int(gap["strategic_importance"] * 3.5),  # Scale 0.7 importance to 1-5 scale
                created_at=datetime.datetime.now(),
                tags=["gap", "opportunity"]
            )
            
            # Add to repository
            self.knowledge_repository.add_insight(insight)
            new_insights.append(insight)
            
        return new_insights
        
    def add_competitor(self, profile: CompetitorProfile) -> Dict:
        """
        Add a new competitor to track
        
        Parameters:
        - profile: Competitor profile to add
        
        Returns status information
        """
        logger.info(f"Adding competitor: {profile.name}")
        
        # Add to competitor monitor
        self.competitor_monitor.add_competitor(profile)
        
        # Run initial pattern detection for this competitor
        self.pattern_recognizer.detect_all_patterns(profile.id)
        
        return {
            "status": "success",
            "message": f"Competitor {profile.name} added successfully",
            "competitor_id": profile.id
        }
        
    def update_competitor(self, competitor_id: str, updates: Dict) -> Dict:
        """
        Update an existing competitor
        
        Parameters:
        - competitor_id: ID of the competitor to update
        - updates: Dictionary of fields to update
        
        Returns status information
        """
        logger.info(f"Updating competitor {competitor_id}")
        
        # Get current profile
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            return {
                "status": "error",
                "message": f"Competitor {competitor_id} not found"
            }
            
        # Update profile
        for field, value in updates.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
                
        # Update last updated timestamp
        profile.last_updated = datetime.datetime.now()
        
        return {
            "status": "success",
            "message": f"Competitor {profile.name} updated successfully"
        }
        
    def record_competitor_event(self, event: CompetitiveEvent) -> Dict:
        """
        Record a competitive event
        
        Parameters:
        - event: The event to record
        
        Returns status information
        """
        logger.info(f"Recording event: {event.title}")
        
        # Add to knowledge repository
        event_id = self.knowledge_repository.add_event(event)
        
        # Check if this event validates any predictions
        self._validate_predictions_with_event(event)
        
        # Generate insight from event if significant
        if event.impact_level in ["high", "medium"]:
            self._generate_insight_from_event(event)
            
        return {
            "status": "success",
            "message": f"Event recorded successfully",
            "event_id": event_id
        }
        
    def _validate_predictions_with_event(self, event: CompetitiveEvent):
        """
        Check if an event validates any predictions
        
        Parameters:
        - event: The event to check against predictions
        """
        logger.info(f"Validating predictions against event: {event.title}")
        
        # Get active predictions for this competitor
        competitor_id = event.competitor_id
        prediction_ids = self.predictive_modeler.competitor_predictions.get(competitor_id, [])
        
        for prediction_id in prediction_ids:
            prediction = self.predictive_modeler.predictions.get(prediction_id)
            if not prediction or prediction.status != "active":
                continue
                
            # Check if event matches prediction
            if event.event_type in prediction.action_type:
                # Mark prediction as occurred
                self.predictive_modeler.update_prediction_status(
                    prediction_id, "occurred", event.date
                )
                logger.info(f"Prediction {prediction_id} validated by event {event.event_id}")
                
    def _generate_insight_from_event(self, event: CompetitiveEvent) -> Optional[CompetitiveInsight]:
        """
        Generate an insight from a significant event
        
        Parameters:
        - event: The event to generate insight from
        
        Returns the generated insight or None
        """
        logger.info(f"Generating insight from event: {event.title}")
        
        # Get competitor name
        competitor_id = event.competitor_id
        profile = self.competitor_monitor.competitors.get(competitor_id)
        competitor_name = profile.name if profile else competitor_id
        
        # Generate insight ID
        insight_id = f"insight_event_{uuid.uuid4().hex[:8]}"
        
        # Determine importance based on impact level
        if event.impact_level == "high":
            importance = 0.9
        elif event.impact_level == "medium":
            importance = 0.7
        else:
            importance = 0.5
            
        # Create insight
        insight = CompetitiveInsight(
            id=insight_id,
            title=f"{event.event_type.replace('_', ' ').title()} by {competitor_name}",
            description=f"{event.description}",
            insight_type="competitor",
            source_type="event",
            source_id=event.event_id,
            related_competitors=[competitor_id],
            priority=int(importance * 5),  # Convert to 1-5 scale
            created_at=datetime.datetime.now(),
            tags=[event.event_type, event.impact_level]
        )
        
        # Add to repository
        self.knowledge_repository.add_insight(insight)
        
        return insight
        
    def get_competitor_intelligence(self, competitor_id: str) -> Dict:
        """
        Get comprehensive intelligence for a specific competitor
        
        Parameters:
        - competitor_id: ID of the competitor
        
        Returns intelligence information
        """
        logger.info(f"Getting intelligence for competitor {competitor_id}")
        
        # Get competitor profile
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            return {
                "status": "error",
                "message": f"Competitor {competitor_id} not found"
            }
            
        # Get market position from the position_analyzer
        market_position = self.position_analyzer.position_data.get(competitor_id)
        
        # Get active patterns
        patterns = self.pattern_recognizer.get_active_patterns(competitor_id)
        
        # Get upcoming predictions
        predictions = [p for p in self.predictive_modeler.get_upcoming_predictions()
                     if p.competitor_id == competitor_id]
        
        # Get recent events
        events = self.knowledge_repository.get_competitor_events(competitor_id, limit=5)
        
        # Get insights
        insights = self.knowledge_repository.get_competitor_insights(competitor_id, limit=5)
        
        # Get competitor summary
        summary = self.knowledge_repository.generate_competitor_summary(competitor_id)
        
        return {
            "competitor_id": competitor_id,
            "name": profile.name,
            "profile": {
                "website": profile.website,
                "industry": profile.industry,
                "key_products": profile.main_products,
                "target_markets": profile.target_markets
            },
            "market_position": {
                "market_share": market_position.market_share if market_position else None,
                "price_position": market_position.price_position if market_position else None,
                "quality_position": market_position.quality_position if market_position else None,
                "innovation_position": market_position.innovation_position if market_position else None,
                "customer_sentiment": market_position.customer_sentiment if market_position else None,
                "share_of_voice": market_position.share_of_voice if market_position else None,
                "unique_selling_points": market_position.unique_selling_points if market_position else []
            },
            "behavior_patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "name": p.name,
                    "pattern_type": p.pattern_type,
                    "confidence": p.confidence
                }
                for p in patterns
            ],
            "upcoming_actions": [
                {
                    "prediction_id": p.prediction_id,
                    "action_type": p.action_type,
                    "description": p.description,
                    "probability": p.probability,
                    "expected_date": p.estimated_timing["expected"].isoformat()
                }
                for p in predictions
            ],
            "recent_events": [
                {
                    "event_id": e.event_id,
                    "title": e.title,
                    "date": e.date.isoformat(),
                    "event_type": e.event_type,
                    "impact_level": e.impact_level
                }
                for e in events
            ],
            "key_insights": [
                {
                    "id": i.id,
                    "title": i.title,
                    "insight_type": i.insight_type,
                    "priority": i.priority
                }
                for i in insights
            ],
            "summary": summary
        }
        
    def get_market_trends(self, min_importance: float = 0.0) -> Dict:
        """
        Get current market trends
        
        Parameters:
        - min_importance: Minimum importance threshold
        
        Returns trend information
        """
        logger.info(f"Getting market trends (min_importance={min_importance})")
        
        # Get trends
        if min_importance > 0:
            trends = self.trend_analyzer.get_trends_by_importance(min_importance)
        else:
            trends = self.trend_analyzer.get_trends_by_category()
            
        # Group by category
        trends_by_category = {}
        for trend in trends:
            category = trend.category
            if category not in trends_by_category:
                trends_by_category[category] = []
                
            trends_by_category[category].append({
                "trend_id": trend.trend_id,
                "name": trend.name,
                "description": trend.description,
                "status": trend.status,
                "adoption_rate": trend.adoption_rate,
                "strategic_importance": trend.strategic_importance
            })
            
        # Get trend gaps
        gaps = self.trend_analyzer.identify_trend_gaps()
        
        return {
            "total_trends": len(trends),
            "trends_by_category": trends_by_category,
            "trend_gaps": [
                {
                    "trend_name": g["trend_name"],
                    "competitor_name": g["competitor_name"],
                    "gap_to_leader": g["gap_to_leader"]
                }
                for g in gaps[:5]  # Top 5 gaps
            ]
        }
        
    def generate_strategic_recommendations(self, competitor_id: Optional[str] = None) -> Dict:
        """
        Generate strategic recommendations based on competitive intelligence
        
        Parameters:
        - competitor_id: Optional competitor to focus on
        
        Returns recommendations
        """
        logger.info(f"Generating strategic recommendations{f' for competitor {competitor_id}' if competitor_id else ''}")
        
        recommendations = []
        
        # Get high-probability predictions
        predictions = self.predictive_modeler.get_high_probability_predictions()
        if competitor_id:
            predictions = [p for p in predictions if p.competitor_id == competitor_id]
            
        # Generate countermeasures for predictions
        for prediction in predictions[:3]:  # Top 3 predictions
            impact = self.predictive_modeler.assess_potential_impact(prediction)
            
            if impact.get("qualitative_assessment", {}).get("severity") in ["high", "medium"]:
                countermeasures = self.countermeasure_engine.generate_countermeasures(
                    prediction.competitor_id, prediction.action_type
                )
                
                recommendations.append({
                    "type": "countermeasure",
                    "trigger": f"Predicted {prediction.action_type} from {prediction.competitor_id}",
                    "description": prediction.description,
                    "urgency": impact.get("qualitative_assessment", {}).get("response_urgency", "monitor"),
                    "actions": countermeasures.get("recommended_actions", [])[:3]
                })
                
        # Get important trends
        trends = self.trend_analyzer.get_trends_by_importance(min_importance=0.7)
        
        # Generate recommendations for trends
        for trend in trends[:3]:  # Top 3 trends
            response = self.trend_analyzer.recommend_trend_responses(trend.trend_id)
            
            recommendations.append({
                "type": "trend_response",
                "trigger": f"Important market trend: {trend.name}",
                "description": trend.description,
                "urgency": response.get("response_urgency", "low"),
                "actions": response.get("recommendations", [])
            })
            
        # Get opportunities
        if competitor_id:
            # For specific competitor, we'll use the existing opportunities but filter them
            self.opportunity_analyzer.run_opportunity_analysis()
            opportunities = [opp for opp in self.opportunity_analyzer.get_opportunities() 
                            if competitor_id in opp.related_competitors]
        else:
            # Run a complete opportunity analysis
            opportunities = self.opportunity_analyzer.run_opportunity_analysis()
            
        # Generate recommendations for opportunities
        for opportunity in opportunities[:3]:  # Top 3 opportunities
            recommendations.append({
                "type": "opportunity",
                "trigger": f"Market opportunity: {opportunity.name}",
                "description": opportunity.description,
                "urgency": "medium",
                "actions": getattr(opportunity, 'recommended_actions', [])
            })
            
        return {
            "total_recommendations": len(recommendations),
            "recommendations": recommendations,
            "generated_at": datetime.datetime.now().isoformat()
        }
        
    def simulate_competitive_scenario(self, scenario_config: Dict) -> Dict:
        """
        Simulate a competitive scenario
        
        Parameters:
        - scenario_config: Configuration for the scenario
        
        Returns simulation results
        """
        logger.info(f"Simulating competitive scenario: {scenario_config.get('name', 'unnamed')}")
        
        # Run simulation
        results = self.war_gaming_simulator.run_simulation(scenario_config)
        
        return results
        
    def export_intelligence_data(self, output_dir: str) -> Dict:
        """
        Export all intelligence data
        
        Parameters:
        - output_dir: Directory to export to
        
        Returns export results
        """
        logger.info(f"Exporting intelligence data to {output_dir}")
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Export repository data
        repository_results = self.knowledge_repository.export_repository(
            os.path.join(output_dir, "repository")
        )
        
        # Export competitor data
        competitors_path = os.path.join(output_dir, "competitors.json")
        competitors_data = {}
        for competitor_id, profile in self.competitor_monitor.competitors.items():
            competitors_data[competitor_id] = {
                "id": profile.id,
                "name": profile.name,
                "website": profile.website,
                "industry": profile.industry,
                "main_products": profile.main_products,
                "target_markets": profile.target_markets,
                "last_updated": profile.last_updated.isoformat()
            }
            
        with open(competitors_path, 'w') as f:
            json.dump(competitors_data, f, indent=2)
            
        # Export trends data
        trends_path = os.path.join(output_dir, "trends.json")
        trends_data = {}
        for trend_id, trend in self.trend_analyzer.trends.items():
            trends_data[trend_id] = {
                "trend_id": trend.trend_id,
                "name": trend.name,
                "description": trend.description,
                "category": trend.category,
                "status": trend.status,
                "strength": trend.strength,
                "adoption_rate": trend.adoption_rate,
                "strategic_importance": trend.strategic_importance,
                "first_observed": trend.first_observed.isoformat(),
                "last_updated": trend.last_updated.isoformat()
            }
            
        with open(trends_path, 'w') as f:
            json.dump(trends_data, f, indent=2)
            
        # Export system status
        status_path = os.path.join(output_dir, "system_status.json")
        status_data = self.get_system_status()
        status_data["export_timestamp"] = datetime.datetime.now().isoformat()
        
        with open(status_path, 'w') as f:
            json.dump(status_data, f, indent=2)
            
        return {
            "status": "success",
            "export_path": output_dir,
            "exported_items": {
                "competitors": len(competitors_data),
                "trends": len(trends_data),
                "events": repository_results.get("events", 0),
                "insights": repository_results.get("insights", 0)
            }
        }
        
    def import_intelligence_data(self, input_dir: str) -> Dict:
        """
        Import intelligence data
        
        Parameters:
        - input_dir: Directory to import from
        
        Returns import results
        """
        logger.info(f"Importing intelligence data from {input_dir}")
        
        # Check if directory exists
        if not os.path.isdir(input_dir):
            return {
                "status": "error",
                "message": f"Directory not found: {input_dir}"
            }
            
        # Import repository data
        repository_results = self.knowledge_repository.import_repository(
            os.path.join(input_dir, "repository")
        )
        
        # Import competitor data
        competitors_path = os.path.join(input_dir, "competitors.json")
        imported_competitors = 0
        
        if os.path.isfile(competitors_path):
            with open(competitors_path, 'r') as f:
                competitors_data = json.load(f)
                
            for competitor_id, data in competitors_data.items():
                profile = CompetitorProfile(
                    competitor_id=data["competitor_id"],
                    name=data["name"],
                    website=data.get("website", ""),
                    description=data.get("description", ""),
                    key_products=data.get("key_products", []),
                    target_markets=data.get("target_markets", []),
                    last_updated=datetime.datetime.fromisoformat(data.get("last_updated", datetime.datetime.now().isoformat()))
                )
                
                self.competitor_monitor.add_competitor(profile)
                imported_competitors += 1
                
        # Import trends data
        trends_path = os.path.join(input_dir, "trends.json")
        imported_trends = 0
        
        if os.path.isfile(trends_path):
            with open(trends_path, 'r') as f:
                trends_data = json.load(f)
                
            for trend_id, data in trends_data.items():
                if trend_id not in self.trend_analyzer.trends:
                    # Create trend object and add to analyzer
                    # This is simplified as the full implementation would be more complex
                    self.trend_analyzer.trends[trend_id] = data
                    
                    # Update category index
                    category = data.get("category")
                    if category:
                        if category not in self.trend_analyzer.category_trends:
                            self.trend_analyzer.category_trends[category] = []
                            
                        if trend_id not in self.trend_analyzer.category_trends[category]:
                            self.trend_analyzer.category_trends[category].append(trend_id)
                            
                    imported_trends += 1
                
        return {
            "status": "success",
            "import_path": input_dir,
            "imported_items": {
                "competitors": imported_competitors,
                "trends": imported_trends,
                "events": repository_results.get("events", 0),
                "insights": repository_results.get("insights", 0)
            }
        }
