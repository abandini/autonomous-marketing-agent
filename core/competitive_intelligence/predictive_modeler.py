"""
Predictive Modeling for Competitive Intelligence

This module provides tools for predicting competitor actions based on
historical patterns and data analysis.
"""

import logging
import json
import datetime
import random
import math
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field

from .monitoring import CompetitorMonitor
from .pattern_recognizer import PatternRecognizer, PatternData

logger = logging.getLogger(__name__)

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
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    triggers: List[str] = field(default_factory=list)
    source_patterns: List[str] = field(default_factory=list)
    status: str = "active"  # active, occurred, invalidated
    actual_occurrence: Optional[datetime.datetime] = None
    
    def update_probability(self, new_probability: float):
        """Update the prediction probability"""
        self.probability = new_probability
        self.updated_at = datetime.datetime.now()
        
    def mark_as_occurred(self, occurrence_date: datetime.datetime):
        """Mark prediction as having occurred"""
        self.status = "occurred"
        self.actual_occurrence = occurrence_date
        self.updated_at = datetime.datetime.now()
        
    def invalidate(self):
        """Mark prediction as invalidated"""
        self.status = "invalidated"
        self.updated_at = datetime.datetime.now()


class PredictiveModeler:
    """
    Predictive Modeling
    
    Forecasts competitor actions based on historical patterns and data analysis.
    """
    
    def __init__(self, competitor_monitor: CompetitorMonitor, pattern_recognizer: PatternRecognizer):
        """Initialize with references to other components"""
        self.competitor_monitor = competitor_monitor
        self.pattern_recognizer = pattern_recognizer
        self.predictions: Dict[str, PredictionData] = {}  # prediction_id -> prediction
        self.competitor_predictions: Dict[str, List[str]] = {}  # competitor_id -> list of prediction_ids
        logger.info("PredictiveModeler initialized")
        
    def predict_next_actions(self, competitor_id: str) -> List[PredictionData]:
        """
        Predict likely next actions for a competitor
        
        Parameters:
        - competitor_id: ID of the competitor to analyze
        
        Returns list of predictions
        """
        logger.info(f"Predicting next actions for competitor {competitor_id}")
        
        # Get competitor profile
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            logger.warning(f"Competitor {competitor_id} not found")
            return []
            
        # Get active patterns for the competitor
        patterns = self.pattern_recognizer.get_active_patterns(competitor_id)
        
        if not patterns:
            logger.warning(f"No active patterns found for competitor {competitor_id}")
            return []
            
        # Generate predictions based on patterns
        new_predictions = []
        
        for pattern in patterns:
            # Skip patterns without expected next occurrence
            if not pattern.expected_next_occurrence:
                continue
                
            # Generate prediction based on pattern type
            if pattern.pattern_type == "pricing":
                prediction = self._predict_pricing_action(competitor_id, pattern)
                if prediction:
                    new_predictions.append(prediction)
                    
            elif pattern.pattern_type == "release":
                prediction = self._predict_product_release(competitor_id, pattern)
                if prediction:
                    new_predictions.append(prediction)
                    
            elif pattern.pattern_type == "marketing":
                prediction = self._predict_marketing_campaign(competitor_id, pattern)
                if prediction:
                    new_predictions.append(prediction)
                    
            elif pattern.pattern_type == "seasonal":
                prediction = self._predict_seasonal_activity(competitor_id, pattern)
                if prediction:
                    new_predictions.append(prediction)
                    
        # Store and return predictions
        for prediction in new_predictions:
            self.predictions[prediction.prediction_id] = prediction
            
            if competitor_id not in self.competitor_predictions:
                self.competitor_predictions[competitor_id] = []
                
            if prediction.prediction_id not in self.competitor_predictions[competitor_id]:
                self.competitor_predictions[competitor_id].append(prediction.prediction_id)
                
        return new_predictions
        
    def _predict_pricing_action(self, competitor_id: str, pattern: PatternData) -> Optional[PredictionData]:
        """Generate pricing action prediction based on pattern"""
        # Get competitor profile
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            return None
            
        # Check if we already have an active prediction for this pattern
        for pred_id in self.competitor_predictions.get(competitor_id, []):
            pred = self.predictions.get(pred_id)
            if (pred and pred.status == "active" and 
                "price" in pred.action_type and 
                pattern.pattern_id in pred.source_patterns):
                return pred
                
        # Generate new prediction
        prediction_id = f"pred_price_{competitor_id}_{pattern.pattern_id[-8:]}"
        
        # Determine action type and details based on pattern name
        if "seasonal" in pattern.name.lower():
            action_type = "price_discount"
            description = f"Seasonal price discount from {profile.name}"
            impact_range = (0.1, 0.25)  # 10-25% discount
        elif "response" in pattern.name.lower():
            action_type = "price_adjustment"
            description = f"Competitive price adjustment from {profile.name}"
            impact_range = (-0.1, 0.1)  # -10% to +10% change
        else:
            action_type = "price_increase"
            description = f"Price increase from {profile.name}"
            impact_range = (0.03, 0.08)  # 3-8% increase
            
        # Estimate timing
        expected_date = pattern.expected_next_occurrence
        min_date = expected_date - datetime.timedelta(days=7)
        max_date = expected_date + datetime.timedelta(days=7)
        
        # Estimate impact
        impact_value = random.uniform(impact_range[0], impact_range[1])
        market_share_impact = impact_value * -2 if impact_value > 0 else impact_value * -1
        revenue_impact = impact_value * -1.5 if impact_value > 0 else impact_value * -0.5
        
        # Create prediction
        prediction = PredictionData(
            prediction_id=prediction_id,
            competitor_id=competitor_id,
            action_type=action_type,
            description=description,
            probability=pattern.confidence * 0.9,  # Slightly lower than pattern confidence
            estimated_timing={
                "min": min_date,
                "max": max_date,
                "expected": expected_date
            },
            estimated_impact={
                "price_change": impact_value,
                "market_share_impact": market_share_impact,
                "revenue_impact": revenue_impact
            },
            confidence=pattern.confidence * 0.8,
            source_patterns=[pattern.pattern_id]
        )
        
        return prediction
        
    def _predict_product_release(self, competitor_id: str, pattern: PatternData) -> Optional[PredictionData]:
        """Generate product release prediction based on pattern"""
        # Get competitor profile
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            return None
            
        # Check if we already have an active prediction for this pattern
        for pred_id in self.competitor_predictions.get(competitor_id, []):
            pred = self.predictions.get(pred_id)
            if (pred and pred.status == "active" and 
                "release" in pred.action_type and 
                pattern.pattern_id in pred.source_patterns):
                return pred
                
        # Generate new prediction
        prediction_id = f"pred_release_{competitor_id}_{pattern.pattern_id[-8:]}"
        
        # Determine if this is likely to be a major or minor release
        is_major = random.random() < 0.3  # 30% chance of major release
        
        if is_major:
            action_type = "major_product_release"
            description = f"Major product release from {profile.name}"
            impact_factor = 1.5
        else:
            action_type = "minor_product_release"
            description = f"Minor product/feature release from {profile.name}"
            impact_factor = 0.7
            
        # Estimate timing
        expected_date = pattern.expected_next_occurrence
        min_date = expected_date - datetime.timedelta(days=10)
        max_date = expected_date + datetime.timedelta(days=14)
        
        # Estimate impact
        market_share_impact = random.uniform(0.01, 0.05) * impact_factor
        revenue_impact = random.uniform(0.02, 0.08) * impact_factor
        
        # Create prediction
        prediction = PredictionData(
            prediction_id=prediction_id,
            competitor_id=competitor_id,
            action_type=action_type,
            description=description,
            probability=pattern.confidence * 0.85,
            estimated_timing={
                "min": min_date,
                "max": max_date,
                "expected": expected_date
            },
            estimated_impact={
                "market_share_impact": market_share_impact,
                "revenue_impact": revenue_impact,
                "customer_churn_risk": market_share_impact * 0.7
            },
            confidence=pattern.confidence * 0.75,
            source_patterns=[pattern.pattern_id]
        )
        
        return prediction
        
    def _predict_marketing_campaign(self, competitor_id: str, pattern: PatternData) -> Optional[PredictionData]:
        """Generate marketing campaign prediction based on pattern"""
        # Get competitor profile
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            return None
            
        # Check if we already have an active prediction for this pattern
        for pred_id in self.competitor_predictions.get(competitor_id, []):
            pred = self.predictions.get(pred_id)
            if (pred and pred.status == "active" and 
                "marketing" in pred.action_type and 
                pattern.pattern_id in pred.source_patterns):
                return pred
                
        # Generate new prediction
        prediction_id = f"pred_marketing_{competitor_id}_{pattern.pattern_id[-8:]}"
        
        # Determine campaign type based on pattern name
        if "event" in pattern.name.lower():
            action_type = "event_marketing"
            description = f"Event-based marketing campaign from {profile.name}"
            impact_factor = 1.2
        elif "quarterly" in pattern.name.lower():
            action_type = "quarterly_marketing"
            description = f"Quarterly marketing campaign from {profile.name}"
            impact_factor = 1.0
        else:
            action_type = "response_marketing"
            description = f"Responsive marketing campaign from {profile.name}"
            impact_factor = 0.8
            
        # Estimate timing
        expected_date = pattern.expected_next_occurrence
        min_date = expected_date - datetime.timedelta(days=5)
        max_date = expected_date + datetime.timedelta(days=10)
        
        # Estimate impact
        market_share_impact = random.uniform(0.01, 0.03) * impact_factor
        brand_awareness_impact = random.uniform(0.05, 0.15) * impact_factor
        
        # Create prediction
        prediction = PredictionData(
            prediction_id=prediction_id,
            competitor_id=competitor_id,
            action_type=action_type,
            description=description,
            probability=pattern.confidence * 0.9,
            estimated_timing={
                "min": min_date,
                "max": max_date,
                "expected": expected_date
            },
            estimated_impact={
                "market_share_impact": market_share_impact,
                "brand_awareness_impact": brand_awareness_impact,
                "lead_generation_impact": market_share_impact * 1.5
            },
            confidence=pattern.confidence * 0.8,
            source_patterns=[pattern.pattern_id]
        )
        
        return prediction
        
    def _predict_seasonal_activity(self, competitor_id: str, pattern: PatternData) -> Optional[PredictionData]:
        """Generate seasonal activity prediction based on pattern"""
        # Get competitor profile
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            return None
            
        # Check if we already have an active prediction for this pattern
        for pred_id in self.competitor_predictions.get(competitor_id, []):
            pred = self.predictions.get(pred_id)
            if (pred and pred.status == "active" and 
                "seasonal" in pred.action_type and 
                pattern.pattern_id in pred.source_patterns):
                return pred
                
        # Generate new prediction
        prediction_id = f"pred_seasonal_{competitor_id}_{pattern.pattern_id[-8:]}"
        
        # Determine season type from pattern name
        if "holiday" in pattern.name.lower():
            season_type = "holiday"
        elif "summer" in pattern.name.lower():
            season_type = "summer"
        elif "back-to-school" in pattern.name.lower():
            season_type = "back-to-school"
        else:
            season_type = "year-end"
            
        action_type = f"seasonal_{season_type}_activity"
        description = f"Seasonal {season_type} activity from {profile.name}"
        
        # Estimate timing
        expected_date = pattern.expected_next_occurrence
        min_date = expected_date - datetime.timedelta(days=14)
        max_date = expected_date + datetime.timedelta(days=14)
        
        # Estimate impact
        market_share_impact = random.uniform(0.02, 0.06)
        revenue_impact = random.uniform(0.03, 0.08)
        
        # Create prediction
        prediction = PredictionData(
            prediction_id=prediction_id,
            competitor_id=competitor_id,
            action_type=action_type,
            description=description,
            probability=pattern.confidence * 0.85,
            estimated_timing={
                "min": min_date,
                "max": max_date,
                "expected": expected_date
            },
            estimated_impact={
                "market_share_impact": market_share_impact,
                "revenue_impact": revenue_impact,
                "duration_days": random.randint(30, 60)
            },
            confidence=pattern.confidence * 0.8,
            source_patterns=[pattern.pattern_id]
        )
        
        return prediction
        
    def estimate_action_timing(self, competitor_id: str, action_type: str) -> Dict:
        """
        Estimate when a specific action might occur
        
        Parameters:
        - competitor_id: ID of the competitor
        - action_type: Type of action to estimate timing for
        
        Returns timing estimate
        """
        logger.info(f"Estimating timing for {action_type} by competitor {competitor_id}")
        
        # Get active predictions for this competitor and action type
        relevant_predictions = []
        
        for pred_id in self.competitor_predictions.get(competitor_id, []):
            pred = self.predictions.get(pred_id)
            if pred and pred.status == "active" and action_type in pred.action_type:
                relevant_predictions.append(pred)
                
        if not relevant_predictions:
            logger.warning(f"No relevant predictions found for {action_type} by {competitor_id}")
            return {
                "competitor_id": competitor_id,
                "action_type": action_type,
                "has_estimate": False,
                "reason": "No relevant predictions found"
            }
            
        # Combine estimates from multiple predictions
        min_dates = [pred.estimated_timing["min"] for pred in relevant_predictions]
        max_dates = [pred.estimated_timing["max"] for pred in relevant_predictions]
        expected_dates = [pred.estimated_timing["expected"] for pred in relevant_predictions]
        probabilities = [pred.probability for pred in relevant_predictions]
        
        # Weight by probability
        total_probability = sum(probabilities)
        if total_probability > 0:
            weighted_expected = sum((date.timestamp() * prob) for date, prob in zip(expected_dates, probabilities)) / total_probability
            weighted_expected_date = datetime.datetime.fromtimestamp(weighted_expected)
        else:
            weighted_expected_date = min(expected_dates, key=lambda d: abs((d - datetime.datetime.now()).total_seconds()))
            
        # Get overall min and max
        earliest_date = min(min_dates)
        latest_date = max(max_dates)
        
        # Calculate confidence
        confidence = sum(pred.confidence * pred.probability for pred in relevant_predictions) / total_probability if total_probability > 0 else 0.5
        
        return {
            "competitor_id": competitor_id,
            "action_type": action_type,
            "has_estimate": True,
            "earliest_date": earliest_date,
            "latest_date": latest_date,
            "expected_date": weighted_expected_date,
            "confidence": confidence,
            "based_on_predictions": len(relevant_predictions)
        }
        
    def assess_potential_impact(self, prediction: PredictionData) -> Dict:
        """
        Assess the potential market impact of a predicted action
        
        Parameters:
        - prediction: The prediction to assess
        
        Returns impact assessment
        """
        logger.info(f"Assessing potential impact of prediction {prediction.prediction_id}")
        
        # Get competitor profile
        profile = self.competitor_monitor.competitors.get(prediction.competitor_id)
        if not profile:
            logger.warning(f"Competitor {prediction.competitor_id} not found")
            return {}
            
        # Base impact assessment on prediction's estimated impact
        impact = prediction.estimated_impact.copy()
        
        # Add qualitative assessment
        market_share_impact = impact.get("market_share_impact", 0)
        revenue_impact = impact.get("revenue_impact", 0)
        
        if market_share_impact > 0.03 or revenue_impact > 0.05:
            severity = "high"
            response_urgency = "immediate"
        elif market_share_impact > 0.01 or revenue_impact > 0.02:
            severity = "medium"
            response_urgency = "soon"
        else:
            severity = "low"
            response_urgency = "monitor"
            
        # Add recommended response types
        if "price" in prediction.action_type:
            response_types = ["pricing_strategy", "value_proposition", "bundling"]
        elif "release" in prediction.action_type:
            response_types = ["product_enhancement", "marketing_campaign", "customer_retention"]
        elif "marketing" in prediction.action_type:
            response_types = ["counter_campaign", "sales_enablement", "customer_communication"]
        else:
            response_types = ["strategic_review", "market_positioning", "customer_engagement"]
            
        # Calculate overall business risk
        business_risk = max(market_share_impact * 100, (revenue_impact * 100) / 2)
        
        return {
            "prediction_id": prediction.prediction_id,
            "competitor_id": prediction.competitor_id,
            "competitor_name": profile.name,
            "action_type": prediction.action_type,
            "quantitative_impact": impact,
            "qualitative_assessment": {
                "severity": severity,
                "response_urgency": response_urgency,
                "business_risk_percent": business_risk
            },
            "recommended_response_types": response_types,
            "confidence": prediction.confidence
        }
        
    def get_high_probability_predictions(self, min_probability: float = 0.7) -> List[PredictionData]:
        """
        Get predictions with high probability
        
        Parameters:
        - min_probability: Minimum probability threshold
        
        Returns list of high-probability predictions
        """
        logger.info(f"Getting high-probability predictions (min={min_probability})")
        
        # Filter active predictions by probability
        high_prob_predictions = [
            pred for pred in self.predictions.values()
            if pred.status == "active" and pred.probability >= min_probability
        ]
        
        # Sort by probability (highest first)
        high_prob_predictions.sort(key=lambda p: p.probability, reverse=True)
        
        return high_prob_predictions
        
    def get_upcoming_predictions(self, days_ahead: int = 30) -> List[PredictionData]:
        """
        Get predictions expected to occur soon
        
        Parameters:
        - days_ahead: Number of days to look ahead
        
        Returns list of upcoming predictions
        """
        logger.info(f"Getting upcoming predictions for next {days_ahead} days")
        
        now = datetime.datetime.now()
        cutoff = now + datetime.timedelta(days=days_ahead)
        
        # Filter active predictions by expected timing
        upcoming = [
            pred for pred in self.predictions.values()
            if pred.status == "active" and pred.estimated_timing.get("expected") and
            pred.estimated_timing["expected"] <= cutoff
        ]
        
        # Sort by expected date
        upcoming.sort(key=lambda p: p.estimated_timing["expected"])
        
        return upcoming
        
    def update_prediction_status(self, prediction_id: str, new_status: str, 
                                occurrence_date: Optional[datetime.datetime] = None) -> bool:
        """
        Update the status of a prediction
        
        Parameters:
        - prediction_id: ID of the prediction to update
        - new_status: New status (occurred, invalidated)
        - occurrence_date: Date of occurrence (for occurred status)
        
        Returns success flag
        """
        logger.info(f"Updating prediction {prediction_id} status to {new_status}")
        
        prediction = self.predictions.get(prediction_id)
        if not prediction:
            logger.warning(f"Prediction {prediction_id} not found")
            return False
            
        if new_status == "occurred":
            if not occurrence_date:
                occurrence_date = datetime.datetime.now()
            prediction.mark_as_occurred(occurrence_date)
            return True
        elif new_status == "invalidated":
            prediction.invalidate()
            return True
        else:
            logger.warning(f"Invalid status: {new_status}")
            return False
            
    def run_prediction_cycle(self) -> Dict:
        """
        Run a complete prediction cycle for all competitors
        
        Returns prediction results
        """
        logger.info("Running complete prediction cycle")
        
        results = {}
        all_new_predictions = []
        
        for competitor_id in self.competitor_monitor.competitors:
            # Generate new predictions
            new_predictions = self.predict_next_actions(competitor_id)
            all_new_predictions.extend(new_predictions)
            
            # Get upcoming predictions
            upcoming = [p for p in self.get_upcoming_predictions() if p.competitor_id == competitor_id]
            
            results[competitor_id] = {
                "new_predictions": len(new_predictions),
                "upcoming_predictions": len(upcoming),
                "prediction_types": list(set(p.action_type for p in upcoming))
            }
            
        # Get high probability predictions
        high_prob = self.get_high_probability_predictions()
        
        return {
            "competitor_results": results,
            "total_new_predictions": len(all_new_predictions),
            "high_probability_predictions": len(high_prob),
            "total_active_predictions": len([p for p in self.predictions.values() if p.status == "active"])
        }
