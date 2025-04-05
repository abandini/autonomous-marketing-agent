"""
Git Integration for Autonomous Marketing Agent.

This module provides functionality to interact with Git repositories,
allowing the system to automatically update website files based on
continuous data and testing results.
"""

import os
import subprocess
import logging
from typing import Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class GitIntegration:
    """
    Handles Git operations for the Autonomous Marketing Agent.
    
    This class provides methods to clone repositories, create branches,
    commit changes, and push updates to remote repositories.
    """
    
    def __init__(self, repo_url: str, local_path: str, username: Optional[str] = None, 
                 token: Optional[str] = None, branch: str = "main"):
        """
        Initialize the Git integration.
        
        Args:
            repo_url: URL of the Git repository
            local_path: Local path where the repository should be cloned
            username: Git username (optional if using token authentication)
            token: Git access token (optional)
            branch: Default branch to work with
        """
        self.repo_url = repo_url
        self.local_path = local_path
        self.username = username
        self.token = token
        self.branch = branch
        self.authenticated_url = self._get_authenticated_url()
        
    def _get_authenticated_url(self) -> str:
        """
        Get the authenticated URL for Git operations.
        
        Returns:
            Authenticated Git URL with credentials if provided
        """
        if self.token and self.username:
            # Format: https://username:token@github.com/user/repo.git
            parts = self.repo_url.split("//")
            if len(parts) > 1:
                return f"{parts[0]}//{self.username}:{self.token}@{parts[1]}"
        return self.repo_url
    
    def _run_git_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[bool, str]:
        """
        Run a Git command and return the result.
        
        Args:
            command: Git command as a list of strings
            cwd: Working directory for the command
            
        Returns:
            Tuple of (success, output)
        """
        try:
            working_dir = cwd or self.local_path
            result = subprocess.run(
                command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(command)}")
            logger.error(f"Error: {e.stderr}")
            return False, e.stderr
        except Exception as e:
            logger.error(f"Error running Git command: {e}")
            return False, str(e)
    
    def clone_repository(self) -> bool:
        """
        Clone the repository to the local path.
        
        Returns:
            True if successful, False otherwise
        """
        if os.path.exists(os.path.join(self.local_path, ".git")):
            logger.info(f"Repository already exists at {self.local_path}")
            return True
            
        os.makedirs(self.local_path, exist_ok=True)
        success, output = self._run_git_command(
            ["git", "clone", self.authenticated_url, "."],
            cwd=self.local_path
        )
        
        if success:
            logger.info(f"Successfully cloned repository to {self.local_path}")
        
        return success
    
    def checkout_branch(self, branch_name: str, create: bool = False) -> bool:
        """
        Checkout a branch in the repository.
        
        Args:
            branch_name: Name of the branch to checkout
            create: Whether to create the branch if it doesn't exist
            
        Returns:
            True if successful, False otherwise
        """
        if create:
            success, output = self._run_git_command(
                ["git", "checkout", "-b", branch_name]
            )
        else:
            success, output = self._run_git_command(
                ["git", "checkout", branch_name]
            )
            
        if success:
            self.branch = branch_name
            logger.info(f"Switched to branch: {branch_name}")
        
        return success
    
    def pull_latest_changes(self, branch: Optional[str] = None) -> bool:
        """
        Pull the latest changes from the remote repository.
        
        Args:
            branch: Branch to pull from (defaults to current branch)
            
        Returns:
            True if successful, False otherwise
        """
        target_branch = branch or self.branch
        success, output = self._run_git_command(
            ["git", "pull", "origin", target_branch]
        )
        
        if success:
            logger.info(f"Successfully pulled latest changes from {target_branch}")
        
        return success
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> bool:
        """
        Commit changes to the repository.
        
        Args:
            message: Commit message
            files: List of files to commit (None for all changes)
            
        Returns:
            True if successful, False otherwise
        """
        if files:
            for file in files:
                self._run_git_command(["git", "add", file])
        else:
            self._run_git_command(["git", "add", "."])
            
        success, output = self._run_git_command(
            ["git", "commit", "-m", message]
        )
        
        if success:
            logger.info(f"Successfully committed changes: {message}")
        
        return success
    
    def push_changes(self, branch: Optional[str] = None) -> bool:
        """
        Push changes to the remote repository.
        
        Args:
            branch: Branch to push to (defaults to current branch)
            
        Returns:
            True if successful, False otherwise
        """
        target_branch = branch or self.branch
        success, output = self._run_git_command(
            ["git", "push", "origin", target_branch]
        )
        
        if success:
            logger.info(f"Successfully pushed changes to {target_branch}")
        
        return success
    
    def create_and_switch_branch(self, branch_name: str, from_branch: Optional[str] = None) -> bool:
        """
        Create a new branch and switch to it.
        
        Args:
            branch_name: Name of the new branch
            from_branch: Branch to create from (defaults to current branch)
            
        Returns:
            True if successful, False otherwise
        """
        if from_branch:
            success = self.checkout_branch(from_branch)
            if not success:
                return False
                
        return self.checkout_branch(branch_name, create=True)
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get the content of a file from the repository.
        
        Args:
            file_path: Path to the file relative to the repository root
            
        Returns:
            File content as string, or None if the file doesn't exist
        """
        full_path = os.path.join(self.local_path, file_path)
        if not os.path.exists(full_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        try:
            with open(full_path, 'r') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def update_file(self, file_path: str, content: str) -> bool:
        """
        Update the content of a file in the repository.
        
        Args:
            file_path: Path to the file relative to the repository root
            content: New content for the file
            
        Returns:
            True if successful, False otherwise
        """
        full_path = os.path.join(self.local_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, 'w') as file:
                file.write(content)
            logger.info(f"Successfully updated file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error updating file {file_path}: {e}")
            return False
    
    def get_modified_files(self) -> List[str]:
        """
        Get a list of modified files in the repository.
        
        Returns:
            List of modified file paths
        """
        success, output = self._run_git_command(
            ["git", "status", "--porcelain"]
        )
        
        if not success:
            return []
            
        modified_files = []
        for line in output.split('\n'):
            if line.strip():
                # Extract the file path from the status line
                status = line[:2]
                file_path = line[3:].strip()
                modified_files.append(file_path)
                
        return modified_files
