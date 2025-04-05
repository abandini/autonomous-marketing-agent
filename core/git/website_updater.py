"""
Website Updater for Autonomous Marketing Agent.

This module provides functionality to automatically update website files
based on continuous data and testing results using Git integration.
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from core.git.git_integration import GitIntegration
from core.analytics.analytics_engine import AnalyticsEngine

logger = logging.getLogger(__name__)

class WebsiteUpdater:
    """
    Handles automatic website updates based on analytics data and testing results.
    
    This class uses Git integration to pull the latest website code,
    make data-driven changes, and push updates back to the repository.
    """
    
    def __init__(self, git_integration: GitIntegration, analytics_engine: AnalyticsEngine,
                 config_path: Optional[str] = None):
        """
        Initialize the website updater.
        
        Args:
            git_integration: GitIntegration instance for Git operations
            analytics_engine: AnalyticsEngine instance for analytics data
            config_path: Path to the configuration file (optional)
        """
        self.git = git_integration
        self.analytics = analytics_engine
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load the configuration from a file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "update_frequency": "daily",  # daily, weekly, on_threshold
            "performance_threshold": 0.05,  # 5% change
            "auto_commit": True,
            "auto_push": False,  # Requires manual review by default
            "update_types": ["content", "meta", "structure"],
            "excluded_files": ["config.js", "sensitive.json"],
            "testing_branch": "testing"
        }
        
        if not config_path or not os.path.exists(config_path):
            logger.info("Using default configuration for website updater")
            return default_config
            
        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
                # Merge with defaults for any missing keys
                return {**default_config, **config}
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
            return default_config
    
    def prepare_repository(self) -> bool:
        """
        Prepare the Git repository for updates.
        
        This method clones the repository if it doesn't exist locally,
        and pulls the latest changes from the remote.
        
        Returns:
            True if successful, False otherwise
        """
        # Clone the repository if it doesn't exist
        if not os.path.exists(os.path.join(self.git.local_path, ".git")):
            success = self.git.clone_repository()
            if not success:
                logger.error("Failed to clone repository")
                return False
        
        # Pull the latest changes
        success = self.git.pull_latest_changes()
        if not success:
            logger.error("Failed to pull latest changes")
            return False
            
        return True
    
    def create_update_branch(self) -> bool:
        """
        Create a new branch for website updates.
        
        Returns:
            True if successful, False otherwise
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name = f"auto_update_{timestamp}"
        
        success = self.git.create_and_switch_branch(branch_name)
        if not success:
            logger.error(f"Failed to create update branch: {branch_name}")
            return False
            
        logger.info(f"Created update branch: {branch_name}")
        return True
    
    def update_content_based_on_analytics(self) -> List[str]:
        """
        Update website content based on analytics data.
        
        This method analyzes performance data and makes content
        adjustments to improve performance.
        
        Returns:
            List of updated file paths
        """
        updated_files = []
        
        # Get performance data from analytics engine
        performance_data = self.analytics.get_content_performance()
        
        # Identify underperforming content
        underperforming = self._identify_underperforming_content(performance_data)
        
        # Update each underperforming content item
        for item in underperforming:
            file_path = item.get("file_path")
            if not file_path or any(excluded in file_path for excluded in self.config["excluded_files"]):
                continue
                
            # Get current content
            current_content = self.git.get_file_content(file_path)
            if current_content is None:
                continue
                
            # Generate optimized content
            optimized_content = self._generate_optimized_content(current_content, item)
            
            # Update the file
            if optimized_content and optimized_content != current_content:
                success = self.git.update_file(file_path, optimized_content)
                if success:
                    updated_files.append(file_path)
                    
        return updated_files
    
    def _identify_underperforming_content(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify underperforming content based on analytics data.
        
        Args:
            performance_data: Content performance data from analytics
            
        Returns:
            List of underperforming content items with metadata
        """
        threshold = self.config["performance_threshold"]
        underperforming = []
        
        for item in performance_data.get("items", []):
            # Check if performance is below threshold
            if item.get("conversion_rate", 1.0) < threshold or \
               item.get("engagement_rate", 1.0) < threshold or \
               item.get("bounce_rate", 0.0) > (1.0 - threshold):
                underperforming.append(item)
                
        return underperforming
    
    def _generate_optimized_content(self, current_content: str, 
                                   performance_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate optimized content based on performance data.
        
        This method would typically use NLP or other ML techniques to
        optimize content. This is a placeholder implementation.
        
        Args:
            current_content: Current content of the file
            performance_data: Performance data for the content
            
        Returns:
            Optimized content, or None if no optimization is needed
        """
        # This is a placeholder - in a real implementation, this would use
        # ML/NLP techniques to optimize the content based on performance data
        
        # For now, just add a comment indicating optimization
        if "<!-- Optimized by Autonomous Marketing Agent -->" in current_content:
            return None
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        optimized_content = f"<!-- Optimized by Autonomous Marketing Agent on {timestamp} -->\n"
        optimized_content += f"<!-- Optimization reason: Low {performance_data.get('issue', 'performance')} -->\n"
        optimized_content += current_content
        
        return optimized_content
    
    def update_meta_tags_based_on_seo(self) -> List[str]:
        """
        Update meta tags based on SEO analysis.
        
        Returns:
            List of updated file paths
        """
        # Implementation would be similar to update_content_based_on_analytics
        # but focused on meta tags, title tags, etc.
        return []
    
    def commit_and_push_changes(self, updated_files: List[str]) -> bool:
        """
        Commit and optionally push changes to the repository.
        
        Args:
            updated_files: List of updated file paths
            
        Returns:
            True if successful, False otherwise
        """
        if not updated_files:
            logger.info("No files were updated, nothing to commit")
            return True
            
        # Create commit message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Auto-update website based on analytics data ({timestamp})\n\n"
        message += "Updated files:\n"
        for file in updated_files:
            message += f"- {file}\n"
            
        # Commit changes
        if self.config["auto_commit"]:
            success = self.git.commit_changes(message, updated_files)
            if not success:
                logger.error("Failed to commit changes")
                return False
                
            # Push changes if auto_push is enabled
            if self.config["auto_push"]:
                success = self.git.push_changes()
                if not success:
                    logger.error("Failed to push changes")
                    return False
                    
            logger.info(f"Successfully committed changes to {len(updated_files)} files")
            return True
        else:
            logger.info(f"Auto-commit disabled, {len(updated_files)} files ready for manual commit")
            return True
    
    def run_update_cycle(self) -> bool:
        """
        Run a complete website update cycle.
        
        This method performs the following steps:
        1. Prepare the repository (clone/pull)
        2. Create a new branch for updates
        3. Update content based on analytics
        4. Update meta tags based on SEO
        5. Commit and push changes
        
        Returns:
            True if successful, False otherwise
        """
        # Prepare the repository
        success = self.prepare_repository()
        if not success:
            return False
            
        # Create a new branch for updates
        success = self.create_update_branch()
        if not success:
            return False
            
        # Update content based on analytics
        updated_content_files = self.update_content_based_on_analytics()
        
        # Update meta tags based on SEO
        updated_meta_files = self.update_meta_tags_based_on_seo()
        
        # Combine all updated files
        all_updated_files = updated_content_files + updated_meta_files
        
        # Commit and push changes
        success = self.commit_and_push_changes(all_updated_files)
        
        return success
