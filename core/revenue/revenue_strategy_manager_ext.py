"""
Enhanced Revenue Strategy Manager Module

This module provides an enhanced version of the Revenue Strategy Manager with
advanced capabilities for strategy evaluation, optimization, and knowledge graph integration.
"""

import os
import json
import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple, Set

from core.revenue.revenue_strategy_manager import RevenueStrategyManager, StrategyType
from core.revenue.revenue_performance_monitor import RevenuePerformanceMonitor
from core.revenue.revenue_knowledge_integration import RevenueKnowledgeIntegration
from core.knowledge_graph.knowledge_graph import MarketingKnowledgeGraph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RevenueStrategy:
    """
    Class representing a revenue strategy.
    
    This class encapsulates all information about a revenue strategy, including
    its type, target channels, segments, and performance metrics.
    """
    
    def __init__(
        self,
        id: str,
        name: str,
        strategy_type: Union[str, StrategyType],
        description: str,
        target_channels: Optional[List[str]] = None,
        target_segments: Optional[List[str]] = None,
        revenue_model: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        is_active: bool = True
    ):
        """
        Initialize a revenue strategy.
        
        Args:
            id: Unique identifier for the strategy
            name: Name of the strategy
            strategy_type: Type of strategy
            description: Detailed description
            target_channels: List of target marketing channels
            target_segments: List of target customer segments
            revenue_model: Revenue model for the strategy
            metrics: Metrics to track for this strategy
            actions: List of actions to implement the strategy
            is_active: Whether the strategy is active
        """
        self.id = id
        self.name = name
        self.strategy_type = strategy_type if isinstance(strategy_type, StrategyType) else self._parse_strategy_type(strategy_type)
        self.description = description
        self.target_channels = target_channels or []
        self.target_segments = target_segments or []
        self.revenue_model = revenue_model
        self.metrics = metrics or {}
        self.actions = actions or []
        self.is_active = is_active
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        
    def _parse_strategy_type(self, strategy_type_str: str) -> StrategyType:
        """
        Parse a strategy type string into a StrategyType enum value.
        
        Args:
            strategy_type_str: String representation of strategy type
            
        Returns:
            StrategyType enum value
        """
        strategy_type_str = strategy_type_str.lower()
        
        if strategy_type_str == StrategyType.ACQUISITION:
            return StrategyType.ACQUISITION
        elif strategy_type_str == StrategyType.RETENTION:
            return StrategyType.RETENTION
        elif strategy_type_str == StrategyType.EXPANSION:
            return StrategyType.EXPANSION
        elif strategy_type_str == StrategyType.MONETIZATION:
            return StrategyType.MONETIZATION
        elif strategy_type_str == StrategyType.PRICING:
            return StrategyType.PRICING
        elif strategy_type_str == StrategyType.BUNDLING:
            return StrategyType.BUNDLING
        elif strategy_type_str == StrategyType.CROSS_SELLING:
            return StrategyType.CROSS_SELLING
        elif strategy_type_str == StrategyType.UP_SELLING:
            return StrategyType.UP_SELLING
        elif strategy_type_str == StrategyType.FREEMIUM:
            return StrategyType.FREEMIUM
        elif strategy_type_str == StrategyType.SUBSCRIPTION:
            return StrategyType.SUBSCRIPTION
        else:
            logger.warning(f"Unknown strategy type: {strategy_type_str}, defaulting to ACQUISITION")
            return StrategyType.ACQUISITION
            
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the strategy to a dictionary representation.
        
        Returns:
            Dictionary representation of the strategy
        """
        return {
            "id": self.id,
            "name": self.name,
            "strategy_type": self.strategy_type if isinstance(self.strategy_type, str) else self.strategy_type.__dict__,
            "description": self.description,
            "target_channels": self.target_channels,
            "target_segments": self.target_segments,
            "revenue_model": self.revenue_model,
            "metrics": self.metrics,
            "actions": self.actions,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "last_updated": self.last_updated.isoformat() if isinstance(self.last_updated, datetime) else self.last_updated
        }

class StrategyPerformanceMetrics:
    """Class to track and analyze strategy performance metrics."""
    
    def __init__(self, strategy_id: str, name: str):
        """
        Initialize strategy performance metrics.
        
        Args:
            strategy_id: ID of the strategy
            name: Name of the strategy
        """
        self.strategy_id = strategy_id
        self.name = name
        self.metrics_history = []
        self.roi = 0.0
        self.conversion_rate = 0.0
        self.cost_per_acquisition = 0.0
        self.revenue = 0.0
        self.cost = 0.0
        self.last_updated = datetime.now()
        
    def update_metrics(self, metrics: Dict[str, Any]):
        """
        Update strategy performance metrics.
        
        Args:
            metrics: Dictionary of metrics to update
        """
        self.metrics_history.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        })
        
        # Update key metrics
        if "revenue" in metrics:
            self.revenue = metrics["revenue"]
        if "cost" in metrics:
            self.cost = metrics["cost"]
        if "conversions" in metrics:
            self.conversion_rate = metrics.get("conversion_rate", 0.0)
            
        # Calculate derived metrics
        if self.cost > 0:
            self.roi = ((self.revenue - self.cost) / self.cost) * 100
            
        if "conversions" in metrics and metrics["conversions"] > 0 and self.cost > 0:
            self.cost_per_acquisition = self.cost / metrics["conversions"]
            
        self.last_updated = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metrics to dictionary.
        
        Returns:
            Dictionary representation of metrics
        """
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "roi": self.roi,
            "conversion_rate": self.conversion_rate,
            "cost_per_acquisition": self.cost_per_acquisition,
            "revenue": self.revenue,
            "cost": self.cost,
            "last_updated": self.last_updated.isoformat(),
            "metrics_history": self.metrics_history
        }

