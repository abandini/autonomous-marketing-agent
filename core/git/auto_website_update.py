"""
Automated Website Update Script for Autonomous Marketing Agent.

This script demonstrates how to use the Git integration and website updater
to automatically update website files based on analytics data and testing results.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.git.git_integration import GitIntegration
from core.git.website_updater import WebsiteUpdater
from core.analytics.analytics_engine import AnalyticsEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/auto_website_update.log')
    ]
)

logger = logging.getLogger(__name__)

def load_git_config(config_path: str) -> Dict[str, Any]:
    """
    Load Git configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading Git config from {config_path}: {e}")
        return {}

def get_git_credentials(config: Dict[str, Any]) -> tuple:
    """
    Get Git credentials from configuration or environment variables.
    
    Args:
        config: Git configuration dictionary
        
    Returns:
        Tuple of (username, token)
    """
    auth_config = config.get("auth", {})
    username = auth_config.get("username", "")
    
    # Try to get token from environment variable
    token_env_var = auth_config.get("token_env_var", "GIT_ACCESS_TOKEN")
    token = os.environ.get(token_env_var, "")
    
    return username, token

def update_website_for_repository(repo_config: Dict[str, Any], username: str, token: str) -> bool:
    """
    Update website files for a specific repository.
    
    Args:
        repo_config: Repository configuration
        username: Git username
        token: Git access token
        
    Returns:
        True if successful, False otherwise
    """
    repo_name = repo_config.get("name", "unknown")
    repo_url = repo_config.get("repo_url", "")
    local_path = repo_config.get("local_path", "")
    default_branch = repo_config.get("default_branch", "main")
    
    if not repo_url or not local_path:
        logger.error(f"Missing required configuration for repository {repo_name}")
        return False
        
    logger.info(f"Starting website update for repository: {repo_name}")
    
    # Create Git integration
    git = GitIntegration(
        repo_url=repo_url,
        local_path=local_path,
        username=username,
        token=token,
        branch=default_branch
    )
    
    # Create analytics engine
    analytics = AnalyticsEngine()
    
    # Create website updater
    updater = WebsiteUpdater(
        git_integration=git,
        analytics_engine=analytics,
        config_path=None  # Use default config for now
    )
    
    # Override config with repository-specific settings
    updater.config.update({
        "update_frequency": repo_config.get("update_frequency", "daily"),
        "performance_threshold": repo_config.get("performance_threshold", 0.05),
        "auto_commit": repo_config.get("auto_commit", True),
        "auto_push": repo_config.get("auto_push", False),
        "update_types": repo_config.get("update_types", ["content", "meta", "structure"]),
        "excluded_files": repo_config.get("excluded_files", []),
        "testing_branch": repo_config.get("testing_branch", "testing")
    })
    
    # Run the update cycle
    success = updater.run_update_cycle()
    
    if success:
        logger.info(f"Successfully updated website for repository: {repo_name}")
    else:
        logger.error(f"Failed to update website for repository: {repo_name}")
        
    return success

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Automated Website Update Script")
    parser.add_argument("--config", default="core/git/git_config.json", help="Path to Git configuration file")
    parser.add_argument("--repo", help="Specific repository name to update (optional)")
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Load configuration
    config = load_git_config(args.config)
    if not config:
        logger.error("Failed to load Git configuration")
        return 1
        
    # Get Git credentials
    username, token = get_git_credentials(config)
    if not token:
        logger.warning("Git access token not found. Some operations may fail.")
        
    # Get repositories to update
    repositories = config.get("repositories", [])
    if not repositories:
        logger.error("No repositories configured for update")
        return 1
        
    # Filter repositories if specific repo is specified
    if args.repo:
        repositories = [r for r in repositories if r.get("name") == args.repo]
        if not repositories:
            logger.error(f"Repository '{args.repo}' not found in configuration")
            return 1
            
    # Update each repository
    success_count = 0
    for repo_config in repositories:
        if update_website_for_repository(repo_config, username, token):
            success_count += 1
            
    # Log summary
    logger.info(f"Website update completed. {success_count}/{len(repositories)} repositories updated successfully.")
    
    return 0 if success_count == len(repositories) else 1

if __name__ == "__main__":
    sys.exit(main())
