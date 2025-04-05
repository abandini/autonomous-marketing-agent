"""
Revenue Optimization Framework for the Autonomous Marketing Agent.

This module integrates all components of the Revenue Optimization Framework and
provides a unified interface for revenue optimization within the marketing agent.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import os
import asyncio

# Import revenue optimization components
from core.revenue.revenue_goal_manager import RevenueGoalManager, RevenueGoal, GoalStatus, GoalPeriod
from core.revenue.revenue_attribution_agent import AttributionModel, TouchPoint, CustomerJourney
from core.revenue.revenue_attribution_agent_impl import RevenueAttributionAgent
from core.revenue.forecast_models import ForecastingMethod, ScenarioType, TimeGranularity
from core.revenue.revenue_forecasting_engine_ext import RevenueForecastingEngineExtended, WarningLevel
from core.revenue.revenue_strategy_manager import RevenueStrategyManager, StrategyType, StrategyStatus
from core.revenue.revenue_performance_monitor import RevenuePerformanceMonitor, AlertType, AlertSeverity, MetricType
from core.revenue.revenue_knowledge_integration import RevenueKnowledgeIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RevenueOptimizationFramework:
    """
    Comprehensive framework for revenue optimization in the autonomous marketing agent.
    
    This framework integrates:
    - Revenue Goal Management
    - Revenue Attribution
    - Revenue Forecasting
    - Monetization Strategy
    - Strategy Management
    - Performance Monitoring
    
    It provides a unified interface for revenue optimization across marketing activities.
    """
    
    def __init__(
        self,
        storage_dir: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        knowledge_graph=None
    ):
        """
        Initialize the Revenue Optimization Framework.
        
        Args:
            storage_dir: Optional directory to store revenue data
            config: Optional configuration parameters
            knowledge_graph: Optional knowledge graph instance for integration
        """
        self.config = config or {}
        self.storage_dir = storage_dir or "data/revenue"
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        # Initialize storage paths
        goals_path = os.path.join(self.storage_dir, "revenue_goals.json")
        attribution_path = os.path.join(self.storage_dir, "revenue_attribution.json")
        forecasting_path = os.path.join(self.storage_dir, "revenue_forecasting.json")
        
        # Initialize components
        self.goal_manager = RevenueGoalManager(storage_path=goals_path)
        self.attribution_agent = RevenueAttributionAgent(storage_path=attribution_path)
        self.forecasting_engine = RevenueForecastingEngineExtended(storage_path=forecasting_path)
        self.strategy_manager = RevenueStrategyManager(storage_dir=self.storage_dir)
        self.performance_monitor = RevenuePerformanceMonitor(storage_dir=self.storage_dir)
        
        # Initialize knowledge graph integration if provided
        self.knowledge_graph = knowledge_graph
        self.knowledge_integration = RevenueKnowledgeIntegration(knowledge_graph=knowledge_graph) if knowledge_graph else None
        
        # Load data if available
        self._load_data()
        
        logger.info("Revenue Optimization Framework initialized")
    
    async def set_revenue_goal(
        self,
        name: str,
        target_value: float,
        period: Union[str, GoalPeriod],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        channel: Optional[str] = None,
        segment: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Set a revenue goal.
        
        Args:
            name: Name of the goal
            target_value: Target revenue value
            period: Goal period (e.g., DAILY, WEEKLY, MONTHLY)
            start_date: Start date for the goal
            end_date: End date for the goal
            channel: Optional channel for the goal
            segment: Optional segment for the goal
            metrics: Optional additional metrics for the goal
            
        Returns:
            Dict containing the created goal
        """
        # Create the goal
        # Create goal data dictionary with only valid parameters for RevenueGoal
        goal_data = {
            "name": name,
            "description": f"Revenue goal for {name}",  # Add a default description
            "target_value": target_value,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "channel": channel
        }
        
        # Store segment and metrics as metadata for knowledge graph integration
        metadata = {}
        if segment:
            metadata["segment"] = segment
        if metrics:
            metadata["metrics"] = metrics
        goal_id = self.goal_manager.create_goal(goal_data=goal_data)
        goal = self.goal_manager.get_goal(goal_id)
        
        # Store in knowledge graph if available
        if self.knowledge_integration and goal:
            # Convert RevenueGoal object to dictionary
            goal_dict = goal.to_dict() if hasattr(goal, 'to_dict') else goal
            
            # Add metadata to goal dictionary for knowledge graph
            if hasattr(goal_dict, 'update'):
                if segment:
                    goal_dict['segment'] = segment
                if metrics:
                    goal_dict['metrics'] = metrics
                    
            await self.knowledge_integration.store_revenue_goal(goal_dict)
        
        logger.info(f"Created revenue goal: {name} with target ${target_value}")
        return goal
    
    async def track_customer_touchpoint(
        self,
        customer_id: str,
        channel: str,
        campaign: Optional[str] = None,
        content: Optional[str] = None,
        interaction_type: Optional[str] = None,
        cost: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track a customer touchpoint for revenue attribution.
        
        Args:
            customer_id: Unique identifier for the customer
            channel: Marketing channel
            campaign: Optional campaign name
            content: Optional content identifier
            interaction_type: Type of interaction
            cost: Cost associated with this touchpoint
            metadata: Additional data about the touchpoint
            
        Returns:
            Dict containing the touchpoint data
        """
        # Record touchpoint
        touchpoint = await self.attribution_agent.record_touchpoint(
            customer_id=customer_id,
            channel=channel,
            campaign=campaign,
            content=content,
            interaction_type=interaction_type,
            cost=cost,
            metadata=metadata
        )
        
        logger.info(f"Tracked touchpoint for customer {customer_id} on channel {channel}")
        return touchpoint
    
    async def record_conversion(
        self,
        customer_id: str,
        value: float,
        goal_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a conversion and attribute revenue.
        
        Args:
            customer_id: Unique identifier for the customer
            value: Conversion value
            goal_id: Optional ID of the associated revenue goal
            metadata: Additional data about the conversion
            
        Returns:
            Dict containing the conversion data
        """
        # Record conversion for attribution
        conversion = await self.attribution_agent.record_conversion(
            customer_id=customer_id,
            value=value,
            metadata=metadata
        )
        
        # Update goal if specified
        if goal_id:
            await self.goal_manager.update_goal_progress(
                goal_id=goal_id,
                current_value=value,
                add_to_current=True
            )
        
        logger.info(f"Recorded conversion of ${value} for customer {customer_id}")
        return conversion
    
    async def forecast_revenue(
        self,
        periods: int,
        granularity: Union[str, TimeGranularity] = TimeGranularity.MONTHLY,
        channel: Optional[str] = None,
        segment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate revenue forecast.
        
        Args:
            periods: Number of periods to forecast
            granularity: Time granularity for forecasting
            channel: Optional channel for specific forecasting
            segment: Optional segment for specific forecasting
            
        Returns:
            Dict containing forecast data
        """
        # Convert string granularity to enum if needed
        if isinstance(granularity, str):
            granularity = TimeGranularity(granularity)
        
        # Generate forecast
        forecast = await self.forecasting_engine.predict_revenue(
            periods=periods,
            granularity=granularity,
            channel=channel,
            segment=segment
        )
        
        logger.info(f"Generated {periods} {granularity.value} revenue forecast")
        return forecast
    
    async def analyze_channel_performance(self) -> Dict[str, Any]:
        """
        Analyze performance across marketing channels.
        
        Returns:
            Dict containing channel performance data
        """
        # Get channel metrics from attribution agent
        channel_metrics = await self.attribution_agent.get_channel_metrics()
        
        # Get high ROI channels
        high_roi_channels = await self.attribution_agent.identify_high_roi_channels()
        
        # Combine data
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "channel_metrics": channel_metrics,
            "high_roi_channels": high_roi_channels["high_roi_channels"],
            "low_roi_channels": high_roi_channels["low_roi_channels"],
            "recommendations": high_roi_channels["recommendations"]
        }
        
        logger.info(f"Analyzed performance across {len(channel_metrics)} channels")
        return analysis
    
    async def optimize_revenue_allocation(
        self,
        budget: float,
        forecast_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize allocation of marketing budget for maximum revenue.
        
        Args:
            budget: Total marketing budget to allocate
            forecast_id: Optional forecast ID to use for optimization
            
        Returns:
            Dict containing allocation recommendations
        """
        # Get channel performance data
        channel_performance = await self.analyze_channel_performance()
        
        # Sort channels by ROI
        channels = []
        for channel, metrics in channel_performance["channel_metrics"].items():
            if metrics["touchpoints"] > 0 and metrics["cost"] > 0:
                channels.append({
                    "channel": channel,
                    "roi": metrics["roi"],
                    "conversion_rate": metrics["conversion_rate"],
                    "cost": metrics["cost"],
                    "revenue": metrics["revenue_contribution"]
                })
        
        # Sort by ROI (highest first)
        channels.sort(key=lambda x: x["roi"], reverse=True)
        
        # Allocate budget based on ROI
        allocations = []
        remaining_budget = budget
        
        # First pass: allocate to high-ROI channels
        for channel_data in channels:
            if channel_data["roi"] <= 0:
                continue  # Skip negative ROI channels
                
            # Calculate allocation based on ROI proportion
            total_roi = sum(c["roi"] for c in channels if c["roi"] > 0)
            allocation = (channel_data["roi"] / total_roi * budget) if total_roi > 0 else 0
            
            # Adjust based on current spending (don't reduce high performers too much)
            current_spend = channel_data["cost"]
            if allocation < current_spend * 0.8 and channel_data["roi"] > 50:  # High performer
                allocation = current_spend * 1.2  # Increase by 20%
            
            allocations.append({
                "channel": channel_data["channel"],
                "allocation": allocation,
                "percentage": allocation / budget * 100 if budget > 0 else 0,
                "current_spend": current_spend,
                "roi": channel_data["roi"],
                "expected_revenue": allocation * (channel_data["roi"] / 100 + 1) if channel_data["roi"] > 0 else 0
            })
            
            remaining_budget -= allocation
        
        # Second pass: adjust to match total budget
        if remaining_budget != 0 and allocations:
            # Distribute remaining budget proportionally
            total_allocated = sum(a["allocation"] for a in allocations)
            for allocation in allocations:
                adjustment = (allocation["allocation"] / total_allocated * remaining_budget) if total_allocated > 0 else 0
                allocation["allocation"] += adjustment
                allocation["percentage"] = allocation["allocation"] / budget * 100 if budget > 0 else 0
                allocation["expected_revenue"] = allocation["allocation"] * (allocation["roi"] / 100 + 1) if allocation["roi"] > 0 else 0
        
        # Calculate expected total revenue
        expected_total_revenue = sum(a["expected_revenue"] for a in allocations)
        
        # Create result
        result = {
            "timestamp": datetime.now().isoformat(),
            "total_budget": budget,
            "allocations": allocations,
            "expected_total_revenue": expected_total_revenue,
            "expected_roi": (expected_total_revenue - budget) / budget * 100 if budget > 0 else 0
        }
        
        logger.info(f"Optimized revenue allocation across {len(allocations)} channels with expected ROI of {result['expected_roi']:.2f}%")
        return result
    
    async def generate_revenue_report(
        self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        include_forecasts: bool = True,
        include_goals: bool = True,
        include_attribution: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive revenue report.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            include_forecasts: Whether to include forecasts in the report
            include_goals: Whether to include goals in the report
            include_attribution: Whether to include attribution data in the report
            
        Returns:
            Dict containing the revenue report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "date_range": {
                "start_date": start_date.isoformat() if isinstance(start_date, datetime) else start_date,
                "end_date": end_date.isoformat() if isinstance(end_date, datetime) else end_date
            }
        }
        
        # Include goals if requested
        if include_goals:
            goals = await self.goal_manager.get_all_goals()
            active_goals = [g for g in goals if g["status"] != GoalStatus.COMPLETED.value]
            completed_goals = [g for g in goals if g["status"] == GoalStatus.COMPLETED.value]
            
            report["goals"] = {
                "active": active_goals,
                "completed": completed_goals,
                "total_active": len(active_goals),
                "total_completed": len(completed_goals),
                "total_target_value": sum(g["target_value"] for g in goals),
                "total_current_value": sum(g["current_value"] for g in goals),
                "overall_progress": sum(g["current_value"] for g in goals) / sum(g["target_value"] for g in goals) * 100 if sum(g["target_value"] for g in goals) > 0 else 0
            }
        
        # Include attribution data if requested
        if include_attribution:
            channel_metrics = await self.attribution_agent.get_channel_metrics(start_date, end_date)
            campaign_metrics = await self.attribution_agent.get_campaign_metrics(start_date, end_date)
            
            report["attribution"] = {
                "channel_metrics": channel_metrics,
                "campaign_metrics": campaign_metrics,
                "total_revenue": sum(metrics["revenue_contribution"] for metrics in channel_metrics.values()),
                "total_cost": sum(metrics["cost"] for metrics in channel_metrics.values()),
                "overall_roi": sum(metrics["revenue_contribution"] for metrics in channel_metrics.values()) / sum(metrics["cost"] for metrics in channel_metrics.values()) * 100 if sum(metrics["cost"] for metrics in channel_metrics.values()) > 0 else 0
            }
        
        # Include forecasts if requested
        if include_forecasts:
            # Get most recent forecast
            forecasts = list(self.forecasting_engine.forecasts.values())
            if forecasts:
                # Sort by timestamp (newest first)
                forecasts.sort(key=lambda x: x["timestamp"], reverse=True)
                latest_forecast = forecasts[0]
                
                report["forecasts"] = {
                    "latest": latest_forecast,
                    "total_forecasted": sum(p["value"] for p in latest_forecast["predictions"])
                }
        
        logger.info("Generated comprehensive revenue report")
        return report
    
    async def create_revenue_strategy(
        self,
        name: str,
        strategy_type: Union[str, StrategyType],
        description: str,
        target_channels: Optional[List[str]] = None,
        target_segments: Optional[List[str]] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        goals: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new revenue strategy.
        
        Args:
            name: Name of the strategy
            strategy_type: Type of strategy (e.g., MONETIZATION, PRICING, PROMOTION)
            description: Description of the strategy
            target_channels: Optional list of target marketing channels
            target_segments: Optional list of target customer segments
            actions: Optional list of actions to implement the strategy
            goals: Optional list of goal IDs associated with this strategy
            metadata: Optional additional metadata
            
        Returns:
            Dict containing the created strategy
        """
        # Create the strategy
        strategy = await self.strategy_manager.create_strategy(
            name=name,
            strategy_type=strategy_type,
            description=description,
            target_channels=target_channels,
            target_segments=target_segments,
            actions=actions
        )
        
        # Associate with goals if provided
        if goals and strategy:
            strategy["goals"] = goals
            await self.strategy_manager.update_strategy(strategy["id"], {"goals": goals})
            
        # Store in knowledge graph if available
        if self.knowledge_integration and strategy:
            await self.knowledge_integration.store_revenue_strategy(strategy)
        
        logger.info(f"Created revenue strategy: {name} of type {strategy_type}")
        return strategy
    
    async def update_strategy_status(self, 
        strategy_id: str, 
        status: Union[str, StrategyStatus],
        performance_data: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the status of a revenue strategy.
        
        Args:
            strategy_id: ID of the strategy to update
            status: New status for the strategy
            performance_data: Optional performance data related to the strategy
            notes: Optional notes about the status update
            
        Returns:
            Dict containing the updated strategy data
        """
        updated_strategy = await self.strategy_manager.update_strategy_status(
            strategy_id=strategy_id,
            status=status,
            performance_data=performance_data,
            notes=notes
        )
        
        # If we have performance data, record it
        if performance_data:
            await self.performance_monitor.record_metrics(
                metrics=performance_data,
                source=f"strategy_{strategy_id}"
            )
            
            # Check if we need to generate alerts based on performance
            if status == StrategyStatus.ACTIVE:
                await self.performance_monitor.detect_anomalies(
                    metrics=performance_data,
                    context={"strategy_id": strategy_id}
                )
        
        logger.info(f"Updated strategy {strategy_id} status to {status}")
        return updated_strategy
    
    async def evaluate_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        Evaluate the performance of a revenue strategy.
        
        Args:
            strategy_id: ID of the strategy to evaluate
            
        Returns:
            Dict containing evaluation results
        """
        # Get strategy details
        strategy = await self.strategy_manager.get_strategy(strategy_id)
        
        # Get performance metrics related to this strategy
        metrics = await self.performance_monitor.get_metrics(
            filter_criteria={"source": f"strategy_{strategy_id}"}
        )
        
        # Get goals associated with this strategy
        goal_ids = strategy.get("goals", [])
        goals = []
        for goal_id in goal_ids:
            goal = await self.goal_manager.get_goal(goal_id)
            if goal:
                goals.append(goal)
        
        # Calculate goal progress
        goal_progress = []
        for goal in goals:
            progress = await self.goal_manager.calculate_goal_progress(goal["id"])
            goal_progress.append({
                "goal_id": goal["id"],
                "goal_name": goal["name"],
                "progress": progress
            })
        
        # Evaluate strategy effectiveness
        evaluation = await self.strategy_manager.evaluate_strategy_effectiveness(
            strategy_id=strategy_id,
            performance_metrics=metrics,
            goal_progress=goal_progress
        )
        
        logger.info(f"Evaluated strategy {strategy_id}")
        return evaluation
    
    async def get_strategy_recommendations(self, 
        goal_ids: Optional[List[str]] = None,
        performance_metrics: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get strategy recommendations based on goals and performance metrics.
        
        Args:
            goal_ids: Optional list of goal IDs to focus recommendations on
            performance_metrics: Optional performance metrics to consider
            limit: Maximum number of recommendations to return
            
        Returns:
            List of strategy recommendations
        """
        # Get goals if IDs are provided
        goals = []
        if goal_ids:
            for goal_id in goal_ids:
                goal = await self.goal_manager.get_goal(goal_id)
                if goal:
                    goals.append(goal)
        
        # Get latest forecast if available
        forecasts = None
        latest_forecast = await self.forecasting_engine.get_latest_forecast()
        if latest_forecast:
            forecasts = [latest_forecast]
        
        # Get recommendations
        recommendations = await self.strategy_manager.recommend_strategies(
            goals=goals,
            current_performance=performance_metrics,
            forecasts=forecasts,
            limit=limit
        )
        
        logger.info(f"Generated {len(recommendations)} strategy recommendations")
        return recommendations
    
    async def record_performance_metrics(
        self,
        metrics: Dict[str, Any],
        source: str,
        timestamp: Optional[Union[str, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Record performance metrics.
        
        Args:
            metrics: Dict of metrics to record
            source: Source of the metrics (e.g., 'email_campaign', 'affiliate')
            timestamp: Optional timestamp for the metrics
            
        Returns:
            Dict containing the recorded metrics
        """
        # Record the metrics
        result = await self.performance_monitor.record_metrics(metrics, source, timestamp)
        
        # Store in knowledge graph if available
        if self.knowledge_integration:
            await self.knowledge_integration.store_performance_metrics(metrics, source)
        
        logger.info(f"Recorded performance metrics from {source}")
        return result
    
    async def generate_performance_summary(self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        sources: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a summary of performance metrics.
        
        Args:
            start_date: Optional start date for filtering metrics
            end_date: Optional end date for filtering metrics
            sources: Optional list of sources to include
            metrics: Optional list of specific metrics to include
            
        Returns:
            Dict containing the performance summary
        """
        summary = await self.performance_monitor.generate_performance_summary(
            start_date=start_date,
            end_date=end_date,
            sources=sources,
            metrics=metrics
        )
        
        logger.info("Generated performance summary")
        return summary
    
    async def get_alerts(self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        severity: Optional[Union[str, AlertSeverity]] = None,
        alert_type: Optional[Union[str, AlertType]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get alerts from the performance monitor.
        
        Args:
            start_date: Optional start date for filtering alerts
            end_date: Optional end date for filtering alerts
            severity: Optional severity level to filter by
            alert_type: Optional alert type to filter by
            limit: Maximum number of alerts to return
            
        Returns:
            List of alerts matching the criteria
        """
        alerts = await self.performance_monitor.get_alerts(
            start_date=start_date,
            end_date=end_date,
            severity=severity,
            alert_type=alert_type,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(alerts)} alerts")
        return alerts
    
    async def integrate_with_affiliate_workflow(
        self,
        affiliate_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integrate revenue optimization with affiliate marketing workflow.
        
        Args:
            affiliate_data: Data from affiliate marketing workflow
            
        Returns:
            Dict containing integration results
        """
        # Extract relevant data
        affiliates = affiliate_data.get("affiliates", [])
        campaigns = affiliate_data.get("campaigns", [])
        
        # Track touchpoints and conversions
        for affiliate in affiliates:
            # Track affiliate as a channel
            customer_id = affiliate.get("referred_customer_id")
            if customer_id:
                # Record touchpoint
                await self.track_customer_touchpoint(
                    customer_id=customer_id,
                    channel="affiliate",
                    campaign=affiliate.get("campaign"),
                    content=affiliate.get("content"),
                    interaction_type="referral",
                    cost=affiliate.get("commission", 0.0),
                    metadata={
                        "affiliate_id": affiliate.get("id"),
                        "affiliate_name": affiliate.get("name")
                    }
                )
                
                # Record conversion if available
                conversion_value = affiliate.get("conversion_value", 0.0)
                if conversion_value > 0:
                    await self.record_conversion(
                        customer_id=customer_id,
                        value=conversion_value,
                        metadata={
                            "affiliate_id": affiliate.get("id"),
                            "affiliate_name": affiliate.get("name"),
                            "campaign": affiliate.get("campaign")
                        }
                    )
                    
                    # Record performance metrics for this affiliate
                    await self.record_performance_metrics(
                        metrics={
                            "revenue": conversion_value,
                            "commission": affiliate.get("commission", 0.0),
                            "roi": (conversion_value - affiliate.get("commission", 0.0)) / affiliate.get("commission", 1.0) * 100 if affiliate.get("commission", 0.0) > 0 else 0,
                            "conversion_rate": 1.0  # Since we have a conversion
                        },
                        source=f"affiliate_{affiliate.get('id')}",
                        timestamp=datetime.now().isoformat()
                    )
        
        # Generate optimization recommendations
        recommendations = []
        strategies = []
        alerts = []
        
        # Analyze affiliate performance
        affiliate_performance = {}
        for affiliate in affiliates:
            affiliate_id = affiliate.get("id")
            if not affiliate_id:
                continue
                
            # Calculate metrics
            cost = affiliate.get("commission", 0.0)
            revenue = affiliate.get("conversion_value", 0.0)
            roi = (revenue - cost) / cost * 100 if cost > 0 else 0
            
            affiliate_performance[affiliate_id] = {
                "name": affiliate.get("name"),
                "cost": cost,
                "revenue": revenue,
                "roi": roi,
                "conversions": 1 if revenue > 0 else 0
            }
            
            # Create a performance metric entry for monitoring
            await self.performance_monitor.record_metrics(
                metrics=affiliate_performance[affiliate_id],
                source=f"affiliate_{affiliate_id}"
            )
        
        # Generate recommendations based on performance
        for affiliate_id, performance in affiliate_performance.items():
            if performance["roi"] > 200:  # Very high ROI
                recommendation = {
                    "type": "affiliate_optimization",
                    "action": "increase_commission",
                    "affiliate_id": affiliate_id,
                    "affiliate_name": performance["name"],
                    "reason": f"Very high ROI of {performance['roi']:.2f}%",
                    "expected_impact": "Incentivize higher volume of referrals"
                }
                recommendations.append(recommendation)
                
                # Create a strategy for high-performing affiliates
                strategy = await self.strategy_manager.create_strategy(
                    name=f"Optimize {performance['name']} Partnership",
                    strategy_type=StrategyType.PARTNERSHIP,
                    description=f"Optimize partnership with high-performing affiliate {performance['name']}",
                    target_channels=["affiliate"],
                    actions=[
                        {
                            "action": "increase_commission",
                            "parameters": {
                                "affiliate_id": affiliate_id,
                                "current_commission": performance["cost"],
                                "suggested_commission": performance["cost"] * 1.2  # 20% increase
                            }
                        },
                        {
                            "action": "provide_exclusive_offers",
                            "parameters": {
                                "affiliate_id": affiliate_id
                            }
                        }
                    ],
                    metadata={
                        "current_roi": performance["roi"],
                        "current_revenue": performance["revenue"]
                    }
                )
                strategies.append(strategy)
                
            elif performance["roi"] < 0:  # Negative ROI
                recommendation = {
                    "type": "affiliate_optimization",
                    "action": "review_partnership",
                    "affiliate_id": affiliate_id,
                    "affiliate_name": performance["name"],
                    "reason": f"Negative ROI of {performance['roi']:.2f}%",
                    "expected_impact": "Reduce losses from unprofitable partnerships"
                }
                recommendations.append(recommendation)
                
                # Create an alert for low-performing affiliates
                alert = await self.performance_monitor.create_alert(
                    alert_type=AlertType.PERFORMANCE_ISSUE,
                    severity=AlertSeverity.MEDIUM,
                    message=f"Low-performing affiliate: {performance['name']}",
                    context={
                        "affiliate_id": affiliate_id,
                        "roi": performance["roi"],
                        "revenue": performance["revenue"],
                        "cost": performance["cost"]
                    },
                    recommended_action="Review partnership and consider adjusting commission structure or providing better resources"
                )
                alerts.append(alert)
                
                # Create a strategy for addressing low-performing affiliates
                strategy = await self.strategy_manager.create_strategy(
                    name=f"Review {performance['name']} Partnership",
                    strategy_type=StrategyType.OPTIMIZATION,
                    description=f"Address issues with low-performing affiliate {performance['name']}",
                    target_channels=["affiliate"],
                    actions=[
                        {
                            "action": "review_partnership",
                            "parameters": {
                                "affiliate_id": affiliate_id,
                                "current_roi": performance["roi"]
                            }
                        },
                        {
                            "action": "provide_training",
                            "parameters": {
                                "affiliate_id": affiliate_id,
                                "training_type": "conversion_optimization"
                            }
                        }
                    ],
                    metadata={
                        "current_roi": performance["roi"],
                        "current_revenue": performance["revenue"]
                    }
                )
                strategies.append(strategy)
        
        # Generate performance summary
        performance_summary = await self.performance_monitor.generate_performance_summary(
            sources=[f"affiliate_{a.get('id')}" for a in affiliates if a.get('id')]
        )
        
        # Create result
        result = {
            "timestamp": datetime.now().isoformat(),
            "affiliate_performance": affiliate_performance,
            "recommendations": recommendations,
            "strategies": strategies,
            "alerts": alerts,
            "performance_summary": performance_summary
        }
        
        logger.info(f"Integrated revenue optimization with affiliate workflow for {len(affiliates)} affiliates")
        return result
    
    async def integrate_with_continuous_improvement(
        self,
        cycle_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integrate revenue optimization with continuous improvement cycle.
        
        Args:
            cycle_data: Data from continuous improvement cycle
            
        Returns:
            Dict containing integration results
        """
        # Extract relevant data
        goals = cycle_data.get("goals", [])
        metrics = cycle_data.get("metrics", {})
        
        # Create or update revenue goals based on improvement cycle
        revenue_goals = []
        for goal in goals:
            if "revenue" in goal.get("type", "").lower():
                # Create or update revenue goal
                revenue_goal = await self.goal_manager.create_goal(
                    name=goal.get("name"),
                    target_value=goal.get("target_value", 0.0),
                    period=goal.get("period", "MONTHLY"),
                    start_date=goal.get("start_date"),
                    end_date=goal.get("end_date"),
                    channel=goal.get("channel"),
                    segment=goal.get("segment"),
                    metrics=goal.get("metrics")
                )
                
                revenue_goals.append(revenue_goal)
        
        # Record performance metrics
        if metrics:
            await self.performance_monitor.record_metrics(
                metrics=metrics,
                source="improvement_cycle"
            )
        
        # Generate revenue forecast based on improvement cycle
        forecast = None
        if metrics.get("revenue_data"):
            # Load historical data
            await self.forecasting_engine.load_historical_data(
                data=metrics["revenue_data"]
            )
            
            # Generate forecast
            forecast = await self.forecasting_engine.predict_revenue(
                periods=12,  # 12 periods
                granularity=TimeGranularity.MONTHLY
            )
        
        # Monitor goal progress
        alerts = await self.performance_monitor.monitor_goal_progress(
            goals=revenue_goals
        )
        
        # Recommend strategies based on goals and performance
        strategy_recommendations = await self.strategy_manager.recommend_strategies(
            goals=revenue_goals,
            current_performance=metrics,
            forecasts=[forecast] if forecast else None
        )
        
        # Create strategies from recommendations
        strategies = []
        for recommendation in strategy_recommendations:
            strategy = await self.strategy_manager.create_strategy(
                name=recommendation.get("name", "Revenue Strategy"),
                strategy_type=recommendation.get("strategy_type", StrategyType.MONETIZATION),
                description=recommendation.get("description", ""),
                target_channels=recommendation.get("target_channels"),
                actions=recommendation.get("actions")
            )
            strategies.append(strategy)
        
        # Create result
        result = {
            "timestamp": datetime.now().isoformat(),
            "revenue_goals": revenue_goals,
            "forecast": forecast,
            "alerts": alerts,
            "strategies": strategies,
            "recommendations": []
        }
        
        # Generate recommendations
        if forecast:
            # Check if forecast meets goals
            for goal in revenue_goals:
                goal_value = goal["target_value"]
                forecast_value = sum(p["value"] for p in forecast["predictions"])
                
                if forecast_value < goal_value:
                    # Forecast doesn't meet goal
                    gap = goal_value - forecast_value
                    gap_percentage = gap / goal_value * 100 if goal_value > 0 else 0
                    
                    result["recommendations"].append({
                        "type": "revenue_gap",
                        "goal_id": goal["id"],
                        "goal_name": goal["name"],
                        "gap": gap,
                        "gap_percentage": gap_percentage,
                        "action": "adjust_strategies",
                        "message": f"Forecasted revenue falls short of goal by ${gap:.2f} ({gap_percentage:.2f}%)"
                    })
        
        # Generate performance summary
        performance_summary = await self.performance_monitor.generate_performance_summary()
        result["performance_summary"] = performance_summary
        
        logger.info(f"Integrated revenue optimization with continuous improvement cycle for {len(revenue_goals)} goals")
        return result
    
    def _load_data(self) -> None:
        """Load data for all components."""
        # Load revenue goals
        self.goal_manager.load_goals()
        
        # Load attribution data
        self.attribution_agent.load_data()
        
        # Note: Forecasting engine doesn't have a load method in our implementation
        # In a real implementation, it would load models and historical data
        
        # Strategy manager and performance monitor load data in their constructors
        
        logger.info("Loaded revenue optimization data")
    
    def _save_data(self) -> None:
        """Save data for all components."""
        # Save methods are called automatically by the components
        pass
        
    async def analyze_channel_performance_from_knowledge_graph(self) -> Dict[str, Any]:
        """
        Analyze channel performance using data from the knowledge graph.
        
        Returns:
            Dict containing channel performance analysis
        """
        if not self.knowledge_integration:
            logger.warning("Knowledge graph integration not available")
            return {"status": "error", "message": "Knowledge graph integration not available"}
            
        return await self.knowledge_integration.analyze_channel_performance()
        
    async def get_strategies_for_goal(self, goal_id: str) -> List[Dict[str, Any]]:
        """
        Get strategies related to a specific revenue goal from the knowledge graph.
        
        Args:
            goal_id: ID of the revenue goal
            
        Returns:
            List of related strategies
        """
        if not self.knowledge_integration:
            logger.warning("Knowledge graph integration not available")
            return []
            
        return await self.knowledge_integration.find_related_strategies(goal_id)
        
    async def get_goals_from_knowledge_graph(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get revenue goals from the knowledge graph.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of revenue goals
        """
        if not self.knowledge_integration:
            logger.warning("Knowledge graph integration not available")
            return []
            
        return await self.knowledge_integration.get_revenue_goals(status)
        
    async def get_strategies_from_knowledge_graph(self, status: Optional[str] = None, strategy_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get revenue strategies from the knowledge graph.
        
        Args:
            status: Optional status filter
            strategy_type: Optional type filter
            
        Returns:
            List of revenue strategies
        """
        if not self.knowledge_integration:
            logger.warning("Knowledge graph integration not available")
            return []
            
        return await self.knowledge_integration.get_revenue_strategies(status, strategy_type)
