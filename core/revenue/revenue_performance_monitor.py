"""
Revenue Performance Monitor module for the Autonomous Marketing Agent.

This module provides capabilities for monitoring revenue performance metrics,
detecting anomalies, and generating alerts.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import asyncio
import uuid
import numpy as np
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    """Enumeration of alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertType(str, Enum):
    """Enumeration of alert types."""
    GOAL_AT_RISK = "goal_at_risk"
    REVENUE_DECLINE = "revenue_decline"
    CONVERSION_DECLINE = "conversion_decline"
    CHANNEL_UNDERPERFORMING = "channel_underperforming"
    FORECAST_DEVIATION = "forecast_deviation"
    ANOMALY_DETECTED = "anomaly_detected"
    OPPORTUNITY_IDENTIFIED = "opportunity_identified"

class MetricType(str, Enum):
    """Enumeration of metric types."""
    REVENUE = "revenue"
    CONVERSION = "conversion"
    AOV = "average_order_value"
    CAC = "customer_acquisition_cost"
    LTV = "lifetime_value"
    ROI = "roi"
    MARGIN = "margin"

class RevenuePerformanceMonitor:
    """
    Monitor for revenue performance metrics.
    
    This class provides functionality for:
    1. Tracking revenue metrics over time
    2. Detecting anomalies and trends in revenue data
    3. Generating alerts for significant changes
    4. Monitoring goal progress and forecasts
    """
    
    def __init__(self, storage_dir: str = "data/revenue"):
        """
        Initialize the Revenue Performance Monitor.
        
        Args:
            storage_dir: Directory for storing performance data
        """
        self.storage_dir = storage_dir
        self.metrics_file = os.path.join(storage_dir, "performance_metrics.json")
        self.alerts_file = os.path.join(storage_dir, "alerts.json")
        
        self.metrics_history = {}
        self.alerts = []
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
            
        # Load existing data
        self._load_data()
        
        logger.info("Revenue Performance Monitor initialized")
        
    def _load_data(self) -> None:
        """Load metrics and alerts from storage."""
        # Load metrics
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    self.metrics_history = json.load(f)
                    
                logger.info(f"Loaded metrics history from {self.metrics_file}")
            except Exception as e:
                logger.error(f"Error loading metrics history: {e}")
                self.metrics_history = {}
        
        # Load alerts
        if os.path.exists(self.alerts_file):
            try:
                with open(self.alerts_file, 'r') as f:
                    self.alerts = json.load(f)
                    
                logger.info(f"Loaded {len(self.alerts)} alerts from {self.alerts_file}")
            except Exception as e:
                logger.error(f"Error loading alerts: {e}")
                self.alerts = []
                
    def _save_metrics(self) -> None:
        """Save metrics history to storage."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
                
            logger.info(f"Saved metrics history to {self.metrics_file}")
        except Exception as e:
            logger.error(f"Error saving metrics history: {e}")
            
    def _save_alerts(self) -> None:
        """Save alerts to storage."""
        try:
            with open(self.alerts_file, 'w') as f:
                json.dump(self.alerts, f, indent=2)
                
            logger.info(f"Saved {len(self.alerts)} alerts to {self.alerts_file}")
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")
            
    async def record_metrics(
        self,
        metrics: Dict[str, Any],
        timestamp: Optional[str] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record revenue performance metrics.
        
        Args:
            metrics: Dict containing metrics to record
            timestamp: Optional timestamp (ISO format)
            source: Optional source of the metrics
            
        Returns:
            Dict containing recorded metrics entry
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        entry_id = f"metrics_{uuid.uuid4().hex[:8]}"
        
        entry = {
            "id": entry_id,
            "timestamp": timestamp,
            "source": source,
            "metrics": metrics
        }
        
        # Add to history
        self.metrics_history[entry_id] = entry
        self._save_metrics()
        
        # Check for anomalies and generate alerts
        await self._analyze_metrics(entry)
        
        logger.info(f"Recorded metrics entry {entry_id}")
        
        return entry
        
    async def get_metrics_history(
        self,
        metric_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metrics history, optionally filtered.
        
        Args:
            metric_name: Optional metric name filter
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)
            source: Optional source filter
            
        Returns:
            List of metrics entries
        """
        entries = list(self.metrics_history.values())
        
        # Apply filters
        if start_date:
            entries = [e for e in entries if e.get("timestamp", "") >= start_date]
            
        if end_date:
            entries = [e for e in entries if e.get("timestamp", "") <= end_date]
            
        if source:
            entries = [e for e in entries if e.get("source") == source]
            
        if metric_name:
            filtered_entries = []
            for entry in entries:
                metrics = entry.get("metrics", {})
                if metric_name in metrics:
                    filtered_entry = {
                        "id": entry.get("id"),
                        "timestamp": entry.get("timestamp"),
                        "source": entry.get("source"),
                        "metrics": {metric_name: metrics[metric_name]}
                    }
                    filtered_entries.append(filtered_entry)
            entries = filtered_entries
            
        # Sort by timestamp
        entries.sort(key=lambda x: x.get("timestamp", ""))
        
        return entries
        
    async def get_metric_time_series(
        self,
        metric_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get a time series for a specific metric.
        
        Args:
            metric_name: Name of the metric
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)
            source: Optional source filter
            
        Returns:
            List of data points with timestamp and value
        """
        entries = await self.get_metrics_history(
            metric_name=metric_name,
            start_date=start_date,
            end_date=end_date,
            source=source
        )
        
        time_series = []
        for entry in entries:
            timestamp = entry.get("timestamp")
            metrics = entry.get("metrics", {})
            value = metrics.get(metric_name)
            
            if timestamp and value is not None:
                time_series.append({
                    "timestamp": timestamp,
                    "value": value
                })
                
        return time_series
        
    async def create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        metrics: Optional[Dict[str, Any]] = None,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a revenue performance alert.
        
        Args:
            alert_type: Type of alert (use AlertType enum)
            severity: Severity level (use AlertSeverity enum)
            message: Alert message
            metrics: Optional metrics related to the alert
            entity_id: Optional ID of related entity (e.g., goal, channel)
            entity_type: Optional type of related entity
            
        Returns:
            Dict containing the created alert
        """
        alert_id = f"alert_{uuid.uuid4().hex[:8]}"
        
        alert = {
            "id": alert_id,
            "type": alert_type,
            "severity": severity,
            "message": message,
            "metrics": metrics or {},
            "entity_id": entity_id,
            "entity_type": entity_type,
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Add to alerts
        self.alerts.append(alert)
        self._save_alerts()
        
        logger.info(f"Created {severity} alert: {message}")
        
        return alert
        
    async def resolve_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Resolve an alert.
        
        Args:
            alert_id: ID of the alert
            
        Returns:
            Dict containing the resolved alert, or None if not found
        """
        for i, alert in enumerate(self.alerts):
            if alert.get("id") == alert_id:
                alert["status"] = "resolved"
                alert["resolved_at"] = datetime.now().isoformat()
                
                self.alerts[i] = alert
                self._save_alerts()
                
                logger.info(f"Resolved alert {alert_id}")
                
                return alert
                
        logger.error(f"Alert {alert_id} not found")
        return None
        
    async def get_active_alerts(
        self,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get active alerts, optionally filtered.
        
        Args:
            severity: Optional severity filter
            alert_type: Optional type filter
            entity_id: Optional entity ID filter
            
        Returns:
            List of active alerts
        """
        active_alerts = [a for a in self.alerts if a.get("status") == "active"]
        
        # Apply filters
        if severity:
            active_alerts = [a for a in active_alerts if a.get("severity") == severity]
            
        if alert_type:
            active_alerts = [a for a in active_alerts if a.get("type") == alert_type]
            
        if entity_id:
            active_alerts = [a for a in active_alerts if a.get("entity_id") == entity_id]
            
        return active_alerts
        
    async def _analyze_metrics(self, entry: Dict[str, Any]) -> None:
        """
        Analyze metrics entry for anomalies and trends.
        
        Args:
            entry: Metrics entry to analyze
        """
        metrics = entry.get("metrics", {})
        
        # Check for significant metrics
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                # Get historical values for this metric
                time_series = await self.get_metric_time_series(metric_name)
                
                if len(time_series) >= 3:  # Need at least 3 points for trend analysis
                    # Check for anomalies
                    is_anomaly, deviation = self._detect_anomaly(time_series, value)
                    
                    if is_anomaly:
                        # Create anomaly alert
                        severity = AlertSeverity.WARNING
                        
                        if deviation > 50:
                            severity = AlertSeverity.CRITICAL
                            
                        await self.create_alert(
                            alert_type=AlertType.ANOMALY_DETECTED,
                            severity=severity,
                            message=f"Anomaly detected in {metric_name}: {value} (deviation: {deviation:.2f}%)",
                            metrics={metric_name: value},
                            entity_type="metric"
                        )
                    
                    # Check for trends
                    trend = self._detect_trend(time_series)
                    
                    if trend == "declining" and metric_name.lower() in ["revenue", "conversion_rate", "roi"]:
                        # Create decline alert
                        alert_type = AlertType.REVENUE_DECLINE
                        if "conversion" in metric_name.lower():
                            alert_type = AlertType.CONVERSION_DECLINE
                            
                        await self.create_alert(
                            alert_type=alert_type,
                            severity=AlertSeverity.WARNING,
                            message=f"Declining trend detected in {metric_name}",
                            metrics={metric_name: value},
                            entity_type="metric"
                        )
                    elif trend == "increasing" and metric_name.lower() in ["revenue", "conversion_rate", "roi"]:
                        # Create opportunity alert
                        await self.create_alert(
                            alert_type=AlertType.OPPORTUNITY_IDENTIFIED,
                            severity=AlertSeverity.INFO,
                            message=f"Positive trend detected in {metric_name}",
                            metrics={metric_name: value},
                            entity_type="metric"
                        )
        
    def _detect_anomaly(
        self,
        time_series: List[Dict[str, Any]],
        current_value: float
    ) -> Tuple[bool, float]:
        """
        Detect if a value is an anomaly based on historical data.
        
        Args:
            time_series: Historical time series data
            current_value: Current value to check
            
        Returns:
            Tuple of (is_anomaly, deviation_percent)
        """
        # Extract values
        values = [point.get("value", 0.0) for point in time_series]
        
        if not values:
            return False, 0.0
            
        # Calculate mean and standard deviation
        mean = sum(values) / len(values)
        std_dev = np.std(values) if len(values) > 1 else 0.0
        
        # Calculate z-score
        if std_dev > 0:
            z_score = abs(current_value - mean) / std_dev
        else:
            z_score = 0.0
            
        # Calculate percent deviation from mean
        if mean > 0:
            deviation_percent = abs(current_value - mean) / mean * 100.0
        else:
            deviation_percent = 0.0
            
        # Determine if anomaly (z-score > 2 and deviation > 20%)
        is_anomaly = z_score > 2.0 and deviation_percent > 20.0
        
        return is_anomaly, deviation_percent
        
    def _detect_trend(self, time_series: List[Dict[str, Any]]) -> str:
        """
        Detect trend in time series data.
        
        Args:
            time_series: Time series data
            
        Returns:
            String indicating trend: "increasing", "declining", or "stable"
        """
        if len(time_series) < 3:
            return "stable"
            
        # Extract values from most recent 3 points
        recent_points = sorted(time_series, key=lambda x: x.get("timestamp", ""))[-3:]
        values = [point.get("value", 0.0) for point in recent_points]
        
        # Check for consistent increase or decrease
        if values[0] < values[1] < values[2]:
            return "increasing"
        elif values[0] > values[1] > values[2]:
            return "declining"
        else:
            return "stable"
            
    async def monitor_goal_progress(self, goals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Monitor progress of revenue goals and generate alerts.
        
        Args:
            goals: List of revenue goals
            
        Returns:
            List of generated alerts
        """
        alerts = []
        
        for goal in goals:
            goal_id = goal.get("id")
            goal_name = goal.get("name", "Unknown Goal")
            target_value = goal.get("target_value", 0.0)
            current_value = goal.get("current_value", 0.0)
            progress = goal.get("progress", 0.0)
            end_date = goal.get("end_date")
            
            # Skip goals without end date
            if not end_date:
                continue
                
            # Calculate days remaining
            try:
                end_datetime = datetime.fromisoformat(end_date)
                days_remaining = (end_datetime - datetime.now()).days
            except (ValueError, TypeError):
                days_remaining = 30  # Default if date parsing fails
                
            # Check if goal is at risk
            if days_remaining > 0 and progress < (100 - days_remaining):
                # Goal is behind schedule
                severity = AlertSeverity.WARNING
                
                if progress < 25 and days_remaining < 7:
                    severity = AlertSeverity.CRITICAL
                    
                alert = await self.create_alert(
                    alert_type=AlertType.GOAL_AT_RISK,
                    severity=severity,
                    message=f"Goal '{goal_name}' is at risk: {progress:.1f}% complete with {days_remaining} days remaining",
                    metrics={
                        "target_value": target_value,
                        "current_value": current_value,
                        "progress": progress,
                        "days_remaining": days_remaining
                    },
                    entity_id=goal_id,
                    entity_type="goal"
                )
                
                alerts.append(alert)
                
        return alerts
        
    async def monitor_channel_performance(
        self,
        channel_metrics: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Monitor performance of revenue channels and generate alerts.
        
        Args:
            channel_metrics: Dict mapping channel names to metrics
            
        Returns:
            List of generated alerts
        """
        alerts = []
        
        # Calculate average metrics across channels
        avg_metrics = {}
        for channel, metrics in channel_metrics.items():
            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)):
                    if metric_name not in avg_metrics:
                        avg_metrics[metric_name] = []
                        
                    avg_metrics[metric_name].append(value)
                    
        # Calculate averages
        for metric_name, values in avg_metrics.items():
            avg_metrics[metric_name] = sum(values) / len(values) if values else 0.0
            
        # Check each channel against averages
        for channel, metrics in channel_metrics.items():
            underperforming_metrics = []
            
            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)) and metric_name in avg_metrics:
                    avg_value = avg_metrics[metric_name]
                    
                    # Check if significantly below average (30% or more)
                    if avg_value > 0 and value < (avg_value * 0.7):
                        underperforming_metrics.append({
                            "name": metric_name,
                            "value": value,
                            "average": avg_value,
                            "deviation": ((avg_value - value) / avg_value) * 100.0
                        })
                        
            if underperforming_metrics:
                # Create alert for underperforming channel
                alert = await self.create_alert(
                    alert_type=AlertType.CHANNEL_UNDERPERFORMING,
                    severity=AlertSeverity.WARNING,
                    message=f"Channel '{channel}' is underperforming in {len(underperforming_metrics)} metrics",
                    metrics={m["name"]: m["value"] for m in underperforming_metrics},
                    entity_id=channel,
                    entity_type="channel"
                )
                
                alerts.append(alert)
                
        return alerts
        
    async def monitor_forecast_accuracy(
        self,
        forecast: Dict[str, Any],
        actual_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Monitor forecast accuracy and generate alerts for significant deviations.
        
        Args:
            forecast: Revenue forecast
            actual_metrics: Actual metrics to compare against forecast
            
        Returns:
            List of generated alerts
        """
        alerts = []
        
        forecast_id = forecast.get("id")
        predictions = forecast.get("predictions", [])
        
        for prediction in predictions:
            # Check if prediction period matches current period
            prediction_date = prediction.get("date")
            prediction_value = prediction.get("value", 0.0)
            
            if not prediction_date:
                continue
                
            # Get actual value for the same metric
            metric_name = prediction.get("metric", "revenue")
            actual_value = actual_metrics.get(metric_name, 0.0)
            
            # Calculate deviation
            if prediction_value > 0:
                deviation_percent = abs(actual_value - prediction_value) / prediction_value * 100.0
            else:
                deviation_percent = 0.0
                
            # Check if significant deviation
            if deviation_percent > 20.0:
                severity = AlertSeverity.WARNING
                
                if deviation_percent > 50.0:
                    severity = AlertSeverity.CRITICAL
                    
                direction = "below" if actual_value < prediction_value else "above"
                
                alert = await self.create_alert(
                    alert_type=AlertType.FORECAST_DEVIATION,
                    severity=severity,
                    message=f"{metric_name.capitalize()} is {deviation_percent:.1f}% {direction} forecast",
                    metrics={
                        "forecast_value": prediction_value,
                        "actual_value": actual_value,
                        "deviation_percent": deviation_percent
                    },
                    entity_id=forecast_id,
                    entity_type="forecast"
                )
                
                alerts.append(alert)
                
        return alerts
        
    async def generate_performance_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a summary of revenue performance.
        
        Args:
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)
            
        Returns:
            Dict containing performance summary
        """
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
            
        if not end_date:
            end_date = datetime.now().isoformat()
            
        # Get metrics history
        entries = await self.get_metrics_history(
            start_date=start_date,
            end_date=end_date
        )
        
        # Extract all unique metric names
        metric_names = set()
        for entry in entries:
            metrics = entry.get("metrics", {})
            metric_names.update(metrics.keys())
            
        # Get time series for each metric
        metric_series = {}
        for metric_name in metric_names:
            series = await self.get_metric_time_series(
                metric_name=metric_name,
                start_date=start_date,
                end_date=end_date
            )
            
            if series:
                metric_series[metric_name] = series
                
        # Calculate summary statistics
        summary = {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "metrics": {},
            "trends": {},
            "alerts": {
                "total": 0,
                "critical": 0,
                "warning": 0,
                "info": 0
            }
        }
        
        # Process each metric
        for metric_name, series in metric_series.items():
            if not series:
                continue
                
            values = [point.get("value", 0.0) for point in series]
            
            # Calculate statistics
            latest = values[-1] if values else 0.0
            average = sum(values) / len(values) if values else 0.0
            minimum = min(values) if values else 0.0
            maximum = max(values) if values else 0.0
            
            # Calculate change
            if len(values) >= 2:
                first = values[0]
                change = latest - first
                percent_change = (change / first * 100.0) if first != 0 else 0.0
            else:
                change = 0.0
                percent_change = 0.0
                
            # Detect trend
            trend = self._detect_trend(series)
            
            # Add to summary
            summary["metrics"][metric_name] = {
                "latest": latest,
                "average": average,
                "minimum": minimum,
                "maximum": maximum,
                "change": change,
                "percent_change": percent_change
            }
            
            summary["trends"][metric_name] = trend
            
        # Get alerts
        active_alerts = await self.get_active_alerts()
        
        # Count alerts by severity
        summary["alerts"]["total"] = len(active_alerts)
        summary["alerts"]["critical"] = len([a for a in active_alerts if a.get("severity") == AlertSeverity.CRITICAL])
        summary["alerts"]["warning"] = len([a for a in active_alerts if a.get("severity") == AlertSeverity.WARNING])
        summary["alerts"]["info"] = len([a for a in active_alerts if a.get("severity") == AlertSeverity.INFO])
        
        return summary
