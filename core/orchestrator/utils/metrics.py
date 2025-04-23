"""
Metrics service for the orchestrator module.

This module provides centralized metrics collection and storage for the GAMS system.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricsService:
    """Service for collecting and storing metrics across the GAMS system."""
    
    def __init__(self):
        """Initialize the metrics service."""
        self.metrics = {}
        self.start_time = datetime.now()
        logger.info("Metrics service initialized")
        
    def record(self, category: str, name: str, value: Any) -> None:
        """
        Record a metric value.
        
        Args:
            category: Category of the metric (e.g., 'workflow', 'campaign', 'goal')
            name: Name of the metric
            value: Value of the metric
        """
        if category not in self.metrics:
            self.metrics[category] = {}
        
        if name not in self.metrics[category]:
            self.metrics[category][name] = []
            
        self.metrics[category][name].append({
            "timestamp": datetime.now().isoformat(),
            "value": value
        })
        
        logger.debug(f"Recorded metric: {category}.{name} = {value}")
        
    def get_metrics(self, category: str = None, name: str = None) -> Dict[str, Any]:
        """
        Get metrics by category and name.
        
        Args:
            category: Optional category to filter by
            name: Optional name to filter by
            
        Returns:
            Dict containing the requested metrics
        """
        if category and name:
            return self.metrics.get(category, {}).get(name, [])
        elif category:
            return self.metrics.get(category, {})
        else:
            return self.metrics
            
    def get_latest(self, category: str, name: str) -> Optional[Any]:
        """
        Get the latest value for a specific metric.
        
        Args:
            category: Category of the metric
            name: Name of the metric
            
        Returns:
            The latest value of the metric, or None if not found
        """
        metrics = self.get_metrics(category, name)
        if not metrics:
            return None
            
        return metrics[-1]["value"] if metrics else None
        
    def get_average(self, category: str, name: str, window: int = None) -> Optional[float]:
        """
        Get the average value for a numeric metric over a window of recent entries.
        
        Args:
            category: Category of the metric
            name: Name of the metric
            window: Optional number of recent entries to average
            
        Returns:
            The average value, or None if not found or not numeric
        """
        metrics = self.get_metrics(category, name)
        if not metrics:
            return None
            
        values = [m["value"] for m in metrics if isinstance(m["value"], (int, float))]
        if not values:
            return None
            
        if window and window < len(values):
            values = values[-window:]
            
        return sum(values) / len(values)
        
    def clear(self, category: str = None, name: str = None) -> None:
        """
        Clear metrics.
        
        Args:
            category: Optional category to clear
            name: Optional name to clear
        """
        if category and name:
            if category in self.metrics and name in self.metrics[category]:
                self.metrics[category][name] = []
        elif category:
            if category in self.metrics:
                self.metrics[category] = {}
        else:
            self.metrics = {}
            
        logger.info(f"Cleared metrics: {category or 'all'}.{name or 'all'}")
        
    def export(self, format_type: str = "json") -> Union[str, Dict]:
        """
        Export metrics in the specified format.
        
        Args:
            format_type: Format type ('json' or 'dict')
            
        Returns:
            Metrics in the requested format
        """
        if format_type == "json":
            import json
            return json.dumps(self.metrics)
        else:
            return self.metrics
