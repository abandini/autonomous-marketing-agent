"""
Orchestrator Integration module for the Revenue Optimization Framework.

This module provides the integration layer between the Revenue Optimization Framework
and the main Marketing Orchestrator.
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union
import asyncio
from datetime import datetime

# Import revenue components
from core.revenue.revenue_optimization_framework import RevenueOptimizationFramework
from core.revenue.revenue_workflow_integrator import RevenueWorkflowIntegrator
from core.revenue.revenue_goal_manager import GoalPeriod, GoalStatus
from core.revenue.forecast_models import ForecastingMethod, ScenarioType, TimeGranularity
from core.knowledge_graph.revenue_knowledge_graph import RevenueKnowledgeGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RevenueOrchestratorIntegration:
    """
    Integration between the Revenue Optimization Framework and the Marketing Orchestrator.
    
    This class:
    1. Initializes the Revenue Optimization Framework
    2. Registers revenue workflows with the orchestrator
    3. Connects revenue optimization to the knowledge graph
    4. Provides revenue-specific agent implementations
    """
    
    def __init__(
        self,
        orchestrator,
        knowledge_graph,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Revenue Orchestrator Integration.
        
        Args:
            orchestrator: Marketing Orchestrator instance
            knowledge_graph: Marketing Knowledge Graph instance
            config: Optional configuration parameters
        """
        self.orchestrator = orchestrator
        self.knowledge_graph = knowledge_graph
        self.config = config or {}
        
        # Create storage directory
        storage_dir = self.config.get("storage_dir", "data/revenue")
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        
        # Initialize Revenue Optimization Framework
        self.revenue_framework = RevenueOptimizationFramework(
            storage_dir=storage_dir,
            config=self.config
        )
        
        # Initialize Revenue Knowledge Graph extension
        self.revenue_kg = RevenueKnowledgeGraph(knowledge_graph)
        
        # Initialize Revenue Workflow Integrator
        self.workflow_integrator = RevenueWorkflowIntegrator(
            revenue_framework=self.revenue_framework,
            register_workflow_callback=self._register_workflow
        )
        
        # Register revenue agents with orchestrator
        self._register_agents()
        
        logger.info("Revenue Orchestrator Integration initialized")
    
    def _register_workflow(self, workflow_name: str, workflow_function) -> None:
        """
        Register a revenue workflow with the orchestrator.
        
        Args:
            workflow_name: Name of the workflow
            workflow_function: Workflow function to register
        """
        self.orchestrator.register_workflow(
            f"revenue_{workflow_name}",
            workflow_function
        )
        
        logger.info(f"Registered revenue workflow: revenue_{workflow_name}")
    
    def _register_agents(self) -> None:
        """Register revenue agents with the orchestrator."""
        # Register Revenue Goal Manager
        self.orchestrator.register_agent(
            "revenue_goal_manager",
            self.revenue_framework.goal_manager
        )
        
        # Register Revenue Attribution Agent
        self.orchestrator.register_agent(
            "revenue_attribution",
            self.revenue_framework.attribution_agent
        )
        
        # Register Revenue Forecasting Engine
        self.orchestrator.register_agent(
            "revenue_forecasting",
            self.revenue_framework.forecasting_engine
        )
        
        logger.info("Registered revenue agents with orchestrator")
    
    async def sync_with_knowledge_graph(self) -> Dict[str, Any]:
        """
        Synchronize revenue data with the knowledge graph.
        
        Returns:
            Dict containing synchronization results
        """
        # Sync revenue goals
        goals_synced = await self._sync_revenue_goals()
        
        # Sync attribution data
        attribution_synced = await self._sync_attribution_data()
        
        # Sync forecasts
        forecasts_synced = await self._sync_forecasts()
        
        logger.info(f"Synchronized revenue data with knowledge graph: {goals_synced} goals, {attribution_synced} attributions, {forecasts_synced} forecasts")
        
        return {
            "status": "success",
            "goals_synced": goals_synced,
            "attribution_synced": attribution_synced,
            "forecasts_synced": forecasts_synced
        }
    
    async def _sync_revenue_goals(self) -> int:
        """
        Synchronize revenue goals with the knowledge graph.
        
        Returns:
            Number of goals synchronized
        """
        # Get all goals from the framework
        goals = await self.revenue_framework.goal_manager.get_all_goals()
        
        count = 0
        for goal in goals:
            # Add or update goal in knowledge graph
            goal_id = goal["id"]
            
            # Check if goal exists in knowledge graph
            existing_goal = self.revenue_kg.kg.get_node(goal_id)
            
            if existing_goal:
                # Update existing goal
                result = self.revenue_kg.update_revenue_goal(
                    goal_id=goal_id,
                    current_value=goal["current_value"],
                    status=goal["status"],
                    metrics=goal["metrics"]
                )
            else:
                # Add new goal
                result = self.revenue_kg.add_revenue_goal(
                    goal_id=goal_id,
                    name=goal["name"],
                    target_value=goal["target_value"],
                    period=goal["period"],
                    start_date=goal["start_date"],
                    end_date=goal["end_date"],
                    channel=goal.get("channel"),
                    segment=goal.get("segment"),
                    metrics=goal.get("metrics")
                )
            
            if result:
                count += 1
        
        return count
    
    async def _sync_attribution_data(self) -> int:
        """
        Synchronize attribution data with the knowledge graph.
        
        Returns:
            Number of attributions synchronized
        """
        # Get all customer journeys from the attribution agent
        journeys = await self.revenue_framework.attribution_agent.get_all_customer_journeys()
        
        count = 0
        for customer_id, journey in journeys.items():
            # Process each conversion in the journey
            for conversion in journey.get("conversions", []):
                # Create attribution ID
                attribution_id = f"attribution:{customer_id}:{conversion['timestamp']}"
                
                # Check if attribution exists in knowledge graph
                if not self.revenue_kg.kg.get_node(attribution_id):
                    # Get touchpoints
                    touchpoints = journey.get("touchpoints", [])
                    
                    # Get attribution model
                    model = conversion.get("attribution_model", "last_touch")
                    
                    # Add attribution to knowledge graph
                    result = self.revenue_kg.add_attribution_data(
                        attribution_id=attribution_id,
                        customer_id=customer_id,
                        touchpoints=touchpoints,
                        conversion_value=conversion.get("value", 0.0),
                        model=model,
                        attributes={
                            "timestamp": conversion.get("timestamp"),
                            "metadata": conversion.get("metadata", {})
                        }
                    )
                    
                    if result:
                        count += 1
        
        return count
    
    async def _sync_forecasts(self) -> int:
        """
        Synchronize forecasts with the knowledge graph.
        
        Returns:
            Number of forecasts synchronized
        """
        # Get all forecasts from the forecasting engine
        forecasts = self.revenue_framework.forecasting_engine.forecasts
        
        count = 0
        for forecast_id, forecast in forecasts.items():
            # Check if forecast exists in knowledge graph
            if not self.revenue_kg.kg.get_node(forecast_id):
                # Add forecast to knowledge graph
                result = self.revenue_kg.add_revenue_forecast(
                    forecast_id=forecast_id,
                    name=forecast.get("name", "Revenue Forecast"),
                    method=forecast.get("method", "unknown"),
                    predictions=forecast.get("predictions", []),
                    channel=forecast.get("channel"),
                    segment=forecast.get("segment"),
                    attributes={
                        "timestamp": forecast.get("timestamp"),
                        "granularity": forecast.get("granularity")
                    }
                )
                
                if result:
                    count += 1
        
        return count
    
    async def handle_revenue_phase(self, cycle_id: str, phase_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the Revenue Optimization phase of an improvement cycle.
        
        Args:
            cycle_id: ID of the improvement cycle
            phase_data: Data for the current phase
            
        Returns:
            Dict containing phase results
        """
        logger.info(f"Handling Revenue Optimization phase for cycle {cycle_id}")
        
        # Get cycle data
        cycle = self.orchestrator.get_improvement_cycle(cycle_id)
        if not cycle:
            return {
                "status": "error",
                "message": f"Improvement cycle {cycle_id} not found"
            }
        
        # Get phase tasks
        tasks = phase_data.get("tasks", [])
        
        # Execute each task
        task_results = []
        for task in tasks:
            task_type = task.get("type")
            task_params = task.get("parameters", {})
            
            result = await self._execute_revenue_task(task_type, task_params, cycle_id)
            task_results.append({
                "task_type": task_type,
                "status": result.get("status"),
                "result": result
            })
        
        # Sync with knowledge graph
        await self.sync_with_knowledge_graph()
        
        # Generate revenue insights
        insights = self.revenue_kg.get_revenue_insights()
        
        return {
            "status": "success",
            "cycle_id": cycle_id,
            "task_results": task_results,
            "insights": insights
        }
    
    async def _execute_revenue_task(
        self,
        task_type: str,
        parameters: Dict[str, Any],
        cycle_id: str
    ) -> Dict[str, Any]:
        """
        Execute a revenue optimization task.
        
        Args:
            task_type: Type of task to execute
            parameters: Task parameters
            cycle_id: ID of the improvement cycle
            
        Returns:
            Dict containing task results
        """
        if task_type == "set_revenue_goal":
            # Set a revenue goal
            goal = await self.revenue_framework.set_revenue_goal(
                name=parameters.get("name", "Revenue Goal"),
                target_value=parameters.get("target_value", 0.0),
                period=parameters.get("period", GoalPeriod.MONTHLY),
                start_date=parameters.get("start_date", datetime.now().isoformat()),
                end_date=parameters.get("end_date"),
                channel=parameters.get("channel"),
                segment=parameters.get("segment"),
                metrics=parameters.get("metrics")
            )
            
            return {
                "status": "success",
                "goal": goal
            }
            
        elif task_type == "forecast_revenue":
            # Generate revenue forecast
            forecast = await self.revenue_framework.forecast_revenue(
                periods=parameters.get("periods", 12),
                granularity=parameters.get("granularity", TimeGranularity.MONTHLY),
                channel=parameters.get("channel"),
                segment=parameters.get("segment")
            )
            
            return {
                "status": "success",
                "forecast": forecast
            }
            
        elif task_type == "analyze_channels":
            # Analyze channel performance
            analysis = await self.revenue_framework.analyze_channel_performance()
            
            return {
                "status": "success",
                "analysis": analysis
            }
            
        elif task_type == "optimize_allocation":
            # Optimize revenue allocation
            allocation = await self.revenue_framework.optimize_revenue_allocation(
                budget=parameters.get("budget", 0.0),
                forecast_id=parameters.get("forecast_id")
            )
            
            return {
                "status": "success",
                "allocation": allocation
            }
            
        elif task_type == "generate_report":
            # Generate revenue report
            report = await self.revenue_framework.generate_revenue_report(
                start_date=parameters.get("start_date"),
                end_date=parameters.get("end_date"),
                include_forecasts=parameters.get("include_forecasts", True),
                include_goals=parameters.get("include_goals", True),
                include_attribution=parameters.get("include_attribution", True)
            )
            
            return {
                "status": "success",
                "report": report
            }
            
        else:
            return {
                "status": "error",
                "message": f"Unknown revenue task type: {task_type}"
            }
    
    async def integrate_with_seo_content_generator(
        self,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integrate revenue optimization with the SEO Content Generator.
        
        Args:
            content_data: Data from the SEO Content Generator
            
        Returns:
            Dict containing integration results
        """
        logger.info("Integrating revenue optimization with SEO Content Generator")
        
        # Extract relevant data
        content_items = content_data.get("content_items", [])
        analytics = content_data.get("analytics", {})
        
        # Track content as revenue source if it has conversions
        sources_added = 0
        for item in content_items:
            item_id = item.get("id")
            if not item_id:
                continue
                
            # Check if content has conversion metrics
            conversions = analytics.get(item_id, {}).get("conversions", 0)
            revenue = analytics.get(item_id, {}).get("revenue", 0.0)
            
            if conversions > 0 and revenue > 0:
                # Add as revenue source
                source_id = f"content:{item_id}"
                
                result = self.revenue_kg.add_revenue_source(
                    source_id=source_id,
                    name=item.get("title", "Content"),
                    source_type="content",
                    attributes={
                        "url": item.get("url"),
                        "keywords": item.get("keywords", []),
                        "conversions": conversions,
                        "revenue": revenue
                    }
                )
                
                if result:
                    sources_added += 1
        
        # Generate revenue insights for content
        content_revenue = {}
        for item_id, metrics in analytics.items():
            revenue = metrics.get("revenue", 0.0)
            if revenue > 0:
                content_revenue[item_id] = revenue
        
        # Sort by revenue (highest first)
        sorted_content = sorted(
            content_revenue.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        top_content = [
            {"content_id": content_id, "revenue": revenue}
            for content_id, revenue in sorted_content[:5]
        ]
        
        return {
            "status": "success",
            "sources_added": sources_added,
            "top_revenue_content": top_content,
            "total_content_revenue": sum(content_revenue.values())
        }
    
    async def integrate_with_analytics_engine(
        self,
        analytics_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integrate revenue optimization with the Analytics Engine.
        
        Args:
            analytics_data: Data from the Analytics Engine
            
        Returns:
            Dict containing integration results
        """
        logger.info("Integrating revenue optimization with Analytics Engine")
        
        # Extract relevant data
        metrics = analytics_data.get("metrics", {})
        reports = analytics_data.get("reports", [])
        
        # Update revenue metrics
        revenue_metrics = {}
        for metric_name, metric_value in metrics.items():
            if "revenue" in metric_name.lower() or "conversion" in metric_name.lower():
                revenue_metrics[metric_name] = metric_value
        
        # Find revenue-related reports
        revenue_reports = []
        for report in reports:
            if "revenue" in report.get("title", "").lower():
                revenue_reports.append(report)
        
        # Load historical data if available
        historical_data = []
        for report in revenue_reports:
            data_points = report.get("data", {}).get("series", [])
            if data_points:
                for point in data_points:
                    if "timestamp" in point and "value" in point:
                        historical_data.append(point)
        
        # Load historical data into forecasting engine if available
        if historical_data:
            await self.revenue_framework.forecasting_engine.load_historical_data(
                data=historical_data
            )
            
            # Generate updated forecast
            forecast = await self.revenue_framework.forecast_revenue(
                periods=12,
                granularity=TimeGranularity.MONTHLY
            )
        else:
            forecast = None
        
        return {
            "status": "success",
            "revenue_metrics": revenue_metrics,
            "revenue_reports": len(revenue_reports),
            "historical_data_points": len(historical_data),
            "forecast": forecast
        }
