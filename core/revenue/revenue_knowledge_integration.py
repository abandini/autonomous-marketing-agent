"""
Revenue Knowledge Integration module for the Autonomous Marketing Agent.

This module provides integration between the Revenue Optimization Framework
and the Knowledge Graph, allowing revenue-related information to be stored
and retrieved from the centralized knowledge repository.
"""

import logging
from typing import Dict, List, Any, Optional, Union
import asyncio
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RevenueKnowledgeIntegration:
    """
    Integration between Revenue Optimization Framework and Knowledge Graph.
    
    This class provides functionality for:
    1. Storing revenue goals in the knowledge graph
    2. Storing revenue strategies in the knowledge graph
    3. Storing performance metrics in the knowledge graph
    4. Retrieving revenue-related information from the knowledge graph
    5. Analyzing revenue data using the knowledge graph
    """
    
    def __init__(self, knowledge_graph=None):
        """
        Initialize the Revenue Knowledge Integration.
        
        Args:
            knowledge_graph: Instance of the Marketing Knowledge Graph
        """
        self.knowledge_graph = knowledge_graph
        logger.info("Revenue Knowledge Integration initialized")
        
    async def store_revenue_goal(self, goal: Dict[str, Any]) -> bool:
        """
        Store a revenue goal in the knowledge graph.
        
        Args:
            goal: Dict containing revenue goal data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return False
            
        try:
            # Create a unique node ID for the goal
            goal_id = goal.get("id", f"revenue_goal_{uuid.uuid4()}")
            
            # Prepare node attributes
            attributes = {
                "type": "revenue_goal",
                "name": goal.get("name", "Unnamed Goal"),
                "target_value": goal.get("target_value", 0.0),
                "period": goal.get("period", "unknown"),
                "start_date": goal.get("start_date", datetime.now().isoformat()),
                "end_date": goal.get("end_date", datetime.now().isoformat()),
                "status": goal.get("status", "active"),
                "channel": goal.get("channel"),
                "segment": goal.get("segment"),
                "created_at": goal.get("created_at", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat()
            }
            
            # Add the goal node to the knowledge graph
            success = self.knowledge_graph.add_node(goal_id, attributes)
            
            if success:
                # Connect the goal to the metrics category
                self.knowledge_graph.add_edge("metrics", goal_id, {"type": "contains"})
                
                # Connect to channel if specified
                if goal.get("channel"):
                    channel_id = f"channel_{goal['channel'].lower().replace(' ', '_')}"
                    self.knowledge_graph.add_edge(channel_id, goal_id, {"type": "has_goal"})
                
                # Connect to segment if specified
                if goal.get("segment"):
                    segment_id = f"segment_{goal['segment'].lower().replace(' ', '_')}"
                    self.knowledge_graph.add_edge(segment_id, goal_id, {"type": "has_goal"})
                    
                logger.info(f"Stored revenue goal '{goal.get('name')}' in knowledge graph")
                return True
            else:
                logger.error(f"Failed to store revenue goal '{goal.get('name')}' in knowledge graph")
                return False
                
        except Exception as e:
            logger.error(f"Error storing revenue goal in knowledge graph: {e}")
            return False
            
    async def store_revenue_strategy(self, strategy: Dict[str, Any]) -> bool:
        """
        Store a revenue strategy in the knowledge graph.
        
        Args:
            strategy: Dict containing revenue strategy data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return False
            
        try:
            # Create a unique node ID for the strategy
            strategy_id = strategy.get("id", f"revenue_strategy_{uuid.uuid4()}")
            
            # Prepare node attributes
            attributes = {
                "type": "revenue_strategy",
                "name": strategy.get("name", "Unnamed Strategy"),
                "strategy_type": strategy.get("strategy_type", "unknown"),
                "description": strategy.get("description", ""),
                "is_active": strategy.get("is_active", True),
                "target_channels": strategy.get("target_channels", []),
                "target_segments": strategy.get("target_segments", []),
                "created_at": strategy.get("created_at", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat()
            }
            
            # Add performance metrics if available
            if "performance" in strategy:
                attributes["performance"] = strategy["performance"]
                
            # Add the strategy node to the knowledge graph
            success = self.knowledge_graph.add_node(strategy_id, attributes)
            
            if success:
                # Connect the strategy to the strategies category
                self.knowledge_graph.add_edge("strategies", strategy_id, {"type": "contains"})
                
                # Connect to revenue_strategies category if it exists
                if self.knowledge_graph.has_node("revenue_strategies"):
                    self.knowledge_graph.add_edge("revenue_strategies", strategy_id, {"type": "contains"})
                
                # Connect to goals if specified
                for goal_id in strategy.get("goals", []):
                    self.knowledge_graph.add_edge(goal_id, strategy_id, {"type": "has_strategy"})
                    
                # Connect to channels if specified
                for channel in strategy.get("target_channels", []):
                    channel_id = f"channel_{channel.lower().replace(' ', '_')}"
                    if self.knowledge_graph.has_node(channel_id):
                        self.knowledge_graph.add_edge(channel_id, strategy_id, {"type": "uses_strategy"})
                    
                # Connect to segments if specified
                for segment in strategy.get("target_segments", []):
                    segment_id = f"segment_{segment.lower().replace(' ', '_')}"
                    if self.knowledge_graph.has_node(segment_id):
                        self.knowledge_graph.add_edge(segment_id, strategy_id, {"type": "targeted_by"})
                    
                logger.info(f"Stored revenue strategy '{strategy.get('name')}' in knowledge graph")
                return True
            else:
                logger.error(f"Failed to store revenue strategy '{strategy.get('name')}' in knowledge graph")
                return False
                
        except Exception as e:
            logger.error(f"Error storing revenue strategy in knowledge graph: {e}")
            return False
            
    async def store_strategy_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Store strategy performance metrics in the knowledge graph.
        
        Args:
            metrics: Dict containing strategy metrics data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return False
            
        try:
            strategy_id = metrics.get("strategy_id")
            if not strategy_id:
                logger.error("Strategy ID not provided in metrics data")
                return False
                
            # Create a unique node ID for the metrics
            metrics_id = f"metrics_{strategy_id}_{uuid.uuid4().hex[:8]}"
            
            # Prepare node attributes
            attributes = {
                "type": "strategy_metrics",
                "strategy_id": strategy_id,
                "strategy_name": metrics.get("name", "Unknown Strategy"),
                "roi": metrics.get("roi", 0.0),
                "conversion_rate": metrics.get("conversion_rate", 0.0),
                "cost_per_acquisition": metrics.get("cost_per_acquisition", 0.0),
                "revenue": metrics.get("revenue", 0.0),
                "cost": metrics.get("cost", 0.0),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add the metrics node to the knowledge graph
            success = self.knowledge_graph.add_node(metrics_id, attributes)
            
            if success:
                # Connect the metrics to the strategy
                self.knowledge_graph.add_edge(strategy_id, metrics_id, {"type": "has_metrics"})
                
                # Connect to revenue_metrics category if it exists
                if self.knowledge_graph.has_node("revenue_metrics"):
                    self.knowledge_graph.add_edge("revenue_metrics", metrics_id, {"type": "contains"})
                    
                logger.info(f"Stored metrics for strategy '{metrics.get('name')}' in knowledge graph")
                return True
            else:
                logger.error(f"Failed to store metrics for strategy '{metrics.get('name')}' in knowledge graph")
                return False
                
        except Exception as e:
            logger.error(f"Error storing strategy metrics in knowledge graph: {e}")
            return False
            
    async def store_strategy_evaluation(self, evaluation: Dict[str, Any]) -> bool:
        """
        Store strategy evaluation results in the knowledge graph.
        
        Args:
            evaluation: Dict containing strategy evaluation data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return False
            
        try:
            strategy_id = evaluation.get("strategy_id")
            if not strategy_id:
                logger.error("Strategy ID not provided in evaluation data")
                return False
                
            # Create a unique node ID for the evaluation
            evaluation_id = f"evaluation_{strategy_id}_{uuid.uuid4().hex[:8]}"
            
            # Prepare node attributes
            attributes = {
                "type": "strategy_evaluation",
                "strategy_id": strategy_id,
                "strategy_name": evaluation.get("name", "Unknown Strategy"),
                "strategy_type": evaluation.get("type", "unknown"),
                "status": evaluation.get("status", "unknown"),
                "performance": evaluation.get("performance", {}),
                "evaluation": evaluation.get("evaluation", {}),
                "timestamp": evaluation.get("last_updated", datetime.now().isoformat())
            }
            
            # Add the evaluation node to the knowledge graph
            success = self.knowledge_graph.add_node(evaluation_id, attributes)
            
            if success:
                # Connect the evaluation to the strategy
                self.knowledge_graph.add_edge(strategy_id, evaluation_id, {"type": "has_evaluation"})
                
                logger.info(f"Stored evaluation for strategy '{evaluation.get('name')}' in knowledge graph")
                return True
            else:
                logger.error(f"Failed to store evaluation for strategy '{evaluation.get('name')}' in knowledge graph")
                return False
                
        except Exception as e:
            logger.error(f"Error storing strategy evaluation in knowledge graph: {e}")
            return False
            
    async def store_strategy_recommendations(self, strategy_id: str, recommendations: List[Dict[str, Any]]) -> bool:
        """
        Store strategy recommendations in the knowledge graph.
        
        Args:
            strategy_id: ID of the strategy
            recommendations: List of recommendation dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return False
            
        if not recommendations:
            logger.warning("No recommendations provided")
            return False
            
        try:
            # Create a unique node ID for the recommendations
            recommendations_id = f"recommendations_{strategy_id}_{uuid.uuid4().hex[:8]}"
            
            # Prepare node attributes
            attributes = {
                "type": "strategy_recommendations",
                "strategy_id": strategy_id,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add the recommendations node to the knowledge graph
            success = self.knowledge_graph.add_node(recommendations_id, attributes)
            
            if success:
                # Connect the recommendations to the strategy
                self.knowledge_graph.add_edge(strategy_id, recommendations_id, {"type": "has_recommendations"})
                
                logger.info(f"Stored recommendations for strategy {strategy_id} in knowledge graph")
                return True
            else:
                logger.error(f"Failed to store recommendations for strategy {strategy_id} in knowledge graph")
                return False
                
        except Exception as e:
            logger.error(f"Error storing strategy recommendations in knowledge graph: {e}")
            return False
            
    async def store_strategy_optimization(self, optimization: Dict[str, Any]) -> bool:
        """
        Store strategy optimization plan in the knowledge graph.
        
        Args:
            optimization: Dict containing optimization plan data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return False
            
        try:
            strategy_id = optimization.get("strategy_id")
            if not strategy_id:
                logger.error("Strategy ID not provided in optimization data")
                return False
                
            # Create a unique node ID for the optimization plan
            optimization_id = f"optimization_{strategy_id}_{uuid.uuid4().hex[:8]}"
            
            # Prepare node attributes
            attributes = {
                "type": "strategy_optimization",
                "strategy_id": strategy_id,
                "strategy_name": optimization.get("name", "Unknown Strategy"),
                "current_performance": optimization.get("current_performance", {}),
                "recommendations": optimization.get("recommendations", []),
                "optimization_actions": optimization.get("optimization_actions", []),
                "expected_improvements": optimization.get("expected_improvements", {}),
                "timestamp": optimization.get("timestamp", datetime.now().isoformat())
            }
            
            # Add the optimization node to the knowledge graph
            success = self.knowledge_graph.add_node(optimization_id, attributes)
            
            if success:
                # Connect the optimization to the strategy
                self.knowledge_graph.add_edge(strategy_id, optimization_id, {"type": "has_optimization"})
                
                logger.info(f"Stored optimization plan for strategy '{optimization.get('name')}' in knowledge graph")
                return True
            else:
                logger.error(f"Failed to store optimization plan for strategy '{optimization.get('name')}' in knowledge graph")
                return False
                
        except Exception as e:
            logger.error(f"Error storing strategy optimization in knowledge graph: {e}")
            return False
            
    async def store_performance_metrics(self, metrics: Dict[str, Any], source: str) -> bool:
        """
        Store performance metrics in the knowledge graph.
        
        Args:
            metrics: Dict containing performance metrics
            source: Source of the metrics (e.g., 'email_campaign', 'affiliate')
            
        Returns:
            True if successful, False otherwise
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return False
            
        try:
            # Create a unique node ID for the metrics
            metrics_id = f"metrics_{source}_{uuid.uuid4()}"
            
            # Prepare node attributes
            attributes = {
                "type": "performance_metrics",
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics
            }
            
            # Add the metrics node to the knowledge graph
            success = self.knowledge_graph.add_node(metrics_id, attributes)
            
            if success:
                # Connect the metrics to the metrics category
                self.knowledge_graph.add_edge("metrics", metrics_id, {"type": "contains"})
                
                # Connect to source if it exists as a node
                source_id = f"channel_{source.lower().replace(' ', '_')}"
                if self.knowledge_graph.get_node(source_id):
                    self.knowledge_graph.add_edge(source_id, metrics_id, {"type": "has_metrics"})
                    
                logger.info(f"Stored performance metrics from '{source}' in knowledge graph")
                return True
            else:
                logger.error(f"Failed to store performance metrics from '{source}' in knowledge graph")
                return False
                
        except Exception as e:
            logger.error(f"Error storing performance metrics in knowledge graph: {e}")
            return False
            
    async def get_revenue_goals(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get revenue goals from the knowledge graph.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of revenue goals
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return []
            
        try:
            # Query the knowledge graph for revenue goals
            attributes = {"type": "revenue_goal"}
            if status:
                attributes["status"] = status
                
            goals = self.knowledge_graph.query(node_type="revenue_goal", attributes=attributes)
            
            logger.info(f"Retrieved {len(goals)} revenue goals from knowledge graph")
            return goals
            
        except Exception as e:
            logger.error(f"Error retrieving revenue goals from knowledge graph: {e}")
            return []
            
    async def get_revenue_strategies(self, status: Optional[str] = None, strategy_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get revenue strategies from the knowledge graph.
        
        Args:
            status: Optional status filter
            strategy_type: Optional type filter
            
        Returns:
            List of revenue strategies
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return []
            
        try:
            # Query the knowledge graph for revenue strategies
            attributes = {"type": "revenue_strategy"}
            if status:
                attributes["status"] = status
            if strategy_type:
                attributes["strategy_type"] = strategy_type
                
            strategies = self.knowledge_graph.query(node_type="revenue_strategy", attributes=attributes)
            
            logger.info(f"Retrieved {len(strategies)} revenue strategies from knowledge graph")
            return strategies
            
        except Exception as e:
            logger.error(f"Error retrieving revenue strategies from knowledge graph: {e}")
            return []
            
    async def get_performance_metrics(self, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get performance metrics from the knowledge graph.
        
        Args:
            source: Optional source filter
            
        Returns:
            List of performance metrics
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return []
            
        try:
            # Query the knowledge graph for performance metrics
            attributes = {"type": "performance_metrics"}
            if source:
                attributes["source"] = source
                
            metrics = self.knowledge_graph.query(node_type="performance_metrics", attributes=attributes)
            
            logger.info(f"Retrieved {len(metrics)} performance metrics records from knowledge graph")
            return metrics
            
        except Exception as e:
            logger.error(f"Error retrieving performance metrics from knowledge graph: {e}")
            return []
            
    async def analyze_channel_performance(self) -> Dict[str, Any]:
        """
        Analyze performance across marketing channels using the knowledge graph.
        
        Returns:
            Dict containing channel performance analysis
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return {"status": "error", "message": "Knowledge graph not available"}
            
        try:
            # Get all channel nodes
            channels = self.knowledge_graph.query(node_type="category", attributes={"name": "Marketing Channels"})
            
            channel_performance = {}
            
            # For each channel, get associated metrics
            for channel in channels:
                channel_id = channel.get("id")
                
                # Get metrics nodes connected to this channel
                metrics_nodes = self.knowledge_graph.get_neighbors(channel_id, edge_type="has_metrics")
                
                # Aggregate metrics
                aggregated_metrics = {
                    "revenue": 0.0,
                    "conversions": 0,
                    "cost": 0.0,
                    "roi": 0.0
                }
                
                for metrics_node in metrics_nodes:
                    node_metrics = metrics_node.get("metrics", {})
                    
                    # Sum up metrics
                    aggregated_metrics["revenue"] += node_metrics.get("revenue", 0.0)
                    aggregated_metrics["conversions"] += node_metrics.get("conversions", 0)
                    aggregated_metrics["cost"] += node_metrics.get("cost", 0.0)
                    
                # Calculate ROI
                if aggregated_metrics["cost"] > 0:
                    aggregated_metrics["roi"] = (aggregated_metrics["revenue"] - aggregated_metrics["cost"]) / aggregated_metrics["cost"] * 100
                    
                channel_performance[channel.get("name")] = aggregated_metrics
                
            logger.info(f"Analyzed performance for {len(channel_performance)} channels")
            
            return {
                "status": "success",
                "channel_performance": channel_performance,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing channel performance: {e}")
            return {"status": "error", "message": str(e)}
            
    async def find_related_strategies(self, goal_id: str) -> List[Dict[str, Any]]:
        """
        Find strategies related to a specific revenue goal.
        
        Args:
            goal_id: ID of the revenue goal
            
        Returns:
            List of related strategies
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return []
            
        try:
            # Get strategies connected to this goal
            strategies = self.knowledge_graph.get_neighbors(goal_id, edge_type="supports")
            
            logger.info(f"Found {len(strategies)} strategies related to goal {goal_id}")
            return strategies
            
        except Exception as e:
            logger.error(f"Error finding related strategies: {e}")
            return []

    async def get_revenue_strategies(self) -> List[Dict[str, Any]]:
        """
        Get all revenue strategies from the knowledge graph.
        
        Returns:
            List of revenue strategy dictionaries
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return []
            
        try:
            # Get all nodes with type 'revenue_strategy'
            strategies = []
            nodes = self.knowledge_graph.get_nodes_by_attribute("type", "revenue_strategy")
            
            for node_id, attributes in nodes.items():
                strategies.append({
                    "id": node_id,
                    **attributes
                })
                
            return strategies
            
        except Exception as e:
            logger.error(f"Error retrieving revenue strategies from knowledge graph: {e}")
            return []
            
    async def get_strategy_metrics(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get metrics for a specific strategy from the knowledge graph.
        
        Args:
            strategy_id: ID of the strategy
            
        Returns:
            Dictionary with strategy metrics or empty dict if not found
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return {}
            
        try:
            # Get all metrics nodes connected to the strategy
            metrics_nodes = self.knowledge_graph.get_connected_nodes(
                node_id=strategy_id,
                edge_type="has_metrics",
                direction="outgoing"
            )
            
            if not metrics_nodes:
                logger.warning(f"No metrics found for strategy {strategy_id}")
                return {}
                
            # Get the most recent metrics (assuming timestamp is present)
            latest_metrics = None
            latest_timestamp = None
            
            for node_id, attributes in metrics_nodes.items():
                timestamp = attributes.get("timestamp")
                if timestamp and (latest_timestamp is None or timestamp > latest_timestamp):
                    latest_timestamp = timestamp
                    latest_metrics = {"id": node_id, **attributes}
                    
            return latest_metrics or {}
            
        except Exception as e:
            logger.error(f"Error retrieving strategy metrics from knowledge graph: {e}")
            return {}
            
    async def get_strategy_recommendations(self, strategy_id: str) -> List[Dict[str, Any]]:
        """
        Get recommendations for a specific strategy from the knowledge graph.
        
        Args:
            strategy_id: ID of the strategy
            
        Returns:
            List of recommendation dictionaries
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return []
            
        try:
            # Get all recommendation nodes connected to the strategy
            recommendation_nodes = self.knowledge_graph.get_connected_nodes(
                node_id=strategy_id,
                edge_type="has_recommendations",
                direction="outgoing"
            )
            
            if not recommendation_nodes:
                logger.warning(f"No recommendations found for strategy {strategy_id}")
                return []
                
            # Get the most recent recommendations
            latest_recommendations = None
            latest_timestamp = None
            
            for node_id, attributes in recommendation_nodes.items():
                timestamp = attributes.get("timestamp")
                if timestamp and (latest_timestamp is None or timestamp > latest_timestamp):
                    latest_timestamp = timestamp
                    latest_recommendations = attributes.get("recommendations", [])
                    
            return latest_recommendations or []
            
        except Exception as e:
            logger.error(f"Error retrieving strategy recommendations from knowledge graph: {e}")
            return []
            
    async def get_strategy_evaluation(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get evaluation for a specific strategy from the knowledge graph.
        
        Args:
            strategy_id: ID of the strategy
            
        Returns:
            Dictionary with strategy evaluation or empty dict if not found
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return {}
            
        try:
            # Get all evaluation nodes connected to the strategy
            evaluation_nodes = self.knowledge_graph.get_connected_nodes(
                node_id=strategy_id,
                edge_type="has_evaluation",
                direction="outgoing"
            )
            
            if not evaluation_nodes:
                logger.warning(f"No evaluation found for strategy {strategy_id}")
                return {}
                
            # Get the most recent evaluation
            latest_evaluation = None
            latest_timestamp = None
            
            for node_id, attributes in evaluation_nodes.items():
                timestamp = attributes.get("timestamp")
                if timestamp and (latest_timestamp is None or timestamp > latest_timestamp):
                    latest_timestamp = timestamp
                    latest_evaluation = {"id": node_id, **attributes}
                    
            return latest_evaluation or {}
            
        except Exception as e:
            logger.error(f"Error retrieving strategy evaluation from knowledge graph: {e}")
            return {}
            
    async def get_strategy_optimization(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get optimization plan for a specific strategy from the knowledge graph.
        
        Args:
            strategy_id: ID of the strategy
            
        Returns:
            Dictionary with strategy optimization plan or empty dict if not found
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return {}
            
        try:
            # Get all optimization nodes connected to the strategy
            optimization_nodes = self.knowledge_graph.get_connected_nodes(
                node_id=strategy_id,
                edge_type="has_optimization",
                direction="outgoing"
            )
            
            if not optimization_nodes:
                logger.warning(f"No optimization plan found for strategy {strategy_id}")
                return {}
                
            # Get the most recent optimization plan
            latest_optimization = None
            latest_timestamp = None
            
            for node_id, attributes in optimization_nodes.items():
                timestamp = attributes.get("timestamp")
                if timestamp and (latest_timestamp is None or timestamp > latest_timestamp):
                    latest_timestamp = timestamp
                    latest_optimization = {"id": node_id, **attributes}
                    
            return latest_optimization or {}
            
        except Exception as e:
            logger.error(f"Error retrieving strategy optimization from knowledge graph: {e}")
            return {}
            
    async def get_strategies_by_channel(self, channel_id: str) -> List[Dict[str, Any]]:
        """
        Get all strategies associated with a specific marketing channel.
        
        Args:
            channel_id: ID of the marketing channel
            
        Returns:
            List of strategy dictionaries
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return []
            
        try:
            # Get all strategy nodes connected to the channel
            strategies = []
            strategy_nodes = self.knowledge_graph.get_connected_nodes(
                node_id=channel_id,
                edge_type="uses_strategy",
                direction="outgoing"
            )
            
            for node_id, attributes in strategy_nodes.items():
                if attributes.get("type") == "revenue_strategy":
                    strategies.append({"id": node_id, **attributes})
                    
            return strategies
            
        except Exception as e:
            logger.error(f"Error retrieving strategies by channel from knowledge graph: {e}")
            return []
            
    async def get_strategies_by_segment(self, segment_id: str) -> List[Dict[str, Any]]:
        """
        Get revenue strategies targeting a specific customer segment.
        
        Args:
            segment_id: ID of the customer segment
            
        Returns:
            List of strategy dictionaries
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return []
            
        try:
            # Get all strategies connected to the segment
            strategies = []
            
            # Get nodes connected to the segment
            connected_nodes = self.knowledge_graph.get_connected_nodes(
                node_id=segment_id,
                edge_type="targeted_by",
                direction="outgoing"
            )
            
            for node_id, attributes in connected_nodes.items():
                if attributes.get("type") == "revenue_strategy":
                    strategies.append({
                        "id": node_id,
                        **attributes
                    })
                    
            return strategies
            
        except Exception as e:
            logger.error(f"Error finding strategies for segment {segment_id}: {e}")
            return []
            
    async def analyze_revenue_performance_by_channel(self) -> Dict[str, Any]:
        """
        Analyze revenue performance across different marketing channels.
        
        Returns:
            Dictionary with channel performance analysis
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return {"channels": [], "total_revenue": 0, "total_cost": 0, "roi": 0}
            
        try:
            # Get all channel nodes
            channel_nodes = {}
            for node_id, node_data in self.knowledge_graph.graph.nodes(data=True):
                if node_data.get("type") == "channel":
                    channel_nodes[node_id] = dict(node_data)
            
            # Analyze performance for each channel
            channel_performance = []
            total_revenue = 0
            total_cost = 0
            
            for channel_id, channel_data in channel_nodes.items():
                # Get strategies for this channel
                channel_strategies = await self.get_strategies_by_channel(channel_id)
                
                # Calculate performance metrics
                channel_revenue = 0
                channel_cost = 0
                strategy_count = len(channel_strategies)
                
                for strategy in channel_strategies:
                    # Get latest metrics for this strategy
                    metrics = await self.get_strategy_metrics(strategy["id"])
                    if metrics:
                        channel_revenue += metrics.get("revenue", 0)
                        channel_cost += metrics.get("cost", 0)
                
                # Calculate ROI
                channel_roi = 0
                if channel_cost > 0:
                    channel_roi = ((channel_revenue - channel_cost) / channel_cost) * 100
                
                # Add to total
                total_revenue += channel_revenue
                total_cost += channel_cost
                
                # Add channel performance data
                channel_performance.append({
                    "channel_id": channel_id,
                    "channel_name": channel_data.get("name", "Unknown Channel"),
                    "strategy_count": strategy_count,
                    "revenue": channel_revenue,
                    "cost": channel_cost,
                    "roi": channel_roi
                })
            
            # Calculate overall ROI
            overall_roi = 0
            if total_cost > 0:
                overall_roi = ((total_revenue - total_cost) / total_cost) * 100
            
            return {
                "channels": channel_performance,
                "total_revenue": total_revenue,
                "total_cost": total_cost,
                "roi": overall_roi
            }
            
        except Exception as e:
            logger.error(f"Error analyzing revenue performance by channel: {e}")
            return {"channels": [], "total_revenue": 0, "total_cost": 0, "roi": 0}
            
    async def analyze_revenue_performance_by_segment(self) -> Dict[str, Any]:
        """
        Analyze revenue performance across different customer segments.
        
        Returns:
            Dictionary with segment performance analysis
        """
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available")
            return {"segments": [], "total_revenue": 0, "total_cost": 0, "roi": 0}
            
        try:
            # Get all segment nodes
            segment_nodes = {}
            for node_id, node_data in self.knowledge_graph.graph.nodes(data=True):
                if node_data.get("type") == "segment":
                    segment_nodes[node_id] = dict(node_data)
            
            # Analyze performance for each segment
            segment_performance = []
            total_revenue = 0
            total_cost = 0
            
            for segment_id, segment_data in segment_nodes.items():
                # Get strategies for this segment
                segment_strategies = await self.get_strategies_by_segment(segment_id)
                
                # Calculate performance metrics
                segment_revenue = 0
                segment_cost = 0
                strategy_count = len(segment_strategies)
                
                for strategy in segment_strategies:
                    # Get latest metrics for this strategy
                    metrics = await self.get_strategy_metrics(strategy["id"])
                    if metrics:
                        segment_revenue += metrics.get("revenue", 0)
                        segment_cost += metrics.get("cost", 0)
                
                # Calculate ROI
                segment_roi = 0
                if segment_cost > 0:
                    segment_roi = ((segment_revenue - segment_cost) / segment_cost) * 100
                
                # Add to total
                total_revenue += segment_revenue
                total_cost += segment_cost
                
                # Add segment performance data
                segment_performance.append({
                    "segment_id": segment_id,
                    "segment_name": segment_data.get("name", "Unknown Segment"),
                    "strategy_count": strategy_count,
                    "revenue": segment_revenue,
                    "cost": segment_cost,
                    "roi": segment_roi
                })
            
            # Calculate overall ROI
            overall_roi = 0
            if total_cost > 0:
                overall_roi = ((total_revenue - total_cost) / total_cost) * 100
            
            return {
                "segments": segment_performance,
                "total_revenue": total_revenue,
                "total_cost": total_cost,
                "roi": overall_roi
            }
            
        except Exception as e:
            logger.error(f"Error analyzing revenue performance by segment: {e}")
            return {"segments": [], "total_revenue": 0, "total_cost": 0, "roi": 0}
