"""
Trend Analysis for Competitive Intelligence

This module provides tools for identifying and analyzing market trends,
assessing competitor positioning relative to trends, and recommending responses.
"""

import logging
import json
import datetime
import random
import math
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field

from .monitoring import CompetitorMonitor

logger = logging.getLogger(__name__)

@dataclass
class TrendData:
    """Data structure for market trends"""
    trend_id: str
    name: str
    description: str
    category: str  # technology, customer_behavior, regulatory, etc.
    strength: float  # 0.0 to 1.0
    adoption_rate: float  # 0.0 to 1.0
    competitor_positions: Dict[str, float] = field(default_factory=dict)  # competitor_id -> adoption level
    first_observed: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = field(default_factory=datetime.datetime.now)
    status: str = "emerging"  # emerging, growing, mature, declining
    sources: List[str] = field(default_factory=list)
    impact_areas: List[str] = field(default_factory=list)
    strategic_importance: float = 0.5  # 0.0 to 1.0
    
    def update_competitor_position(self, competitor_id: str, position: float):
        """Update a competitor's position relative to this trend"""
        self.competitor_positions[competitor_id] = position
        self.last_updated = datetime.datetime.now()
        
    def update_status(self, new_status: str):
        """Update the trend status"""
        valid_statuses = ["emerging", "growing", "mature", "declining"]
        if new_status in valid_statuses:
            self.status = new_status
            self.last_updated = datetime.datetime.now()
            
    def calculate_strategic_importance(self):
        """Calculate strategic importance based on strength, adoption and status"""
        # Status factor
        status_factors = {
            "emerging": 1.2,
            "growing": 1.0,
            "mature": 0.7,
            "declining": 0.3
        }
        status_factor = status_factors.get(self.status, 1.0)
        
        # Calculate importance
        self.strategic_importance = min(1.0, (self.strength * 0.4 + self.adoption_rate * 0.6) * status_factor)
        return self.strategic_importance


