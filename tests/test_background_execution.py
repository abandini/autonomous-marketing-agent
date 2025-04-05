#!/usr/bin/env python3
"""
Test suite for the Background Execution Framework components.
Tests the integration between ProcessOrchestrator, TaskScheduler, EventManager, and RecoveryManager.
"""

import asyncio
import json
import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.background_execution.process_orchestrator import ProcessOrchestrator
from core.background_execution.task_scheduler import TaskScheduler
from core.background_execution.event_manager import EventManager
from core.background_execution.recovery_manager import RecoveryManager


class TestBackgroundExecution(unittest.TestCase):
    """Test suite for the Background Execution Framework."""

    def setUp(self):
        """Set up the test environment."""
        # Create mock configuration
        self.config = {
            'process_orchestrator': {
                'scheduler_interval': 10,
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
                'health_check_interval': 30,
                'max_recovery_attempts': 3
            },
            'git_integration': {
                'config_path': 'tests/test_data/git_config.json'
            },
            'content_repo_mapping': {
                'content_1': 'repo_1',
                'content_2': 'repo_2'
            }
        }
        
        # Create test directory if it doesn't exist
        os.makedirs('tests/test_data', exist_ok=True)
        
        # Create test git config
        with open('tests/test_data/git_config.json', 'w') as f:
            json.dump({
                'repositories': [
                    {
                        'name': 'repo_1',
                        'url': 'https://github.com/test/repo1.git',
                        'branch': 'main'
                    },
                    {
                        'name': 'repo_2',
                        'url': 'https://github.com/test/repo2.git',
                        'branch': 'main'
                    }
                ]
            }, f)
        
        # Create mock components
        self.task_scheduler = TaskScheduler(self.config.get('task_scheduler', {}))
        self.event_manager = EventManager(self.config.get('event_manager', {}))
        self.recovery_manager = RecoveryManager(self.config.get('recovery_manager', {}))
        
        # Patch the run method of TaskScheduler to prevent it from running in the background
        self.task_scheduler_run_patch = patch.object(
            TaskScheduler, 'run', 
            return_value=asyncio.Future()
        )
        self.task_scheduler_run_mock = self.task_scheduler_run_patch.start()
        
        # Patch the start_health_monitoring method of RecoveryManager
        self.recovery_manager_monitor_patch = patch.object(
            RecoveryManager, 'start_health_monitoring', 
            return_value=asyncio.Future()
        )
        self.recovery_manager_monitor_mock = self.recovery_manager_monitor_patch.start()
        
        # Create the ProcessOrchestrator with mocked components
        self.orchestrator = ProcessOrchestrator(
            config=self.config,
            task_scheduler=self.task_scheduler,
            event_manager=self.event_manager,
            recovery_manager=self.recovery_manager
        )
        
        # Mock Git integration and website updater
        self.orchestrator.git_integration = MagicMock()
        self.orchestrator.website_updater = MagicMock()
        self.orchestrator.website_updater.get_all_repository_configs.return_value = [
            {'name': 'repo_1'}, 
            {'name': 'repo_2'}
        ]
        self.orchestrator.website_updater.update_website = MagicMock(
            return_value=asyncio.Future()
        )
        self.orchestrator.website_updater.update_website.return_value.set_result({
            'status': 'success',
            'message': 'Website updated successfully'
        })
        
    def tearDown(self):
        """Clean up after the tests."""
        self.task_scheduler_run_patch.stop()
        self.recovery_manager_monitor_patch.stop()
        
        # Remove test git config
        if os.path.exists('tests/test_data/git_config.json'):
            os.remove('tests/test_data/git_config.json')
            
    async def async_test(self, coroutine):
        """Helper method to run async tests."""
        return await coroutine
        
    def test_process_orchestrator_initialization(self):
        """Test that the ProcessOrchestrator initializes correctly."""
        self.assertIsNotNone(self.orchestrator)
        self.assertEqual(self.orchestrator.task_scheduler, self.task_scheduler)
        self.assertEqual(self.orchestrator.event_manager, self.event_manager)
        self.assertEqual(self.orchestrator.recovery_manager, self.recovery_manager)
        
    def test_start_process_orchestrator(self):
        """Test starting the ProcessOrchestrator."""
        # Patch the initialize_all_processes and start_scheduler methods
        with patch.object(
            ProcessOrchestrator, 'initialize_all_processes', 
            return_value=asyncio.Future()
        ) as init_mock, patch.object(
            ProcessOrchestrator, 'start_scheduler', 
            return_value=asyncio.Future()
        ) as scheduler_mock, patch.object(
            EventManager, 'register_analytics_events',
            return_value=asyncio.Future()
        ) as events_mock:
            
            # Set the result for the futures
            init_mock.return_value.set_result(None)
            scheduler_mock.return_value.set_result(None)
            events_mock.return_value.set_result(None)
            
            # Run the test
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.orchestrator.start())
            
            # Check that the methods were called
            init_mock.assert_called_once()
            scheduler_mock.assert_called_once()
            events_mock.assert_called_once()
            self.task_scheduler_run_mock.assert_called_once()
            self.recovery_manager_monitor_mock.assert_called_once()
            
    def test_schedule_website_update(self):
        """Test scheduling a website update."""
        # Patch the publish method of EventManager
        with patch.object(
            EventManager, 'publish', 
            return_value=asyncio.Future()
        ) as publish_mock:
            publish_mock.return_value.set_result(None)
            
            # Run the test
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                self.orchestrator.schedule_website_update('repo_1', 'once', datetime.now())
            )
            
            # Check the result
            self.assertEqual(result['type'], 'website_update')
            self.assertEqual(result['params']['repository_name'], 'repo_1')
            self.assertEqual(result['status'], 'scheduled')
            
            # Check that the task was scheduled
            self.task_scheduler.schedule_task.assert_called_once()
            
            # Check that the event was published
            publish_mock.assert_called_once()
            
    def test_handle_content_performance_change(self):
        """Test handling a content performance change event."""
        # Create a test event
        event = {
            'name': 'content_performance_change',
            'data': {
                'content_id': 'content_1',
                'change': -25  # 25% decrease
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Patch the schedule_website_update method
        with patch.object(
            ProcessOrchestrator, 'schedule_website_update', 
            return_value=asyncio.Future()
        ) as schedule_mock:
            schedule_mock.return_value.set_result({
                'id': 'test_process',
                'status': 'scheduled'
            })
            
            # Run the test
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                self.orchestrator._handle_content_performance_change(event)
            )
            
            # Check the result
            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['action'], 'website_update_scheduled')
            
            # Check that schedule_website_update was called
            schedule_mock.assert_called_once_with('repo_1', 'immediate', None)
            
    def test_handle_traffic_spike(self):
        """Test handling a traffic spike event."""
        # Create a test event
        event = {
            'name': 'traffic_spike',
            'data': {
                'page_url': 'https://example.com/page1',
                'spike_percentage': 150
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Run the test
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.orchestrator._handle_traffic_spike(event)
        )
        
        # Check the result
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['action'], 'analysis_task_scheduled')
        
        # Check that the task was scheduled
        task_call = self.task_scheduler.schedule_task.call_args
        self.assertEqual(task_call[1]['schedule_type'], 'immediate')
        self.assertEqual(task_call[1]['priority'], 2)  # High priority
        
    def test_handle_system_error(self):
        """Test handling a system error event."""
        # Create a test event
        event = {
            'name': 'system_error',
            'data': {
                'error_type': 'ConnectionError',
                'error_details': {
                    'message': 'Failed to connect to API',
                    'service': 'analytics'
                },
                'component': 'metrics_collector'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Patch the report_error method of RecoveryManager
        with patch.object(
            RecoveryManager, 'report_error', 
            return_value=asyncio.Future()
        ) as report_mock:
            report_mock.return_value.set_result({
                'status': 'success',
                'recovery_action': 'restart_component'
            })
            
            # Run the test
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                self.orchestrator._handle_system_error(event)
            )
            
            # Check the result
            self.assertEqual(result['status'], 'success')
            
            # Check that report_error was called with the correct arguments
            report_mock.assert_called_once_with(
                error_type='ConnectionError',
                error_details={
                    'message': 'Failed to connect to API',
                    'service': 'analytics'
                },
                component='metrics_collector'
            )
            
    def test_analyze_traffic_spike(self):
        """Test analyzing a traffic spike."""
        # Patch the publish method of EventManager
        with patch.object(
            EventManager, 'publish', 
            return_value=asyncio.Future()
        ) as publish_mock:
            publish_mock.return_value.set_result(None)
            
            # Run the test
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                self.orchestrator._analyze_traffic_spike(
                    'https://example.com/page1', 150
                )
            )
            
            # Check the result
            self.assertEqual(result['page_url'], 'https://example.com/page1')
            self.assertEqual(result['spike_percentage'], 150)
            self.assertEqual(result['analysis']['source'], 'organic')
            self.assertEqual(result['analysis']['significance'], 'high')
            
            # Check that the event was published
            publish_mock.assert_called_once()
            
    def test_health_checks(self):
        """Test the health check methods."""
        # Test Git integration health check
        self.orchestrator.git_integration.list_repositories.return_value = ['repo_1', 'repo_2']
        
        # Run the tests
        loop = asyncio.get_event_loop()
        git_health = loop.run_until_complete(self.orchestrator._check_git_integration_health())
        task_health = loop.run_until_complete(self.orchestrator._check_task_scheduler_health())
        event_health = loop.run_until_complete(self.orchestrator._check_event_manager_health())
        
        # Check Git integration health
        self.assertEqual(git_health['status'], 'healthy')
        self.assertTrue(git_health['critical'])
        
        # Check Task Scheduler health (should be degraded since it's not running)
        self.assertEqual(task_health['status'], 'degraded')
        self.assertTrue(task_health['critical'])
        
        # Check Event Manager health
        self.assertEqual(event_health['status'], 'healthy')
        self.assertFalse(event_health['critical'])
            

if __name__ == '__main__':
    unittest.main()
