"""
Background Execution Framework for the Autonomous Marketing Agent.

This module provides the infrastructure for running marketing activities
in the background without disruption, with self-healing capabilities
and event-driven architecture.
"""

from core.background_execution.process_orchestrator import ProcessOrchestrator
from core.background_execution.task_scheduler import TaskScheduler
from core.background_execution.event_manager import EventManager
from core.background_execution.recovery_manager import RecoveryManager
from core.background_execution.background_learner import BackgroundLearner

__all__ = [
    'ProcessOrchestrator',
    'TaskScheduler',
    'EventManager',
    'RecoveryManager',
    'BackgroundLearner'
]
