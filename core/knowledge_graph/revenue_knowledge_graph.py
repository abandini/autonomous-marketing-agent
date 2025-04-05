"""
Revenue Knowledge Graph module for the Autonomous Marketing Agent.

This module extends the base knowledge graph with revenue-specific nodes,
relationships, and query capabilities to support the Revenue Optimization Framework.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import networkx as nx
import pandas as pd

from core.knowledge_graph.knowledge_graph import MarketingKnowledgeGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RevenueKnowledgeGraph:
    """
    Extension of the Marketing Knowledge Graph focused on revenue optimization.
    
    This class adds revenue-specific nodes and relationships to the knowledge graph:
    1. Revenue goals and targets
    2. Revenue sources and channels
    3. Customer lifetime value data
    4. Monetization strategies
    5. Revenue attribution models
    6. Historical revenue data and forecasts
    """
    
    def __init__(self, knowledge_graph: MarketingKnowledgeGraph):
        """
        Initialize the Revenue Knowledge Graph extension.
        
        Args:
            knowledge_graph: Base marketing knowledge graph instance
        """
        self.kg = knowledge_graph
        
        # Initialize revenue-specific nodes
        self._initialize_revenue_nodes()
        
        logger.info("Revenue Knowledge Graph extension initialized")
        
    def _initialize_revenue_nodes(self) -> None:
        """Initialize revenue-specific base nodes in the knowledge graph."""
        revenue_nodes = [
            {"id": "revenue", "type": "category", "name": "Revenue"},
            {"id": "revenue_goals", "type": "category", "name": "Revenue Goals"},
            {"id": "revenue_sources", "type": "category", "name": "Revenue Sources"},
            {"id": "monetization_strategies", "type": "category", "name": "Monetization Strategies"},
            {"id": "revenue_forecasts", "type": "category", "name": "Revenue Forecasts"},
            {"id": "customer_ltv", "type": "category", "name": "Customer Lifetime Value"},
            {"id": "attribution_models", "type": "category", "name": "Attribution Models"}
        ]
        
        # Add revenue nodes
        for node in revenue_nodes:
            self.kg.add_node(node["id"], node)
            
            # Connect to root
            self.kg.add_edge("root", node["id"], {"type": "contains"})
            
        # Connect revenue to other relevant categories
        self.kg.add_edge("revenue", "metrics", {"type": "related_to"})
        self.kg.add_edge("revenue", "channels", {"type": "attributed_to"})
        self.kg.add_edge("revenue", "campaigns", {"type": "generated_by"})
        
        logger.debug("Initialized revenue nodes in knowledge graph")
        
    def add_revenue_goal(
        self,
        goal_id: str,
        name: str,
        target_value: float,
        period: str,
        start_date: str,
        end_date: str,
        channel: Optional[str] = None,
        segment: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a revenue goal to the knowledge graph.
        
        Args:
            goal_id: Unique identifier for the goal
            name: Name of the goal
            target_value: Target revenue value
            period: Goal period (e.g., DAILY, WEEKLY, MONTHLY)
            start_date: Start date for the goal
            end_date: End date for the goal
            channel: Optional channel for the goal
            segment: Optional segment for the goal
            metrics: Optional additional metrics for the goal
            
        Returns:
            True if the goal was added, False otherwise
        """
        # Create goal node
        goal_node = {
            "type": "revenue_goal",
            "name": name,
            "target_value": target_value,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "current_value": 0.0,
            "progress": 0.0,
            "status": "active",
            "channel": channel,
            "segment": segment,
            "metrics": metrics or {}
        }
        
        # Add goal node
        result = self.kg.add_node(goal_id, goal_node)
        
        if result:
            # Connect to revenue_goals category
            self.kg.add_edge("revenue_goals", goal_id, {"type": "contains"})
            
            # Connect to channel if specified
            if channel:
                channel_id = f"channel:{channel}"
                
                # Create channel node if it doesn't exist
                if not self.kg.get_node(channel_id):
                    self.kg.add_node(channel_id, {
                        "type": "channel",
                        "name": channel
                    })
                    self.kg.add_edge("channels", channel_id, {"type": "contains"})
                
                # Connect goal to channel
                self.kg.add_edge(goal_id, channel_id, {"type": "targets"})
            
            # Connect to segment if specified
            if segment:
                segment_id = f"segment:{segment}"
                
                # Create segment node if it doesn't exist
                if not self.kg.get_node(segment_id):
                    self.kg.add_node(segment_id, {
                        "type": "segment",
                        "name": segment
                    })
                    self.kg.add_edge("audiences", segment_id, {"type": "contains"})
                
                # Connect goal to segment
                self.kg.add_edge(goal_id, segment_id, {"type": "targets"})
            
            logger.info(f"Added revenue goal {name} to knowledge graph")
        
        return result
        
    def update_revenue_goal(
        self,
        goal_id: str,
        current_value: Optional[float] = None,
        status: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a revenue goal in the knowledge graph.
        
        Args:
            goal_id: Unique identifier for the goal
            current_value: Optional updated current value
            status: Optional updated status
            metrics: Optional updated metrics
            
        Returns:
            True if the goal was updated, False otherwise
        """
        # Get existing goal
        goal_node = self.kg.get_node(goal_id)
        
        if not goal_node or goal_node.get("type") != "revenue_goal":
            logger.error(f"Revenue goal {goal_id} not found")
            return False
            
        # Update attributes
        updates = {}
        
        if current_value is not None:
            updates["current_value"] = current_value
            
            # Update progress
            target_value = goal_node.get("target_value", 0.0)
            if target_value > 0:
                updates["progress"] = (current_value / target_value) * 100.0
            
        if status is not None:
            updates["status"] = status
            
        if metrics is not None:
            # Merge metrics
            existing_metrics = goal_node.get("metrics", {})
            merged_metrics = {**existing_metrics, **metrics}
            updates["metrics"] = merged_metrics
            
        # Apply updates
        if updates:
            result = self.kg.update_node(goal_id, updates)
            
            if result:
                logger.info(f"Updated revenue goal {goal_id} in knowledge graph")
                
            return result
        
        return True  # No updates needed
        
    def add_revenue_source(
        self,
        source_id: str,
        name: str,
        source_type: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a revenue source to the knowledge graph.
        
        Args:
            source_id: Unique identifier for the source
            name: Name of the source
            source_type: Type of revenue source (e.g., affiliate, product, service)
            attributes: Optional additional attributes
            
        Returns:
            True if the source was added, False otherwise
        """
        # Create source node
        source_node = {
            "type": "revenue_source",
            "name": name,
            "source_type": source_type,
            **(attributes or {})
        }
        
        # Add source node
        result = self.kg.add_node(source_id, source_node)
        
        if result:
            # Connect to revenue_sources category
            self.kg.add_edge("revenue_sources", source_id, {"type": "contains"})
            
            logger.info(f"Added revenue source {name} to knowledge graph")
        
        return result
        
    def add_monetization_strategy(
        self,
        strategy_id: str,
        name: str,
        description: str,
        revenue_model: str,
        target_channels: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a monetization strategy to the knowledge graph.
        
        Args:
            strategy_id: Unique identifier for the strategy
            name: Name of the strategy
            description: Description of the strategy
            revenue_model: Revenue model (e.g., subscription, one-time, freemium)
            target_channels: Optional list of target channels
            attributes: Optional additional attributes
            
        Returns:
            True if the strategy was added, False otherwise
        """
        # Create strategy node
        strategy_node = {
            "type": "monetization_strategy",
            "name": name,
            "description": description,
            "revenue_model": revenue_model,
            **(attributes or {})
        }
        
        # Add strategy node
        result = self.kg.add_node(strategy_id, strategy_node)
        
        if result:
            # Connect to monetization_strategies category
            self.kg.add_edge("monetization_strategies", strategy_id, {"type": "contains"})
            
            # Connect to target channels
            if target_channels:
                for channel in target_channels:
                    channel_id = f"channel:{channel}"
                    
                    # Create channel node if it doesn't exist
                    if not self.kg.get_node(channel_id):
                        self.kg.add_node(channel_id, {
                            "type": "channel",
                            "name": channel
                        })
                        self.kg.add_edge("channels", channel_id, {"type": "contains"})
                    
                    # Connect strategy to channel
                    self.kg.add_edge(strategy_id, channel_id, {"type": "targets"})
            
            logger.info(f"Added monetization strategy {name} to knowledge graph")
        
        return result
        
    def add_revenue_forecast(
        self,
        forecast_id: str,
        name: str,
        method: str,
        predictions: List[Dict[str, Any]],
        channel: Optional[str] = None,
        segment: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a revenue forecast to the knowledge graph.
        
        Args:
            forecast_id: Unique identifier for the forecast
            name: Name of the forecast
            method: Forecasting method used
            predictions: List of prediction data points
            channel: Optional channel for the forecast
            segment: Optional segment for the forecast
            attributes: Optional additional attributes
            
        Returns:
            True if the forecast was added, False otherwise
        """
        # Create forecast node
        forecast_node = {
            "type": "revenue_forecast",
            "name": name,
            "method": method,
            "predictions": predictions,
            "channel": channel,
            "segment": segment,
            "created_at": datetime.now().isoformat(),
            **(attributes or {})
        }
        
        # Add forecast node
        result = self.kg.add_node(forecast_id, forecast_node)
        
        if result:
            # Connect to revenue_forecasts category
            self.kg.add_edge("revenue_forecasts", forecast_id, {"type": "contains"})
            
            # Connect to channel if specified
            if channel:
                channel_id = f"channel:{channel}"
                
                # Create channel node if it doesn't exist
                if not self.kg.get_node(channel_id):
                    self.kg.add_node(channel_id, {
                        "type": "channel",
                        "name": channel
                    })
                    self.kg.add_edge("channels", channel_id, {"type": "contains"})
                
                # Connect forecast to channel
                self.kg.add_edge(forecast_id, channel_id, {"type": "analyzes"})
            
            # Connect to segment if specified
            if segment:
                segment_id = f"segment:{segment}"
                
                # Create segment node if it doesn't exist
                if not self.kg.get_node(segment_id):
                    self.kg.add_node(segment_id, {
                        "type": "segment",
                        "name": segment
                    })
                    self.kg.add_edge("audiences", segment_id, {"type": "contains"})
                
                # Connect forecast to segment
                self.kg.add_edge(forecast_id, segment_id, {"type": "analyzes"})
            
            logger.info(f"Added revenue forecast {name} to knowledge graph")
        
        return result
        
    def add_attribution_data(
        self,
        attribution_id: str,
        customer_id: str,
        touchpoints: List[Dict[str, Any]],
        conversion_value: float,
        model: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add revenue attribution data to the knowledge graph.
        
        Args:
            attribution_id: Unique identifier for the attribution
            customer_id: ID of the customer
            touchpoints: List of touchpoint data
            conversion_value: Value of the conversion
            model: Attribution model used
            attributes: Optional additional attributes
            
        Returns:
            True if the attribution data was added, False otherwise
        """
        # Create attribution node
        attribution_node = {
            "type": "revenue_attribution",
            "customer_id": customer_id,
            "touchpoints": touchpoints,
            "conversion_value": conversion_value,
            "model": model,
            "timestamp": datetime.now().isoformat(),
            **(attributes or {})
        }
        
        # Add attribution node
        result = self.kg.add_node(attribution_id, attribution_node)
        
        if result:
            # Connect to attribution_models category
            self.kg.add_edge("attribution_models", attribution_id, {"type": "contains"})
            
            # Create customer node if it doesn't exist
            customer_node_id = f"customer:{customer_id}"
            if not self.kg.get_node(customer_node_id):
                self.kg.add_node(customer_node_id, {
                    "type": "customer",
                    "customer_id": customer_id
                })
                
                # Connect to audiences
                self.kg.add_edge("audiences", customer_node_id, {"type": "contains"})
            
            # Connect attribution to customer
            self.kg.add_edge(attribution_id, customer_node_id, {"type": "attributes"})
            
            # Connect touchpoints to channels
            for touchpoint in touchpoints:
                channel = touchpoint.get("channel")
                if channel:
                    channel_id = f"channel:{channel}"
                    
                    # Create channel node if it doesn't exist
                    if not self.kg.get_node(channel_id):
                        self.kg.add_node(channel_id, {
                            "type": "channel",
                            "name": channel
                        })
                        self.kg.add_edge("channels", channel_id, {"type": "contains"})
                    
                    # Connect attribution to channel with weight
                    weight = touchpoint.get("weight", 0.0)
                    self.kg.add_edge(attribution_id, channel_id, {
                        "type": "attributes",
                        "weight": weight,
                        "value": conversion_value * weight
                    })
            
            logger.info(f"Added revenue attribution data for customer {customer_id}")
        
        return result
        
    def query_revenue_goals(
        self,
        status: Optional[str] = None,
        channel: Optional[str] = None,
        period: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query revenue goals in the knowledge graph.
        
        Args:
            status: Optional filter for goal status
            channel: Optional filter for channel
            period: Optional filter for period
            
        Returns:
            List of revenue goals matching the query
        """
        # Build query attributes
        attributes = {"type": "revenue_goal"}
        
        if status:
            attributes["status"] = status
            
        if channel:
            attributes["channel"] = channel
            
        if period:
            attributes["period"] = period
            
        # Query nodes
        return self.kg.query(attributes=attributes)
        
    def query_revenue_by_channel(self) -> Dict[str, float]:
        """
        Query total revenue attributed to each channel.
        
        Returns:
            Dict mapping channel names to revenue values
        """
        channel_revenue = {}
        
        # Get all attribution edges
        for source, target, edge_data in self.kg.graph.edges(data=True):
            if edge_data.get("type") == "attributes" and "value" in edge_data:
                target_node = self.kg.get_node(target)
                
                if target_node and target_node.get("type") == "channel":
                    channel_name = target_node.get("name", "unknown")
                    
                    if channel_name not in channel_revenue:
                        channel_revenue[channel_name] = 0.0
                        
                    channel_revenue[channel_name] += edge_data["value"]
        
        return channel_revenue
        
    def query_monetization_strategies(
        self,
        revenue_model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query monetization strategies in the knowledge graph.
        
        Args:
            revenue_model: Optional filter for revenue model
            
        Returns:
            List of monetization strategies matching the query
        """
        # Build query attributes
        attributes = {"type": "monetization_strategy"}
        
        if revenue_model:
            attributes["revenue_model"] = revenue_model
            
        # Query nodes
        return self.kg.query(attributes=attributes)
        
    def query_revenue_forecasts(
        self,
        channel: Optional[str] = None,
        method: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query revenue forecasts in the knowledge graph.
        
        Args:
            channel: Optional filter for channel
            method: Optional filter for forecasting method
            
        Returns:
            List of revenue forecasts matching the query
        """
        # Build query attributes
        attributes = {"type": "revenue_forecast"}
        
        if channel:
            attributes["channel"] = channel
            
        if method:
            attributes["method"] = method
            
        # Query nodes
        return self.kg.query(attributes=attributes)
        
    def get_revenue_insights(self) -> Dict[str, Any]:
        """
        Generate insights from revenue data in the knowledge graph.
        
        Returns:
            Dict containing revenue insights
        """
        insights = {
            "top_channels": [],
            "goal_progress": {},
            "forecast_summary": {},
            "monetization_strategies": []
        }
        
        # Get top revenue channels
        channel_revenue = self.query_revenue_by_channel()
        sorted_channels = sorted(
            channel_revenue.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        insights["top_channels"] = [
            {"channel": channel, "revenue": revenue}
            for channel, revenue in sorted_channels[:5]
        ]
        
        # Get goal progress
        active_goals = self.query_revenue_goals(status="active")
        
        if active_goals:
            total_target = sum(goal.get("target_value", 0.0) for goal in active_goals)
            total_current = sum(goal.get("current_value", 0.0) for goal in active_goals)
            
            insights["goal_progress"] = {
                "total_goals": len(active_goals),
                "total_target": total_target,
                "total_current": total_current,
                "overall_progress": (total_current / total_target * 100) if total_target > 0 else 0.0
            }
        
        # Get forecast summary
        forecasts = self.query_revenue_forecasts()
        
        if forecasts:
            # Sort by created_at (newest first)
            forecasts.sort(
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )
            
            # Get most recent forecast
            latest_forecast = forecasts[0]
            predictions = latest_forecast.get("predictions", [])
            
            if predictions:
                total_forecast = sum(p.get("value", 0.0) for p in predictions)
                
                insights["forecast_summary"] = {
                    "latest_forecast": latest_forecast.get("name", "Unknown"),
                    "method": latest_forecast.get("method", "Unknown"),
                    "periods": len(predictions),
                    "total_forecast": total_forecast
                }
        
        # Get monetization strategies
        strategies = self.query_monetization_strategies()
        
        insights["monetization_strategies"] = [
            {
                "name": strategy.get("name", "Unknown"),
                "revenue_model": strategy.get("revenue_model", "Unknown")
            }
            for strategy in strategies[:5]
        ]
        
        return insights
