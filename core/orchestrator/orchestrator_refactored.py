"""
Refactored Marketing Orchestrator module for the Autonomous Marketing Agent.

This module implements the central orchestration layer that coordinates
activities across specialized marketing agents.
"""

import logging
import json
import yaml
import uuid
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Type

# Import utility modules
from core.orchestrator.utils.metrics import MetricsService
from core.orchestrator.utils.rate_limiter import CategoryRateLimiter
from core.orchestrator.utils.registry import AgentRegistry, WorkflowRegistry
from core.orchestrator.utils.config_validator import ConfigValidator
from core.orchestrator.cycle import ContinuousImprovementCycle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketingOrchestrator:
    """Central orchestrator that coordinates all marketing agents and activities.
    
    This class serves as the central coordination point for the GAMS system,
    managing specialized marketing agents, workflows, campaigns, and improvement cycles.
    It provides a unified interface for controlling the entire marketing system.
    """
    
    def __init__(self, config_path: str = None, agent_registry: AgentRegistry = None, 
                 workflow_registry: WorkflowRegistry = None, metrics_service: MetricsService = None,
                 rate_limiter: CategoryRateLimiter = None):
        """Initialize the Marketing Orchestrator.
        
        Args:
            config_path: Path to the orchestrator configuration file
            agent_registry: Optional agent registry instance
            workflow_registry: Optional workflow registry instance
            metrics_service: Optional metrics service instance
            rate_limiter: Optional rate limiter instance
        """
        # Initialize registries and services
        self.agent_registry = agent_registry or AgentRegistry()
        self.workflow_registry = workflow_registry or WorkflowRegistry()
        self.metrics_service = metrics_service or MetricsService()
        self.rate_limiter = rate_limiter or CategoryRateLimiter()
        
        # Initialize data structures
        self.agents = {}
        self.campaigns = {}
        self.improvement_cycles = {}
        self.goals = {}
        self.knowledge_graph = None
        self.config = {}
        self.test_mode = False
        self.test_results = {}
        
        # Load configuration if provided
        if config_path:
            self._load_and_validate_config(config_path)
            
        # Register default agents if registry is empty
        if not self.agent_registry.agent_classes:
            self.agent_registry.register_default_agents()
            
        logger.info("Marketing Orchestrator initialized")
        
    def _load_and_validate_config(self, config_path: str) -> bool:
        """Load and validate orchestrator configuration.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            True if configuration was loaded and validated successfully, False otherwise
        """
        # Use the config validator to load and validate the configuration
        config = None
        if config_path.endswith('.json'):
            config = ConfigValidator.load_and_validate_json(config_path, "orchestrator")
        elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
            config = ConfigValidator.load_and_validate_yaml(config_path, "orchestrator")
        else:
            # Default to JSON if file extension is not recognized
            config = ConfigValidator.load_and_validate_json(config_path, "orchestrator")
            
        if not config:
            logger.error(f"Failed to load valid orchestrator configuration from {config_path}")
            return False
            
        self.config = config
        
        # Configure rate limiter if settings are provided
        if "settings" in config and "rate_limits" in config["settings"]:
            self._configure_rate_limits(config["settings"]["rate_limits"])
            
        # Initialize agents from configuration
        self._initialize_agents_from_config()
        
        # Initialize workflows from configuration
        self._initialize_workflows_from_config()
        
        logger.info(f"Loaded and validated orchestrator configuration from {config_path}")
        return True
        
    def _configure_rate_limits(self, rate_limits_config: Dict[str, Any]) -> None:
        """Configure rate limits based on configuration.
        
        Args:
            rate_limits_config: Rate limits configuration
        """
        # Configure default rate limits
        if "default" in rate_limits_config:
            default_config = rate_limits_config["default"]
            if "per_minute" in default_config and "concurrent" in default_config:
                self.rate_limiter = CategoryRateLimiter(
                    default_max_per_minute=default_config["per_minute"],
                    default_max_concurrent=default_config["concurrent"]
                )
                logger.info(f"Configured default rate limits: {default_config['per_minute']} per minute, {default_config['concurrent']} concurrent")
                
        # Configure category-specific rate limits
        for category, limits in rate_limits_config.items():
            if category != "default" and "per_minute" in limits and "concurrent" in limits:
                self.rate_limiter.configure_category(
                    category,
                    limits["per_minute"],
                    limits["concurrent"]
                )
                logger.info(f"Configured rate limits for {category}: {limits['per_minute']} per minute, {limits['concurrent']} concurrent")
                
    def _initialize_agents_from_config(self) -> None:
        """Initialize agents from configuration."""
        if "agents" not in self.config:
            return
            
        for agent_type, agent_config in self.config["agents"].items():
            try:
                # Get agent class from registry or configuration
                agent_class = self._get_agent_class(agent_type)
                if not agent_class:
                    logger.warning(f"Could not find agent class for type: {agent_type}")
                    continue
                    
                # Initialize agent instance
                agent_instance = agent_class(**agent_config.get("config", {}))
                
                # Register agent
                self.register_agent(agent_type, agent_instance)
                logger.info(f"Initialized agent of type {agent_type} from configuration")
            except Exception as e:
                logger.error(f"Failed to initialize agent {agent_type}: {str(e)}")
                
    def _initialize_workflows_from_config(self) -> None:
        """Initialize workflows from configuration."""
        if "workflows" not in self.config:
            return
            
        for workflow_name, workflow_config in self.config["workflows"].items():
            try:
                # Register workflow
                self.register_workflow(workflow_name, workflow_config)
                logger.info(f"Registered workflow {workflow_name} from configuration")
            except Exception as e:
                logger.error(f"Failed to register workflow {workflow_name}: {str(e)}")
                
    def register_agent(self, agent_type: str, agent_instance: Any) -> None:
        """Register a specialized marketing agent with the orchestrator.
        
        Args:
            agent_type: Type of the agent
            agent_instance: Instance of the agent
        """
        self.agents[agent_type] = agent_instance
        logger.info(f"Registered agent of type: {agent_type}")
        
        # Record metrics
        self.metrics_service.record("orchestrator", "agent_registration", {
            "type": agent_type,
            "timestamp": datetime.now().isoformat()
        })
        
    def register_workflow(self, workflow_name: str, workflow_config: Dict[str, Any]) -> None:
        """Register a marketing workflow with the orchestrator.
        
        Args:
            workflow_name: Name of the workflow
            workflow_config: Configuration for the workflow
        """
        self.workflow_registry.register(workflow_name, None, workflow_config)
        logger.info(f"Registered workflow: {workflow_name}")
        
        # Record metrics
        self.metrics_service.record("orchestrator", "workflow_registration", {
            "name": workflow_name,
            "timestamp": datetime.now().isoformat()
        })
        
    def set_knowledge_graph(self, knowledge_graph: Any) -> None:
        """Set the knowledge graph for the orchestrator.
        
        Args:
            knowledge_graph: Knowledge graph instance
        """
        self.knowledge_graph = knowledge_graph
        logger.info("Set knowledge graph for orchestrator")
        
    async def execute_workflow(self, workflow_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a marketing workflow asynchronously.
        
        Args:
            workflow_name: Name of the workflow to execute
            params: Parameters for the workflow
            
        Returns:
            Dict containing workflow execution results
        """
        start_time = time.time()
        params = params or {}
        
        # Check if workflow exists
        workflow_info = self.workflow_registry.get(workflow_name)
        if not workflow_info:
            error_msg = f"Workflow {workflow_name} not found"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        # In test mode, return injected test result if available
        if self.test_mode and workflow_name in self.test_results:
            logger.info(f"Returning test result for workflow {workflow_name}")
            return self.test_results[workflow_name]
            
        # Execute workflow with retry
        try:
            result = await self._execute_workflow_with_retry(workflow_name, params)
            execution_time = time.time() - start_time
            
            # Record metrics
            self._record_workflow_metrics(workflow_name, execution_time, result)
            
            return result
        except Exception as e:
            error_msg = f"Error executing workflow {workflow_name}: {str(e)}"
            logger.error(error_msg)
            
            # Record error metrics
            self.metrics_service.record("workflow", f"{workflow_name}.error", {
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return {"status": "error", "message": error_msg}
            
    async def _execute_workflow_with_retry(self, workflow_name: str, params: Dict[str, Any], 
                                         max_retries: int = 3, retry_delay: float = 1.0) -> Dict[str, Any]:
        """Execute a workflow with retry capability.
        
        Args:
            workflow_name: Name of the workflow to execute
            params: Parameters for the workflow
            max_retries: Maximum number of retries
            retry_delay: Initial delay between retries (increases exponentially)
            
        Returns:
            Dict containing workflow execution results
            
        Raises:
            Exception: If all retries fail
        """
        workflow_info = self.workflow_registry.get(workflow_name)
        workflow_func = workflow_info.get("func")
        workflow_config = workflow_info.get("config", {})
        
        # If no function is registered, use the default execution method
        if not workflow_func:
            workflow_func = self._default_workflow_executor
            
        # Merge workflow config with params
        merged_params = {**workflow_config, **params}
        
        retries = 0
        last_error = None
        
        while retries <= max_retries:
            try:
                # Apply rate limiting
                if not await self.rate_limiter.acquire("workflow"):
                    logger.warning(f"Rate limit exceeded for workflow {workflow_name}, waiting...")
                    await asyncio.sleep(retry_delay)
                    continue
                    
                # Execute the workflow function
                result = await self.rate_limiter.execute("workflow", workflow_func, workflow_name, merged_params)
                return {"status": "success", "result": result}
            except Exception as e:
                retries += 1
                last_error = e
                
                if retries > max_retries:
                    logger.error(f"Final error executing workflow {workflow_name}: {str(e)}")
                    break
                    
                # Use exponential backoff
                current_delay = retry_delay * (2 ** (retries - 1))
                logger.warning(f"Error executing workflow {workflow_name}, retry {retries}/{max_retries} in {current_delay:.2f}s: {str(e)}")
                await asyncio.sleep(current_delay)
                
        # If we get here, all retries failed
        raise last_error or Exception(f"Failed to execute workflow {workflow_name} after {max_retries} retries")
        
    async def _default_workflow_executor(self, workflow_name: str, params: Dict[str, Any]) -> Any:
        """Default executor for workflows without a registered function.
        
        Args:
            workflow_name: Name of the workflow
            params: Parameters for the workflow
            
        Returns:
            Workflow execution result
        """
        logger.info(f"Executing workflow {workflow_name} with default executor")
        
        # Get workflow configuration
        workflow_info = self.workflow_registry.get(workflow_name)
        if not workflow_info:
            raise Exception(f"Workflow {workflow_name} not found")
            
        workflow_config = workflow_info.get("config", {})
        steps = workflow_config.get("steps", [])
        
        results = {}
        
        # Execute each step in the workflow
        for step in steps:
            step_type = step.get("type")
            step_params = step.get("params", {})
            
            # Merge global params with step params
            merged_params = {**params, **step_params}
            
            if step_type == "agent_action":
                # Execute an agent action
                agent_type = step.get("agent")
                action = step.get("action")
                
                if agent_type not in self.agents:
                    raise Exception(f"Agent {agent_type} not found for workflow {workflow_name}")
                    
                agent = self.agents[agent_type]
                if not hasattr(agent, action):
                    raise Exception(f"Action {action} not found for agent {agent_type}")
                    
                # Execute the agent action
                action_func = getattr(agent, action)
                step_result = await action_func(**merged_params)
                
                # Store the result
                step_id = step.get("id", f"step_{len(results)}")
                results[step_id] = step_result
                
        return results
        
    def _record_workflow_metrics(self, workflow_name: str, execution_time: float, result: Dict[str, Any]) -> None:
        """Record metrics for workflow execution.
        
        Args:
            workflow_name: Name of the workflow
            execution_time: Execution time in seconds
            result: Workflow execution result
        """
        # Record execution time
        self.metrics_service.record("workflow", f"{workflow_name}.execution_time", execution_time)
        
        # Record success/failure
        status = result.get("status")
        self.metrics_service.record("workflow", f"{workflow_name}.status", status)
        
        # Record additional metrics if available
        if "metrics" in result:
            for metric_name, metric_value in result["metrics"].items():
                self.metrics_service.record("workflow", f"{workflow_name}.{metric_name}", metric_value)
                
    def create_campaign(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new marketing campaign.
        
        Args:
            campaign_config: Configuration for the campaign
            
        Returns:
            Dict containing campaign creation status and ID
        """
        # Generate campaign ID
        campaign_id = str(uuid.uuid4())
        
        # Validate campaign configuration
        if not self._validate_campaign_config(campaign_config):
            return {"status": "error", "message": "Invalid campaign configuration"}
            
        # Store campaign
        self.campaigns[campaign_id] = {
            "id": campaign_id,
            "config": campaign_config,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "metrics": {},
            "competitive_insights": {}
        }
        
        logger.info(f"Created campaign {campaign_id}")
        
        # Record metrics
        self.metrics_service.record("campaign", f"{campaign_id}.creation", {
            "timestamp": datetime.now().isoformat(),
            "config": campaign_config
        })
        
        # Fetch initial competitive insights if competitive intelligence agent is available
        if "competitive_intelligence" in self.agents:
            try:
                # Get initial competitive insights asynchronously
                asyncio.create_task(self._fetch_competitive_insights(campaign_id))
            except Exception as e:
                logger.warning(f"Failed to fetch initial competitive insights for campaign {campaign_id}: {str(e)}")
        
        return {
            "status": "success",
            "campaign_id": campaign_id
        }
        
    def _validate_campaign_config(self, campaign_config: Dict[str, Any]) -> bool:
        """Validate campaign configuration.
        
        Args:
            campaign_config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["name", "target_audience", "channels"]
        for field in required_fields:
            if field not in campaign_config:
                logger.error(f"Missing required field in campaign config: {field}")
                return False
                
        # Validate channels
        channels = campaign_config.get("channels", [])
        if not channels or not isinstance(channels, list):
            logger.error("Campaign must have at least one channel")
            return False
            
        return True
        
    async def _fetch_competitive_insights(self, campaign_id: str) -> Dict[str, Any]:
        """Fetch competitive insights for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dict containing competitive insights
        """
        if campaign_id not in self.campaigns:
            logger.error(f"Campaign {campaign_id} not found")
            return {}
            
        if "competitive_intelligence" not in self.agents:
            logger.warning("Competitive intelligence agent not available")
            return {}
            
        try:
            # Get campaign configuration
            campaign = self.campaigns[campaign_id]
            campaign_config = campaign["config"]
            
            # Get competitive intelligence agent
            ci_agent = self.agents["competitive_intelligence"]
            
            # Request insights
            insights = await ci_agent.analyze_competitive_landscape({
                "campaign_name": campaign_config.get("name"),
                "target_audience": campaign_config.get("target_audience"),
                "channels": campaign_config.get("channels"),
                "keywords": campaign_config.get("keywords", [])
            })
            
            # Store insights in campaign
            campaign["competitive_insights"] = insights
            
            # Record metrics
            self.metrics_service.record("campaign", f"{campaign_id}.competitive_insights", {
                "timestamp": datetime.now().isoformat(),
                "insight_count": len(insights)
            })
            
            logger.info(f"Fetched competitive insights for campaign {campaign_id}")
            return insights
        except Exception as e:
            logger.error(f"Error fetching competitive insights: {str(e)}")
            return {}
            
    def start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Start a marketing campaign.
        
        Args:
            campaign_id: ID of the campaign to start
            
        Returns:
            Dict containing campaign status
        """
        if campaign_id not in self.campaigns:
            error_msg = f"Campaign {campaign_id} not found"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        campaign = self.campaigns[campaign_id]
        
        # Check if campaign is already running
        if campaign["status"] == "running":
            return {"status": "success", "message": "Campaign already running"}
            
        # Update campaign status
        campaign["status"] = "running"
        campaign["started_at"] = datetime.now().isoformat()
        
        # Execute campaign start workflow if available
        if "campaign_start" in self.workflow_registry.get_all():
            try:
                # Execute workflow asynchronously
                asyncio.create_task(self.execute_workflow("campaign_start", {
                    "campaign_id": campaign_id,
                    "campaign_config": campaign["config"]
                }))
            except Exception as e:
                logger.error(f"Failed to execute campaign start workflow: {str(e)}")
        
        logger.info(f"Started campaign {campaign_id}")
        
        # Record metrics
        self.metrics_service.record("campaign", f"{campaign_id}.start", {
            "timestamp": campaign["started_at"]
        })
        
        return {
            "status": "success",
            "campaign_id": campaign_id,
            "campaign_status": campaign["status"]
        }
        
    def stop_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Stop a marketing campaign.
        
        Args:
            campaign_id: ID of the campaign to stop
            
        Returns:
            Dict containing campaign status
        """
        if campaign_id not in self.campaigns:
            error_msg = f"Campaign {campaign_id} not found"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        campaign = self.campaigns[campaign_id]
        
        # Check if campaign is already stopped
        if campaign["status"] != "running":
            return {"status": "success", "message": "Campaign not running"}
            
        # Update campaign status
        campaign["status"] = "stopped"
        campaign["stopped_at"] = datetime.now().isoformat()
        
        # Calculate campaign duration
        if "started_at" in campaign:
            started_at = datetime.fromisoformat(campaign["started_at"])
            stopped_at = datetime.fromisoformat(campaign["stopped_at"])
            duration = (stopped_at - started_at).total_seconds()
            campaign["duration_seconds"] = duration
        
        # Execute campaign stop workflow if available
        if "campaign_stop" in self.workflow_registry.get_all():
            try:
                # Execute workflow asynchronously
                asyncio.create_task(self.execute_workflow("campaign_stop", {
                    "campaign_id": campaign_id,
                    "campaign_config": campaign["config"],
                    "campaign_metrics": campaign.get("metrics", {})
                }))
            except Exception as e:
                logger.error(f"Failed to execute campaign stop workflow: {str(e)}")
        
        logger.info(f"Stopped campaign {campaign_id}")
        
        # Record metrics
        self.metrics_service.record("campaign", f"{campaign_id}.stop", {
            "timestamp": campaign["stopped_at"],
            "duration_seconds": campaign.get("duration_seconds")
        })
        
        return {
            "status": "success",
            "campaign_id": campaign_id,
            "campaign_status": campaign["status"]
        }
        
    def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get the status of a marketing campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dict containing campaign status and metrics
        """
        if campaign_id not in self.campaigns:
            error_msg = f"Campaign {campaign_id} not found"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        campaign = self.campaigns[campaign_id]
        
        # Get latest competitive insights if available
        if "competitive_intelligence" in self.agents and campaign["status"] == "running":
            try:
                # Update competitive insights asynchronously
                asyncio.create_task(self._fetch_competitive_insights(campaign_id))
            except Exception as e:
                logger.warning(f"Failed to update competitive insights for campaign {campaign_id}: {str(e)}")
        
        return {
            "status": "success",
            "campaign_id": campaign_id,
            "campaign_status": campaign["status"],
            "created_at": campaign.get("created_at"),
            "started_at": campaign.get("started_at"),
            "stopped_at": campaign.get("stopped_at"),
            "duration_seconds": campaign.get("duration_seconds"),
            "metrics": campaign.get("metrics", {}),
            "competitive_insights": campaign.get("competitive_insights", {})
        }
        
    def start(self) -> Dict[str, Any]:
        """Start the marketing orchestrator.
        
        Returns:
            Dict containing orchestrator status
        """
        start_time = datetime.now()
        
        # Initialize any pending agents
        for agent_type, agent in self.agents.items():
            if hasattr(agent, "initialize"):
                try:
                    agent.initialize()
                    logger.info(f"Initialized agent: {agent_type}")
                except Exception as e:
                    logger.error(f"Failed to initialize agent {agent_type}: {str(e)}")
        
        # Record start metrics
        self.metrics_service.record("orchestrator", "start", {
            "timestamp": start_time.isoformat(),
            "agent_count": len(self.agents),
            "workflow_count": len(self.workflow_registry.get_all())
        })
        
        logger.info("Marketing orchestrator started")
        
        return {
            "status": "success",
            "start_time": start_time.isoformat(),
            "agents": list(self.agents.keys()),
            "workflows": list(self.workflow_registry.get_all().keys())
        }
        
    def _get_agent_class(self, agent_type: str) -> Optional[Type]:
        """Get the agent class based on agent type.
        
        Args:
            agent_type: Type of the agent
            
        Returns:
            Agent class, or None if not found
        """
        # First check the registry
        agent_class = self.agent_registry.get(agent_type)
        if agent_class:
            return agent_class
            
        # If not in registry, try to import dynamically
        try:
            if agent_type == "seo":
                from core.seo.agent import SEOAgent
                return SEOAgent
            elif agent_type == "content":
                from core.content.agent import ContentAgent
                return ContentAgent
            elif agent_type == "social":
                from core.social.agent import SocialMediaAgent
                return SocialMediaAgent
            elif agent_type == "email":
                from core.email.agent import EmailAgent
                return EmailAgent
            elif agent_type == "analytics":
                from core.analytics.agent import AnalyticsAgent
                return AnalyticsAgent
            elif agent_type == "competitive_intelligence":
                from core.competitive_intelligence.agent import CompetitiveIntelligenceAgent
                return CompetitiveIntelligenceAgent
            else:
                logger.error(f"Unknown agent type: {agent_type}")
                return None
        except ImportError as e:
            logger.error(f"Failed to import agent class for type {agent_type}: {str(e)}")
            return None
            
    def create_improvement_cycle(self, cycle_name: str, config_path: str) -> Dict[str, Any]:
        """Create a continuous improvement cycle.
        
        Args:
            cycle_name: Name of the improvement cycle
            config_path: Path to the cycle configuration file
            
        Returns:
            Dict containing cycle creation status
        """
        # Generate cycle ID
        cycle_id = str(uuid.uuid4())
        
        try:
            # Create cycle instance with metrics service
            cycle = ContinuousImprovementCycle(config_path, self.metrics_service)
            
            # Store cycle
            self.improvement_cycles[cycle_id] = {
                "id": cycle_id,
                "name": cycle_name,
                "cycle": cycle,
                "status": "created",
                "created_at": datetime.now().isoformat(),
                "campaigns": []
            }
            
            logger.info(f"Created improvement cycle {cycle_name} with ID {cycle_id}")
            
            # Record metrics
            self.metrics_service.record("cycle", f"{cycle_id}.creation", {
                "name": cycle_name,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "status": "success",
                "cycle_id": cycle_id,
                "cycle_name": cycle_name
            }
        except Exception as e:
            error_msg = f"Failed to create improvement cycle: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
    def start_improvement_cycle(self, cycle_id: str, initial_phase: str = None) -> Dict[str, Any]:
        """Start a continuous improvement cycle.
        
        Args:
            cycle_id: ID of the cycle to start
            initial_phase: Optional initial phase to start with
            
        Returns:
            Dict containing cycle start status
        """
        if cycle_id not in self.improvement_cycles:
            error_msg = f"Improvement cycle {cycle_id} not found"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        cycle_info = self.improvement_cycles[cycle_id]
        cycle = cycle_info["cycle"]
        
        try:
            # Start the cycle
            cycle_status = cycle.start_cycle(initial_phase)
            
            # Update cycle info
            cycle_info["status"] = "running"
            cycle_info["started_at"] = datetime.now().isoformat()
            cycle_info["current_phase"] = cycle.current_phase
            
            logger.info(f"Started improvement cycle {cycle_id} with phase {cycle.current_phase}")
            
            # Execute phase workflows
            self._execute_phase_workflows(cycle_id, cycle.current_phase)
            
            # Record metrics
            self.metrics_service.record("cycle", f"{cycle_id}.start", {
                "timestamp": cycle_info["started_at"],
                "initial_phase": cycle.current_phase
            })
            
            return {
                "status": "success",
                "cycle_id": cycle_id,
                "cycle_status": cycle_status
            }
        except Exception as e:
            error_msg = f"Failed to start improvement cycle: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
    def advance_cycle_phase(self, cycle_id: str) -> Dict[str, Any]:
        """Advance a continuous improvement cycle to the next phase.
        
        Args:
            cycle_id: ID of the cycle to advance
            
        Returns:
            Dict containing phase advancement status
        """
        if cycle_id not in self.improvement_cycles:
            error_msg = f"Improvement cycle {cycle_id} not found"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        cycle_info = self.improvement_cycles[cycle_id]
        cycle = cycle_info["cycle"]
        
        try:
            # Get current phase before advancing
            previous_phase = cycle.current_phase
            
            # Advance the cycle
            cycle_status = cycle.advance_phase()
            
            # Update cycle info
            cycle_info["current_phase"] = cycle.current_phase
            cycle_info["last_phase_change"] = datetime.now().isoformat()
            
            logger.info(f"Advanced improvement cycle {cycle_id} from phase {previous_phase} to {cycle.current_phase}")
            
            # Execute phase workflows for the new phase
            self._execute_phase_workflows(cycle_id, cycle.current_phase)
            
            # Record metrics
            self.metrics_service.record("cycle", f"{cycle_id}.phase_advance", {
                "timestamp": cycle_info["last_phase_change"],
                "from_phase": previous_phase,
                "to_phase": cycle.current_phase
            })
            
            return {
                "status": "success",
                "cycle_id": cycle_id,
                "previous_phase": previous_phase,
                "current_phase": cycle.current_phase,
                "cycle_status": cycle_status
            }
        except Exception as e:
            error_msg = f"Failed to advance improvement cycle phase: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
    def _execute_phase_workflows(self, cycle_id: str, phase_name: str) -> None:
        """Execute workflows associated with a specific phase of an improvement cycle.
        
        Args:
            cycle_id: ID of the improvement cycle
            phase_name: Name of the phase
        """
        cycle_info = self._get_cycle_info(cycle_id)
        if not cycle_info:
            return
            
        phase_tasks = self._get_phase_tasks(cycle_info["cycle"], phase_name)
        self._execute_tasks(phase_tasks)
        
    def _get_cycle_info(self, cycle_id: str) -> Optional[Dict]:
        """Get cycle information or log error if not found.
        
        Args:
            cycle_id: ID of the improvement cycle
            
        Returns:
            Dict containing cycle information, or None if not found
        """
        if cycle_id not in self.improvement_cycles:
            logger.error(f"Improvement cycle {cycle_id} not found")
            return None
            
        return self.improvement_cycles[cycle_id]
        
    def _get_phase_tasks(self, cycle: ContinuousImprovementCycle, phase_name: str) -> List[Dict[str, Any]]:
        """Get tasks for a specific phase.
        
        Args:
            cycle: Continuous improvement cycle instance
            phase_name: Name of the phase
            
        Returns:
            List of task configurations
        """
        return cycle.phases.get(phase_name, {}).get("tasks", [])
        
    def _execute_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        """Execute workflow tasks asynchronously.
        
        Args:
            tasks: List of task configurations
        """
        for task in tasks:
            workflow_name = task.get("workflow")
            if not workflow_name or workflow_name not in self.workflow_registry.get_all():
                logger.warning(f"Workflow {workflow_name} not found for task")
                continue
                
            params = task.get("params", {})
            try:
                asyncio.create_task(self.execute_workflow(workflow_name, params))
                logger.info(f"Scheduled task execution for workflow {workflow_name}")
            except Exception as e:
                logger.error(f"Failed to schedule task for workflow {workflow_name}: {str(e)}")
                
    def trigger_feedback_loop(self, cycle_id: str, loop_type: str) -> Dict[str, Any]:
        """Trigger a feedback loop in a continuous improvement cycle.
        
        Args:
            cycle_id: ID of the improvement cycle
            loop_type: Type of feedback loop to trigger (short, medium, long)
            
        Returns:
            Dict containing feedback loop trigger status
        """
        if cycle_id not in self.improvement_cycles:
            error_msg = f"Improvement cycle {cycle_id} not found"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        cycle_info = self.improvement_cycles[cycle_id]
        cycle = cycle_info["cycle"]
        
        try:
            # Trigger the feedback loop
            loop_result = cycle.trigger_feedback_loop(loop_type)
            
            if loop_result["status"] == "error":
                return loop_result
                
            # Execute feedback loop actions if defined
            loop_config = loop_result["config"]
            actions = loop_config.get("actions", [])
            
            for action in actions:
                action_type = action.get("type")
                
                if action_type == "workflow":
                    # Execute workflow action
                    workflow_name = action.get("workflow")
                    params = action.get("params", {})
                    
                    # Add cycle context to params
                    params["cycle_id"] = cycle_id
                    params["cycle_phase"] = cycle.current_phase
                    params["loop_type"] = loop_type
                    
                    try:
                        asyncio.create_task(self.execute_workflow(workflow_name, params))
                        logger.info(f"Scheduled feedback loop action for workflow {workflow_name}")
                    except Exception as e:
                        logger.error(f"Failed to schedule feedback loop action: {str(e)}")
            
            # Record metrics
            self.metrics_service.record("cycle", f"{cycle_id}.feedback_loop", {
                "timestamp": datetime.now().isoformat(),
                "loop_type": loop_type,
                "action_count": len(actions)
            })
            
            return {
                "status": "success",
                "cycle_id": cycle_id,
                "loop_type": loop_type,
                "actions_scheduled": len(actions)
            }
        except Exception as e:
            error_msg = f"Failed to trigger feedback loop: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
            
    # API Interface Methods
    
    async def handle_api_request(self, endpoint: str, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle API requests to the orchestrator.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Request parameters
            
        Returns:
            Dict containing API response
        """
        params = params or {}
        start_time = time.time()
        
        # Record API request metrics
        self.metrics_service.record("api", f"{endpoint}.request", {
            "method": method,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            # Route to appropriate handler
            if endpoint == "campaigns" and method == "GET":
                response = self.api_get_campaigns(params)
            elif endpoint == "campaigns" and method == "POST":
                response = self.api_create_campaign(params)
            elif endpoint.startswith("campaigns/") and method == "GET":
                campaign_id = endpoint.split("/")[1]
                response = self.api_get_campaign(campaign_id)
            elif endpoint.startswith("campaigns/") and method == "PUT":
                campaign_id = endpoint.split("/")[1]
                action = params.get("action")
                if action == "start":
                    response = self.start_campaign(campaign_id)
                elif action == "stop":
                    response = self.stop_campaign(campaign_id)
                else:
                    response = {"status": "error", "message": f"Unknown action: {action}"}
            elif endpoint == "cycles" and method == "GET":
                response = self.api_get_cycles(params)
            elif endpoint == "cycles" and method == "POST":
                response = self.api_create_cycle(params)
            elif endpoint.startswith("cycles/") and method == "GET":
                cycle_id = endpoint.split("/")[1]
                response = self.api_get_cycle(cycle_id)
            elif endpoint.startswith("cycles/") and method == "PUT":
                cycle_id = endpoint.split("/")[1]
                action = params.get("action")
                if action == "start":
                    initial_phase = params.get("initial_phase")
                    response = self.start_improvement_cycle(cycle_id, initial_phase)
                elif action == "advance":
                    response = self.advance_cycle_phase(cycle_id)
                elif action == "feedback":
                    loop_type = params.get("loop_type")
                    response = self.trigger_feedback_loop(cycle_id, loop_type)
                else:
                    response = {"status": "error", "message": f"Unknown action: {action}"}
            elif endpoint == "workflows" and method == "GET":
                response = self.api_get_workflows()
            elif endpoint.startswith("workflows/") and method == "POST":
                workflow_name = endpoint.split("/")[1]
                response = await self.api_execute_workflow(workflow_name, params)
            elif endpoint == "agents" and method == "GET":
                response = self.api_get_agents()
            elif endpoint == "status" and method == "GET":
                response = self.api_get_status()
            elif endpoint == "metrics" and method == "GET":
                response = self.api_get_metrics(params)
            else:
                response = {"status": "error", "message": f"Unknown endpoint: {endpoint} with method {method}"}
                
            # Record API response time
            execution_time = time.time() - start_time
            self.metrics_service.record("api", f"{endpoint}.response_time", execution_time)
            
            return response
        except Exception as e:
            error_msg = f"Error handling API request to {endpoint}: {str(e)}"
            logger.error(error_msg)
            
            # Record API error
            self.metrics_service.record("api", f"{endpoint}.error", {
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return {"status": "error", "message": error_msg}
            
    def api_get_campaigns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all campaigns.
        
        Args:
            params: Request parameters
            
        Returns:
            Dict containing campaigns
        """
        # Filter campaigns if needed
        status_filter = params.get("status")
        campaigns = []
        
        for campaign_id, campaign in self.campaigns.items():
            if status_filter and campaign["status"] != status_filter:
                continue
                
            campaigns.append({
                "id": campaign_id,
                "name": campaign["config"].get("name"),
                "status": campaign["status"],
                "created_at": campaign.get("created_at"),
                "started_at": campaign.get("started_at"),
                "stopped_at": campaign.get("stopped_at")
            })
            
        return {
            "status": "success",
            "campaigns": campaigns
        }
        
    def api_create_campaign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new campaign.
        
        Args:
            params: Campaign configuration
            
        Returns:
            Dict containing campaign creation status
        """
        return self.create_campaign(params)
        
    def api_get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign details.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dict containing campaign details
        """
        return self.get_campaign_status(campaign_id)
        
    def api_get_cycles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all improvement cycles.
        
        Args:
            params: Request parameters
            
        Returns:
            Dict containing improvement cycles
        """
        # Filter cycles if needed
        status_filter = params.get("status")
        cycles = []
        
        for cycle_id, cycle_info in self.improvement_cycles.items():
            if status_filter and cycle_info["status"] != status_filter:
                continue
                
            cycles.append({
                "id": cycle_id,
                "name": cycle_info["name"],
                "status": cycle_info["status"],
                "created_at": cycle_info.get("created_at"),
                "started_at": cycle_info.get("started_at"),
                "current_phase": cycle_info.get("current_phase")
            })
            
        return {
            "status": "success",
            "cycles": cycles
        }
        
    def api_create_cycle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new improvement cycle.
        
        Args:
            params: Cycle configuration
            
        Returns:
            Dict containing cycle creation status
        """
        cycle_name = params.get("name")
        config_path = params.get("config_path")
        
        if not cycle_name or not config_path:
            return {"status": "error", "message": "Missing required parameters: name, config_path"}
            
        return self.create_improvement_cycle(cycle_name, config_path)
        
    def api_get_cycle(self, cycle_id: str) -> Dict[str, Any]:
        """Get improvement cycle details.
        
        Args:
            cycle_id: ID of the improvement cycle
            
        Returns:
            Dict containing cycle details
        """
        if cycle_id not in self.improvement_cycles:
            return {"status": "error", "message": f"Improvement cycle {cycle_id} not found"}
            
        cycle_info = self.improvement_cycles[cycle_id]
        cycle = cycle_info["cycle"]
        
        return {
            "status": "success",
            "cycle_id": cycle_id,
            "name": cycle_info["name"],
            "status": cycle_info["status"],
            "created_at": cycle_info.get("created_at"),
            "started_at": cycle_info.get("started_at"),
            "current_phase": cycle_info.get("current_phase"),
            "phases": list(cycle.phases.keys()),
            "campaigns": cycle_info.get("campaigns", [])
        }
        
    def api_get_workflows(self) -> Dict[str, Any]:
        """Get all registered workflows.
        
        Returns:
            Dict containing workflows
        """
        workflows = []
        
        for workflow_name, workflow_info in self.workflow_registry.get_all().items():
            workflows.append({
                "name": workflow_name,
                "description": workflow_info.get("description", ""),
                "has_custom_function": workflow_info.get("func") is not None
            })
            
        return {
            "status": "success",
            "workflows": workflows
        }
        
    async def api_execute_workflow(self, workflow_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow.
        
        Args:
            workflow_name: Name of the workflow
            params: Workflow parameters
            
        Returns:
            Dict containing workflow execution result
        """
        return await self.execute_workflow(workflow_name, params)
        
    def api_get_agents(self) -> Dict[str, Any]:
        """Get all registered agents.
        
        Returns:
            Dict containing agents
        """
        agents = []
        
        for agent_type, agent in self.agents.items():
            agent_info = {
                "type": agent_type,
                "class": agent.__class__.__name__,
                "actions": []
            }
            
            # Get available actions
            for attr_name in dir(agent):
                if attr_name.startswith("_"):
                    continue
                    
                attr = getattr(agent, attr_name)
                if callable(attr):
                    agent_info["actions"].append(attr_name)
                    
            agents.append(agent_info)
            
        return {
            "status": "success",
            "agents": agents
        }
        
    def api_get_status(self) -> Dict[str, Any]:
        """Get orchestrator status.
        
        Returns:
            Dict containing orchestrator status
        """
        return {
            "status": "success",
            "orchestrator": {
                "agent_count": len(self.agents),
                "workflow_count": len(self.workflow_registry.get_all()),
                "campaign_count": len(self.campaigns),
                "cycle_count": len(self.improvement_cycles),
                "test_mode": self.test_mode
            }
        }
        
    def api_get_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get orchestrator metrics.
        
        Args:
            params: Request parameters
            
        Returns:
            Dict containing metrics
        """
        category = params.get("category")
        name = params.get("name")
        limit = params.get("limit", 100)
        
        metrics = self.metrics_service.get_metrics(category, name, limit)
        
        return {
            "status": "success",
            "metrics": metrics
        }
