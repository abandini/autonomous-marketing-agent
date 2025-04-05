"""
AI-Powered Competitive Analysis

This module provides tools for sentiment analysis, pattern recognition,
predictive modeling, and trend analysis of competitive intelligence.
"""

import logging
import json
import datetime
import random
import math
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass

from .monitoring import CompetitorMonitor, CompetitorProfile

logger = logging.getLogger(__name__)

@dataclass
class SentimentData:
    """Data structure for sentiment analysis results"""
    competitor_id: str
    source: str  # social, news, customer_feedback, etc.
    sentiment_score: float  # -1.0 to 1.0
    volume: int  # number of mentions/data points
    keywords: List[str]
    timestamp: datetime.datetime
    
@dataclass
class PatternData:
    """Data structure for detected patterns"""
    pattern_id: str
    name: str
    description: str
    competitors: List[str]
    confidence: float  # 0.0 to 1.0
    occurrences: List[Dict]
    first_detected: datetime.datetime
    last_detected: datetime.datetime
    status: str = "active"  # active, fading, inactive
    
@dataclass
class PredictionData:
    """Data structure for competitor action predictions"""
    prediction_id: str
    competitor_id: str
    action_type: str  # price_change, product_launch, marketing_campaign, etc.
    description: str
    probability: float  # 0.0 to 1.0
    estimated_timing: Dict[str, datetime.datetime]  # min, max, expected
    estimated_impact: Dict[str, float]
    confidence: float  # 0.0 to 1.0
    created_at: datetime.datetime
    triggers: List[str] = None
    
    def __post_init__(self):
        if self.triggers is None:
            self.triggers = []
            
@dataclass
class TrendData:
    """Data structure for market trends"""
    trend_id: str
    name: str
    description: str
    category: str  # technology, customer_behavior, regulatory, etc.
    strength: float  # 0.0 to 1.0
    adoption_rate: float  # 0.0 to 1.0
    competitor_positions: Dict[str, float]  # competitor_id -> adoption level
    first_observed: datetime.datetime
    last_updated: datetime.datetime
    status: str = "emerging"  # emerging, growing, mature, declining
    sources: List[str] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []


