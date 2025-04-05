"""
Process Orchestrator for the Background Execution Framework.

This module coordinates complex marketing activities in the background,
including website updates based on analytics data, task scheduling, event handling,
and self-healing capabilities.
"""

import logging
import asyncio
import json
import os
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta

# Import Git integration components
from core.git.git_integration import GitIntegration
from core.git.website_updater import WebsiteUpdater

# Import Background Execution Framework components
from core.background_execution.task_scheduler import TaskScheduler
from core.background_execution.event_manager import EventManager
from core.background_execution.recovery_manager import RecoveryManager

logger = logging.getLogger(__name__)

class ProcessOrchestrator:
    """
    Coordinates complex marketing activities in the background.
    
    This class orchestrates various processes, including website updates
    based on analytics data, and provides scheduling, event handling,
    and self-healing capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the process orchestrator.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = self._load_config(config_path)
        self.processes = {}
        self.running_processes = set()
        self.process_history = {}
        
        # Initialize Git integration
        git_config_path = self.config.get('git_integration', {}).get(
            'config_path', 'core/git/git_config.json'
        )
        self.git_integration = GitIntegration(config_path=git_config_path)
        
        # Initialize website updater
        self.website_updater = WebsiteUpdater(self.git_integration)
        
        # Initialize Task Scheduler
        self.task_scheduler = TaskScheduler(self.config.get('task_scheduler', {}))
        
        # Initialize Event Manager
        self.event_manager = EventManager(self.config.get('event_manager', {}))
        
        # Initialize Recovery Manager
        self.recovery_manager = RecoveryManager(self.config.get('recovery_manager', {}))
        
        # Register health checks
        self._register_health_checks()
        
        # Register event handlers
        self._register_event_handlers()
        
        logger.info("Process Orchestrator initialized with all components")
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            'max_concurrent_processes': 5,
            'process_timeout': 3600,  # 1 hour
            'git_integration': {
                'enabled': True,
                'config_path': 'core/git/git_config.json'
            },
            'website_updates': {
                'enabled': True,
                'schedule': {
                    'type': 'interval',
                    'value': 86400  # 24 hours
                }
            },
            'task_scheduler': {
                'max_concurrent_tasks': 10
            },
            'event_manager': {
                'event_history_limit': 100,
                'analytics_integration': {
                    'enabled': True
                }
            },
            'recovery_manager': {
                'git_integration': {
                    'enabled': True
                }
            }
        }
        
        if not config_path:
            logger.info("No config path provided, using default configuration")
            return default_config
            
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return {**default_config, **config}
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
            logger.info("Using default configuration")
            return default_config
            
    def _init_git_integration(self):
        """Initialize Git integration and website updater."""
        try:
            git_config_path = self.config.get('git_integration', {}).get(
                'config_path', 'core/git/git_config.json'
            )
            self.git_integration = GitIntegration(config_path=git_config_path)
            self.website_updater = WebsiteUpdater(self.git_integration)
            logger.info("Git integration initialized")
        except Exception as e:
            logger.error(f"Error initializing Git integration: {e}")
            
    def _register_health_checks(self):
        """Register health checks with the Recovery Manager."""
        # Register health check for Git integration
        self.recovery_manager.register_health_check(
            'git_integration',
            self._check_git_integration_health
        )
        
        # Register health check for Task Scheduler
        self.recovery_manager.register_health_check(
            'task_scheduler',
            self._check_task_scheduler_health
        )
        
        # Register health check for Event Manager
        self.recovery_manager.register_health_check(
            'event_manager',
            self._check_event_manager_health
        )
        
    def _register_event_handlers(self):
        """Register event handlers with the Event Manager."""
        # Register handler for content performance changes
        self.event_manager.subscribe(
            'content_performance_change',
            self._handle_content_performance_change,
            'process_orchestrator'
        )
        
        # Register handler for traffic spikes
        self.event_manager.subscribe(
            'traffic_spike',
            self._handle_traffic_spike,
            'process_orchestrator'
        )
        
        # Register handler for system errors
        self.event_manager.subscribe(
            'system_error',
            self._handle_system_error,
            'process_orchestrator'
        )
        
    async def _check_git_integration_health(self) -> Dict[str, Any]:
        """Check the health of the Git integration."""
        try:
            # Perform a simple Git operation to check health
            repos = self.git_integration.list_repositories()
            return {
                'status': 'healthy',
                'message': f'Git integration is healthy, {len(repos)} repositories available',
                'critical': True  # Git integration is critical for website updates
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Git integration is unhealthy: {str(e)}',
                'critical': True
            }
            
    async def _check_task_scheduler_health(self) -> Dict[str, Any]:
        """Check the health of the Task Scheduler."""
        try:
            # Check if Task Scheduler is running
            if hasattr(self.task_scheduler, 'running') and self.task_scheduler.running:
                return {
                    'status': 'healthy',
                    'message': 'Task Scheduler is running',
                    'critical': True
                }
            else:
                return {
                    'status': 'degraded',
                    'message': 'Task Scheduler is not running',
                    'critical': True
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Task Scheduler is unhealthy: {str(e)}',
                'critical': True
            }
            
    async def _check_event_manager_health(self) -> Dict[str, Any]:
        """Check the health of the Event Manager."""
        try:
            # Check if Event Manager has subscribers
            subscriber_counts = self.event_manager.get_subscriber_count()
            return {
                'status': 'healthy',
                'message': f'Event Manager is healthy with {sum(subscriber_counts.values())} total subscribers',
                'critical': False  # Event Manager is important but not critical
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Event Manager is unhealthy: {str(e)}',
                'critical': False
            }
            
    def register_process(self, process_id: str, process_func: Callable, 
                        dependencies: Optional[List[str]] = None,
                        schedule: Optional[Dict[str, Any]] = None,
                        event_triggers: Optional[List[str]] = None) -> bool:
        """
        Register a process with the orchestrator.
        
        Args:
            process_id: Unique identifier for the process
            process_func: Function to execute for this process
            dependencies: List of process IDs that must complete before this one
            schedule: Scheduling information (frequency, start time, etc.)
            event_triggers: List of events that can trigger this process
            
        Returns:
            True if registration successful, False otherwise
        """
        if process_id in self.processes:
            logger.warning(f"Process {process_id} already registered")
            return False
            
        self.processes[process_id] = {
            'func': process_func,
            'schedule': schedule or {},
            'last_run': None,
            'last_status': None,
            'retry_count': 0
        }
        
        self.dependencies[process_id] = dependencies or []
        
        if event_triggers:
            for event in event_triggers:
                if event not in self.event_hooks:
                    self.event_hooks[event] = []
                self.event_hooks[event].append(process_id)
                
        logger.info(f"Registered process: {process_id}")
        return True
        
    async def execute_process(self, process_id: str, 
                             params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a registered process.
        
        Args:
            process_id: ID of the process to execute
            params: Parameters to pass to the process
            
        Returns:
            Result of the process execution
        """
        if process_id not in self.processes:
            logger.error(f"Process {process_id} not registered")
            return {'status': 'error', 'message': 'Process not registered'}
            
        # Check dependencies
        for dep_id in self.dependencies[process_id]:
            if dep_id in self.running_processes:
                logger.info(f"Waiting for dependency {dep_id} to complete")
                # Wait for dependency to complete
                while dep_id in self.running_processes:
                    await asyncio.sleep(1)
                    
            # Check if dependency completed successfully
            if (dep_id not in self.processes or 
                self.processes[dep_id]['last_status'] != 'success'):
                logger.error(f"Dependency {dep_id} failed or not executed")
                return {
                    'status': 'error', 
                    'message': f'Dependency {dep_id} failed or not executed'
                }
                
        # Mark process as running
        self.running_processes[process_id] = datetime.now()
        
        try:
            # Execute the process
            logger.info(f"Executing process: {process_id}")
            result = await self.processes[process_id]['func'](params or {})
            
            # Update process status
            self.processes[process_id]['last_run'] = datetime.now()
            self.processes[process_id]['last_status'] = 'success'
            self.processes[process_id]['retry_count'] = 0
            
            logger.info(f"Process {process_id} completed successfully")
            return {'status': 'success', 'result': result}
            
        except Exception as e:
            logger.error(f"Error executing process {process_id}: {e}")
            
            # Update process status
            self.processes[process_id]['last_run'] = datetime.now()
            self.processes[process_id]['last_status'] = 'error'
            
            # Handle retry logic
            if self.processes[process_id]['retry_count'] < self.config['retry_attempts']:
                self.processes[process_id]['retry_count'] += 1
                retry_delay = self.config['retry_delay']
                logger.info(f"Scheduling retry for {process_id} in {retry_delay} seconds")
                
                # Schedule retry
                asyncio.create_task(self._retry_process(process_id, params, retry_delay))
                
            return {'status': 'error', 'message': str(e)}
            
        finally:
            # Remove from running processes
            if process_id in self.running_processes:
                del self.running_processes[process_id]
                
    async def _retry_process(self, process_id: str, params: Dict[str, Any], delay: int):
        """
        Retry a failed process after a delay.
        
        Args:
            process_id: ID of the process to retry
            params: Parameters to pass to the process
            delay: Delay in seconds before retrying
        """
        await asyncio.sleep(delay)
        logger.info(f"Retrying process {process_id}")
        await self.execute_process(process_id, params)
        
    async def trigger_event(self, event_name: str, event_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Trigger processes associated with an event.
        
        Args:
            event_name: Name of the event
            event_data: Data associated with the event
            
        Returns:
            List of results from triggered processes
        """
        if event_name not in self.event_hooks:
            logger.info(f"No processes registered for event: {event_name}")
            return []
            
        results = []
        for process_id in self.event_hooks[event_name]:
            logger.info(f"Triggering process {process_id} for event {event_name}")
            result = await self.execute_process(process_id, event_data)
            results.append({
                'process_id': process_id,
                'result': result
            })
            
        return results
        
    async def schedule_website_update(self, repository_name: str = None, 
                                    schedule_type: str = 'interval',
                                    schedule_value: Any = 86400):
        """
        Schedule a website update using Git integration.
        
        Args:
            repository_name: Name of the repository to update (optional)
            schedule_type: Type of schedule ('interval', 'cron', 'once', 'immediate')
            schedule_value: Value for the schedule type
            
        Returns:
            Result of the update process
        """
        if not self.website_updater:
            logger.error("Website updater not initialized")
            return {
                'status': 'error',
                'message': 'Website updater not initialized'
            }
            
        process_id = f"website_update_{repository_name or 'all'}_{int(datetime.now().timestamp())}"
        
        # Create a task for the website update
        task_id = f"task_{process_id}"
        
        self.task_scheduler.schedule_task(
            task_id=task_id,
            task_func=self._run_website_update,
            schedule_type=schedule_type,
            schedule_value=schedule_value,
            priority=5,  # Medium priority
            params={'repository_name': repository_name}
        )
        
        process = {
            'id': process_id,
            'type': 'website_update',
            'params': {
                'repository_name': repository_name
            },
            'task_id': task_id,
            'schedule': {
                'type': schedule_type,
                'value': schedule_value
            },
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }
        
        self.processes[process_id] = process
        logger.info(f"Scheduled website update for {repository_name or 'all'}, process ID: {process_id}")
        
        # Publish an event for the scheduled update
        await self.event_manager.publish(
            event_name='website_update_scheduled',
            event_data={
                'process_id': process_id,
                'repository_name': repository_name,
                'schedule_type': schedule_type,
                'schedule_value': schedule_value
            },
            publisher_id='process_orchestrator'
        )
        
        return process
        
    async def _run_website_update(self, repository_name: str = None):
        """
        Run a website update using Git integration.
        
        Args:
            repository_name: Name of the repository to update (optional)
            
        Returns:
            Result of the update process
        """
        try:
            logger.info(f"Running website update for repository: {repository_name or 'all'}")
            
            if repository_name:
                # Update specific repository
                result = await self.website_updater.update_website(repository_name)
            else:
                # Update all repositories
                results = []
                for repo in self.website_updater.get_all_repository_configs():
                    repo_name = repo.get('name')
                    if repo_name:
                        result = await self.website_updater.update_website(repo_name)
                        results.append({
                            'repository': repo_name,
                            'result': result
                        })
                result = {'repositories': results}
                
            # Record the update in history
            update_id = f"website_update_{repository_name or 'all'}"
            self.process_history[update_id] = {
                'timestamp': datetime.now().isoformat(),
                'result': result
            }
            
            # Publish event for completed update
            await self.event_manager.publish(
                event_name='website_update_completed',
                event_data={
                    'repository_name': repository_name,
                    'result': result
                },
                publisher_id='process_orchestrator'
            )
            
            return {
                'status': 'success',
                'result': result
            }
        except Exception as e:
            logger.error(f"Error updating website: {e}")
            
            # Report error to Recovery Manager
            await self.recovery_manager.report_error(
                error_type="GitOperationError",
                error_details={
                    'repository': repository_name,
                    'operation': 'website_update',
                    'error_message': str(e)
                },
                component="website_updater"
            )
            
            return {
                'status': 'error',
                'message': str(e)
            }
    async def run_scheduled_processes(self) -> Dict[str, Any]:
        """
        Run all processes that are due according to their schedules.
        
        Returns:
            Dictionary of process IDs and their execution results
        """
        results = {}
        now = datetime.now()
        
        for process_id, process in self.processes.items():
            if not process.get('schedule'):
                continue
                
            schedule = process['schedule']
            last_run = process.get('last_run')
            
            # Check if process should run
            should_run = False
            
            if not last_run:
                should_run = True
            elif 'interval' in schedule:
                # Interval-based scheduling (in seconds)
                interval = schedule['interval']
                time_since_last_run = (now - last_run).total_seconds()
                should_run = time_since_last_run >= interval
            elif 'cron' in schedule:
                # TODO: Implement cron-based scheduling
                pass
                
            if should_run and process_id not in self.running_processes:
                logger.info(f"Running scheduled process: {process_id}")
                result = await self.execute_process(process_id)
                results[process_id] = result
                
        return results
        
    async def start_scheduler(self):
        """Start the process scheduler to run in the background."""
        logger.info("Starting process scheduler")
        
        while True:
            try:
                await self.run_scheduled_processes()
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                
            # Sleep for a minute before checking schedules again
            await asyncio.sleep(60)
            
    def register_website_update_process(self, repository_name: str = None,
                                       schedule: Dict[str, Any] = None) -> bool:
        """
        Register a website update process.
        
        Args:
            repository_name: Name of the repository to update (optional)
            schedule: Scheduling information (frequency, start time, etc.)
            
        Returns:
            True if registration successful, False otherwise
        """
        if not self.website_updater:
            logger.error("Website updater not initialized")
            return False
            
        process_id = f"website_update_{repository_name}" if repository_name else "website_update_all"
        
        async def update_website_process(params):
            return await self.schedule_website_update(repository_name)
            
        return self.register_process(
            process_id=process_id,
            process_func=update_website_process,
            schedule=schedule or {'interval': 86400},  # Default: daily
            event_triggers=["content_performance_change", "analytics_update"]
        )
        
    async def initialize_all_processes(self):
        """Initialize and register all standard processes."""
        # Register website update process if Git integration is enabled
        if self.website_updater:
            self.register_website_update_process()
            
            # Register individual repository update processes
            for repo in self.website_updater.get_all_repository_configs():
                repo_name = repo.get('name')
                if repo_name:
                    self.register_website_update_process(
                        repository_name=repo_name,
                        schedule={'interval': repo.get('update_interval', 86400)}
                    )
                    
        # TODO: Register other standard processes
        
        logger.info("All standard processes initialized")
        
    async def start(self):
        """Start the process orchestrator."""
        logger.info("Starting Process Orchestrator")
        
        # Initialize all processes
        await self.initialize_all_processes()
        
        # Start the Task Scheduler
        asyncio.create_task(self.task_scheduler.run())
        
        # Start the Recovery Manager health monitoring
        asyncio.create_task(self.recovery_manager.start_health_monitoring())
        
        # Register standard analytics events
        await self.event_manager.register_analytics_events()
        
        # Start the scheduler
        asyncio.create_task(self.start_scheduler())
        
        logger.info("Process Orchestrator started with all components")
        
    async def _handle_content_performance_change(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content performance change events."""
        logger.info(f"Handling content performance change: {event}")
        
        # Extract relevant data
        content_id = event.get('data', {}).get('content_id')
        performance_change = event.get('data', {}).get('change')
        
        if not content_id or not performance_change:
            return {
                'status': 'error',
                'message': 'Missing required event data'
            }
            
        # Schedule a website update if performance decreased significantly
        if performance_change < -20:  # 20% decrease
            repo_name = self._get_repo_for_content(content_id)
            if repo_name:
                await self.schedule_website_update(repo_name, 'immediate', None)
                
                return {
                    'status': 'success',
                    'message': f'Scheduled immediate website update for {repo_name} due to performance drop',
                    'action': 'website_update_scheduled'
                }
                
        return {
            'status': 'success',
            'message': 'Content performance change processed',
            'action': 'no_action_needed'
        }
        
    async def _handle_traffic_spike(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle traffic spike events."""
        logger.info(f"Handling traffic spike: {event}")
        
        # Extract relevant data
        page_url = event.get('data', {}).get('page_url')
        spike_percentage = event.get('data', {}).get('spike_percentage')
        
        if not page_url or not spike_percentage:
            return {
                'status': 'error',
                'message': 'Missing required event data'
            }
            
        # Schedule a task to analyze the traffic spike
        task_id = f"analyze_traffic_spike_{int(datetime.now().timestamp())}"
        
        self.task_scheduler.schedule_task(
            task_id=task_id,
            task_func=self._analyze_traffic_spike,
            schedule_type='immediate',
            schedule_value=None,
            priority=2,  # High priority
            params={
                'page_url': page_url,
                'spike_percentage': spike_percentage
            }
        )
        
        return {
            'status': 'success',
            'message': f'Scheduled traffic spike analysis task: {task_id}',
            'action': 'analysis_task_scheduled'
        }
        
    async def _handle_system_error(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system error events."""
        logger.info(f"Handling system error: {event}")
        
        # Extract relevant data
        error_type = event.get('data', {}).get('error_type')
        error_details = event.get('data', {}).get('error_details', {})
        component = event.get('data', {}).get('component')
        
        if not error_type:
            return {
                'status': 'error',
                'message': 'Missing required event data'
            }
            
        # Report the error to the Recovery Manager
        recovery_result = await self.recovery_manager.report_error(
            error_type=error_type,
            error_details=error_details,
            component=component
        )
        
        return {
            'status': 'success',
            'message': f'Reported error to Recovery Manager',
            'recovery_result': recovery_result
        }
        
    async def _analyze_traffic_spike(self, page_url: str, spike_percentage: float) -> Dict[str, Any]:
        """Analyze a traffic spike on a specific page."""
        logger.info(f"Analyzing traffic spike of {spike_percentage}% on {page_url}")
        
        # In a real implementation, this would perform detailed analysis
        # and potentially trigger actions based on the results
        
        # For now, just return a placeholder result
        analysis_result = {
            'page_url': page_url,
            'spike_percentage': spike_percentage,
            'analysis': {
                'source': 'social_media' if spike_percentage > 200 else 'organic',
                'significance': 'high' if spike_percentage > 100 else 'medium',
                'recommendation': 'optimize_content' if spike_percentage > 50 else 'monitor'
            }
        }
        
        # Publish an event with the analysis results
        await self.event_manager.publish(
            event_name='traffic_spike_analysis_complete',
            event_data=analysis_result,
            publisher_id='process_orchestrator'
        )
        
        return analysis_result
        
    def _get_repo_for_content(self, content_id: str) -> Optional[str]:
        """Get the repository name for a content ID."""
        # In a real implementation, this would look up the repository
        # based on the content ID in a database or configuration
        
        # For now, just return a placeholder result
        content_repo_mapping = self.config.get('content_repo_mapping', {})
        return content_repo_mapping.get(content_id)
