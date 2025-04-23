"""
Continuous Improvement Cycle module for the Autonomous Marketing Agent.

This module implements the six-phase improvement cycle for marketing optimization.
"""

import logging
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional

from core.orchestrator.utils.config_validator import ConfigValidator
from core.orchestrator.utils.metrics import MetricsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CyclePhase(Enum):
    """Enum representing phases in a continuous improvement cycle."""
    WEBSITE_OPTIMIZATION = "website_optimization"
    MULTI_CHANNEL_MARKETING = "multi_channel_marketing"
    DATA_LEARNING = "data_learning"
    CONTENT_REFINEMENT = "content_refinement"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    SYSTEM_EXPANSION = "system_expansion"

class FeedbackLoopType(Enum):
    """Enum representing types of feedback loops in a continuous improvement cycle."""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

class ContinuousImprovementCycle:
    """Manages the continuous improvement cycle for marketing campaigns.
    
    This class implements the six-phase cycle for affiliate marketing:
    1. Website Optimization
    2. Multi-Channel Marketing
    3. Data Learning & Analysis
    4. Content & Offering Refinement
    5. Revenue Optimization
    6. System Expansion
    
    Each phase has specific tasks, metrics, and feedback loops to ensure
    continuous improvement and revenue growth.
    """
    
    def __init__(self, config_path: str = None, metrics_service: MetricsService = None):
        """
        Initialize the continuous improvement cycle.
        
        Args:
            config_path: Path to the cycle configuration file
            metrics_service: Optional metrics service instance
        """
        self.phases = {}
        self.current_phase = None
        self.start_time = None
        self.last_phase_change = None
        self.metrics = {}
        self.feedback_loops = {}
        self.acceleration_strategies = {}
        self.metrics_service = metrics_service or MetricsService()
        
        if config_path:
            self.load_config(config_path)
        
    def load_config(self, config_path: str) -> bool:
        """
        Load cycle configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            True if configuration was loaded successfully, False otherwise
        """
        try:
            # Use the config validator to load and validate the configuration
            config = None
            if config_path.endswith('.json'):
                config = ConfigValidator.load_and_validate_json(config_path, "cycle")
            elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config = ConfigValidator.load_and_validate_yaml(config_path, "cycle")
            else:
                # Default to JSON if file extension is not recognized
                config = ConfigValidator.load_and_validate_json(config_path, "cycle")
                
            if not config:
                logger.error(f"Failed to load valid cycle configuration from {config_path}")
                return False
                
            # Load phases
            for phase_name, phase_config in config.get("phases", {}).items():
                self.phases[phase_name] = phase_config
            
            # Load feedback loops
            for loop_name, loop_config in config.get("feedback_loops", {}).items():
                self.feedback_loops[loop_name] = loop_config
            
            # Load acceleration strategies
            for strategy_name, strategy_config in config.get("acceleration_strategies", {}).items():
                self.acceleration_strategies[strategy_name] = strategy_config
            
            logger.info(f"Loaded continuous improvement cycle config from {config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load cycle configuration: {str(e)}")
            return False
    
    def start_cycle(self, initial_phase: str = None) -> Dict[str, Any]:
        """
        Start the continuous improvement cycle.
        
        Args:
            initial_phase: Optional initial phase to start with
            
        Returns:
            Dict containing cycle status
        """
        self.start_time = datetime.now()
        self.last_phase_change = self.start_time
        
        # Set initial phase
        if initial_phase and initial_phase in self.phases:
            self.current_phase = initial_phase
        else:
            # Default to first phase
            self.current_phase = next(iter(self.phases)) if self.phases else None
        
        logger.info(f"Started continuous improvement cycle with phase: {self.current_phase}")
        
        # Record metrics
        self._record_cycle_start_metrics()
        
        return self.get_cycle_status()
    
    def _record_cycle_start_metrics(self) -> None:
        """Record metrics when the cycle starts."""
        self.metrics_service.record("cycle", "start_time", self.start_time.isoformat())
        self.metrics_service.record("cycle", "initial_phase", self.current_phase)
    
    def advance_phase(self) -> Dict[str, Any]:
        """
        Advance to the next phase in the cycle.
        
        Returns:
            Dict containing updated cycle status
        """
        if not self.current_phase:
            logger.error("Cannot advance phase: no current phase set")
            return {"status": "error", "message": "No current phase set"}
        
        # Get ordered list of phases
        phase_names = list(self.phases.keys())
        if not phase_names:
            logger.error("Cannot advance phase: no phases defined")
            return {"status": "error", "message": "No phases defined"}
        
        # Find current phase index
        try:
            current_index = phase_names.index(self.current_phase)
        except ValueError:
            logger.error(f"Current phase {self.current_phase} not found in phases")
            return {"status": "error", "message": f"Current phase {self.current_phase} not found"}
        
        # Calculate next phase index (wrap around to beginning if at end)
        next_index = (current_index + 1) % len(phase_names)
        next_phase = phase_names[next_index]
        
        # Update phase
        previous_phase = self.current_phase
        self.current_phase = next_phase
        self.last_phase_change = datetime.now()
        
        logger.info(f"Advanced from phase {previous_phase} to {next_phase}")
        
        # Record metrics
        self._record_phase_change_metrics(previous_phase, next_phase)
        
        return self.get_cycle_status()
    
    def _record_phase_change_metrics(self, previous_phase: str, next_phase: str) -> None:
        """
        Record metrics when the phase changes.
        
        Args:
            previous_phase: Previous phase name
            next_phase: Next phase name
        """
        self.metrics_service.record("cycle", "phase_change", {
            "from": previous_phase,
            "to": next_phase,
            "timestamp": self.last_phase_change.isoformat()
        })
        
        # Record phase duration
        if self.start_time:
            phase_duration = (self.last_phase_change - self.start_time).total_seconds()
            self.metrics_service.record("cycle", f"phase_duration.{previous_phase}", phase_duration)
    
    def get_current_phase_tasks(self) -> List[Dict[str, Any]]:
        """
        Get the tasks for the current phase.
        
        Returns:
            List of task configurations
        """
        if not self.current_phase or self.current_phase not in self.phases:
            logger.warning(f"Cannot get tasks: current phase {self.current_phase} not found")
            return []
        
        return self.phases[self.current_phase].get("tasks", [])
    
    def get_phase_metrics(self, phase_name: str = None) -> Dict[str, Any]:
        """
        Get the metrics for a specific phase or the current phase.
        
        Args:
            phase_name: Optional name of the phase to get metrics for
            
        Returns:
            Dict containing phase metrics
        """
        target_phase = phase_name or self.current_phase
        if not target_phase or target_phase not in self.phases:
            logger.warning(f"Cannot get metrics: phase {target_phase} not found")
            return {}
        
        return self.phases[target_phase].get("metrics", {})
    
    def update_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update cycle metrics with new values.
        
        Args:
            metrics: Dict of metrics to update
            
        Returns:
            Dict containing updated metrics
        """
        # Update global metrics
        for key, value in metrics.items():
            self.metrics[key] = value
            
            # Record in metrics service
            self.metrics_service.record("cycle", key, value)
        
        # Update phase-specific metrics if applicable
        if self.current_phase and self.current_phase in self.phases:
            phase_metrics = self.phases[self.current_phase].get("metrics", {})
            for key, value in metrics.items():
                if key in phase_metrics:
                    phase_metrics[key] = value
                    
                    # Record in metrics service with phase prefix
                    self.metrics_service.record("cycle", f"phase.{self.current_phase}.{key}", value)
        
        logger.info(f"Updated cycle metrics: {metrics}")
        return self.metrics
    
    def trigger_feedback_loop(self, loop_type: str) -> Dict[str, Any]:
        """
        Trigger a feedback loop of the specified type.
        
        Args:
            loop_type: Type of feedback loop to trigger (short, medium, long)
            
        Returns:
            Dict containing feedback loop configuration
        """
        if loop_type not in [t.value for t in FeedbackLoopType]:
            logger.error(f"Invalid feedback loop type: {loop_type}")
            return {"status": "error", "message": f"Invalid feedback loop type: {loop_type}"}
        
        if loop_type not in self.feedback_loops:
            logger.error(f"Feedback loop type {loop_type} not configured")
            return {"status": "error", "message": f"Feedback loop type {loop_type} not configured"}
        
        loop_config = self.feedback_loops[loop_type]
        
        logger.info(f"Triggered {loop_type} feedback loop")
        
        # Record metrics
        self.metrics_service.record("cycle", "feedback_loop_trigger", {
            "type": loop_type,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "status": "success",
            "loop_type": loop_type,
            "config": loop_config
        }
    
    def apply_acceleration_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """
        Apply an acceleration strategy to the cycle.
        
        Args:
            strategy_name: Name of the acceleration strategy to apply
            
        Returns:
            Dict containing strategy application results
        """
        if strategy_name not in self.acceleration_strategies:
            logger.error(f"Acceleration strategy {strategy_name} not found")
            return {"status": "error", "message": f"Strategy {strategy_name} not found"}
        
        strategy = self.acceleration_strategies[strategy_name]
        
        # Apply strategy adjustments
        adjustments = strategy.get("adjustments", {})
        
        # Apply phase-specific adjustments
        for phase_name, phase_adjustments in adjustments.get("phases", {}).items():
            if phase_name in self.phases:
                for key, value in phase_adjustments.items():
                    self.phases[phase_name][key] = value
        
        logger.info(f"Applied acceleration strategy: {strategy_name}")
        
        # Record metrics
        self.metrics_service.record("cycle", "acceleration_strategy", {
            "name": strategy_name,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "status": "success",
            "strategy": strategy_name,
            "adjustments": adjustments
        }
    
    def get_cycle_status(self) -> Dict[str, Any]:
        """
        Get the current status of the improvement cycle.
        
        Returns:
            Dict containing cycle status information
        """
        now = datetime.now()
        
        # Calculate cycle duration
        cycle_duration = None
        if self.start_time:
            cycle_duration = (now - self.start_time).total_seconds()
        
        # Calculate time in current phase
        time_in_phase = None
        if self.last_phase_change:
            time_in_phase = (now - self.last_phase_change).total_seconds()
        
        # Get current phase configuration
        current_phase_config = {}
        if self.current_phase and self.current_phase in self.phases:
            current_phase_config = self.phases[self.current_phase]
        
        return {
            "status": "running" if self.current_phase else "not_started",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "current_phase": self.current_phase,
            "last_phase_change": self.last_phase_change.isoformat() if self.last_phase_change else None,
            "cycle_duration_seconds": cycle_duration,
            "time_in_phase_seconds": time_in_phase,
            "phases": list(self.phases.keys()),
            "current_phase_config": current_phase_config,
            "metrics": self.metrics
        }