class EnhancedRevenueStrategyManager(RevenueStrategyManager):
    """
    Enhanced Revenue Strategy Manager with advanced capabilities for strategy evaluation,
    optimization, and knowledge graph integration.
    """
    
    def __init__(
        self, 
        storage_dir: str = "data/revenue",
        performance_monitor: Optional[RevenuePerformanceMonitor] = None,
        knowledge_integration: Optional[RevenueKnowledgeIntegration] = None
    ):
        """
        Initialize the Enhanced Revenue Strategy Manager.
        
        Args:
            storage_dir: Directory for storing strategy data
            performance_monitor: Revenue Performance Monitor instance
            knowledge_integration: Revenue Knowledge Integration instance
        """
        super().__init__(storage_dir)
        self.performance_monitor = performance_monitor
        self.knowledge_integration = knowledge_integration
        self.strategy_metrics = {}  # Dict[str, StrategyPerformanceMetrics]
        self.strategy_recommendations = {}  # Dict[str, List[Dict[str, Any]]]
        
    async def create_strategy(
        self, 
        name: str, 
        strategy_type: Union[str, StrategyType], 
        description: str,
        target_channels: Optional[List[str]] = None,
        target_segments: Optional[List[str]] = None,
        revenue_model: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        actions: Optional[List[Dict[str, Any]]] = None
    ) -> RevenueStrategy:
        """
        Create a new revenue strategy with enhanced metadata.
        
        Args:
            name: Name of the strategy
            strategy_type: Type of strategy
            description: Detailed description
            target_channels: List of target marketing channels
            target_segments: List of target customer segments
            revenue_model: Optional revenue model
            metrics: Optional metrics to track
            actions: Optional list of actions to implement the strategy
            
        Returns:
            Created RevenueStrategy instance
        """
        # Create the base strategy in the parent class
        strategy_dict = await super().create_strategy(
            name=name,
            strategy_type=strategy_type,
            description=description,
            target_channels=target_channels,
            target_segments=target_segments,
            revenue_model=revenue_model,
            metrics=metrics,
            actions=actions
        )
        
        # Create a RevenueStrategy object from the dictionary
        strategy = RevenueStrategy(
            id=strategy_dict.get("id"),
            name=strategy_dict.get("name"),
            strategy_type=strategy_dict.get("strategy_type"),
            description=strategy_dict.get("description"),
            target_channels=strategy_dict.get("target_channels"),
            target_segments=strategy_dict.get("target_segments"),
            revenue_model=strategy_dict.get("revenue_model"),
            metrics=strategy_dict.get("metrics"),
            actions=strategy_dict.get("actions"),
            is_active=strategy_dict.get("is_active", True)
        )
        
        # Initialize performance metrics for the strategy
        self.strategy_metrics[strategy.id] = StrategyPerformanceMetrics(
            strategy_id=strategy.id,
            name=strategy.name
        )
        
        # Store in knowledge graph if available
        if self.knowledge_integration:
            await self.knowledge_integration.store_revenue_strategy(strategy.to_dict())
            
        return strategy
        
    async def update_strategy_metrics(
        self, 
        strategy_id: str, 
        metrics: Dict[str, Any]
    ) -> bool:
        """
        Update metrics for a specific strategy.
        
        Args:
            strategy_id: ID of the strategy to update
            metrics: Dictionary of metrics to update
            
        Returns:
            True if successful, False otherwise
        """
        if strategy_id not in self.strategies:
            logger.warning(f"Strategy {strategy_id} not found")
            return False
            
        if strategy_id not in self.strategy_metrics:
            self.strategy_metrics[strategy_id] = StrategyPerformanceMetrics(
                strategy_id=strategy_id,
                name=self.strategies[strategy_id].name
            )
            
        # Update the metrics
        self.strategy_metrics[strategy_id].update_metrics(metrics)
        
        # Update strategy last_updated timestamp
        if isinstance(self.strategies[strategy_id], dict):
            self.strategies[strategy_id]["updated_at"] = datetime.now().isoformat()
        else:
            self.strategies[strategy_id].last_updated = datetime.now()
        
        # Save changes
        self._save_strategies()
        
        # Store in knowledge graph if available
        if self.knowledge_integration:
            strategy_metrics = self.strategy_metrics[strategy_id].to_dict()
            await self.knowledge_integration.store_strategy_metrics(strategy_metrics)
            
        return True
        
    async def evaluate_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        Evaluate the performance of a strategy.
        
        Args:
            strategy_id: ID of the strategy to evaluate
            
        Returns:
            Dictionary with evaluation results
        """
        if strategy_id not in self.strategies:
            return {"status": "error", "message": f"Strategy {strategy_id} not found"}
            
        strategy = self.strategies[strategy_id]
        
        # Get metrics for the strategy
        metrics = self.strategy_metrics.get(strategy_id)
        if not metrics:
            strategy_name = strategy['name'] if isinstance(strategy, dict) else strategy.name
            return {
                "status": "warning", 
                "message": f"No metrics available for strategy {strategy_name}"
            }
            
        # Evaluate based on strategy type
        if isinstance(strategy, dict):
            strategy_name = strategy.get('name')
            strategy_type = strategy.get('strategy_type')
            is_active = strategy.get('is_active', True)
        else:
            strategy_name = strategy.name
            strategy_type = strategy.strategy_type.value if hasattr(strategy.strategy_type, 'value') else strategy.strategy_type
            is_active = strategy.is_active
            
        evaluation = {
            "strategy_id": strategy_id,
            "name": strategy_name,
            "type": strategy_type,
            "status": "active" if is_active else "inactive",
            "performance": {
                "roi": metrics.roi,
                "conversion_rate": metrics.conversion_rate,
                "cost_per_acquisition": metrics.cost_per_acquisition,
                "revenue": metrics.revenue,
                "cost": metrics.cost
            },
            "evaluation": self._get_performance_rating(metrics),
            "last_updated": datetime.now().isoformat()
        }
        
        # Store evaluation in knowledge graph if available
        if self.knowledge_integration:
            await self.knowledge_integration.store_strategy_evaluation(evaluation)
            
        return evaluation
        
    def _get_performance_rating(self, metrics: StrategyPerformanceMetrics) -> Dict[str, Any]:
        """
        Get a performance rating for a strategy based on its metrics.
        
        Args:
            metrics: Strategy performance metrics
            
        Returns:
            Dictionary with performance ratings
        """
        # Define threshold values for different metrics
        roi_thresholds = {"excellent": 200, "good": 100, "average": 50, "poor": 0}
        conversion_thresholds = {"excellent": 0.05, "good": 0.03, "average": 0.01, "poor": 0}
        
        # Calculate ratings
        roi_rating = "excellent"
        for level, threshold in roi_thresholds.items():
            if metrics.roi < threshold:
                roi_rating = level
                break
                
        conversion_rating = "excellent"
        for level, threshold in conversion_thresholds.items():
            if metrics.conversion_rate < threshold:
                conversion_rating = level
                break
                
        # Calculate overall rating (simple average)
        ratings = {"excellent": 4, "good": 3, "average": 2, "poor": 1, "insufficient_data": 0}
        
        if metrics.roi == 0 and metrics.conversion_rate == 0:
            overall_rating = "insufficient_data"
        else:
            score = (ratings[roi_rating] + ratings[conversion_rating]) / 2
            if score >= 3.5:
                overall_rating = "excellent"
            elif score >= 2.5:
                overall_rating = "good"
            elif score >= 1.5:
                overall_rating = "average"
            else:
                overall_rating = "poor"
                
        return {
            "overall": overall_rating,
            "roi": roi_rating,
            "conversion": conversion_rating,
            "details": {
                "roi_value": metrics.roi,
                "conversion_value": metrics.conversion_rate
            }
        }
        
    async def generate_recommendations(self, strategy_id: str) -> List[Dict[str, Any]]:
        """
        Generate recommendations for improving a strategy.
        
        Args:
            strategy_id: ID of the strategy
            
        Returns:
            List of recommendation dictionaries
        """
        if strategy_id not in self.strategies:
            logger.warning(f"Strategy {strategy_id} not found")
            return []
            
        strategy = self.strategies[strategy_id]
        metrics = self.strategy_metrics.get(strategy_id)
        
        if not metrics:
            return [{
                "type": "info",
                "message": "Insufficient data to generate recommendations",
                "action": "Continue collecting performance data"
            }]
            
        recommendations = []
        
        # ROI-based recommendations
        if metrics.roi < 50:
            recommendations.append({
                "type": "warning",
                "message": f"Low ROI ({metrics.roi:.1f}%)",
                "action": "Review cost structure and targeting"
            })
            
        # Conversion rate recommendations
        if metrics.conversion_rate < 0.02:
            recommendations.append({
                "type": "warning",
                "message": f"Low conversion rate ({metrics.conversion_rate:.1%})",
                "action": "Optimize landing pages and calls to action"
            })
            
        # Cost per acquisition recommendations
        if metrics.cost_per_acquisition > 0 and metrics.revenue / metrics.cost_per_acquisition < 3:
            recommendations.append({
                "type": "warning",
                "message": f"High cost per acquisition relative to revenue",
                "action": "Refine targeting to focus on higher-value prospects"
            })
            
        # Strategy type specific recommendations
        strategy_type = strategy.get('strategy_type') if isinstance(strategy, dict) else strategy.strategy_type
        
        # Handle different types of strategy_type
        strategy_type_str = None
        if isinstance(strategy_type, StrategyType):
            strategy_type_str = strategy_type.value
        elif isinstance(strategy_type, str):
            strategy_type_str = strategy_type.upper()
        elif hasattr(strategy_type, 'value'):
            strategy_type_str = strategy_type.value
        
        if strategy_type_str == 'ACQUISITION':
            recommendations.append({
                "type": "suggestion",
                "message": "Consider A/B testing different acquisition channels",
                "action": "Set up experiments with different targeting parameters"
            })
        elif strategy_type_str == 'MONETIZATION':
            recommendations.append({
                "type": "suggestion",
                "message": "Analyze customer segments for upsell opportunities",
                "action": "Segment customers by purchase history and target high-value segments"
            })
        elif strategy_type_str == 'RETENTION':
            recommendations.append({
                "type": "suggestion",
                "message": "Review customer feedback for retention improvement opportunities",
                "action": "Implement customer satisfaction surveys and address common issues"
            })
            
        # Store recommendations
        self.strategy_recommendations[strategy_id] = recommendations
        
        # Store in knowledge graph if available
        if self.knowledge_integration:
            await self.knowledge_integration.store_strategy_recommendations(
                strategy_id=strategy_id,
                recommendations=recommendations
            )
            
        return recommendations
        
    async def optimize_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        Optimize a strategy based on performance data and recommendations.
        
        Args:
            strategy_id: ID of the strategy to optimize
            
        Returns:
            Dictionary with optimization results
        """
        if strategy_id not in self.strategies:
            return {"status": "error", "message": f"Strategy {strategy_id} not found"}
            
        strategy = self.strategies[strategy_id]
        metrics = self.strategy_metrics.get(strategy_id)
        
        if not metrics or not metrics.metrics_history:
            return {
                "status": "warning",
                "message": "Insufficient data for optimization",
                "strategy_id": strategy_id
            }
            
        # Generate recommendations if not already available
        if strategy_id not in self.strategy_recommendations:
            await self.generate_recommendations(strategy_id)
            
        recommendations = self.strategy_recommendations.get(strategy_id, [])
        
        # Create optimization plan
        strategy_name = strategy.get('name') if isinstance(strategy, dict) else strategy.name
        
        optimization_plan = {
            "strategy_id": strategy_id,
            "name": strategy_name,
            "current_performance": {
                "roi": metrics.roi,
                "conversion_rate": metrics.conversion_rate,
                "revenue": metrics.revenue
            },
            "recommendations": recommendations,
            "optimization_actions": [],
            "expected_improvements": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Add optimization actions based on strategy type and metrics
        strategy_type = strategy.get('strategy_type') if isinstance(strategy, dict) else strategy.strategy_type
        
        # Handle different types of strategy_type
        strategy_type_str = None
        if isinstance(strategy_type, StrategyType):
            strategy_type_str = strategy_type.value
        elif isinstance(strategy_type, str):
            strategy_type_str = strategy_type.upper()
        elif hasattr(strategy_type, 'value'):
            strategy_type_str = strategy_type.value
                
        if strategy_type_str == 'ACQUISITION':
            if metrics.cost_per_acquisition > 0:
                optimization_plan["optimization_actions"].append({
                    "action": "Refine targeting parameters",
                    "expected_impact": "Reduce cost per acquisition by 15-20%"
                })
                optimization_plan["expected_improvements"]["cost_per_acquisition"] = -0.15
                
            optimization_plan["optimization_actions"].append({
                "action": "Test new creative variations",
                "expected_impact": "Improve conversion rate by 10-15%"
            })
            optimization_plan["expected_improvements"]["conversion_rate"] = 0.12
            
        elif strategy_type_str == 'MONETIZATION':
            optimization_plan["optimization_actions"].append({
                "action": "Implement personalized offers",
                "expected_impact": "Increase average order value by 10-15%"
            })
            optimization_plan["expected_improvements"]["revenue"] = 0.12
            
        elif strategy_type_str == 'RETENTION':
            optimization_plan["optimization_actions"].append({
                "action": "Implement customer loyalty program",
                "expected_impact": "Improve retention rate by 15-20%"
            })
            optimization_plan["expected_improvements"]["retention_rate"] = 0.15
            
        # Store optimization plan in knowledge graph if available
        if self.knowledge_integration:
            await self.knowledge_integration.store_strategy_optimization(optimization_plan)
            
        return optimization_plan
        
    async def get_strategies_by_performance(self, min_roi: float = 0.0) -> List[Dict[str, Any]]:
        """
        Get strategies sorted by performance (ROI).
        
        Args:
            min_roi: Minimum ROI threshold
            
        Returns:
            List of strategies with performance data
        """
        result = []
        
        for strategy_id, strategy in self.strategies.items():
            metrics = self.strategy_metrics.get(strategy_id)
            
            if not metrics or metrics.roi < min_roi:
                continue
                
            # Handle different strategy object types
            if isinstance(strategy, dict):
                strategy_name = strategy.get('name')
                strategy_type = strategy.get('strategy_type')
                is_active = strategy.get('is_active', True)
            else:
                strategy_name = strategy.name
                strategy_type = strategy.strategy_type.value if hasattr(strategy.strategy_type, 'value') else strategy.strategy_type
                is_active = strategy.is_active
                
            result.append({
                "id": strategy_id,
                "name": strategy_name,
                "type": strategy_type,
                "roi": metrics.roi,
                "revenue": metrics.revenue,
                "cost": metrics.cost,
                "is_active": is_active
            })
            
        # Sort by ROI (descending)
        result.sort(key=lambda x: x["roi"], reverse=True)
        return result
        
    async def get_strategies_from_knowledge_graph(self) -> List[Dict[str, Any]]:
        """
        Get strategies from the knowledge graph.
        
        Returns:
            List of strategies from the knowledge graph
        """
        if not self.knowledge_integration:
            logger.warning("Knowledge graph integration not available")
            return []
            
        return await self.knowledge_integration.get_revenue_strategies()
        
    async def get_strategy_metrics_from_knowledge_graph(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get strategy metrics from the knowledge graph.
        
        Args:
            strategy_id: ID of the strategy
            
        Returns:
            Dictionary with strategy metrics
        """
        if not self.knowledge_integration:
            logger.warning("Knowledge graph integration not available")
            return {}
            
        return await self.knowledge_integration.get_strategy_metrics(strategy_id)
        
    async def get_strategy_recommendations_from_knowledge_graph(self, strategy_id: str) -> List[Dict[str, Any]]:
        """
        Get strategy recommendations from the knowledge graph.
        
        Args:
            strategy_id: ID of the strategy
            
        Returns:
            List of recommendations
        """
        if not self.knowledge_integration:
            logger.warning("Knowledge graph integration not available")
            return []
            
        return await self.knowledge_integration.get_strategy_recommendations(strategy_id)
        
    async def analyze_strategies_by_channel(self) -> Dict[str, Any]:
        """
        Analyze strategies grouped by channel.
        
        Returns:
            Dictionary with channel analysis
        """
        channel_performance = {}
        
        for strategy_id, strategy in self.strategies.items():
            metrics = self.strategy_metrics.get(strategy_id)
            
            if not metrics:
                continue
                
            # Get target channels based on strategy type
            target_channels = strategy.get('target_channels') if isinstance(strategy, dict) else strategy.target_channels
            
            # Get strategy name based on type
            strategy_name = strategy.get('name') if isinstance(strategy, dict) else strategy.name
            
            for channel in target_channels:
                if channel not in channel_performance:
                    channel_performance[channel] = {
                        "strategies": [],
                        "total_revenue": 0.0,
                        "total_cost": 0.0,
                        "average_roi": 0.0
                    }
                    
                channel_performance[channel]["strategies"].append({
                    "id": strategy_id,
                    "name": strategy_name,
                    "roi": metrics.roi,
                    "revenue": metrics.revenue,
                    "cost": metrics.cost
                })
                
                channel_performance[channel]["total_revenue"] += metrics.revenue
                channel_performance[channel]["total_cost"] += metrics.cost
                
        # Calculate average ROI for each channel
        for channel, data in channel_performance.items():
            if data["total_cost"] > 0:
                data["average_roi"] = ((data["total_revenue"] - data["total_cost"]) / data["total_cost"]) * 100
                
            # Sort strategies by ROI
            data["strategies"].sort(key=lambda x: x["roi"], reverse=True)
            
        return {
            "status": "success",
            "channel_performance": channel_performance,
            "timestamp": datetime.now().isoformat()
        }
        
    async def analyze_strategies_by_segment(self) -> Dict[str, Any]:
        """
        Analyze strategies grouped by customer segment.
        
        Returns:
            Dictionary with segment analysis
        """
        segment_performance = {}
        
        for strategy_id, strategy in self.strategies.items():
            metrics = self.strategy_metrics.get(strategy_id)
            
            if not metrics:
                continue
                
            # Get target segments based on strategy type
            target_segments = strategy.get('target_segments') if isinstance(strategy, dict) else strategy.target_segments
            
            # Get strategy name based on type
            strategy_name = strategy.get('name') if isinstance(strategy, dict) else strategy.name
            
            for segment in target_segments:
                if segment not in segment_performance:
                    segment_performance[segment] = {
                        "strategies": [],
                        "total_revenue": 0.0,
                        "total_cost": 0.0,
                        "average_roi": 0.0
                    }
                    
                segment_performance[segment]["strategies"].append({
                    "id": strategy_id,
                    "name": strategy_name,
                    "roi": metrics.roi,
                    "revenue": metrics.revenue,
                    "cost": metrics.cost
                })
                
                segment_performance[segment]["total_revenue"] += metrics.revenue
                segment_performance[segment]["total_cost"] += metrics.cost
                
        # Calculate average ROI for each segment
        for segment, data in segment_performance.items():
            if data["total_cost"] > 0:
                data["average_roi"] = ((data["total_revenue"] - data["total_cost"]) / data["total_cost"]) * 100
                
            # Sort strategies by ROI
            data["strategies"].sort(key=lambda x: x["roi"], reverse=True)
            
        return {
            "status": "success",
            "segment_performance": segment_performance,
            "timestamp": datetime.now().isoformat()
        }
