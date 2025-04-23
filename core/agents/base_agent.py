"""
Base Agent module for the Autonomous Marketing Agent.

This module defines the BaseAgent class that all specialized marketing agents
will inherit from, providing common functionality and interfaces.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

# Configure logging (configured centrally in main application)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all marketing agents in the system.
    
    Provides common functionality and interfaces that all specialized
    agents must implement.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the base agent.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.actions = {}
        self.knowledge_graph = None
        self.metrics = {}
        self._register_actions()
        logger.info(f"Initialized agent: {self.name}")
        
    def connect_knowledge_graph(self, knowledge_graph: Any) -> None:
        """
        Connect the agent to the knowledge graph.
        
        Args:
            knowledge_graph: Knowledge graph instance
        """
        self.knowledge_graph = knowledge_graph
        logger.info(f"Agent {self.name} connected to knowledge graph")
        
    def _register_actions(self) -> None:
        """
        Register all actions that this agent can perform.
        
        This method should be overridden by subclasses to register
        their specific actions.
        """
        pass
        
    def register_action(self, action_name: str, action_func: callable) -> None:
        """
        Register an action that this agent can perform.
        
        Args:
            action_name: Name of the action
            action_func: Function that implements the action
        """
        self.actions[action_name] = action_func
        logger.debug(f"Agent {self.name} registered action: {action_name}")
        
    async def execute_action(self, action_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute an action asynchronously.
        
        Args:
            action_name: Name of the action to execute
            params: Parameters for the action
            
        Returns:
            Dict containing action execution results
        """
        if action_name not in self.actions:
            logger.error(f"Action {action_name} not found in agent {self.name}")
            return {
                "status": "error",
                "message": f"Action {action_name} not found in agent {self.name}"
            }
            
        try:
            action_func = self.actions[action_name]
            result = await action_func(**(params or {}))
            
            # Update metrics
            self._update_metrics(action_name, result)
            
            return result
        except Exception as e:
            logger.error(f"Error executing action {action_name} in agent {self.name}: {str(e)}")
            return {
                "status": "error",
                "action": action_name,
                "message": str(e)
            }
            
    def _update_metrics(self, action_name: str, result: Dict[str, Any]) -> None:
        """
        Update agent metrics based on action execution.
        
        Args:
            action_name: Name of the executed action
            result: Result of the action execution
        """
        if action_name not in self.metrics:
            self.metrics[action_name] = {
                "executions": 0,
                "successes": 0,
                "failures": 0,
                "avg_execution_time": 0
            }
            
        metrics = self.metrics[action_name]
        metrics["executions"] += 1
        
        if result.get("status") == "success":
            metrics["successes"] += 1
        else:
            metrics["failures"] += 1
            
        if "execution_time" in result:
            # Update average execution time
            avg_time = metrics["avg_execution_time"]
            executions = metrics["executions"]
            metrics["avg_execution_time"] = (avg_time * (executions - 1) + result["execution_time"]) / executions
            
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get the agent's performance metrics.
        
        Returns:
            Dict containing agent metrics
        """
        return self.metrics
        
    async def call_mcp(self, mcp_id: str, capability: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Invoke an MCP service via the A2A resolver.
        """
        import os, httpx
        resolver_url = os.getenv("A2A_RESOLVER_URL", "http://localhost:8000/invoke")
        payload = {"agent": mcp_id, "capability": capability, "params": params or {}}
        async with httpx.AsyncClient() as client:
            resp = await client.post(resolver_url, json=payload)
            resp.raise_for_status()
            return resp.json()
        
    @abstractmethod
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize the agent.
        
        This method should be implemented by subclasses to perform
        any necessary initialization.
        
        Returns:
            Dict containing initialization status
        """
        pass
        
    @abstractmethod
    async def shutdown(self) -> Dict[str, Any]:
        """
        Shutdown the agent.
        
        This method should be implemented by subclasses to perform
        any necessary cleanup.
        
        Returns:
            Dict containing shutdown status
        """
        pass
