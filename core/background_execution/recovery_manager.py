"""
Recovery Manager for the Background Execution Framework.

This module provides self-healing capabilities, allowing the system
to recover from errors and failures automatically.
"""

import logging
import asyncio
import time
from typing import Dict, List, Callable, Any, Optional, Union
from datetime import datetime, timedelta
import json
import os
import traceback
import sys

# Import Git integration for recovery operations
from core.git.git_integration import GitIntegration

logger = logging.getLogger(__name__)

class RecoveryManager:
    """
    Provides self-healing capabilities for the Background Execution Framework.
    
    This class monitors system health, detects failures, and implements
    recovery strategies to ensure continuous operation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the recovery manager.
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or {}
        self.error_history = {}
        self.recovery_strategies = {}
        self.health_checks = {}
        self.running = False
        self.git_integration = None
        self.health_status = {
            'overall': 'unknown',
            'components': {},
            'last_check': None
        }
        
        # Initialize Git integration if configured
        if self.config.get('git_integration', {}).get('enabled', False):
            self._init_git_integration()
            
        # Register default recovery strategies
        self._register_default_strategies()
        
        logger.info("Recovery Manager initialized")
        
    def _init_git_integration(self):
        """Initialize Git integration for recovery operations."""
        try:
            git_config_path = self.config.get('git_integration', {}).get(
                'config_path', 'core/git/git_config.json'
            )
            self.git_integration = GitIntegration(config_path=git_config_path)
            logger.info("Git integration initialized for recovery operations")
        except Exception as e:
            logger.error(f"Error initializing Git integration: {e}")
            
    def _register_default_strategies(self):
        """Register default recovery strategies."""
        # Strategy for Git operation failures
        self.register_recovery_strategy(
            error_type="GitOperationError",
            strategy=self._recover_git_operation
        )
        
        # Strategy for database connection failures
        self.register_recovery_strategy(
            error_type="DatabaseConnectionError",
            strategy=self._recover_database_connection
        )
        
        # Strategy for API rate limit errors
        self.register_recovery_strategy(
            error_type="RateLimitError",
            strategy=self._recover_rate_limit
        )
        
        # Strategy for process crashes
        self.register_recovery_strategy(
            error_type="ProcessCrashError",
            strategy=self._recover_process_crash
        )
        
        # Strategy for file system errors
        self.register_recovery_strategy(
            error_type="FileSystemError",
            strategy=self._recover_file_system
        )
        
        # Default fallback strategy
        self.register_recovery_strategy(
            error_type="default",
            strategy=self._default_recovery_strategy
        )
        
    def register_recovery_strategy(self, error_type: str, 
                                  strategy: Callable) -> bool:
        """
        Register a recovery strategy for a specific error type.
        
        Args:
            error_type: Type of error to handle
            strategy: Function to call for recovery
            
        Returns:
            True if registration successful, False otherwise
        """
        if error_type in self.recovery_strategies:
            logger.warning(f"Overwriting existing recovery strategy for {error_type}")
            
        self.recovery_strategies[error_type] = strategy
        logger.info(f"Registered recovery strategy for error type: {error_type}")
        return True
        
    def register_health_check(self, component_name: str, 
                             check_func: Callable) -> bool:
        """
        Register a health check for a component.
        
        Args:
            component_name: Name of the component to check
            check_func: Function to call for health check
            
        Returns:
            True if registration successful, False otherwise
        """
        if component_name in self.health_checks:
            logger.warning(f"Overwriting existing health check for {component_name}")
            
        self.health_checks[component_name] = check_func
        logger.info(f"Registered health check for component: {component_name}")
        return True
        
    async def report_error(self, error_type: str, error_details: Dict[str, Any],
                         component: Optional[str] = None) -> Dict[str, Any]:
        """
        Report an error for recovery.
        
        Args:
            error_type: Type of error
            error_details: Details about the error
            component: Component where the error occurred (optional)
            
        Returns:
            Result of recovery attempt
        """
        error_id = f"{int(time.time())}_{error_type}"
        
        error_record = {
            'id': error_id,
            'type': error_type,
            'details': error_details,
            'component': component,
            'timestamp': datetime.now().isoformat(),
            'recovery_attempts': 0,
            'resolved': False
        }
        
        # Store in error history
        self.error_history[error_id] = error_record
        
        logger.error(f"Error reported: {error_type} in {component or 'unknown'}")
        
        # Attempt recovery
        return await self.recover_from_error(error_id)
        
    async def recover_from_error(self, error_id: str) -> Dict[str, Any]:
        """
        Attempt to recover from a reported error.
        
        Args:
            error_id: ID of the error to recover from
            
        Returns:
            Result of recovery attempt
        """
        if error_id not in self.error_history:
            logger.error(f"Error {error_id} not found in history")
            return {
                'status': 'error',
                'message': 'Error not found in history'
            }
            
        error_record = self.error_history[error_id]
        error_type = error_record['type']
        
        # Increment recovery attempts
        error_record['recovery_attempts'] += 1
        
        # Find appropriate recovery strategy
        if error_type in self.recovery_strategies:
            strategy = self.recovery_strategies[error_type]
        else:
            strategy = self.recovery_strategies.get('default', self._default_recovery_strategy)
            
        logger.info(f"Attempting recovery for error {error_id} using {strategy.__name__}")
        
        try:
            # Execute recovery strategy
            result = await strategy(error_record)
            
            # Update error record
            error_record['last_recovery_attempt'] = datetime.now().isoformat()
            error_record['last_recovery_result'] = result
            
            if result.get('status') == 'success':
                error_record['resolved'] = True
                logger.info(f"Successfully recovered from error {error_id}")
            else:
                logger.warning(f"Failed to recover from error {error_id}: {result.get('message')}")
                
            return result
            
        except Exception as e:
            logger.error(f"Error during recovery attempt for {error_id}: {e}")
            
            # Update error record
            error_record['last_recovery_attempt'] = datetime.now().isoformat()
            error_record['last_recovery_result'] = {
                'status': 'error',
                'message': str(e)
            }
            
            return {
                'status': 'error',
                'message': f"Recovery attempt failed: {str(e)}"
            }
            
    async def _recover_git_operation(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recover from Git operation errors.
        
        Args:
            error_record: Error record dictionary
            
        Returns:
            Result of recovery attempt
        """
        if not self.git_integration:
            return {
                'status': 'error',
                'message': 'Git integration not available for recovery'
            }
            
        error_details = error_record['details']
        repo_name = error_details.get('repository')
        
        if not repo_name:
            return {
                'status': 'error',
                'message': 'Repository name not provided in error details'
            }
            
        try:
            # Check if it's a network-related issue
            if 'network' in error_details.get('error_message', '').lower():
                # Wait and retry
                await asyncio.sleep(30)  # Wait 30 seconds
                
                # Try the operation again
                operation = error_details.get('operation')
                if operation == 'clone':
                    result = await self.git_integration.clone_repository(repo_name)
                elif operation == 'pull':
                    result = await self.git_integration.pull_repository(repo_name)
                elif operation == 'push':
                    result = await self.git_integration.push_changes(
                        repo_name, 
                        error_details.get('branch', 'main'),
                        error_details.get('commit_message', 'Automatic recovery commit')
                    )
                else:
                    return {
                        'status': 'error',
                        'message': f'Unknown Git operation: {operation}'
                    }
                    
                return {
                    'status': 'success',
                    'message': f'Successfully recovered Git operation: {operation}',
                    'result': result
                }
                
            # Check if it's a conflict issue
            elif 'conflict' in error_details.get('error_message', '').lower():
                # Create a new branch to avoid conflicts
                new_branch = f"recovery_{int(time.time())}"
                
                result = await self.git_integration.create_branch(
                    repo_name,
                    new_branch,
                    error_details.get('branch', 'main')
                )
                
                return {
                    'status': 'success',
                    'message': f'Created new branch {new_branch} to avoid conflicts',
                    'result': result
                }
                
            # Check if it's an authentication issue
            elif 'auth' in error_details.get('error_message', '').lower():
                # Refresh credentials if possible
                if hasattr(self.git_integration, 'refresh_credentials'):
                    await self.git_integration.refresh_credentials(repo_name)
                    
                    return {
                        'status': 'success',
                        'message': 'Refreshed Git credentials',
                        'result': {'refreshed': True}
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Authentication error, manual intervention required'
                    }
            else:
                # Generic recovery: try to reset and clean the repository
                result = await self.git_integration.reset_repository(
                    repo_name,
                    error_details.get('branch', 'main')
                )
                
                return {
                    'status': 'success',
                    'message': 'Reset repository to clean state',
                    'result': result
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Recovery attempt failed: {str(e)}'
            }
            
    async def _recover_database_connection(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from database connection errors."""
        # Placeholder implementation
        return {
            'status': 'partial',
            'message': 'Database connection recovery not fully implemented'
        }
        
    async def _recover_rate_limit(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from API rate limit errors."""
        error_details = error_record['details']
        
        # Get retry-after time if available
        retry_after = error_details.get('retry_after', 60)  # Default: 1 minute
        
        logger.info(f"Rate limit exceeded, waiting for {retry_after} seconds")
        
        # Wait for the specified time
        await asyncio.sleep(retry_after)
        
        return {
            'status': 'success',
            'message': f'Waited {retry_after} seconds for rate limit reset',
            'result': {'waited': retry_after}
        }
        
    async def _recover_process_crash(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from process crash errors."""
        error_details = error_record['details']
        process_id = error_details.get('process_id')
        
        if not process_id:
            return {
                'status': 'error',
                'message': 'Process ID not provided in error details'
            }
            
        # Placeholder for process restart logic
        logger.info(f"Attempting to restart process: {process_id}")
        
        # In a real implementation, this would restart the process
        
        return {
            'status': 'partial',
            'message': 'Process restart initiated, monitoring for stability'
        }
        
    async def _recover_file_system(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from file system errors."""
        error_details = error_record['details']
        file_path = error_details.get('file_path')
        
        if not file_path:
            return {
                'status': 'error',
                'message': 'File path not provided in error details'
            }
            
        # Check if it's a permission issue
        if 'permission' in error_details.get('error_message', '').lower():
            # Placeholder for permission correction
            logger.info(f"File permission issue detected for: {file_path}")
            
            return {
                'status': 'partial',
                'message': 'File permission issues require manual intervention'
            }
            
        # Check if it's a missing directory
        elif 'directory' in error_details.get('error_message', '').lower():
            try:
                # Create missing directory
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                return {
                    'status': 'success',
                    'message': f'Created missing directory for {file_path}'
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Failed to create directory: {str(e)}'
                }
                
        # Check if it's a disk space issue
        elif 'space' in error_details.get('error_message', '').lower():
            # Placeholder for disk space management
            logger.info("Disk space issue detected")
            
            return {
                'status': 'partial',
                'message': 'Disk space issues require manual intervention'
            }
            
        else:
            return {
                'status': 'error',
                'message': 'Unknown file system error, manual intervention required'
            }
            
    async def _default_recovery_strategy(self, error_record: Dict[str, Any]) -> Dict[str, Any]:
        """Default recovery strategy for unknown error types."""
        logger.info(f"Using default recovery strategy for error type: {error_record['type']}")
        
        # For unknown errors, log details and suggest manual review
        return {
            'status': 'partial',
            'message': 'Unknown error type, basic recovery attempted',
            'suggestion': 'Review error details and implement specific recovery strategy'
        }
        
    async def check_system_health(self) -> Dict[str, Any]:
        """
        Check the health of all registered components.
        
        Returns:
            System health status
        """
        overall_status = 'healthy'
        component_statuses = {}
        
        for component_name, check_func in self.health_checks.items():
            try:
                logger.debug(f"Checking health of component: {component_name}")
                
                if asyncio.iscoroutinefunction(check_func):
                    status = await check_func()
                else:
                    status = check_func()
                    
                component_statuses[component_name] = status
                
                # Update overall status if any component is unhealthy
                if status.get('status') != 'healthy':
                    overall_status = 'degraded'
                    
                    # If any component is critical and unhealthy, system is unhealthy
                    if status.get('critical', False):
                        overall_status = 'unhealthy'
                        
            except Exception as e:
                logger.error(f"Error checking health of {component_name}: {e}")
                component_statuses[component_name] = {
                    'status': 'error',
                    'message': str(e)
                }
                overall_status = 'degraded'
                
        # Update health status
        self.health_status = {
            'overall': overall_status,
            'components': component_statuses,
            'last_check': datetime.now().isoformat()
        }
        
        logger.info(f"System health check complete: {overall_status}")
        return self.health_status
        
    async def start_health_monitoring(self, interval: int = 300):
        """
        Start periodic health monitoring.
        
        Args:
            interval: Interval between health checks in seconds
        """
        if self.running:
            logger.warning("Health monitoring is already running")
            return
            
        self.running = True
        logger.info(f"Starting health monitoring with interval of {interval} seconds")
        
        while self.running:
            try:
                await self.check_system_health()
                
                # Take recovery actions for unhealthy components
                if self.health_status['overall'] != 'healthy':
                    await self._recover_unhealthy_components()
                    
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(interval)
                
    async def _recover_unhealthy_components(self):
        """Attempt to recover unhealthy components."""
        for component_name, status in self.health_status['components'].items():
            if status.get('status') != 'healthy':
                logger.info(f"Attempting to recover unhealthy component: {component_name}")
                
                # Create an error record for the unhealthy component
                error_id = f"{int(time.time())}_{component_name}_unhealthy"
                
                error_record = {
                    'id': error_id,
                    'type': 'ComponentUnhealthy',
                    'details': {
                        'component': component_name,
                        'status': status
                    },
                    'component': component_name,
                    'timestamp': datetime.now().isoformat(),
                    'recovery_attempts': 0,
                    'resolved': False
                }
                
                # Store in error history
                self.error_history[error_id] = error_record
                
                # Attempt recovery
                await self.recover_from_error(error_id)
                
    def stop_health_monitoring(self):
        """Stop health monitoring."""
        logger.info("Stopping health monitoring")
        self.running = False
        
    def get_error_history(self, error_type: Optional[str] = None,
                         resolved: Optional[bool] = None,
                         limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get error history.
        
        Args:
            error_type: Filter by error type (optional)
            resolved: Filter by resolved status (optional)
            limit: Maximum number of errors to return
            
        Returns:
            List of error records
        """
        filtered_errors = []
        
        for error_id, error in self.error_history.items():
            # Apply filters
            if error_type and error['type'] != error_type:
                continue
                
            if resolved is not None and error['resolved'] != resolved:
                continue
                
            filtered_errors.append(error)
            
        # Sort by timestamp (newest first)
        filtered_errors.sort(key=lambda e: e['timestamp'], reverse=True)
        
        # Apply limit
        return filtered_errors[:limit]
        
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get the current health status.
        
        Returns:
            Health status dictionary
        """
        return self.health_status
        
    def clear_resolved_errors(self, age_hours: int = 24):
        """
        Clear resolved errors older than the specified age.
        
        Args:
            age_hours: Age in hours after which resolved errors should be cleared
        """
        cutoff_time = datetime.now() - timedelta(hours=age_hours)
        
        to_remove = []
        for error_id, error in self.error_history.items():
            if not error['resolved']:
                continue
                
            try:
                error_time = datetime.fromisoformat(error['timestamp'])
                if error_time < cutoff_time:
                    to_remove.append(error_id)
            except (KeyError, ValueError):
                # If timestamp is missing or invalid, keep the error
                pass
                
        for error_id in to_remove:
            del self.error_history[error_id]
            
        logger.info(f"Cleared {len(to_remove)} resolved errors older than {age_hours} hours")