class SentimentAnalyzer:
    """
    Sentiment Analysis
    
    Analyzes sentiment in competitor communications, social media, and customer feedback
    to identify trends and significant shifts.
    """
    
    def __init__(self, competitor_monitor: CompetitorMonitor):
        """Initialize with reference to competitor monitor"""
        self.competitor_monitor = competitor_monitor
        self.sentiment_data: Dict[str, List[SentimentData]] = {}  # competitor_id -> list of sentiment data
        self.sentiment_alerts: List[Dict] = []
        self.sources = ["social", "news", "customer_feedback", "product_reviews", "investor_relations"]
        logger.info("SentimentAnalyzer initialized")
        
    def analyze_social_sentiment(self, competitor_id: str) -> List[SentimentData]:
        """
        Analyze sentiment in competitor social media
        
        Parameters:
        - competitor_id: ID of the competitor to analyze
        
        Returns list of sentiment data points
        """
        logger.info(f"Analyzing social sentiment for competitor {competitor_id}")
        
        # Placeholder implementation
        # In a real system, this would connect to social media APIs and use NLP
        
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            logger.warning(f"Competitor {competitor_id} not found")
            return []
            
        now = datetime.datetime.now()
        sentiment_points = []
        
        # Generate some sample data for different platforms
        platforms = ["twitter", "linkedin", "facebook"]
        
        for platform in platforms:
            # Generate semi-random sentiment based on competitor ID and platform
            base_sentiment = (hash(competitor_id + platform) % 100 - 50) / 100  # -0.5 to 0.5
            
            # Add some randomness
            sentiment = max(-1.0, min(1.0, base_sentiment + (random.random() * 0.4 - 0.2)))
            
            # Volume depends on platform
            if platform == "twitter":
                volume = 50 + (hash(competitor_id) % 200)
            elif platform == "linkedin":
                volume = 20 + (hash(competitor_id) % 80)
            else:
                volume = 30 + (hash(competitor_id) % 100)
                
            # Generate some relevant keywords
            keywords = ["product", "service", "customer", "quality", "price"]
            selected_keywords = random.sample(keywords, min(3, len(keywords)))
            
            sentiment_data = SentimentData(
                competitor_id=competitor_id,
                source=f"social_{platform}",
                sentiment_score=sentiment,
                volume=volume,
                keywords=selected_keywords,
                timestamp=now
            )
            
            sentiment_points.append(sentiment_data)
            
        # Store the data
        if competitor_id not in self.sentiment_data:
            self.sentiment_data[competitor_id] = []
            
        self.sentiment_data[competitor_id].extend(sentiment_points)
        
        return sentiment_points
        
    def analyze_news_sentiment(self, competitor_id: str) -> List[SentimentData]:
        """
        Analyze sentiment in news articles about the competitor
        
        Parameters:
        - competitor_id: ID of the competitor to analyze
        
        Returns list of sentiment data points
        """
        logger.info(f"Analyzing news sentiment for competitor {competitor_id}")
        
        # Placeholder implementation
        # In a real system, this would connect to news APIs and use NLP
        
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            logger.warning(f"Competitor {competitor_id} not found")
            return []
            
        now = datetime.datetime.now()
        
        # Generate semi-random sentiment
        base_sentiment = (hash(competitor_id + "news") % 100 - 40) / 100  # -0.4 to 0.6
        sentiment = max(-1.0, min(1.0, base_sentiment + (random.random() * 0.4 - 0.2)))
        
        # News volume
        volume = 10 + (hash(competitor_id) % 40)
        
        # Generate some relevant keywords
        keywords = ["announcement", "results", "launch", "partnership", "industry"]
        selected_keywords = random.sample(keywords, min(3, len(keywords)))
        
        sentiment_data = SentimentData(
            competitor_id=competitor_id,
            source="news",
            sentiment_score=sentiment,
            volume=volume,
            keywords=selected_keywords,
            timestamp=now
        )
        
        # Store the data
        if competitor_id not in self.sentiment_data:
            self.sentiment_data[competitor_id] = []
            
        self.sentiment_data[competitor_id].append(sentiment_data)
        
        return [sentiment_data]
        
    def analyze_customer_feedback(self, competitor_id: str) -> List[SentimentData]:
        """
        Analyze sentiment in customer feedback about the competitor
        
        Parameters:
        - competitor_id: ID of the competitor to analyze
        
        Returns list of sentiment data points
        """
        logger.info(f"Analyzing customer feedback sentiment for competitor {competitor_id}")
        
        # Placeholder implementation
        # In a real system, this would analyze review sites, support forums, etc.
        
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            logger.warning(f"Competitor {competitor_id} not found")
            return []
            
        now = datetime.datetime.now()
        sentiment_points = []
        
        # Generate sample data for different feedback sources
        sources = ["product_reviews", "support_forums", "app_store"]
        
        for source in sources:
            # Generate semi-random sentiment
            base_sentiment = (hash(competitor_id + source) % 100 - 30) / 100  # -0.3 to 0.7
            sentiment = max(-1.0, min(1.0, base_sentiment + (random.random() * 0.4 - 0.2)))
            
            # Volume depends on source
            if source == "product_reviews":
                volume = 100 + (hash(competitor_id) % 300)
            elif source == "support_forums":
                volume = 50 + (hash(competitor_id) % 150)
            else:
                volume = 200 + (hash(competitor_id) % 500)
                
            # Generate some relevant keywords
            keywords = ["usability", "reliability", "support", "features", "value"]
            selected_keywords = random.sample(keywords, min(3, len(keywords)))
            
            sentiment_data = SentimentData(
                competitor_id=competitor_id,
                source=f"customer_{source}",
                sentiment_score=sentiment,
                volume=volume,
                keywords=selected_keywords,
                timestamp=now
            )
            
            sentiment_points.append(sentiment_data)
            
        # Store the data
        if competitor_id not in self.sentiment_data:
            self.sentiment_data[competitor_id] = []
            
        self.sentiment_data[competitor_id].extend(sentiment_points)
        
        return sentiment_points
        
    def detect_sentiment_shifts(self, competitor_id: str, threshold: float = 0.2) -> List[Dict]:
        """
        Detect significant shifts in sentiment
        
        Parameters:
        - competitor_id: ID of the competitor to analyze
        - threshold: Minimum change to be considered significant
        
        Returns list of detected shifts
        """
        logger.info(f"Detecting sentiment shifts for competitor {competitor_id}")
        
        # Get sentiment data for the competitor
        sentiment_points = self.sentiment_data.get(competitor_id, [])
        if len(sentiment_points) < 2:
            logger.warning(f"Insufficient sentiment data for competitor {competitor_id}")
            return []
            
        # Group by source
        by_source = {}
        for point in sentiment_points:
            source_type = point.source.split('_')[0]  # Extract main source type
            if source_type not in by_source:
                by_source[source_type] = []
            by_source[source_type].append(point)
            
        # Sort each group by timestamp
        for source_type in by_source:
            by_source[source_type].sort(key=lambda x: x.timestamp)
            
        # Detect shifts
        shifts = []
        
        for source_type, points in by_source.items():
            if len(points) < 2:
                continue
                
            # Compare most recent to previous
            current = points[-1]
            previous = points[-2]
            
            change = current.sentiment_score - previous.sentiment_score
            
            if abs(change) >= threshold:
                shift = {
                    "competitor_id": competitor_id,
                    "source": source_type,
                    "previous_sentiment": previous.sentiment_score,
                    "current_sentiment": current.sentiment_score,
                    "change": change,
                    "previous_date": previous.timestamp,
                    "current_date": current.timestamp,
                    "significance": abs(change) / 2  # 0.0 to 1.0 scale
                }
                
                shifts.append(shift)
                
                # Create alert for significant shifts
                if abs(change) >= threshold * 1.5:
                    alert = {
                        "type": "sentiment_shift",
                        "competitor_id": competitor_id,
                        "description": f"Significant {source_type} sentiment shift of {change:.2f} detected",
                        "data": shift,
                        "timestamp": datetime.datetime.now()
                    }
                    
                    self.sentiment_alerts.append(alert)
                    
        return shifts
        
    def compare_competitor_sentiment(self) -> Dict[str, Dict]:
        """
        Compare sentiment across competitors
        
        Returns comparative sentiment analysis
        """
        logger.info("Comparing sentiment across competitors")
        
        # Get all competitors with sentiment data
        competitors_with_data = {}
        for competitor_id, points in self.sentiment_data.items():
            if points:
                profile = self.competitor_monitor.competitors.get(competitor_id)
                if profile:
                    competitors_with_data[competitor_id] = profile
                    
        if not competitors_with_data:
            logger.warning("No sentiment data available for comparison")
            return {}
            
        # Calculate average sentiment by source for each competitor
        comparison = {}
        
        for competitor_id, profile in competitors_with_data.items():
            points = self.sentiment_data[competitor_id]
            
            # Group by source
            by_source = {}
            for point in points:
                source_type = point.source.split('_')[0]  # Extract main source type
                if source_type not in by_source:
                    by_source[source_type] = []
                by_source[source_type].append(point)
                
            # Calculate averages
            averages = {}
            for source_type, source_points in by_source.items():
                if not source_points:
                    continue
                    
                total_sentiment = sum(p.sentiment_score * p.volume for p in source_points)
                total_volume = sum(p.volume for p in source_points)
                
                if total_volume > 0:
                    averages[source_type] = {
                        "sentiment": total_sentiment / total_volume,
                        "volume": total_volume,
                        "data_points": len(source_points)
                    }
                    
            # Calculate overall average
            all_points = points
            total_sentiment = sum(p.sentiment_score * p.volume for p in all_points)
            total_volume = sum(p.volume for p in all_points)
            
            if total_volume > 0:
                averages["overall"] = {
                    "sentiment": total_sentiment / total_volume,
                    "volume": total_volume,
                    "data_points": len(all_points)
                }
                
            comparison[competitor_id] = {
                "name": profile.name,
                "sentiment": averages
            }
            
        # Add rankings
        if comparison:
            # Rank by overall sentiment
            competitors_by_sentiment = sorted(
                [(cid, data["sentiment"].get("overall", {}).get("sentiment", 0)) 
                 for cid, data in comparison.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            for rank, (cid, _) in enumerate(competitors_by_sentiment, 1):
                if cid in comparison and "sentiment" in comparison[cid] and "overall" in comparison[cid]["sentiment"]:
                    comparison[cid]["sentiment"]["overall"]["rank"] = rank
                    
        return comparison
        
    def run_sentiment_analysis(self) -> Dict:
        """
        Run a complete sentiment analysis cycle for all competitors
        
        Returns sentiment analysis results
        """
        logger.info("Running complete sentiment analysis cycle")
        
        results = {}
        
        for competitor_id in self.competitor_monitor.competitors:
            # Run all analysis types
            social_data = self.analyze_social_sentiment(competitor_id)
            news_data = self.analyze_news_sentiment(competitor_id)
            feedback_data = self.analyze_customer_feedback(competitor_id)
            
            # Detect shifts
            shifts = self.detect_sentiment_shifts(competitor_id)
            
            results[competitor_id] = {
                "social_data_points": len(social_data),
                "news_data_points": len(news_data),
                "feedback_data_points": len(feedback_data),
                "detected_shifts": shifts
            }
            
        # Compare across competitors
        comparison = self.compare_competitor_sentiment()
        
        return {
            "competitor_results": results,
            "comparison": comparison,
            "alerts": self.sentiment_alerts
        }
        
    def get_sentiment_trends(self, competitor_id: str, source_type: Optional[str] = None, 
                            days: int = 90) -> Dict:
        """
        Get sentiment trends over time
        
        Parameters:
        - competitor_id: ID of the competitor
        - source_type: Optional source type to filter by
        - days: Number of days to include
        
        Returns sentiment trend data
        """
        logger.info(f"Getting sentiment trends for competitor {competitor_id}")
        
        # Get sentiment data for the competitor
        all_points = self.sentiment_data.get(competitor_id, [])
        
        # Filter by date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        points = [p for p in all_points if p.timestamp >= cutoff_date]
        
        # Filter by source type if specified
        if source_type:
            points = [p for p in points if p.source.startswith(source_type)]
            
        if not points:
            logger.warning(f"No sentiment data found for the specified criteria")
            return {}
            
        # Group by week
        weeks = {}
        for point in points:
            # Get week number
            week_num = point.timestamp.isocalendar()[1]
            year = point.timestamp.year
            week_key = f"{year}-W{week_num:02d}"
            
            if week_key not in weeks:
                weeks[week_key] = []
                
            weeks[week_key].append(point)
            
        # Calculate weekly averages
        trend_data = []
        
        for week_key, week_points in sorted(weeks.items()):
            total_sentiment = sum(p.sentiment_score * p.volume for p in week_points)
            total_volume = sum(p.volume for p in week_points)
            
            if total_volume > 0:
                trend_data.append({
                    "period": week_key,
                    "sentiment": total_sentiment / total_volume,
                    "volume": total_volume,
                    "data_points": len(week_points)
                })
                
        # Calculate overall statistics
        if trend_data:
            overall_sentiment = sum(d["sentiment"] * d["volume"] for d in trend_data) / sum(d["volume"] for d in trend_data)
            min_sentiment = min(d["sentiment"] for d in trend_data)
            max_sentiment = max(d["sentiment"] for d in trend_data)
            
            # Calculate trend direction
            if len(trend_data) >= 2:
                first_half = trend_data[:len(trend_data)//2]
                second_half = trend_data[len(trend_data)//2:]
                
                first_avg = sum(d["sentiment"] * d["volume"] for d in first_half) / sum(d["volume"] for d in first_half)
                second_avg = sum(d["sentiment"] * d["volume"] for d in second_half) / sum(d["volume"] for d in second_half)
                
                trend_direction = second_avg - first_avg
            else:
                trend_direction = 0
                
            return {
                "competitor_id": competitor_id,
                "source_type": source_type or "all",
                "days": days,
                "overall_sentiment": overall_sentiment,
                "min_sentiment": min_sentiment,
                "max_sentiment": max_sentiment,
                "trend_direction": trend_direction,
                "trend_data": trend_data
            }
            
        return {}
