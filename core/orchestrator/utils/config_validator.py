"""
Configuration validator for the orchestrator module.

This module provides schema validation for configuration files.
"""

import logging
import json
import yaml
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigValidator:
    """Validator for configuration files."""
    
    # Schema for orchestrator configuration
    ORCHESTRATOR_SCHEMA = {
        "type": "object",
        "properties": {
            "agents": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "required": ["class", "config"],
                    "properties": {
                        "class": {"type": "string"},
                        "config": {"type": "object"}
                    }
                }
            },
            "workflows": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "required": ["steps"],
                    "properties": {
                        "steps": {"type": "array"},
                        "config": {"type": "object"}
                    }
                }
            },
            "settings": {
                "type": "object",
                "properties": {
                    "max_concurrent_workflows": {"type": "integer"},
                    "rate_limits": {
                        "type": "object",
                        "properties": {
                            "default": {
                                "type": "object",
                                "properties": {
                                    "per_minute": {"type": "integer"},
                                    "concurrent": {"type": "integer"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "required": ["agents", "workflows"]
    }
    
    # Schema for improvement cycle configuration
    CYCLE_SCHEMA = {
        "type": "object",
        "properties": {
            "phases": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "required": ["tasks", "metrics"],
                    "properties": {
                        "tasks": {"type": "array"},
                        "metrics": {"type": "object"},
                        "duration": {"type": "integer"}
                    }
                }
            },
            "feedback_loops": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "required": ["trigger", "actions"],
                    "properties": {
                        "trigger": {"type": "object"},
                        "actions": {"type": "array"}
                    }
                }
            },
            "acceleration_strategies": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "required": ["phases", "adjustments"],
                    "properties": {
                        "phases": {"type": "array"},
                        "adjustments": {"type": "object"}
                    }
                }
            }
        },
        "required": ["phases"]
    }
    
    @staticmethod
    def validate_orchestrator_config(config: Dict[str, Any]) -> bool:
        """
        Validate orchestrator configuration against schema.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            validate(instance=config, schema=ConfigValidator.ORCHESTRATOR_SCHEMA)
            logger.info("Orchestrator configuration validated successfully")
            return True
        except ValidationError as e:
            logger.error(f"Orchestrator configuration validation failed: {str(e)}")
            return False
            
    @staticmethod
    def validate_cycle_config(config: Dict[str, Any]) -> bool:
        """
        Validate improvement cycle configuration against schema.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            validate(instance=config, schema=ConfigValidator.CYCLE_SCHEMA)
            logger.info("Improvement cycle configuration validated successfully")
            return True
        except ValidationError as e:
            logger.error(f"Improvement cycle configuration validation failed: {str(e)}")
            return False
            
    @staticmethod
    def load_and_validate_yaml(file_path: str, schema_type: str = "orchestrator") -> Optional[Dict[str, Any]]:
        """
        Load and validate a YAML configuration file.
        
        Args:
            file_path: Path to the YAML file
            schema_type: Type of schema to validate against ('orchestrator' or 'cycle')
            
        Returns:
            Validated configuration dict, or None if invalid
        """
        try:
            with open(file_path, 'r') as file:
                config = yaml.safe_load(file)
                
            if schema_type == "orchestrator":
                if ConfigValidator.validate_orchestrator_config(config):
                    return config
            elif schema_type == "cycle":
                if ConfigValidator.validate_cycle_config(config):
                    return config
            else:
                logger.error(f"Unknown schema type: {schema_type}")
                
            return None
        except Exception as e:
            logger.error(f"Failed to load and validate configuration: {str(e)}")
            return None
            
    @staticmethod
    def load_and_validate_json(file_path: str, schema_type: str = "orchestrator") -> Optional[Dict[str, Any]]:
        """
        Load and validate a JSON configuration file.
        
        Args:
            file_path: Path to the JSON file
            schema_type: Type of schema to validate against ('orchestrator' or 'cycle')
            
        Returns:
            Validated configuration dict, or None if invalid
        """
        try:
            with open(file_path, 'r') as file:
                config = json.load(file)
                
            if schema_type == "orchestrator":
                if ConfigValidator.validate_orchestrator_config(config):
                    return config
            elif schema_type == "cycle":
                if ConfigValidator.validate_cycle_config(config):
                    return config
            else:
                logger.error(f"Unknown schema type: {schema_type}")
                
            return None
        except Exception as e:
            logger.error(f"Failed to load and validate configuration: {str(e)}")
            return None
