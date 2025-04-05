"""
Git Integration Module for Autonomous Marketing Agent.

This module provides functionality to interact with Git repositories,
allowing the system to automatically update website files based on
continuous data and testing results.
"""

from core.git.git_integration import GitIntegration
from core.git.website_updater import WebsiteUpdater

__all__ = ['GitIntegration', 'WebsiteUpdater']
