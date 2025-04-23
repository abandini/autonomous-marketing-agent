"""
Orchestrator module for the Autonomous Marketing Agent.

This module implements the central orchestration layer that coordinates
activities across specialized marketing agents.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Callable, Awaitable, Optional, Tuple
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CyclePhase(Enum):
    """Enum representing phases in a continuous improvement cycle."""
    WEBSITE_OPTIMIZATION = "website_optimization"
    MULTI_CHANNEL_MARKETING = "multi_channel_marketing"
    DATA_LEARNING = "data_learning"
    CONTENT_REFINEMENT = "content_refinement"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    SYSTEM_EXPANSION = "system_expansion"

class FeedbackLoopType(Enum):
    """Enum representing types of feedback loops in a continuous improvement cycle."""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

class ContinuousImprovementCycle:
    """Manages the continuous improvement cycle for marketing campaigns.
    
    This class implements the six-phase cycle for affiliate marketing:
    1. Website Optimization
    2. Multi-Channel Marketing
    3. Data Learning & Analysis
    4. Content & Offering Refinement
    5. Revenue Optimization
    6. System Expansion
    
    Each phase has specific tasks, metrics, and feedback loops to ensure
    continuous improvement and revenue growth.
    """
    
    def __init__(self, config_path: str = None):
        """Initialize the continuous improvement cycle.
        
        Args:
            config_path: Path to the cycle configuration file
        """
        self.phases = {}
        self.current_phase = None
        self.start_time = None
        self.last_phase_change = None
        self.metrics = {}
        self.feedback_loops = {}
        self.acceleration_strategies = {}
        
        if config_path:
            self.load_config(config_path)
        
    def load_config(self, config_path: str) -> None:
        """Load cycle configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
                
                # Load phases
                for phase_name, phase_config in config.get("phases", {}).items():
                    self.phases[phase_name] = phase_config
                
                # Load feedback loops
                for loop_name, loop_config in config.get("feedback_loops", {}).items():
                    self.feedback_loops[loop_name] = loop_config
                
                # Load acceleration strategies
                for strategy_name, strategy_config in config.get("acceleration_strategies", {}).items():
                    self.acceleration_strategies[strategy_name] = strategy_config
                
                logger.info(f"Loaded continuous improvement cycle config from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load cycle configuration: {str(e)}")
    
    def start_cycle(self, initial_phase: str = None) -> Dict[str, Any]:
        """Start the continuous improvement cycle.
        
        Args:
            initial_phase: Optional initial phase to start with
            
        Returns:
            Dict containing cycle status
        """
        self.start_time = datetime.now()
        self.last_phase_change = self.start_time
        
        # Set initial phase
        if initial_phase and initial_phase in self.phases:
            self.current_phase = initial_phase
        else:
            # Default to first phase
            self.current_phase = next(iter(self.phases)) if self.phases else None
        
        logger.info(f"Started continuous improvement cycle with phase: {self.current_phase}")
        return {
            "status": "success",
            "current_phase": self.current_phase,
            "start_time": self.start_time.isoformat()
        }
    
    def advance_phase(self) -> Dict[str, Any]:
        """Advance to the next phase in the cycle.
        
        Returns:
            Dict containing updated cycle status
        """
        if not self.current_phase or not self.phases:
            return {
                "status": "error",
                "message": "Cycle not started or no phases defined"
            }
        
        # Get ordered list of phases
        phase_keys = list(self.phases.keys())
        current_index = phase_keys.index(self.current_phase)
        next_index = (current_index + 1) % len(phase_keys)
        
        # Update phase
        previous_phase = self.current_phase
        self.current_phase = phase_keys[next_index]
        self.last_phase_change = datetime.now()
        
        logger.info(f"Advanced cycle from {previous_phase} to {self.current_phase}")
        return {
            "status": "success",
            "previous_phase": previous_phase,
            "current_phase": self.current_phase,
            "phase_change_time": self.last_phase_change.isoformat()
        }
    
    def get_current_phase_tasks(self) -> List[Dict[str, Any]]:
        """Get the tasks for the current phase.
        
        Returns:
            List of task configurations
        """
        if not self.current_phase or self.current_phase not in self.phases:
            return []
        
        return self.phases[self.current_phase].get("tasks", [])
    
    def get_phase_metrics(self, phase_name: str = None) -> Dict[str, Any]:
        """Get the metrics for a specific phase or the current phase.
        
        Args:
            phase_name: Optional name of the phase to get metrics for
            
        Returns:
            Dict containing phase metrics
        """
        target_phase = phase_name if phase_name else self.current_phase
        
        if not target_phase or target_phase not in self.phases:
            return {}
        
        return self.phases[target_phase].get("metrics", {})
    
    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update cycle metrics with new values.
        
        Args:
            metrics: Dict of metrics to update
        """
        for key, value in metrics.items():
            if key in self.metrics:
                # If existing metric is a list, append the new value
                if isinstance(self.metrics[key], list):
                    self.metrics[key].append(value)
                # If it's a number, update with the new value
                elif isinstance(self.metrics[key], (int, float)):
                    self.metrics[key] = value
                # Otherwise, replace with the new value
                else:
                    self.metrics[key] = value
            else:
                # Initialize the metric
                self.metrics[key] = value
    
    def trigger_feedback_loop(self, loop_type: str) -> Dict[str, Any]:
        """Trigger a feedback loop of the specified type.
        
        Args:
            loop_type: Type of feedback loop to trigger (short, medium, long)
            
        Returns:
            Dict containing feedback loop configuration
        """
        if loop_type not in self.feedback_loops:
            return {
                "status": "error",
                "message": f"Feedback loop type not found: {loop_type}"
            }
        
        loop_config = self.feedback_loops[loop_type]
        logger.info(f"Triggered {loop_type} feedback loop")
        
        return {
            "status": "success",
            "loop_type": loop_type,
            "loop_config": loop_config
        }
    
    def apply_acceleration_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """Apply an acceleration strategy to the cycle.
        
        Args:
            strategy_name: Name of the acceleration strategy to apply
            
        Returns:
            Dict containing strategy application results
        """
        if strategy_name not in self.acceleration_strategies:
            return {
                "status": "error",
                "message": f"Acceleration strategy not found: {strategy_name}"
            }
        
        strategy = self.acceleration_strategies[strategy_name]
        logger.info(f"Applied acceleration strategy: {strategy_name}")
        
        return {
            "status": "success",
            "strategy_name": strategy_name,
            "strategy": strategy
        }
    
    def get_cycle_status(self) -> Dict[str, Any]:
        """Get the current status of the improvement cycle.
        
        Returns:
            Dict containing cycle status information
        """
        if not self.start_time:
            return {
                "status": "not_started"
            }
        
        current_time = datetime.now()
        cycle_duration = (current_time - self.start_time).total_seconds()
        phase_duration = (current_time - self.last_phase_change).total_seconds()
        
        return {
            "status": "running",
            "start_time": self.start_time.isoformat(),
            "current_phase": self.current_phase,
            "cycle_duration_seconds": cycle_duration,
            "phase_duration_seconds": phase_duration,
            "metrics": self.metrics
        }

class MarketingOrchestrator:
    """
    Central orchestrator that coordinates all marketing agents and activities.
    
    The orchestrator is responsible for:
    1. Initializing and managing all specialized agents
    2. Coordinating workflows across agents
    3. Managing the execution of marketing campaigns
    4. Monitoring performance and adjusting strategies
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Marketing Orchestrator.
        
        Args:
            config_path: Path to the configuration file
        """
        self.agents = {}
        self.workflows = {}
        self.active_campaigns = {}
        self.improvement_cycles = {}
        self.goals = {}
        self.config = self._load_config(config_path)
        self.knowledge_graph = None
        self.event_loop = asyncio.get_event_loop()
        logger.info("Marketing Orchestrator initialized")
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing configuration settings
        """
        if not config_path:
            logger.warning("No config path provided, using default settings")
            return {}
            
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return {}
    
    def register_agent(self, agent_type: str, agent_instance: Any) -> None:
        """
        Register a specialized marketing agent with the orchestrator.
        
        Args:
            agent_type: Type of the agent (e.g., 'seo', 'content', 'social')
            agent_instance: Instance of the agent
        """
        self.agents[agent_type] = agent_instance
        logger.info(f"Registered {agent_type} agent")
        
    def register_workflow(self, workflow_name: str, workflow_config: Dict[str, Any]) -> None:
        """
        Register a marketing workflow with the orchestrator.
        
        Args:
            workflow_name: Name of the workflow
            workflow_config: Configuration for the workflow
        """
        self.workflows[workflow_name] = workflow_config
        logger.info(f"Registered workflow: {workflow_name}")
        
    def set_knowledge_graph(self, knowledge_graph: Any) -> None:
        """
        Set the knowledge graph for the orchestrator.
        
        Args:
            knowledge_graph: Knowledge graph instance
        """
        self.knowledge_graph = knowledge_graph
        logger.info("Knowledge graph connected to orchestrator")
        
    async def execute_workflow(self, workflow_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a marketing workflow asynchronously.
        
        Args:
            workflow_name: Name of the workflow to execute
            params: Parameters for the workflow
            
        Returns:
            Dict containing workflow execution results
        """
        if workflow_name not in self.workflows:
            logger.error(f"Workflow {workflow_name} not found")
            return {"status": "error", "message": f"Workflow {workflow_name} not found"}
            
        workflow = self.workflows[workflow_name]
        results = {}
        
        try:
            # Execute each step in the workflow
            for step in workflow["steps"]:
                agent_type = step["agent"]
                action = step["action"]
                
                if agent_type not in self.agents:
                    logger.error(f"Agent {agent_type} not found")
                    continue
                    
                agent = self.agents[agent_type]
                step_params = {**step.get("params", {}), **(params or {})}
                
                # Execute the agent action
                step_result = await agent.execute_action(action, step_params)
                results[f"{agent_type}_{action}"] = step_result
                
                # Check if we need to continue based on step result
                if step.get("continue_on_failure", False) is False and step_result.get("status") != "success":
                    logger.warning(f"Workflow {workflow_name} stopped at step {agent_type}_{action}")
                    break
                    
            return {
                "status": "success",
                "workflow": workflow_name,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_name}: {str(e)}")
            return {
                "status": "error",
                "workflow": workflow_name,
                "message": str(e)
            }
    
    def create_campaign(self, campaign_config: Dict[str, Any]) -> str:
        """
        Create a new marketing campaign.
        
        Args:
            campaign_config: Configuration for the campaign
            
        Returns:
            Campaign ID
        """
        campaign_id = campaign_config.get("id", f"campaign_{len(self.active_campaigns) + 1}")
        self.active_campaigns[campaign_id] = {
            "config": campaign_config,
            "status": "created",
            "metrics": {},
            "created_at": asyncio.get_event_loop().time()
        }
        
        logger.info(f"Created campaign: {campaign_id}")
        return campaign_id
        
    def start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Start a marketing campaign.
        
        Args:
            campaign_id: ID of the campaign to start
            
        Returns:
            Dict containing campaign status
        """
        if campaign_id not in self.active_campaigns:
            logger.error(f"Campaign {campaign_id} not found")
            return {"status": "error", "message": f"Campaign {campaign_id} not found"}
            
        campaign = self.active_campaigns[campaign_id]
        campaign["status"] = "running"
        
        # Schedule the campaign workflows
        for workflow in campaign["config"].get("workflows", []):
            asyncio.create_task(self.execute_workflow(
                workflow["name"],
                workflow.get("params", {})
            ))
            
        logger.info(f"Started campaign: {campaign_id}")
        return {"status": "success", "campaign_id": campaign_id}
        
    def stop_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Stop a marketing campaign.
        
        Args:
            campaign_id: ID of the campaign to stop
            
        Returns:
            Dict containing campaign status
        """
        if campaign_id not in self.active_campaigns:
            logger.error(f"Campaign {campaign_id} not found")
            return {"status": "error", "message": f"Campaign {campaign_id} not found"}
            
        campaign = self.active_campaigns[campaign_id]
        campaign["status"] = "stopped"
        
        logger.info(f"Stopped campaign: {campaign_id}")
        return {"status": "success", "campaign_id": campaign_id}
        
    def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get the status of a marketing campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dict containing campaign status and metrics
        """
        if campaign_id not in self.active_campaigns:
            logger.error(f"Campaign {campaign_id} not found")
            return {"status": "error", "message": f"Campaign {campaign_id} not found"}
            
        return self.active_campaigns[campaign_id]
        
    def start(self) -> None:
        """
        Start the marketing orchestrator.
        """
        logger.info("Starting Marketing Orchestrator")
        
        # Initialize all agents
        for agent_config in self.config.get("agents", []):
            agent_type = agent_config["type"]
            agent_class = self._get_agent_class(agent_type)
            
            if agent_class:
                agent_instance = agent_class(agent_config)
                self.register_agent(agent_type, agent_instance)
                
        # Initialize knowledge graph
        if "knowledge_graph" in self.config:
            from core.knowledge_graph.knowledge_graph import MarketingKnowledgeGraph
            self.knowledge_graph = MarketingKnowledgeGraph(self.config["knowledge_graph"])
            
        # Load workflows
        for workflow_config in self.config.get("workflows", []):
            self.register_workflow(workflow_config["name"], workflow_config)
            
        logger.info("Marketing Orchestrator started")
        
    def _get_agent_class(self, agent_type: str) -> Any:
        """
        Get the agent class based on agent type.
        
        Args:
            agent_type: Type of the agent
            
        Returns:
            Agent class
        """
        agent_mapping = {
            "seo": "core.agents.seo_agent.SEOAgent",
            "content": "core.agents.content_agent.ContentAgent",
            "social": "core.agents.social_media_agent.SocialMediaAgent",
            "email": "core.agents.email_agent.EmailAgent",
            "advertising": "core.agents.advertising_agent.AdvertisingAgent",
            "affiliate": "core.agents.affiliate_agent.affiliate_agent.AffiliateAgent"
        }
        
        if agent_type not in agent_mapping:
            logger.error(f"Unknown agent type: {agent_type}")
            return None
            
        try:
            module_path, class_name = agent_mapping[agent_type].rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to import agent class for {agent_type}: {str(e)}")
            return None
            
    def register_goal(self, goal_name: str, goal_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a marketing goal with the orchestrator.
        
        Args:
            goal_name: Name of the goal
            goal_config: Configuration for the goal
            
        Returns:
            Dict containing registration status
        """
        goal_id = f"goal_{uuid.uuid4().hex[:8]}"
        
        self.goals[goal_id] = {
            "id": goal_id,
            "name": goal_name,
            "config": goal_config,
            "status": "registered",
            "created_at": datetime.now().isoformat(),
            "metrics": {},
            "campaigns": []
        }
        
        logger.info(f"Registered goal: {goal_name} with ID {goal_id}")
        return {
            "status": "success",
            "goal_id": goal_id,
            "goal_name": goal_name
        }
        
    def create_improvement_cycle(self, cycle_name: str, config_path: str) -> Dict[str, Any]:
        """
        Create a continuous improvement cycle.
        
        Args:
            cycle_name: Name of the improvement cycle
            config_path: Path to the cycle configuration file
            
        Returns:
            Dict containing cycle creation status
        """
        cycle_id = f"cycle_{uuid.uuid4().hex[:8]}"
        
        try:
            cycle = ContinuousImprovementCycle(config_path)
            self.improvement_cycles[cycle_id] = {
                "id": cycle_id,
                "name": cycle_name,
                "cycle": cycle,
                "status": "created",
                "created_at": datetime.now().isoformat(),
                "associated_campaigns": []
            }
            
            logger.info(f"Created improvement cycle: {cycle_name} with ID {cycle_id}")
            return {
                "status": "success",
                "cycle_id": cycle_id,
                "cycle_name": cycle_name
            }
        except Exception as e:
            logger.error(f"Failed to create improvement cycle: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create improvement cycle: {str(e)}"
            }
            
    def start_improvement_cycle(self, cycle_id: str, initial_phase: str = None) -> Dict[str, Any]:
        """
        Start a continuous improvement cycle.
        
        Args:
            cycle_id: ID of the cycle to start
            initial_phase: Optional initial phase to start with
            
        Returns:
            Dict containing cycle start status
        """
        if cycle_id not in self.improvement_cycles:
            logger.error(f"Improvement cycle {cycle_id} not found")
            return {
                "status": "error",
                "message": f"Improvement cycle {cycle_id} not found"
            }
            
        cycle_info = self.improvement_cycles[cycle_id]
        cycle = cycle_info["cycle"]
        
        result = cycle.start_cycle(initial_phase)
        
        if result["status"] == "success":
            cycle_info["status"] = "running"
            cycle_info["start_time"] = datetime.now().isoformat()
            
            logger.info(f"Started improvement cycle: {cycle_id}")
            return {
                "status": "success",
                "cycle_id": cycle_id,
                "cycle_name": cycle_info["name"],
                "current_phase": result["current_phase"]
            }
        else:
            return result
            
    def advance_cycle_phase(self, cycle_id: str) -> Dict[str, Any]:
        """
        Advance a continuous improvement cycle to the next phase.
        
        Args:
            cycle_id: ID of the cycle to advance
            
        Returns:
            Dict containing phase advancement status
        """
        if cycle_id not in self.improvement_cycles:
            logger.error(f"Improvement cycle {cycle_id} not found")
            return {
                "status": "error",
                "message": f"Improvement cycle {cycle_id} not found"
            }
            
        cycle_info = self.improvement_cycles[cycle_id]
        cycle = cycle_info["cycle"]
        
        result = cycle.advance_phase()
        
        if result["status"] == "success":
            logger.info(f"Advanced cycle {cycle_id} from {result['previous_phase']} to {result['current_phase']}")
            
            # Execute phase-specific workflows
            self._execute_phase_workflows(cycle_id, result["current_phase"])
            
            return {
                "status": "success",
                "cycle_id": cycle_id,
                "cycle_name": cycle_info["name"],
                "previous_phase": result["previous_phase"],
                "current_phase": result["current_phase"]
            }
        else:
            return result
            
    def _execute_phase_workflows(self, cycle_id: str, phase_name: str) -> None:
        """
        Execute workflows associated with a specific phase of an improvement cycle.
        
        Args:
            cycle_id: ID of the improvement cycle
            phase_name: Name of the phase
        """
        if cycle_id not in self.improvement_cycles:
            logger.error(f"Improvement cycle {cycle_id} not found")
            return
            
        cycle_info = self.improvement_cycles[cycle_id]
        cycle = cycle_info["cycle"]
        
        # Get tasks for the current phase
        tasks = cycle.get_current_phase_tasks()
        
        for task in tasks:
            workflow_name = task.get("workflow")
            if workflow_name and workflow_name in self.workflows:
                params = task.get("params", {})
                
                # Add cycle context to params
                params["cycle_id"] = cycle_id
                params["phase_name"] = phase_name
                
                # Execute workflow asynchronously
                asyncio.create_task(self.execute_workflow(workflow_name, params))
                logger.info(f"Scheduled phase workflow: {workflow_name} for cycle {cycle_id}")
            else:
                logger.warning(f"Workflow {workflow_name} not found for task in phase {phase_name}")
                
    def trigger_feedback_loop(self, cycle_id: str, loop_type: str) -> Dict[str, Any]:
        """
        Trigger a feedback loop in a continuous improvement cycle.
        
        Args:
            cycle_id: ID of the improvement cycle
            loop_type: Type of feedback loop to trigger (short, medium, long)
            
        Returns:
            Dict containing feedback loop trigger status
        """
        if cycle_id not in self.improvement_cycles:
            logger.error(f"Improvement cycle {cycle_id} not found")
            return {
                "status": "error",
                "message": f"Improvement cycle {cycle_id} not found"
            }
            
        cycle_info = self.improvement_cycles[cycle_id]
        cycle = cycle_info["cycle"]
        
        result = cycle.trigger_feedback_loop(loop_type)
        
        if result["status"] == "success":
            logger.info(f"Triggered {loop_type} feedback loop for cycle {cycle_id}")
            
            # Execute feedback loop workflows
            loop_config = result["loop_config"]
            for workflow_name in loop_config.get("workflows", []):
                if workflow_name in self.workflows:
                    params = {
                        "cycle_id": cycle_id,
                        "loop_type": loop_type,
                        "feedback_config": loop_config
                    }
                    
                    # Execute workflow asynchronously
                    asyncio.create_task(self.execute_workflow(workflow_name, params))
                    logger.info(f"Scheduled feedback loop workflow: {workflow_name} for cycle {cycle_id}")
                else:
                    logger.warning(f"Workflow {workflow_name} not found for feedback loop {loop_type}")
            
            return {
                "status": "success",
                "cycle_id": cycle_id,
                "cycle_name": cycle_info["name"],
                "loop_type": loop_type,
                "loop_config": loop_config
            }
        else:
            return result
            
    def apply_acceleration_strategy(self, cycle_id: str, strategy_name: str) -> Dict[str, Any]:
        """
        Apply an acceleration strategy to a continuous improvement cycle.
        
        Args:
            cycle_id: ID of the improvement cycle
            strategy_name: Name of the acceleration strategy to apply
            
        Returns:
            Dict containing strategy application status
        """
        if cycle_id not in self.improvement_cycles:
            logger.error(f"Improvement cycle {cycle_id} not found")
            return {
                "status": "error",
                "message": f"Improvement cycle {cycle_id} not found"
            }
            
        cycle_info = self.improvement_cycles[cycle_id]
        cycle = cycle_info["cycle"]
        
        result = cycle.apply_acceleration_strategy(strategy_name)
        
        if result["status"] == "success":
            logger.info(f"Applied acceleration strategy {strategy_name} to cycle {cycle_id}")
            
            # Execute strategy-specific workflows
            strategy = result["strategy"]
            for workflow_name in strategy.get("workflows", []):
                if workflow_name in self.workflows:
                    params = {
                        "cycle_id": cycle_id,
                        "strategy_name": strategy_name,
                        "strategy_config": strategy
                    }
                    
                    # Execute workflow asynchronously
                    asyncio.create_task(self.execute_workflow(workflow_name, params))
                    logger.info(f"Scheduled acceleration strategy workflow: {workflow_name} for cycle {cycle_id}")
                else:
                    logger.warning(f"Workflow {workflow_name} not found for acceleration strategy {strategy_name}")
            
            return {
                "status": "success",
                "cycle_id": cycle_id,
                "cycle_name": cycle_info["name"],
                "strategy_name": strategy_name,
                "strategy": strategy
            }
        else:
            return result
            
    def get_cycle_status(self, cycle_id: str) -> Dict[str, Any]:
        """
        Get the status of a continuous improvement cycle.
        
        Args:
            cycle_id: ID of the improvement cycle
            
        Returns:
            Dict containing cycle status
        """
        if cycle_id not in self.improvement_cycles:
            logger.error(f"Improvement cycle {cycle_id} not found")
            return {
                "status": "error",
                "message": f"Improvement cycle {cycle_id} not found"
            }
            
        cycle_info = self.improvement_cycles[cycle_id]
        cycle = cycle_info["cycle"]
        
        cycle_status = cycle.get_cycle_status()
        
        return {
            "status": "success",
            "cycle_id": cycle_id,
            "cycle_name": cycle_info["name"],
            "cycle_status": cycle_status,
            "associated_campaigns": cycle_info["associated_campaigns"]
        }
        
    def create_goal_oriented_campaign(self, campaign_config: Dict[str, Any], goal_id: str, cycle_id: str = None) -> Dict[str, Any]:
        """
        Create a goal-oriented marketing campaign associated with a specific goal and optionally an improvement cycle.
        
        Args:
            campaign_config: Configuration for the campaign
            goal_id: ID of the goal to associate with the campaign
            cycle_id: Optional ID of the improvement cycle to associate with the campaign
            
        Returns:
            Dict containing campaign creation status
        """
        if goal_id not in self.goals:
            logger.error(f"Goal {goal_id} not found")
            return {
                "status": "error",
                "message": f"Goal {goal_id} not found"
            }
            
        if cycle_id and cycle_id not in self.improvement_cycles:
            logger.error(f"Improvement cycle {cycle_id} not found")
            return {
                "status": "error",
                "message": f"Improvement cycle {cycle_id} not found"
            }
            
        # Create campaign ID
        campaign_id = f"campaign_{uuid.uuid4().hex[:8]}"
        
        # Create campaign object
        campaign = {
            "id": campaign_id,
            "name": campaign_config.get("name", "Unnamed Campaign"),
            "config": campaign_config,
            "goal_id": goal_id,
            "cycle_id": cycle_id,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "metrics": {},
            "workflows": []
        }
        
        # Store campaign
        self.active_campaigns[campaign_id] = campaign
        
        # Update goal with campaign reference
        self.goals[goal_id]["campaigns"].append(campaign_id)
        
        # Update cycle with campaign reference if provided
        if cycle_id:
            self.improvement_cycles[cycle_id]["associated_campaigns"].append(campaign_id)
            
        logger.info(f"Created goal-oriented campaign: {campaign_id} for goal {goal_id}")
        return {
            "status": "success",
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"],
            "goal_id": goal_id,
            "cycle_id": cycle_id
        }
        
    def update_campaign_metrics(self, campaign_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update metrics for a marketing campaign and propagate to associated goal and improvement cycle.
        
        Args:
            campaign_id: ID of the campaign to update
            metrics: Dict of metrics to update
            
        Returns:
            Dict containing update status
        """
        if campaign_id not in self.active_campaigns:
            logger.error(f"Campaign {campaign_id} not found")
            return {
                "status": "error",
                "message": f"Campaign {campaign_id} not found"
            }
            
        campaign = self.active_campaigns[campaign_id]
        
        # Update campaign metrics
        for key, value in metrics.items():
            campaign["metrics"][key] = value
            
        # Update goal metrics if associated
        goal_id = campaign.get("goal_id")
        if goal_id and goal_id in self.goals:
            goal = self.goals[goal_id]
            for key, value in metrics.items():
                if key in goal["metrics"]:
                    # If existing metric is a list, append the new value
                    if isinstance(goal["metrics"][key], list):
                        goal["metrics"][key].append(value)
                    # If it's a number, update with the new value
                    elif isinstance(goal["metrics"][key], (int, float)):
                        goal["metrics"][key] = value
                    # Otherwise, replace with the new value
                    else:
                        goal["metrics"][key] = value
                else:
                    # Initialize the metric
                    goal["metrics"][key] = value
                    
        # Update cycle metrics if associated
        cycle_id = campaign.get("cycle_id")
        if cycle_id and cycle_id in self.improvement_cycles:
            cycle = self.improvement_cycles[cycle_id]["cycle"]
            cycle.update_metrics(metrics)
            
        logger.info(f"Updated metrics for campaign {campaign_id}")
        return {
            "status": "success",
            "campaign_id": campaign_id,
            "updated_metrics": metrics
        }
        
    def get_goal_status(self, goal_id: str) -> Dict[str, Any]:
        """
        Get the status of a marketing goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Dict containing goal status and metrics
        """
        if goal_id not in self.goals:
            logger.error(f"Goal {goal_id} not found")
            return {
                "status": "error",
                "message": f"Goal {goal_id} not found"
            }
            
        goal = self.goals[goal_id]
        
        # Get associated campaign statuses
        campaign_statuses = []
        for campaign_id in goal["campaigns"]:
            if campaign_id in self.active_campaigns:
                campaign = self.active_campaigns[campaign_id]
                campaign_statuses.append({
                    "id": campaign_id,
                    "name": campaign["name"],
                    "status": campaign["status"],
                    "metrics": campaign["metrics"]
                })
                
        return {
            "status": "success",
            "goal_id": goal_id,
            "goal_name": goal["name"],
            "goal_status": goal["status"],
            "metrics": goal["metrics"],
            "campaigns": campaign_statuses
        }
