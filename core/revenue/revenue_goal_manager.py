"""
Revenue Goal Management Module for the Autonomous Marketing Agent.

This module implements the Revenue Goal Management component of the Revenue Optimization Framework,
allowing the system to set, track, and optimize toward specific monetary targets.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoalPeriod(Enum):
    """Enumeration of possible goal time periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"

class GoalStatus(Enum):
    """Enumeration of possible goal statuses."""
    PENDING = "pending"
    ACTIVE = "active"
    ACHIEVED = "achieved"
    AT_RISK = "at_risk"
    MISSED = "missed"
    ADJUSTED = "adjusted"

class RevenueGoal:
    """
    Represents a specific revenue goal with targets, timeframes, and tracking metrics.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        target_value: float,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        period: GoalPeriod = GoalPeriod.MONTHLY,
        channel: Optional[str] = None,
        source: Optional[str] = None,
        current_value: float = 0.0,
        milestones: Optional[List[Dict[str, Any]]] = None,
        parent_goal_id: Optional[str] = None
    ):
        """
        Initialize a revenue goal.
        
        Args:
            name: Name of the goal
            description: Detailed description
            target_value: Target monetary value
            start_date: Start date for the goal period
            end_date: End date for the goal period
            period: Time period for the goal (daily, weekly, monthly, etc.)
            channel: Optional marketing channel this goal is tied to
            source: Optional revenue source this goal is tied to
            current_value: Current progress toward the target
            milestones: List of milestone targets with dates
            parent_goal_id: ID of a parent goal if this is a sub-goal
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.target_value = float(target_value)
        self.current_value = float(current_value)
        self.period = period if isinstance(period, GoalPeriod) else GoalPeriod(period)
        self.channel = channel
        self.source = source
        self.parent_goal_id = parent_goal_id
        self.status = GoalStatus.PENDING
        self.creation_date = datetime.now()
        self.last_updated = datetime.now()
        self.history = []
        
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            self.start_date = datetime.fromisoformat(start_date)
        else:
            self.start_date = start_date
            
        if isinstance(end_date, str):
            self.end_date = datetime.fromisoformat(end_date)
        else:
            self.end_date = end_date
        
        # Initialize milestones
        self.milestones = milestones or []
        
        # Initialize metrics tracking
        self.metrics = {
            "progress_percentage": 0.0,
            "time_elapsed_percentage": 0.0,
            "velocity": 0.0,
            "projected_completion": None,
            "variance_from_target": 0.0
        }
        
        self.update_metrics()
        logger.info(f"Created revenue goal: {self.name} with target ${self.target_value}")
    
    def update_value(self, new_value: float) -> None:
        """
        Update the current value of the goal.
        
        Args:
            new_value: New current value
        """
        # Record history before updating
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "previous_value": self.current_value,
            "new_value": new_value,
            "change": new_value - self.current_value
        })
        
        self.current_value = float(new_value)
        self.last_updated = datetime.now()
        self.update_metrics()
        self.update_status()
        
        logger.info(f"Updated goal '{self.name}' value to ${self.current_value}")
    
    def increment_value(self, amount: float) -> None:
        """
        Increment the current value by the specified amount.
        
        Args:
            amount: Amount to add to the current value
        """
        self.update_value(self.current_value + float(amount))
    
    def update_metrics(self) -> None:
        """Update all calculated metrics for this goal."""
        # Calculate progress percentage
        if self.target_value > 0:
            self.metrics["progress_percentage"] = (self.current_value / self.target_value) * 100
        else:
            self.metrics["progress_percentage"] = 0
            
        # Calculate time elapsed percentage
        total_duration = (self.end_date - self.start_date).total_seconds()
        if total_duration > 0:
            elapsed = (datetime.now() - self.start_date).total_seconds()
            self.metrics["time_elapsed_percentage"] = min(100, (elapsed / total_duration) * 100)
        else:
            self.metrics["time_elapsed_percentage"] = 100
            
        # Calculate velocity (average daily progress)
        days_elapsed = max(1, (datetime.now() - self.start_date).days)
        self.metrics["velocity"] = self.current_value / days_elapsed
        
        # Project completion based on current velocity
        if self.metrics["velocity"] > 0:
            remaining_value = self.target_value - self.current_value
            days_needed = remaining_value / self.metrics["velocity"]
            self.metrics["projected_completion"] = (datetime.now() + timedelta(days=days_needed)).isoformat()
        else:
            self.metrics["projected_completion"] = None
            
        # Calculate variance from target (expected progress vs actual progress)
        expected_progress = self.target_value * (self.metrics["time_elapsed_percentage"] / 100)
        self.metrics["variance_from_target"] = self.current_value - expected_progress
    
    def update_status(self) -> None:
        """Update the status of the goal based on current metrics."""
        now = datetime.now()
        
        # Check if goal period has started
        if now < self.start_date:
            self.status = GoalStatus.PENDING
            return
            
        # Check if goal has been achieved
        if self.current_value >= self.target_value:
            self.status = GoalStatus.ACHIEVED
            return
            
        # Check if goal period has ended
        if now > self.end_date:
            self.status = GoalStatus.MISSED
            return
            
        # Check if goal is at risk
        if self.metrics["time_elapsed_percentage"] > 50 and self.metrics["progress_percentage"] < 40:
            self.status = GoalStatus.AT_RISK
            return
            
        # Default to active
        self.status = GoalStatus.ACTIVE
    
    def adjust_target(self, new_target: float, reason: str) -> None:
        """
        Adjust the target value of the goal.
        
        Args:
            new_target: New target value
            reason: Reason for the adjustment
        """
        # Record adjustment in history
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "target_adjustment",
            "previous_target": self.target_value,
            "new_target": new_target,
            "reason": reason
        })
        
        self.target_value = float(new_target)
        self.status = GoalStatus.ADJUSTED
        self.last_updated = datetime.now()
        self.update_metrics()
        self.update_status()
        
        logger.info(f"Adjusted goal '{self.name}' target to ${self.target_value}: {reason}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the goal to a dictionary for serialization.
        
        Returns:
            Dict containing all goal data
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "period": self.period.value,
            "channel": self.channel,
            "source": self.source,
            "parent_goal_id": self.parent_goal_id,
            "status": self.status.value,
            "creation_date": self.creation_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "metrics": self.metrics,
            "milestones": self.milestones,
            "history": self.history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RevenueGoal':
        """
        Create a RevenueGoal instance from a dictionary.
        
        Args:
            data: Dictionary containing goal data
            
        Returns:
            RevenueGoal instance
        """
        goal = cls(
            name=data["name"],
            description=data["description"],
            target_value=data["target_value"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            period=data["period"],
            channel=data.get("channel"),
            source=data.get("source"),
            current_value=data["current_value"],
            milestones=data.get("milestones", []),
            parent_goal_id=data.get("parent_goal_id")
        )
        
        # Restore additional properties
        goal.id = data["id"]
        goal.status = GoalStatus(data["status"])
        goal.creation_date = datetime.fromisoformat(data["creation_date"])
        goal.last_updated = datetime.fromisoformat(data["last_updated"])
        goal.metrics = data["metrics"]
        goal.history = data["history"]
        
        return goal


class RevenueGoalManager:
    """
    Manages revenue goals for the autonomous marketing agent.
    
    This class handles the creation, tracking, and optimization of revenue goals,
    including hierarchical goal structures and dynamic adjustments based on performance.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the Revenue Goal Manager.
        
        Args:
            storage_path: Optional path to store goal data
        """
        self.goals = {}  # Dictionary of goals by ID
        self.storage_path = storage_path
        logger.info("Revenue Goal Manager initialized")
    
    def create_goal(self, goal_data: Dict[str, Any]) -> str:
        """
        Create a new revenue goal.
        
        Args:
            goal_data: Dictionary containing goal parameters
            
        Returns:
            ID of the created goal
        """
        goal = RevenueGoal(**goal_data)
        self.goals[goal.id] = goal
        
        # If this is a sub-goal, update the parent goal
        if goal.parent_goal_id and goal.parent_goal_id in self.goals:
            parent = self.goals[goal.parent_goal_id]
            if not hasattr(parent, 'sub_goals'):
                parent.sub_goals = []
            parent.sub_goals.append(goal.id)
        
        self._save_goals()
        logger.info(f"Created new revenue goal: {goal.name} (ID: {goal.id})")
        return goal.id
    
    def get_goal(self, goal_id: str) -> Optional[RevenueGoal]:
        """
        Get a goal by ID.
        
        Args:
            goal_id: ID of the goal to retrieve
            
        Returns:
            RevenueGoal instance or None if not found
        """
        return self.goals.get(goal_id)
    
    def update_goal_value(self, goal_id: str, value: float) -> bool:
        """
        Update the current value of a goal.
        
        Args:
            goal_id: ID of the goal to update
            value: New current value
            
        Returns:
            True if successful, False otherwise
        """
        goal = self.get_goal(goal_id)
        if not goal:
            logger.error(f"Goal not found: {goal_id}")
            return False
            
        goal.update_value(value)
        self._propagate_updates(goal_id)
        self._save_goals()
        return True
    
    def increment_goal_value(self, goal_id: str, amount: float) -> bool:
        """
        Increment the current value of a goal.
        
        Args:
            goal_id: ID of the goal to update
            amount: Amount to add to the current value
            
        Returns:
            True if successful, False otherwise
        """
        goal = self.get_goal(goal_id)
        if not goal:
            logger.error(f"Goal not found: {goal_id}")
            return False
            
        goal.increment_value(amount)
        self._propagate_updates(goal_id)
        self._save_goals()
        return True
    
    def adjust_goal_target(self, goal_id: str, new_target: float, reason: str) -> bool:
        """
        Adjust the target value of a goal.
        
        Args:
            goal_id: ID of the goal to adjust
            new_target: New target value
            reason: Reason for the adjustment
            
        Returns:
            True if successful, False otherwise
        """
        goal = self.get_goal(goal_id)
        if not goal:
            logger.error(f"Goal not found: {goal_id}")
            return False
            
        goal.adjust_target(new_target, reason)
        self._save_goals()
        return True
    
    def delete_goal(self, goal_id: str) -> bool:
        """
        Delete a goal.
        
        Args:
            goal_id: ID of the goal to delete
            
        Returns:
            True if successful, False otherwise
        """
        if goal_id not in self.goals:
            logger.error(f"Goal not found: {goal_id}")
            return False
            
        # Remove from parent if it's a sub-goal
        goal = self.goals[goal_id]
        if goal.parent_goal_id and goal.parent_goal_id in self.goals:
            parent = self.goals[goal.parent_goal_id]
            if hasattr(parent, 'sub_goals') and goal_id in parent.sub_goals:
                parent.sub_goals.remove(goal_id)
        
        # Delete the goal
        del self.goals[goal_id]
        self._save_goals()
        logger.info(f"Deleted goal: {goal_id}")
        return True
    
    def get_all_goals(self) -> Dict[str, RevenueGoal]:
        """
        Get all goals.
        
        Returns:
            Dictionary of all goals by ID
        """
        return self.goals
    
    def get_top_level_goals(self) -> Dict[str, RevenueGoal]:
        """
        Get all top-level goals (goals without a parent).
        
        Returns:
            Dictionary of top-level goals by ID
        """
        return {
            goal_id: goal for goal_id, goal in self.goals.items()
            if not goal.parent_goal_id
        }
    
    def get_goals_by_status(self, status: GoalStatus) -> Dict[str, RevenueGoal]:
        """
        Get goals by status.
        
        Args:
            status: Status to filter by
            
        Returns:
            Dictionary of matching goals by ID
        """
        return {
            goal_id: goal for goal_id, goal in self.goals.items()
            if goal.status == status
        }
    
    def get_goals_by_channel(self, channel: str) -> Dict[str, RevenueGoal]:
        """
        Get goals by marketing channel.
        
        Args:
            channel: Channel to filter by
            
        Returns:
            Dictionary of matching goals by ID
        """
        return {
            goal_id: goal for goal_id, goal in self.goals.items()
            if goal.channel == channel
        }
    
    def get_goals_by_source(self, source: str) -> Dict[str, RevenueGoal]:
        """
        Get goals by revenue source.
        
        Args:
            source: Source to filter by
            
        Returns:
            Dictionary of matching goals by ID
        """
        return {
            goal_id: goal for goal_id, goal in self.goals.items()
            if goal.source == source
        }
    
    def get_at_risk_goals(self) -> Dict[str, RevenueGoal]:
        """
        Get all goals that are at risk of not being achieved.
        
        Returns:
            Dictionary of at-risk goals by ID
        """
        return self.get_goals_by_status(GoalStatus.AT_RISK)
    
    def get_goal_hierarchy(self, goal_id: str) -> Dict[str, Any]:
        """
        Get a goal and all its sub-goals as a hierarchical structure.
        
        Args:
            goal_id: ID of the parent goal
            
        Returns:
            Dictionary containing the goal hierarchy
        """
        goal = self.get_goal(goal_id)
        if not goal:
            logger.error(f"Goal not found: {goal_id}")
            return {}
            
        result = goal.to_dict()
        result["sub_goals"] = []
        
        # Add sub-goals if any
        if hasattr(goal, 'sub_goals'):
            for sub_goal_id in goal.sub_goals:
                sub_goal_hierarchy = self.get_goal_hierarchy(sub_goal_id)
                if sub_goal_hierarchy:
                    result["sub_goals"].append(sub_goal_hierarchy)
        
        return result
    
    def update_all_goals(self) -> None:
        """Update metrics and status for all goals."""
        for goal in self.goals.values():
            goal.update_metrics()
            goal.update_status()
        
        self._save_goals()
        logger.info("Updated all goal metrics and statuses")
    
    def generate_revenue_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive revenue report.
        
        Returns:
            Dictionary containing the revenue report
        """
        now = datetime.now()
        
        report = {
            "timestamp": now.isoformat(),
            "total_goals": len(self.goals),
            "status_summary": {
                status.value: len(self.get_goals_by_status(status))
                for status in GoalStatus
            },
            "total_current_revenue": sum(goal.current_value for goal in self.goals.values()),
            "total_target_revenue": sum(goal.target_value for goal in self.goals.values()),
            "overall_progress_percentage": 0,
            "top_performing_channels": [],
            "at_risk_goals": [goal.to_dict() for goal in self.get_at_risk_goals().values()],
            "recently_achieved_goals": [
                goal.to_dict() for goal in self.goals.values()
                if goal.status == GoalStatus.ACHIEVED and 
                (now - goal.last_updated).days <= 7
            ],
            "channel_breakdown": {},
            "source_breakdown": {},
            "period_breakdown": {}
        }
        
        # Calculate overall progress percentage
        if report["total_target_revenue"] > 0:
            report["overall_progress_percentage"] = (
                report["total_current_revenue"] / report["total_target_revenue"]
            ) * 100
        
        # Generate channel breakdown
        channels = set(goal.channel for goal in self.goals.values() if goal.channel)
        for channel in channels:
            channel_goals = self.get_goals_by_channel(channel)
            current_revenue = sum(goal.current_value for goal in channel_goals.values())
            target_revenue = sum(goal.target_value for goal in channel_goals.values())
            
            report["channel_breakdown"][channel] = {
                "goal_count": len(channel_goals),
                "current_revenue": current_revenue,
                "target_revenue": target_revenue,
                "progress_percentage": (current_revenue / target_revenue * 100) if target_revenue > 0 else 0
            }
        
        # Generate source breakdown
        sources = set(goal.source for goal in self.goals.values() if goal.source)
        for source in sources:
            source_goals = self.get_goals_by_source(source)
            current_revenue = sum(goal.current_value for goal in source_goals.values())
            target_revenue = sum(goal.target_value for goal in source_goals.values())
            
            report["source_breakdown"][source] = {
                "goal_count": len(source_goals),
                "current_revenue": current_revenue,
                "target_revenue": target_revenue,
                "progress_percentage": (current_revenue / target_revenue * 100) if target_revenue > 0 else 0
            }
        
        # Generate period breakdown
        periods = set(goal.period for goal in self.goals.values())
        for period in periods:
            period_goals = {
                goal_id: goal for goal_id, goal in self.goals.items()
                if goal.period == period
            }
            current_revenue = sum(goal.current_value for goal in period_goals.values())
            target_revenue = sum(goal.target_value for goal in period_goals.values())
            
            report["period_breakdown"][period.value] = {
                "goal_count": len(period_goals),
                "current_revenue": current_revenue,
                "target_revenue": target_revenue,
                "progress_percentage": (current_revenue / target_revenue * 100) if target_revenue > 0 else 0
            }
        
        # Identify top performing channels
        if report["channel_breakdown"]:
            top_channels = sorted(
                report["channel_breakdown"].items(),
                key=lambda x: x[1]["progress_percentage"],
                reverse=True
            )
            report["top_performing_channels"] = [
                {
                    "channel": channel,
                    "progress_percentage": data["progress_percentage"],
                    "current_revenue": data["current_revenue"]
                }
                for channel, data in top_channels[:3]
            ]
        
        logger.info("Generated revenue report")
        return report
    
    def _propagate_updates(self, goal_id: str) -> None:
        """
        Propagate updates from a sub-goal to its parent goals.
        
        Args:
            goal_id: ID of the goal that was updated
        """
        goal = self.get_goal(goal_id)
        if not goal or not goal.parent_goal_id:
            return
            
        parent_id = goal.parent_goal_id
        parent = self.get_goal(parent_id)
        if not parent:
            return
            
        # Calculate sum of all sub-goals
        sub_goal_sum = 0
        if hasattr(parent, 'sub_goals'):
            for sub_id in parent.sub_goals:
                sub_goal = self.get_goal(sub_id)
                if sub_goal:
                    sub_goal_sum += sub_goal.current_value
        
        # Update parent value
        parent.update_value(sub_goal_sum)
        
        # Recursively update parent's parent
        self._propagate_updates(parent_id)
    
    def _save_goals(self) -> None:
        """Save goals to storage if a storage path is configured."""
        if not self.storage_path:
            return
            
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(
                    {goal_id: goal.to_dict() for goal_id, goal in self.goals.items()},
                    f,
                    indent=2
                )
            logger.info(f"Saved goals to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving goals: {e}")
    
    def load_goals(self) -> bool:
        """
        Load goals from storage.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.storage_path:
            logger.warning("No storage path configured, cannot load goals")
            return False
            
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            self.goals = {
                goal_id: RevenueGoal.from_dict(goal_data)
                for goal_id, goal_data in data.items()
            }
            
            logger.info(f"Loaded {len(self.goals)} goals from {self.storage_path}")
            return True
        except FileNotFoundError:
            logger.warning(f"Goals file not found: {self.storage_path}")
            return False
        except Exception as e:
            logger.error(f"Error loading goals: {e}")
            return False
