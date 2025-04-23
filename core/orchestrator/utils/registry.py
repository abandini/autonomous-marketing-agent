"""
Registry module for the orchestrator.

This module provides registry functionality for agents and workflows,
enabling dependency injection and better testability.
"""

import logging
from typing import Dict, Any, Optional, Type, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentRegistry:
    """Registry for agent classes."""
    
    def __init__(self):
        """Initialize the agent registry."""
        self.agent_classes = {}
        logger.info("Agent registry initialized")
        
    def register(self, agent_type: str, agent_class: Any) -> None:
        """
        Register an agent class.
        
        Args:
            agent_type: Type of the agent
            agent_class: Agent class
        """
        self.agent_classes[agent_type] = agent_class
        logger.info(f"Registered agent class for type: {agent_type}")
        
    def get(self, agent_type: str) -> Optional[Any]:
        """
        Get an agent class by type.
        
        Args:
            agent_type: Type of the agent
            
        Returns:
            Agent class, or None if not found
        """
        if agent_type not in self.agent_classes:
            logger.warning(f"Agent class not found for type: {agent_type}")
            return None
            
        return self.agent_classes[agent_type]
        
    def register_default_agents(self) -> None:
        """Register default agent classes."""
        try:
            # Import agent classes
            from core.seo.agent import SEOAgent
            from core.content.agent import ContentAgent
            from core.social.agent import SocialMediaAgent
            from core.email.agent import EmailAgent
            from core.analytics.agent import AnalyticsAgent
            from core.competitive_intelligence.agent import CompetitiveIntelligenceAgent
            
            # Register agent classes
            self.register("seo", SEOAgent)
            self.register("content", ContentAgent)
            self.register("social", SocialMediaAgent)
            self.register("email", EmailAgent)
            self.register("analytics", AnalyticsAgent)
            self.register("competitive_intelligence", CompetitiveIntelligenceAgent)
            
            logger.info("Registered default agent classes")
        except ImportError as e:
            logger.warning(f"Could not import all default agent classes: {str(e)}")

class WorkflowRegistry:
    """Registry for workflow functions."""
    
    def __init__(self):
        """Initialize the workflow registry."""
        self.workflows = {}
        logger.info("Workflow registry initialized")
        
    def register(self, workflow_name: str, workflow_func: Callable, config: Dict[str, Any] = None) -> None:
        """
        Register a workflow function.
        
        Args:
            workflow_name: Name of the workflow
            workflow_func: Workflow function
            config: Optional workflow configuration
        """
        self.workflows[workflow_name] = {
            "func": workflow_func,
            "config": config or {}
        }
        logger.info(f"Registered workflow: {workflow_name}")
        
    def get(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a workflow by name.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Dict containing workflow function and config, or None if not found
        """
        if workflow_name not in self.workflows:
            logger.warning(f"Workflow not found: {workflow_name}")
            return None
            
        return self.workflows[workflow_name]
        
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered workflows.
        
        Returns:
            Dict containing all workflows
        """
        return self.workflows
        
    def remove(self, workflow_name: str) -> bool:
        """
        Remove a workflow from the registry.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            True if the workflow was removed, False otherwise
        """
        if workflow_name in self.workflows:
            del self.workflows[workflow_name]
            logger.info(f"Removed workflow: {workflow_name}")
            return True
            
        logger.warning(f"Cannot remove workflow, not found: {workflow_name}")
        return False
