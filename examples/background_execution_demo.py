#!/usr/bin/env python3
"""
Demonstration of the Background Execution Framework components.
Shows how to use ProcessOrchestrator with TaskScheduler, EventManager, and RecoveryManager.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.background_execution.process_orchestrator import ProcessOrchestrator
from core.background_execution.task_scheduler import TaskScheduler
from core.background_execution.event_manager import EventManager
from core.background_execution.recovery_manager import RecoveryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('background_execution_demo.log')
    ]
)

logger = logging.getLogger('background_execution_demo')


async def example_task(param1, param2):
    """Example task function that will be scheduled."""
    logger.info(f"Running example task with params: {param1}, {param2}")
    # Simulate some work
    await asyncio.sleep(2)
    return {
        'status': 'success',
        'result': f"Processed {param1} and {param2}",
        'timestamp': datetime.now().isoformat()
    }


async def failing_task(should_fail=True):
    """Example task that fails if should_fail is True."""
    logger.info(f"Running failing task with should_fail={should_fail}")
    if should_fail:
        raise Exception("Task failed as expected")
    return {
        'status': 'success',
        'message': "Task didn't fail"
    }


async def simulate_traffic_spike():
    """Simulate a traffic spike event."""
    logger.info("Simulating traffic spike event")
    return {
        'page_url': 'https://example.com/trending-page',
        'spike_percentage': 250,
        'timestamp': datetime.now().isoformat()
    }


async def simulate_content_performance_drop():
    """Simulate a content performance drop event."""
    logger.info("Simulating content performance drop event")
    return {
        'content_id': 'content_1',
        'change': -30,  # 30% decrease
        'timestamp': datetime.now().isoformat()
    }


async def main():
    """Main function to demonstrate the Background Execution Framework."""
    # Create configuration
    config = {
        'process_orchestrator': {
            'scheduler_interval': 5,  # Check every 5 seconds
            'max_concurrent_processes': 5
        },
        'task_scheduler': {
            'max_concurrent_tasks': 10,
            'default_priority': 5
        },
        'event_manager': {
            'max_events_history': 100
        },
        'recovery_manager': {
            'health_check_interval': 10,  # Check every 10 seconds
            'max_recovery_attempts': 3
        },
        'git_integration': {
            'config_path': 'config/git_config.json'
        },
        'content_repo_mapping': {
            'content_1': 'marketing-website',
            'content_2': 'blog-content'
        }
    }

    # Create the components
    task_scheduler = TaskScheduler(config.get('task_scheduler', {}))
    event_manager = EventManager(config.get('event_manager', {}))
    recovery_manager = RecoveryManager(config.get('recovery_manager', {}))

    # Create the ProcessOrchestrator
    orchestrator = ProcessOrchestrator(
        config=config,
        task_scheduler=task_scheduler,
        event_manager=event_manager,
        recovery_manager=recovery_manager
    )

    # Start the orchestrator
    await orchestrator.start()
    logger.info("Process Orchestrator started")

    # Schedule some tasks
    task1_id = await task_scheduler.schedule_task(
        task_id="example_task_1",
        task_func=example_task,
        schedule_type='once',
        schedule_value=datetime.now() + timedelta(seconds=5),
        priority=3,
        params={
            'param1': 'value1',
            'param2': 'value2'
        }
    )
    logger.info(f"Scheduled task 1: {task1_id}")

    task2_id = await task_scheduler.schedule_task(
        task_id="example_task_2",
        task_func=example_task,
        schedule_type='interval',
        schedule_value=10,  # Every 10 seconds
        priority=5,
        params={
            'param1': 'interval_value1',
            'param2': 'interval_value2'
        }
    )
    logger.info(f"Scheduled task 2: {task2_id}")

    # Schedule a failing task to test recovery
    failing_task_id = await task_scheduler.schedule_task(
        task_id="failing_task",
        task_func=failing_task,
        schedule_type='once',
        schedule_value=datetime.now() + timedelta(seconds=15),
        priority=2,
        params={
            'should_fail': True
        }
    )
    logger.info(f"Scheduled failing task: {failing_task_id}")

    # Register custom event handlers
    await event_manager.subscribe(
        event_name='custom_event',
        handler=lambda event: logger.info(f"Received custom event: {event}"),
        subscriber_id='demo_app'
    )

    # Simulate events
    await asyncio.sleep(20)  # Wait for some tasks to run

    # Publish a custom event
    await event_manager.publish(
        event_name='custom_event',
        event_data={
            'message': 'This is a custom event',
            'timestamp': datetime.now().isoformat()
        },
        publisher_id='demo_app'
    )

    # Simulate a traffic spike
    traffic_spike_data = await simulate_traffic_spike()
    await event_manager.publish(
        event_name='traffic_spike',
        event_data=traffic_spike_data,
        publisher_id='analytics_system'
    )

    # Simulate a content performance drop
    performance_drop_data = await simulate_content_performance_drop()
    await event_manager.publish(
        event_name='content_performance_change',
        event_data=performance_drop_data,
        publisher_id='analytics_system'
    )

    # Schedule a website update
    update_process = await orchestrator.schedule_website_update(
        repository_name='marketing-website',
        schedule_type='once',
        schedule_value=datetime.now() + timedelta(seconds=10)
    )
    logger.info(f"Scheduled website update: {update_process['id']}")

    # Run for a while to see everything in action
    logger.info("Running for 60 seconds to demonstrate the framework...")
    await asyncio.sleep(60)

    # Get task results
    task1_result = task_scheduler.get_task_result("example_task_1")
    logger.info(f"Task 1 result: {task1_result}")

    failing_task_result = task_scheduler.get_task_result("failing_task")
    logger.info(f"Failing task result: {failing_task_result}")

    # Get event history
    events_history = event_manager.get_events_history()
    logger.info(f"Event history count: {len(events_history)}")

    # Stop the task scheduler
    await task_scheduler.stop()
    logger.info("Task Scheduler stopped")

    # Print summary
    logger.info("Background Execution Framework demonstration completed")
    logger.info(f"Total tasks scheduled: {len(task_scheduler.tasks)}")
    logger.info(f"Total events processed: {len(events_history)}")
    logger.info(f"Total processes: {len(orchestrator.processes)}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
