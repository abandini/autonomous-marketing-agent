"""
Autonomous Marketing Agent - Main Application

This is the main entry point for the Autonomous Marketing Agent system.
It initializes and coordinates all components of the marketing automation system.
"""

import os
import sys
import logging
import asyncio
import argparse
import yaml
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("marketing_agent.log")
    ]
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core components
from core.orchestrator.orchestrator import MarketingOrchestrator
from core.knowledge_graph.knowledge_graph import MarketingKnowledgeGraph
from core.agents.seo_agent.seo_agent import SEOAgent
from core.agents.content_agent.content_agent import ContentAgent

class MarketingAgentApp:
    """
    Main application class for the Autonomous Marketing Agent.
    
    This class initializes and coordinates all components of the system,
    providing a unified interface for users to interact with the marketing agent.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Marketing Agent Application.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.orchestrator = None
        self.knowledge_graph = None
        self.agents = {}
        logger.info("Marketing Agent Application initialized")
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing configuration settings
        """
        if not config_path:
            config_path = "config/default.yaml"
            
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    config = yaml.safe_load(file)
                    logger.info(f"Configuration loaded from {config_path}")
                    return config
            else:
                logger.warning(f"Configuration file {config_path} not found, using default settings")
                return self._create_default_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return self._create_default_config()
            
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Create default configuration.
        
        Returns:
            Dict containing default configuration settings
        """
        default_config = {
            "orchestrator": {
                "name": "Marketing Orchestrator"
            },
            "knowledge_graph": {
                "persistence_path": "data/knowledge_graph.json",
                "load_on_init": True
            },
            "agents": {
                "seo": {
                    "name": "SEO Agent",
                    "keyword_database_path": "data/keyword_database.json"
                },
                "content": {
                    "name": "Content Agent",
                    "templates_path": "data/content_templates.json",
                    "calendar_path": "data/content_calendar.json"
                },
                "social": {
                    "name": "Social Media Agent",
                    "platforms": ["twitter", "facebook", "linkedin", "instagram"]
                },
                "email": {
                    "name": "Email Agent",
                    "templates_path": "data/email_templates.json"
                },
                "advertising": {
                    "name": "Advertising Agent",
                    "platforms": ["google_ads", "facebook_ads", "linkedin_ads"]
                }
            },
            "workflows": {
                "content_creation": {
                    "name": "Content Creation Workflow",
                    "steps": [
                        {
                            "agent": "seo",
                            "action": "analyze_keywords",
                            "params": {}
                        },
                        {
                            "agent": "content",
                            "action": "create_content_brief",
                            "params": {}
                        },
                        {
                            "agent": "content",
                            "action": "generate_content",
                            "params": {}
                        },
                        {
                            "agent": "seo",
                            "action": "optimize_content",
                            "params": {}
                        }
                    ]
                },
                "content_distribution": {
                    "name": "Content Distribution Workflow",
                    "steps": [
                        {
                            "agent": "content",
                            "action": "optimize_content",
                            "params": {}
                        },
                        {
                            "agent": "social",
                            "action": "publish_content",
                            "params": {}
                        },
                        {
                            "agent": "email",
                            "action": "send_newsletter",
                            "params": {}
                        }
                    ]
                },
                "performance_analysis": {
                    "name": "Performance Analysis Workflow",
                    "steps": [
                        {
                            "agent": "seo",
                            "action": "track_rankings",
                            "params": {}
                        },
                        {
                            "agent": "content",
                            "action": "analyze_content_performance",
                            "params": {}
                        },
                        {
                            "agent": "social",
                            "action": "analyze_social_performance",
                            "params": {}
                        }
                    ]
                }
            }
        }
        
        # Ensure config directory exists
        os.makedirs("config", exist_ok=True)
        
        # Save default config
        with open("config/default.yaml", 'w') as file:
            yaml.dump(default_config, file)
            
        logger.info("Created default configuration")
        return default_config
        
    async def initialize(self) -> None:
        """
        Initialize all components of the marketing agent.
        """
        try:
            # Initialize knowledge graph
            logger.info("Initializing Knowledge Graph")
            self.knowledge_graph = MarketingKnowledgeGraph(self.config.get("knowledge_graph", {}))
            
            # Initialize orchestrator
            logger.info("Initializing Marketing Orchestrator")
            self.orchestrator = MarketingOrchestrator(self.config.get("orchestrator", {}))
            self.orchestrator.set_knowledge_graph(self.knowledge_graph)
            
            # Initialize agents
            agents_config = self.config.get("agents", {})
            
            # Initialize SEO Agent
            if "seo" in agents_config:
                logger.info("Initializing SEO Agent")
                seo_agent = SEOAgent(agents_config["seo"])
                seo_agent.connect_knowledge_graph(self.knowledge_graph)
                await seo_agent.initialize()
                self.agents["seo"] = seo_agent
                self.orchestrator.register_agent("seo", seo_agent)
                
            # Initialize Content Agent
            if "content" in agents_config:
                logger.info("Initializing Content Agent")
                content_agent = ContentAgent(agents_config["content"])
                content_agent.connect_knowledge_graph(self.knowledge_graph)
                await content_agent.initialize()
                self.agents["content"] = content_agent
                self.orchestrator.register_agent("content", content_agent)
                
            # Register workflows
            for workflow_name, workflow_config in self.config.get("workflows", {}).items():
                self.orchestrator.register_workflow(workflow_name, workflow_config)
                
            logger.info("Marketing Agent Application initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Marketing Agent Application: {str(e)}")
            raise
            
    async def shutdown(self) -> None:
        """
        Shutdown all components of the marketing agent.
        """
        try:
            # Shutdown agents
            for agent_name, agent in self.agents.items():
                logger.info(f"Shutting down {agent_name} Agent")
                await agent.shutdown()
                
            # Save knowledge graph
            if self.knowledge_graph:
                logger.info("Saving Knowledge Graph")
                self.knowledge_graph.save()
                
            logger.info("Marketing Agent Application shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down Marketing Agent Application: {str(e)}")
            
    async def execute_workflow(self, workflow_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a marketing workflow.
        
        Args:
            workflow_name: Name of the workflow to execute
            params: Parameters for the workflow
            
        Returns:
            Dict containing workflow execution results
        """
        if not self.orchestrator:
            logger.error("Orchestrator not initialized")
            return {"status": "error", "message": "Orchestrator not initialized"}
            
        logger.info(f"Executing workflow: {workflow_name}")
        return await self.orchestrator.execute_workflow(workflow_name, params)
        
    async def create_campaign(self, campaign_config: Dict[str, Any]) -> str:
        """
        Create a new marketing campaign.
        
        Args:
            campaign_config: Configuration for the campaign
            
        Returns:
            Campaign ID
        """
        if not self.orchestrator:
            logger.error("Orchestrator not initialized")
            return None
            
        logger.info(f"Creating campaign: {campaign_config.get('name', 'Unnamed Campaign')}")
        return self.orchestrator.create_campaign(campaign_config)
        
    async def start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Start a marketing campaign.
        
        Args:
            campaign_id: ID of the campaign to start
            
        Returns:
            Dict containing campaign status
        """
        if not self.orchestrator:
            logger.error("Orchestrator not initialized")
            return {"status": "error", "message": "Orchestrator not initialized"}
            
        logger.info(f"Starting campaign: {campaign_id}")
        return self.orchestrator.start_campaign(campaign_id)
        
    async def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get the status of a marketing campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dict containing campaign status
        """
        if not self.orchestrator:
            logger.error("Orchestrator not initialized")
            return {"status": "error", "message": "Orchestrator not initialized"}
            
        return self.orchestrator.get_campaign_status(campaign_id)
        
    def get_knowledge_graph_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.
        
        Returns:
            Dict containing graph statistics
        """
        if not self.knowledge_graph:
            logger.error("Knowledge Graph not initialized")
            return {"status": "error", "message": "Knowledge Graph not initialized"}
            
        return self.knowledge_graph.get_statistics()

async def main():
    """
    Main entry point for the application.
    """
    parser = argparse.ArgumentParser(description="Autonomous Marketing Agent")
    parser.add_argument("--config", help="Path to configuration file", default="config/default.yaml")
    parser.add_argument("--workflow", help="Workflow to execute")
    parser.add_argument("--campaign", help="Campaign to create/start")
    args = parser.parse_args()
    
    try:
        # Initialize application
        app = MarketingAgentApp(args.config)
        await app.initialize()
        
        # Execute workflow if specified
        if args.workflow:
            result = await app.execute_workflow(args.workflow)
            print(f"Workflow execution result: {result}")
            
        # Create and start campaign if specified
        if args.campaign:
            campaign_config = {
                "name": args.campaign,
                "workflows": ["content_creation", "content_distribution", "performance_analysis"]
            }
            campaign_id = await app.create_campaign(campaign_config)
            result = await app.start_campaign(campaign_id)
            print(f"Campaign start result: {result}")
            
        # Get knowledge graph statistics
        stats = app.get_knowledge_graph_statistics()
        print(f"Knowledge Graph Statistics: {stats}")
        
        # Shutdown application
        await app.shutdown()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        
if __name__ == "__main__":
    asyncio.run(main())
