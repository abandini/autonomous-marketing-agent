"""
Task Scheduler for the Background Execution Framework.

This module provides scheduling capabilities for marketing tasks,
supporting various scheduling patterns and priorities.
"""

import logging
import asyncio
import time
from typing import Dict, List, Callable, Any, Optional, Union
from datetime import datetime, timedelta
import heapq
import json
from croniter import croniter

logger = logging.getLogger(__name__)

class TaskScheduler:
    """
    Manages scheduling and execution of marketing tasks.
    
    This class provides advanced scheduling capabilities including
    cron-style scheduling, interval-based scheduling, and priority-based
    execution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the task scheduler.
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or {}
        self.tasks = {}
        self.task_queue = []  # Priority queue
        self.running_tasks = set()
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 10)
        self.running = False
        self.task_results = {}
        
        logger.info("Task Scheduler initialized")
        
    def schedule_task(self, task_id: str, task_func: Callable, 
                     schedule_type: str, schedule_value: Any,
                     priority: int = 5, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Schedule a task for execution.
        
        Args:
            task_id: Unique identifier for the task
            task_func: Function to execute for this task
            schedule_type: Type of schedule ('interval', 'cron', 'once', 'immediate')
            schedule_value: Value for the schedule type (seconds for interval, cron expression for cron, datetime for once)
            priority: Priority level (1-10, 1 being highest)
            params: Parameters to pass to the task function
            
        Returns:
            True if scheduling successful, False otherwise
        """
        if task_id in self.tasks:
            logger.warning(f"Task {task_id} already scheduled")
            return False
            
        next_run = self._calculate_next_run(schedule_type, schedule_value)
        if next_run is None:
            logger.error(f"Invalid schedule for task {task_id}")
            return False
            
        task = {
            'id': task_id,
            'func': task_func,
            'schedule_type': schedule_type,
            'schedule_value': schedule_value,
            'priority': priority,
            'params': params or {},
            'next_run': next_run,
            'last_run': None,
            'last_status': None,
            'run_count': 0
        }
        
        self.tasks[task_id] = task
        
        # Add to priority queue
        self._add_to_queue(task)
        
        logger.info(f"Scheduled task: {task_id}, next run: {next_run}")
        return True
        
    def _calculate_next_run(self, schedule_type: str, schedule_value: Any) -> Optional[datetime]:
        """
        Calculate the next run time for a task.
        
        Args:
            schedule_type: Type of schedule
            schedule_value: Value for the schedule type
            
        Returns:
            Next run time as datetime or None if invalid
        """
        now = datetime.now()
        
        if schedule_type == 'interval':
            # Interval in seconds
            try:
                interval = int(schedule_value)
                return now + timedelta(seconds=interval)
            except (ValueError, TypeError):
                logger.error(f"Invalid interval value: {schedule_value}")
                return None
                
        elif schedule_type == 'cron':
            # Cron expression
            try:
                iter = croniter(schedule_value, now)
                return iter.get_next(datetime)
            except Exception as e:
                logger.error(f"Invalid cron expression: {schedule_value}, error: {e}")
                return None
                
        elif schedule_type == 'once':
            # Specific datetime
            if isinstance(schedule_value, datetime):
                return schedule_value
            elif isinstance(schedule_value, str):
                try:
                    return datetime.fromisoformat(schedule_value)
                except ValueError:
                    logger.error(f"Invalid datetime string: {schedule_value}")
                    return None
            else:
                logger.error(f"Invalid schedule_value type for 'once': {type(schedule_value)}")
                return None
                
        elif schedule_type == 'immediate':
            # Run immediately
            return now
            
        else:
            logger.error(f"Unknown schedule type: {schedule_type}")
            return None
            
    def _add_to_queue(self, task: Dict[str, Any]):
        """
        Add a task to the priority queue.
        
        Args:
            task: Task dictionary
        """
        # Queue items are (next_run, priority, task_id)
        # Lower priority number means higher priority
        queue_item = (task['next_run'], task['priority'], task['id'])
        heapq.heappush(self.task_queue, queue_item)
        
    def _update_next_run(self, task_id: str) -> bool:
        """
        Update the next run time for a task.
        
        Args:
            task_id: ID of the task to update
            
        Returns:
            True if update successful, False otherwise
        """
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        
        if task['schedule_type'] == 'once':
            # One-time tasks don't get rescheduled
            return False
            
        task['next_run'] = self._calculate_next_run(
            task['schedule_type'], 
            task['schedule_value']
        )
        
        if task['next_run']:
            self._add_to_queue(task)
            return True
            
        return False
        
    async def _execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        Execute a scheduled task.
        
        Args:
            task_id: ID of the task to execute
            
        Returns:
            Result of the task execution
        """
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return {'status': 'error', 'message': 'Task not found'}
            
        task = self.tasks[task_id]
        
        # Mark as running
        self.running_tasks.add(task_id)
        
        try:
            # Execute the task
            logger.info(f"Executing task: {task_id}")
            start_time = time.time()
            
            if asyncio.iscoroutinefunction(task['func']):
                result = await task['func'](**task['params'])
            else:
                result = task['func'](**task['params'])
                
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Update task status
            task['last_run'] = datetime.now()
            task['last_status'] = 'success'
            task['run_count'] += 1
            
            # Store result
            self.task_results[task_id] = {
                'timestamp': datetime.now().isoformat(),
                'execution_time': execution_time,
                'result': result
            }
            
            logger.info(f"Task {task_id} completed successfully in {execution_time:.2f} seconds")
            return {
                'status': 'success', 
                'result': result,
                'execution_time': execution_time
            }
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            
            # Update task status
            task['last_run'] = datetime.now()
            task['last_status'] = 'error'
            task['run_count'] += 1
            
            # Store result
            self.task_results[task_id] = {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            
            return {'status': 'error', 'message': str(e)}
            
        finally:
            # Remove from running tasks
            self.running_tasks.remove(task_id)
            
            # Update next run time
            self._update_next_run(task_id)
            
    async def run(self):
        """Run the task scheduler."""
        if self.running:
            logger.warning("Task Scheduler is already running")
            return
            
        self.running = True
        logger.info("Starting Task Scheduler")
        
        while self.running:
            try:
                await self._process_due_tasks()
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error in task scheduler: {e}")
                await asyncio.sleep(5)  # Wait a bit longer on error
                
    async def _process_due_tasks(self):
        """Process all tasks that are due for execution."""
        now = datetime.now()
        
        # Check if we can run more tasks
        available_slots = self.max_concurrent_tasks - len(self.running_tasks)
        if available_slots <= 0:
            return
            
        # Get tasks that are due
        due_tasks = []
        while self.task_queue and len(due_tasks) < available_slots:
            # Peek at the next task
            next_run, priority, task_id = self.task_queue[0]
            
            if next_run <= now and task_id not in self.running_tasks:
                # Task is due, remove from queue
                heapq.heappop(self.task_queue)
                due_tasks.append(task_id)
            else:
                # No more due tasks
                break
                
        # Execute due tasks
        for task_id in due_tasks:
            asyncio.create_task(self._execute_task(task_id))
            
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task status dictionary
        """
        if task_id not in self.tasks:
            return {'status': 'error', 'message': 'Task not found'}
            
        task = self.tasks[task_id]
        status = {
            'id': task_id,
            'schedule_type': task['schedule_type'],
            'next_run': task['next_run'].isoformat() if task['next_run'] else None,
            'last_run': task['last_run'].isoformat() if task['last_run'] else None,
            'last_status': task['last_status'],
            'run_count': task['run_count'],
            'is_running': task_id in self.running_tasks
        }
        
        # Add last result if available
        if task_id in self.task_results:
            status['last_result'] = self.task_results[task_id]
            
        return status
        
    def get_all_task_statuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the status of all tasks.
        
        Returns:
            Dictionary of task IDs to status dictionaries
        """
        return {task_id: self.get_task_status(task_id) for task_id in self.tasks}
        
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            True if cancellation successful, False otherwise
        """
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found for cancellation")
            return False
            
        # Remove from tasks dictionary
        del self.tasks[task_id]
        
        # Note: We don't remove from the queue immediately as that would be inefficient
        # Instead, we'll just ignore it when it comes up for execution
        
        logger.info(f"Cancelled task: {task_id}")
        return True
        
    def stop(self):
        """Stop the task scheduler."""
        logger.info("Stopping Task Scheduler")
        self.running = False
        
    def clear_completed_results(self, age_hours: int = 24):
        """
        Clear task results older than the specified age.
        
        Args:
            age_hours: Age in hours after which results should be cleared
        """
        cutoff_time = datetime.now() - timedelta(hours=age_hours)
        
        to_remove = []
        for task_id, result in self.task_results.items():
            try:
                result_time = datetime.fromisoformat(result['timestamp'])
                if result_time < cutoff_time:
                    to_remove.append(task_id)
            except (KeyError, ValueError):
                # If timestamp is missing or invalid, remove the result
                to_remove.append(task_id)
                
        for task_id in to_remove:
            if task_id in self.task_results:
                del self.task_results[task_id]
                
        logger.info(f"Cleared {len(to_remove)} old task results")