class TrendAnalyzer:
    """
    Trend Analysis
    
    Identifies and analyzes market trends, assesses competitor positioning,
    and recommends strategic responses.
    """
    
    def __init__(self, competitor_monitor: CompetitorMonitor):
        """Initialize with reference to competitor monitor"""
        self.competitor_monitor = competitor_monitor
        self.trends: Dict[str, TrendData] = {}  # trend_id -> trend
        self.category_trends: Dict[str, List[str]] = {}  # category -> list of trend_ids
        logger.info("TrendAnalyzer initialized")
        
    def identify_emerging_trends(self) -> List[TrendData]:
        """
        Identify new and emerging industry trends
        
        Returns list of emerging trends
        """
        logger.info("Identifying emerging trends")
        
        # Placeholder implementation
        # In a real system, this would analyze industry news, research, social media, etc.
        
        # Sample trend categories and names
        trend_categories = {
            "technology": [
                "AI-Powered Personalization", 
                "Voice Search Optimization", 
                "Blockchain for Marketing", 
                "Extended Reality Experiences",
                "Edge Computing Applications"
            ],
            "customer_behavior": [
                "Privacy-First Marketing", 
                "Subscription Economy Growth", 
                "Social Commerce Expansion", 
                "Micro-Moment Marketing",
                "Value-Based Purchasing"
            ],
            "marketing_strategy": [
                "Account-Based Marketing", 
                "Content Atomization", 
                "Interactive Content Experiences", 
                "Community-Led Growth",
                "Hyper-Personalization"
            ],
            "regulatory": [
                "Data Privacy Regulations", 
                "Digital Advertising Restrictions", 
                "Sustainability Reporting Requirements", 
                "Algorithm Transparency Mandates",
                "Consumer Protection Expansion"
            ]
        }
        
        # Generate some emerging trends
        emerging_trends = []
        now = datetime.datetime.now()
        
        for category, trend_names in trend_categories.items():
            # Randomly select 1-2 trends from each category
            num_trends = random.randint(1, 2)
            selected_trends = random.sample(trend_names, num_trends)
            
            for trend_name in selected_trends:
                trend_id = f"trend_{category}_{trend_name.lower().replace(' ', '_')}"
                
                # Skip if we already have this trend
                if trend_id in self.trends:
                    continue
                    
                # Generate trend description
                descriptions = {
                    "technology": f"{trend_name} is transforming how companies engage with customers through advanced technological capabilities.",
                    "customer_behavior": f"{trend_name} represents a significant shift in how customers interact with brands and make purchasing decisions.",
                    "marketing_strategy": f"{trend_name} is changing how marketing teams approach campaign development and customer engagement.",
                    "regulatory": f"{trend_name} is creating new compliance requirements and changing the rules of engagement in digital marketing."
                }
                
                description = descriptions.get(category, f"{trend_name} is an emerging trend in the {category} space.")
                
                # Generate trend data
                trend = TrendData(
                    trend_id=trend_id,
                    name=trend_name,
                    description=description,
                    category=category,
                    strength=random.uniform(0.3, 0.7),  # Moderate strength for emerging trends
                    adoption_rate=random.uniform(0.1, 0.4),  # Low to moderate adoption for emerging trends
                    first_observed=now - datetime.timedelta(days=random.randint(30, 90)),
                    status="emerging",
                    sources=["industry_research", "competitor_analysis", "market_reports"],
                    impact_areas=random.sample(["marketing", "product", "sales", "customer_experience", "operations"], k=random.randint(2, 3))
                )
                
                # Add competitor positions
                for competitor_id in self.competitor_monitor.competitors:
                    # Generate semi-random position based on competitor ID and trend
                    base_position = (hash(competitor_id + trend_id) % 100) / 100
                    position = min(0.8, max(0.1, base_position))  # 0.1 to 0.8 range
                    trend.competitor_positions[competitor_id] = position
                    
                # Calculate strategic importance
                trend.calculate_strategic_importance()
                
                # Store the trend
                self.trends[trend_id] = trend
                
                if category not in self.category_trends:
                    self.category_trends[category] = []
                    
                self.category_trends[category].append(trend_id)
                
                emerging_trends.append(trend)
                
        return emerging_trends
        
    def assess_trend_adoption(self, trend_id: str) -> Dict:
        """
        Assess adoption rate and trajectory of a specific trend
        
        Parameters:
        - trend_id: ID of the trend to assess
        
        Returns adoption assessment
        """
        logger.info(f"Assessing adoption of trend {trend_id}")
        
        trend = self.trends.get(trend_id)
        if not trend:
            logger.warning(f"Trend {trend_id} not found")
            return {}
            
        # Calculate average competitor adoption
        competitor_positions = trend.competitor_positions
        if competitor_positions:
            avg_adoption = sum(competitor_positions.values()) / len(competitor_positions)
            min_adoption = min(competitor_positions.values())
            max_adoption = max(competitor_positions.values())
            adoption_range = max_adoption - min_adoption
        else:
            avg_adoption = 0
            min_adoption = 0
            max_adoption = 0
            adoption_range = 0
            
        # Determine adoption trajectory based on status
        if trend.status == "emerging":
            trajectory = "accelerating"
            projected_adoption_6m = trend.adoption_rate * 1.5
            projected_adoption_12m = trend.adoption_rate * 2.5
        elif trend.status == "growing":
            trajectory = "steady_growth"
            projected_adoption_6m = min(1.0, trend.adoption_rate * 1.3)
            projected_adoption_12m = min(1.0, trend.adoption_rate * 1.7)
        elif trend.status == "mature":
            trajectory = "plateau"
            projected_adoption_6m = min(1.0, trend.adoption_rate * 1.1)
            projected_adoption_12m = min(1.0, trend.adoption_rate * 1.2)
        else:  # declining
            trajectory = "decreasing"
            projected_adoption_6m = trend.adoption_rate * 0.9
            projected_adoption_12m = trend.adoption_rate * 0.7
            
        # Determine adoption stage
        if trend.adoption_rate < 0.2:
            adoption_stage = "early_adopters"
            market_penetration = "low"
        elif trend.adoption_rate < 0.5:
            adoption_stage = "early_majority"
            market_penetration = "medium"
        elif trend.adoption_rate < 0.8:
            adoption_stage = "late_majority"
            market_penetration = "high"
        else:
            adoption_stage = "laggards"
            market_penetration = "very_high"
            
        return {
            "trend_id": trend_id,
            "trend_name": trend.name,
            "current_adoption_rate": trend.adoption_rate,
            "adoption_trajectory": trajectory,
            "adoption_stage": adoption_stage,
            "market_penetration": market_penetration,
            "competitor_adoption": {
                "average": avg_adoption,
                "minimum": min_adoption,
                "maximum": max_adoption,
                "range": adoption_range
            },
            "projections": {
                "6_months": projected_adoption_6m,
                "12_months": projected_adoption_12m
            }
        }
        
    def evaluate_competitor_positioning(self, trend_id: str, competitor_id: str) -> Dict:
        """
        Evaluate a competitor's position relative to a trend
        
        Parameters:
        - trend_id: ID of the trend
        - competitor_id: ID of the competitor
        
        Returns positioning evaluation
        """
        logger.info(f"Evaluating positioning of competitor {competitor_id} for trend {trend_id}")
        
        trend = self.trends.get(trend_id)
        if not trend:
            logger.warning(f"Trend {trend_id} not found")
            return {}
            
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            logger.warning(f"Competitor {competitor_id} not found")
            return {}
            
        # Get competitor's position
        position = trend.competitor_positions.get(competitor_id, 0)
        
        # Get all competitor positions for comparison
        all_positions = list(trend.competitor_positions.values())
        if all_positions:
            avg_position = sum(all_positions) / len(all_positions)
            position_rank = sorted(all_positions, reverse=True).index(position) + 1 if position in all_positions else 0
        else:
            avg_position = 0
            position_rank = 0
            
        # Determine positioning category
        if position > 0.7:
            positioning = "leader"
            description = f"{profile.name} is a leader in adopting and implementing this trend"
        elif position > 0.4:
            positioning = "follower"
            description = f"{profile.name} has made significant progress in adopting this trend"
        elif position > 0.2:
            positioning = "laggard"
            description = f"{profile.name} has begun adopting this trend but lags behind leaders"
        else:
            positioning = "non_adopter"
            description = f"{profile.name} shows little to no adoption of this trend"
            
        # Calculate relative position
        relative_position = position / avg_position if avg_position > 0 else 0
        
        # Determine competitive advantage
        if relative_position > 1.5:
            competitive_advantage = "strong"
        elif relative_position > 1.0:
            competitive_advantage = "moderate"
        elif relative_position > 0.7:
            competitive_advantage = "neutral"
        else:
            competitive_advantage = "disadvantage"
            
        return {
            "trend_id": trend_id,
            "trend_name": trend.name,
            "competitor_id": competitor_id,
            "competitor_name": profile.name,
            "adoption_level": position,
            "positioning": positioning,
            "description": description,
            "relative_to_average": relative_position,
            "competitive_advantage": competitive_advantage,
            "rank": position_rank,
            "total_competitors": len(all_positions)
        }
        
    def recommend_trend_responses(self, trend_id: str) -> Dict:
        """
        Recommend strategic responses to a trend
        
        Parameters:
        - trend_id: ID of the trend
        
        Returns response recommendations
        """
        logger.info(f"Recommending responses for trend {trend_id}")
        
        trend = self.trends.get(trend_id)
        if not trend:
            logger.warning(f"Trend {trend_id} not found")
            return {}
            
        # Determine response urgency based on trend characteristics
        if trend.status == "emerging" and trend.strength > 0.5:
            urgency = "high"
            timeframe = "immediate"
        elif trend.status == "growing" or (trend.status == "emerging" and trend.strength > 0.3):
            urgency = "medium"
            timeframe = "near_term"
        else:
            urgency = "low"
            timeframe = "long_term"
            
        # Generate recommendations based on trend category
        if trend.category == "technology":
            recommendations = [
                "Evaluate technology adoption roadmap",
                "Conduct pilot implementation",
                "Develop expertise through training or hiring",
                "Monitor competitor implementations"
            ]
            response_type = "technology_adoption"
        elif trend.category == "customer_behavior":
            recommendations = [
                "Update customer personas and journey maps",
                "Adapt marketing messaging",
                "Modify product features to align with new behaviors",
                "Conduct customer research to validate impact"
            ]
            response_type = "customer_strategy"
        elif trend.category == "marketing_strategy":
            recommendations = [
                "Pilot new marketing approach",
                "Reallocate marketing budget",
                "Develop new content strategy",
                "Train marketing team on new methodologies"
            ]
            response_type = "marketing_adaptation"
        else:  # regulatory
            recommendations = [
                "Conduct compliance assessment",
                "Update policies and procedures",
                "Implement necessary technical changes",
                "Monitor regulatory developments"
            ]
            response_type = "compliance"
            
        # Select subset of recommendations based on trend strength
        num_recommendations = max(2, min(4, int(trend.strength * 5)))
        selected_recommendations = recommendations[:num_recommendations]
        
        # Determine resource requirements
        if trend.strategic_importance > 0.7:
            resource_level = "significant"
        elif trend.strategic_importance > 0.4:
            resource_level = "moderate"
        else:
            resource_level = "minimal"
            
        return {
            "trend_id": trend_id,
            "trend_name": trend.name,
            "response_urgency": urgency,
            "timeframe": timeframe,
            "response_type": response_type,
            "strategic_importance": trend.strategic_importance,
            "recommendations": selected_recommendations,
            "resource_requirements": resource_level,
            "impact_areas": trend.impact_areas
        }
        
    def update_trend_status(self, trend_id: str, new_status: str) -> bool:
        """
        Update the status of a trend
        
        Parameters:
        - trend_id: ID of the trend to update
        - new_status: New status (emerging, growing, mature, declining)
        
        Returns success flag
        """
        logger.info(f"Updating trend {trend_id} status to {new_status}")
        
        trend = self.trends.get(trend_id)
        if not trend:
            logger.warning(f"Trend {trend_id} not found")
            return False
            
        valid_statuses = ["emerging", "growing", "mature", "declining"]
        if new_status not in valid_statuses:
            logger.warning(f"Invalid status: {new_status}")
            return False
            
        trend.update_status(new_status)
        
        # Update adoption rate based on new status
        if new_status == "growing":
            trend.adoption_rate = min(0.7, trend.adoption_rate * 1.5)
        elif new_status == "mature":
            trend.adoption_rate = min(0.9, trend.adoption_rate * 1.2)
        elif new_status == "declining":
            trend.adoption_rate = min(0.95, trend.adoption_rate)
            
        # Recalculate strategic importance
        trend.calculate_strategic_importance()
        
        return True
        
    def get_trends_by_category(self, category: Optional[str] = None) -> List[TrendData]:
        """
        Get trends filtered by category
        
        Parameters:
        - category: Optional category to filter by
        
        Returns list of trends
        """
        logger.info(f"Getting trends{f' for category {category}' if category else ''}")
        
        if category:
            trend_ids = self.category_trends.get(category, [])
            return [self.trends[tid] for tid in trend_ids if tid in self.trends]
        else:
            return list(self.trends.values())
            
    def get_trends_by_status(self, status: str) -> List[TrendData]:
        """
        Get trends filtered by status
        
        Parameters:
        - status: Status to filter by (emerging, growing, mature, declining)
        
        Returns list of trends
        """
        logger.info(f"Getting trends with status {status}")
        
        return [trend for trend in self.trends.values() if trend.status == status]
        
    def get_trends_by_importance(self, min_importance: float = 0.7) -> List[TrendData]:
        """
        Get high-importance trends
        
        Parameters:
        - min_importance: Minimum strategic importance threshold
        
        Returns list of important trends
        """
        logger.info(f"Getting high-importance trends (min={min_importance})")
        
        important_trends = [
            trend for trend in self.trends.values()
            if trend.strategic_importance >= min_importance
        ]
        
        # Sort by importance (highest first)
        important_trends.sort(key=lambda t: t.strategic_importance, reverse=True)
        
        return important_trends
        
    def identify_trend_gaps(self) -> List[Dict]:
        """
        Identify gaps in trend adoption compared to competitors
        
        Returns list of trend adoption gaps
        """
        logger.info("Identifying trend adoption gaps")
        
        gaps = []
        
        for trend_id, trend in self.trends.items():
            # Skip low-importance trends
            if trend.strategic_importance < 0.4:
                continue
                
            # Get competitor positions
            positions = trend.competitor_positions
            if not positions:
                continue
                
            # Calculate average and max adoption
            avg_adoption = sum(positions.values()) / len(positions)
            max_adoption = max(positions.values())
            
            # Identify competitors with significant gaps
            for competitor_id, position in positions.items():
                # Skip if position is close to or above average
                if position >= avg_adoption * 0.8:
                    continue
                    
                # Calculate gap
                gap_to_avg = avg_adoption - position
                gap_to_leader = max_adoption - position
                
                # Only report significant gaps
                if gap_to_avg > 0.2 or gap_to_leader > 0.3:
                    profile = self.competitor_monitor.competitors.get(competitor_id)
                    competitor_name = profile.name if profile else competitor_id
                    
                    gaps.append({
                        "trend_id": trend_id,
                        "trend_name": trend.name,
                        "competitor_id": competitor_id,
                        "competitor_name": competitor_name,
                        "competitor_position": position,
                        "average_position": avg_adoption,
                        "leader_position": max_adoption,
                        "gap_to_average": gap_to_avg,
                        "gap_to_leader": gap_to_leader,
                        "strategic_importance": trend.strategic_importance
                    })
                    
        # Sort by strategic importance and gap size
        gaps.sort(key=lambda g: (g["strategic_importance"], g["gap_to_leader"]), reverse=True)
        
        return gaps
        
    def run_trend_analysis(self) -> Dict:
        """
        Run a complete trend analysis cycle
        
        Returns analysis results
        """
        logger.info("Running complete trend analysis cycle")
        
        # Identify new trends
        new_trends = self.identify_emerging_trends()
        
        # Update existing trends
        for trend in self.trends.values():
            # Update status based on time since first observed
            days_since_first = (datetime.datetime.now() - trend.first_observed).days
            
            if trend.status == "emerging" and days_since_first > 180:
                self.update_trend_status(trend.trend_id, "growing")
            elif trend.status == "growing" and days_since_first > 365:
                self.update_trend_status(trend.trend_id, "mature")
            elif trend.status == "mature" and days_since_first > 730:
                # 50% chance of becoming declining after 2 years of maturity
                if random.random() > 0.5:
                    self.update_trend_status(trend.trend_id, "declining")
                    
        # Get trends by status
        emerging = self.get_trends_by_status("emerging")
        growing = self.get_trends_by_status("growing")
        mature = self.get_trends_by_status("mature")
        declining = self.get_trends_by_status("declining")
        
        # Get important trends
        important = self.get_trends_by_importance()
        
        # Identify gaps
        gaps = self.identify_trend_gaps()
        
        return {
            "new_trends": len(new_trends),
            "total_trends": len(self.trends),
            "by_status": {
                "emerging": len(emerging),
                "growing": len(growing),
                "mature": len(mature),
                "declining": len(declining)
            },
            "important_trends": len(important),
            "adoption_gaps": len(gaps)
        }
