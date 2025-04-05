"""
Revenue Forecasting Engine Extensions for the Autonomous Marketing Agent.

This module implements additional functionality for the Revenue Forecasting Engine component,
including gap analysis, early warnings, and reporting capabilities.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
import os
import uuid
import asyncio
from enum import Enum

# Import forecast models and base engine
from core.revenue.forecast_models import (
    ForecastingMethod, ScenarioType, TimeGranularity
)
from core.revenue.revenue_forecasting_engine import RevenueForecastingEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WarningLevel(Enum):
    """Enumeration of warning levels for revenue forecasts."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RevenueForecastingEngineExtended(RevenueForecastingEngine):
    """
    Extended Revenue Forecasting Engine with additional capabilities.
    
    This extended engine adds:
    - Revenue gap analysis
    - Early warning system
    - Comprehensive reporting
    - Resource requirement forecasting
    - Forecast accuracy tracking
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        default_method: ForecastingMethod = ForecastingMethod.EXPONENTIAL_SMOOTHING,
        default_granularity: TimeGranularity = TimeGranularity.MONTHLY
    ):
        """
        Initialize the Extended Revenue Forecasting Engine.
        
        Args:
            storage_path: Optional path to store forecasting data and models
            default_method: Default forecasting method to use
            default_granularity: Default time granularity for forecasting
        """
        super().__init__(storage_path, default_method, default_granularity)
        
        # Additional storage
        self.gap_analyses = {}  # Dictionary of gap analyses by ID
        self.accuracy_reports = {}  # Dictionary of accuracy reports by ID
        self.resource_forecasts = {}  # Dictionary of resource forecasts by ID
        
        logger.info("Extended Revenue Forecasting Engine initialized")
    
    async def detect_seasonality(
        self,
        data_key: Optional[str] = None,
        min_periods: int = 12
    ) -> Dict[str, Any]:
        """
        Detect seasonal patterns in historical revenue data.
        
        Args:
            data_key: Key for historical data (defaults to 'all:all')
            min_periods: Minimum number of periods required for detection
            
        Returns:
            Dict containing seasonality analysis
        """
        # Use default data key if not specified
        if data_key is None:
            data_key = "all:all"
        
        # Check if data exists
        if data_key not in self.historical_data or not self.historical_data[data_key]:
            return {
                "status": "error",
                "message": f"No historical data found for {data_key}"
            }
        
        # Check if enough data points
        if len(self.historical_data[data_key]) < min_periods:
            return {
                "status": "error",
                "message": f"Not enough data points for seasonality detection (need at least {min_periods})"
            }
        
        # Extract values
        data = sorted(self.historical_data[data_key], key=lambda x: x["timestamp"])
        values = [float(point["value"]) for point in data]
        
        # Simple seasonality detection using autocorrelation
        # In a real implementation, this would use more sophisticated methods
        
        # Calculate mean and variance
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        # Calculate autocorrelation for different lags
        max_lag = min(len(values) // 2, 24)  # Maximum lag to check
        autocorrelations = []
        
        for lag in range(1, max_lag + 1):
            numerator = sum((values[i] - mean) * (values[i - lag] - mean) for i in range(lag, len(values)))
            denominator = variance * (len(values) - lag)
            
            if denominator > 0:
                autocorr = numerator / denominator
                autocorrelations.append({
                    "lag": lag,
                    "value": autocorr
                })
            else:
                autocorrelations.append({
                    "lag": lag,
                    "value": 0
                })
        
        # Find peaks in autocorrelation
        peaks = []
        for i in range(1, len(autocorrelations) - 1):
            if (autocorrelations[i]["value"] > autocorrelations[i-1]["value"] and 
                autocorrelations[i]["value"] > autocorrelations[i+1]["value"] and
                autocorrelations[i]["value"] > 0.3):  # Threshold for significance
                peaks.append(autocorrelations[i])
        
        # Sort peaks by autocorrelation value
        peaks.sort(key=lambda x: x["value"], reverse=True)
        
        # Determine likely seasonal periods
        seasonal_periods = []
        if peaks:
            for peak in peaks[:3]:  # Top 3 peaks
                seasonal_periods.append({
                    "periods": peak["lag"],
                    "strength": peak["value"],
                    "description": self._get_seasonality_description(peak["lag"])
                })
        
        # Calculate seasonal factors if seasonality detected
        seasonal_factors = []
        if seasonal_periods:
            primary_period = seasonal_periods[0]["periods"]
            
            # Calculate average value for each position in the seasonal cycle
            seasonal_sums = [0] * primary_period
            seasonal_counts = [0] * primary_period
            
            for i, value in enumerate(values):
                position = i % primary_period
                seasonal_sums[position] += value
                seasonal_counts[position] += 1
            
            # Calculate average for each position
            seasonal_averages = [
                seasonal_sums[i] / seasonal_counts[i] if seasonal_counts[i] > 0 else 0
                for i in range(primary_period)
            ]
            
            # Calculate overall average
            overall_average = sum(seasonal_averages) / len(seasonal_averages)
            
            # Calculate seasonal factors
            seasonal_factors = [avg / overall_average if overall_average > 0 else 1.0 for avg in seasonal_averages]
        
        # Create result
        result = {
            "status": "success",
            "data_key": data_key,
            "data_points": len(values),
            "autocorrelations": autocorrelations,
            "seasonal_periods": seasonal_periods,
            "seasonal_factors": seasonal_factors,
            "has_seasonality": len(seasonal_periods) > 0
        }
        
        logger.info(f"Detected {len(seasonal_periods)} seasonal patterns in {data_key} data")
        return result
    
    async def identify_revenue_gaps(
        self,
        forecast_id: str,
        target_values: List[float]
    ) -> Dict[str, Any]:
        """
        Identify gaps between forecasted revenue and target values.
        
        Args:
            forecast_id: ID of the forecast to analyze
            target_values: List of target revenue values for each period
            
        Returns:
            Dict containing gap analysis
        """
        # Check if forecast exists
        if forecast_id not in self.forecasts:
            return {
                "status": "error",
                "message": f"Forecast not found: {forecast_id}"
            }
        
        forecast = self.forecasts[forecast_id]
        predictions = forecast["predictions"]
        
        # Check if target values match forecast periods
        if len(target_values) != len(predictions):
            return {
                "status": "error",
                "message": f"Target values count ({len(target_values)}) does not match forecast periods ({len(predictions)})"
            }
        
        # Calculate gaps
        gaps = []
        total_gap = 0
        total_target = 0
        total_forecast = 0
        
        for i, (prediction, target) in enumerate(zip(predictions, target_values)):
            forecast_value = prediction["value"]
            gap = target - forecast_value
            gap_percentage = (gap / target * 100) if target > 0 else 0
            
            gaps.append({
                "period": i,
                "timestamp": prediction["timestamp"],
                "forecast_value": forecast_value,
                "target_value": target,
                "gap": gap,
                "gap_percentage": gap_percentage,
                "status": "surplus" if gap <= 0 else "deficit"
            })
            
            total_gap += gap
            total_target += target
            total_forecast += forecast_value
        
        # Calculate overall gap percentage
        overall_gap_percentage = (total_gap / total_target * 100) if total_target > 0 else 0
        
        # Create gap analysis
        analysis_id = str(uuid.uuid4())
        analysis = {
            "id": analysis_id,
            "timestamp": datetime.now().isoformat(),
            "forecast_id": forecast_id,
            "gaps": gaps,
            "summary": {
                "total_gap": total_gap,
                "total_target": total_target,
                "total_forecast": total_forecast,
                "overall_gap_percentage": overall_gap_percentage,
                "status": "surplus" if total_gap <= 0 else "deficit"
            }
        }
        
        # Store analysis
        self.gap_analyses[analysis_id] = analysis
        
        # Save data
        self._save_data()
        
        logger.info(f"Identified revenue gaps with overall gap of {total_gap:.2f} ({overall_gap_percentage:.2f}%)")
        return analysis
    
    async def generate_early_warnings(
        self,
        forecast_id: str,
        target_values: List[float],
        thresholds: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Generate early warnings for potential revenue shortfalls.
        
        Args:
            forecast_id: ID of the forecast to analyze
            target_values: List of target revenue values for each period
            thresholds: Optional thresholds for warning levels
            
        Returns:
            Dict containing warning data
        """
        # Use default thresholds if not specified
        if thresholds is None:
            thresholds = {
                "low": 5.0,      # 5% gap
                "medium": 10.0,  # 10% gap
                "high": 20.0,    # 20% gap
                "critical": 30.0  # 30% gap
            }
        
        # Perform gap analysis
        gap_analysis = await self.identify_revenue_gaps(forecast_id, target_values)
        
        if "status" in gap_analysis and gap_analysis["status"] == "error":
            return gap_analysis
        
        # Generate warnings
        warnings = []
        
        for gap_data in gap_analysis["gaps"]:
            if gap_data["status"] == "deficit":
                # Determine warning level based on gap percentage
                gap_percentage = abs(gap_data["gap_percentage"])
                
                if gap_percentage >= thresholds["critical"]:
                    level = WarningLevel.CRITICAL
                elif gap_percentage >= thresholds["high"]:
                    level = WarningLevel.HIGH
                elif gap_percentage >= thresholds["medium"]:
                    level = WarningLevel.MEDIUM
                elif gap_percentage >= thresholds["low"]:
                    level = WarningLevel.LOW
                else:
                    level = WarningLevel.INFO
                
                warnings.append({
                    "period": gap_data["period"],
                    "timestamp": gap_data["timestamp"],
                    "level": level.value,
                    "gap": gap_data["gap"],
                    "gap_percentage": gap_data["gap_percentage"],
                    "message": f"Revenue shortfall of {gap_data['gap']:.2f} ({gap_data['gap_percentage']:.2f}%)"
                })
        
        # Create warning data
        warning_id = str(uuid.uuid4())
        warning_data = {
            "id": warning_id,
            "timestamp": datetime.now().isoformat(),
            "forecast_id": forecast_id,
            "gap_analysis_id": gap_analysis["id"],
            "thresholds": thresholds,
            "warnings": warnings,
            "summary": {
                "total_warnings": len(warnings),
                "by_level": {
                    "info": sum(1 for w in warnings if w["level"] == WarningLevel.INFO.value),
                    "low": sum(1 for w in warnings if w["level"] == WarningLevel.LOW.value),
                    "medium": sum(1 for w in warnings if w["level"] == WarningLevel.MEDIUM.value),
                    "high": sum(1 for w in warnings if w["level"] == WarningLevel.HIGH.value),
                    "critical": sum(1 for w in warnings if w["level"] == WarningLevel.CRITICAL.value)
                }
            }
        }
        
        # Store warning data
        self.warnings[warning_id] = warning_data
        
        # Save data
        self._save_data()
        
        logger.info(f"Generated {len(warnings)} early warnings for forecast {forecast_id}")
        return warning_data
    
    async def forecast_resource_requirements(
        self,
        forecast_id: str,
        resource_factors: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Forecast resource requirements based on revenue predictions.
        
        Args:
            forecast_id: ID of the forecast to analyze
            resource_factors: Dictionary mapping resource types to factors
            
        Returns:
            Dict containing resource forecast data
        """
        # Check if forecast exists
        if forecast_id not in self.forecasts:
            return {
                "status": "error",
                "message": f"Forecast not found: {forecast_id}"
            }
        
        forecast = self.forecasts[forecast_id]
        predictions = forecast["predictions"]
        
        # Calculate resource requirements
        resources = []
        
        for i, prediction in enumerate(predictions):
            revenue = prediction["value"]
            period_resources = {
                "period": i,
                "timestamp": prediction["timestamp"],
                "revenue": revenue,
                "resources": {}
            }
            
            # Calculate each resource type
            for resource_type, factor in resource_factors.items():
                resource_value = revenue * factor
                period_resources["resources"][resource_type] = resource_value
            
            resources.append(period_resources)
        
        # Calculate totals
        total_revenue = sum(prediction["value"] for prediction in predictions)
        total_resources = {
            resource_type: total_revenue * factor
            for resource_type, factor in resource_factors.items()
        }
        
        # Create resource forecast
        forecast_id = str(uuid.uuid4())
        resource_forecast = {
            "id": forecast_id,
            "timestamp": datetime.now().isoformat(),
            "forecast_id": forecast_id,
            "resource_factors": resource_factors,
            "resources": resources,
            "summary": {
                "total_revenue": total_revenue,
                "total_resources": total_resources
            }
        }
        
        # Store resource forecast
        self.resource_forecasts[forecast_id] = resource_forecast
        
        # Save data
        self._save_data()
        
        logger.info(f"Forecasted resource requirements for {len(resource_factors)} resource types")
        return resource_forecast
    
    async def calculate_forecast_accuracy(
        self,
        forecast_id: str,
        actual_values: List[float]
    ) -> Dict[str, Any]:
        """
        Calculate accuracy of a previous forecast compared to actual values.
        
        Args:
            forecast_id: ID of the forecast to evaluate
            actual_values: List of actual revenue values for each period
            
        Returns:
            Dict containing accuracy report
        """
        # Check if forecast exists
        if forecast_id not in self.forecasts:
            return {
                "status": "error",
                "message": f"Forecast not found: {forecast_id}"
            }
        
        forecast = self.forecasts[forecast_id]
        predictions = forecast["predictions"]
        
        # Check if actual values match forecast periods
        if len(actual_values) > len(predictions):
            actual_values = actual_values[:len(predictions)]
        elif len(actual_values) < len(predictions):
            return {
                "status": "error",
                "message": f"Not enough actual values ({len(actual_values)}) to evaluate forecast ({len(predictions)} periods)"
            }
        
        # Calculate accuracy metrics
        periods = []
        total_actual = 0
        total_forecast = 0
        total_absolute_error = 0
        total_squared_error = 0
        
        for i, (prediction, actual) in enumerate(zip(predictions, actual_values)):
            forecast_value = prediction["value"]
            error = actual - forecast_value
            absolute_error = abs(error)
            squared_error = error ** 2
            percentage_error = (absolute_error / actual * 100) if actual > 0 else 0
            
            periods.append({
                "period": i,
                "timestamp": prediction["timestamp"],
                "forecast_value": forecast_value,
                "actual_value": actual,
                "error": error,
                "absolute_error": absolute_error,
                "squared_error": squared_error,
                "percentage_error": percentage_error
            })
            
            total_actual += actual
            total_forecast += forecast_value
            total_absolute_error += absolute_error
            total_squared_error += squared_error
        
        # Calculate overall metrics
        n = len(periods)
        mae = total_absolute_error / n if n > 0 else 0
        mse = total_squared_error / n if n > 0 else 0
        rmse = mse ** 0.5
        
        # Calculate MAPE
        mape_sum = sum(
            period["percentage_error"]
            for period in periods
            if period["actual_value"] > 0
        )
        mape_count = sum(1 for period in periods if period["actual_value"] > 0)
        mape = mape_sum / mape_count if mape_count > 0 else 0
        
        # Calculate overall bias
        bias = (total_forecast - total_actual) / total_actual * 100 if total_actual > 0 else 0
        
        # Create accuracy report
        report_id = str(uuid.uuid4())
        report = {
            "id": report_id,
            "timestamp": datetime.now().isoformat(),
            "forecast_id": forecast_id,
            "periods": periods,
            "metrics": {
                "mae": mae,
                "mse": mse,
                "rmse": rmse,
                "mape": mape,
                "bias": bias
            },
            "summary": {
                "total_actual": total_actual,
                "total_forecast": total_forecast,
                "overall_error": total_actual - total_forecast,
                "overall_error_percentage": (total_actual - total_forecast) / total_actual * 100 if total_actual > 0 else 0
            }
        }
        
        # Store accuracy report
        self.accuracy_reports[report_id] = report
        
        # Save data
        self._save_data()
        
        logger.info(f"Calculated forecast accuracy with MAPE of {mape:.2f}%")
        return report
    
    async def generate_forecast_report(
        self,
        forecast_id: str,
        scenarios: Optional[List[str]] = None,
        warning_id: Optional[str] = None,
        gap_analysis_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive forecast report.
        
        Args:
            forecast_id: ID of the forecast to include
            scenarios: Optional list of scenario IDs to include
            warning_id: Optional ID of warning data to include
            gap_analysis_id: Optional ID of gap analysis to include
            
        Returns:
            Dict containing the forecast report
        """
        # Check if forecast exists
        if forecast_id not in self.forecasts:
            return {
                "status": "error",
                "message": f"Forecast not found: {forecast_id}"
            }
        
        forecast = self.forecasts[forecast_id]
        
        # Get scenarios
        scenario_data = []
        if scenarios:
            for scenario_id in scenarios:
                if scenario_id in self.scenarios:
                    scenario_data.append(self.scenarios[scenario_id])
                else:
                    logger.warning(f"Scenario not found: {scenario_id}")
        
        # Get warning data
        warning_data = None
        if warning_id:
            if warning_id in self.warnings:
                warning_data = self.warnings[warning_id]
            else:
                logger.warning(f"Warning data not found: {warning_id}")
        
        # Get gap analysis
        gap_analysis = None
        if gap_analysis_id:
            if gap_analysis_id in self.gap_analyses:
                gap_analysis = self.gap_analyses[gap_analysis_id]
            else:
                logger.warning(f"Gap analysis not found: {gap_analysis_id}")
        
        # Create report
        report_id = str(uuid.uuid4())
        report = {
            "id": report_id,
            "timestamp": datetime.now().isoformat(),
            "title": f"Revenue Forecast Report - {datetime.now().strftime('%Y-%m-%d')}",
            "forecast": forecast,
            "scenarios": scenario_data,
            "warnings": warning_data,
            "gap_analysis": gap_analysis,
            "metadata": {
                "generated_by": "Revenue Forecasting Engine",
                "version": "1.0"
            }
        }
        
        logger.info(f"Generated comprehensive forecast report with {len(scenario_data)} scenarios")
        return report
    
    def _get_seasonality_description(self, periods: int) -> str:
        """
        Get a human-readable description of a seasonal pattern.
        
        Args:
            periods: Number of periods in the seasonal cycle
            
        Returns:
            String description of the seasonality
        """
        if periods == 4:
            return "Quarterly seasonality"
        elif periods == 12:
            return "Monthly seasonality"
        elif periods == 52 or periods == 53:
            return "Weekly seasonality"
        elif periods == 7:
            return "Day-of-week seasonality"
        elif periods == 24:
            return "Hourly seasonality"
        elif periods == 365 or periods == 366:
            return "Daily seasonality"
        else:
            return f"{periods}-period seasonality"
