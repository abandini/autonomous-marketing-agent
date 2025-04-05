"""
Forecast Models for the Revenue Forecasting Engine.

This module implements the core forecasting models used by the Revenue Forecasting Engine
to predict future revenue, detect seasonality, and model various scenarios.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum
import math
import numpy as np
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ForecastingMethod(Enum):
    """Enumeration of forecasting methods."""
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    LINEAR_REGRESSION = "linear_regression"
    ARIMA = "arima"
    PROPHET = "prophet"
    LSTM = "lstm"
    ENSEMBLE = "ensemble"
    CUSTOM = "custom"

class ScenarioType(Enum):
    """Enumeration of scenario types for forecasting."""
    BASELINE = "baseline"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    SEASONAL = "seasonal"
    CAMPAIGN = "campaign"
    MARKET_SHIFT = "market_shift"
    COMPETITOR_ACTION = "competitor_action"
    CUSTOM = "custom"

class TimeGranularity(Enum):
    """Enumeration of time granularities for forecasting."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class ForecastModel(ABC):
    """
    Abstract base class for all forecasting models.
    """
    
    def __init__(
        self,
        name: str,
        method: ForecastingMethod,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a forecast model.
        
        Args:
            name: Name of the forecast model
            method: Forecasting method to use
            config: Configuration parameters for the model
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.method = method
        self.config = config or {}
        self.creation_date = datetime.now()
        self.last_updated = datetime.now()
        self.last_trained = None
        self.metrics = {
            "mape": None,  # Mean Absolute Percentage Error
            "rmse": None,  # Root Mean Square Error
            "mae": None,   # Mean Absolute Error
            "r2": None     # R-squared
        }
        
        logger.info(f"Initialized {self.method.value} forecast model: {self.name}")
    
    @abstractmethod
    def train(self, data: List[Dict[str, Any]]) -> None:
        """
        Train the forecast model on historical data.
        
        Args:
            data: List of data points with timestamp and value
        """
        pass
    
    @abstractmethod
    def predict(
        self,
        periods: int,
        granularity: TimeGranularity,
        start_date: Optional[Union[str, datetime]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate predictions for future periods.
        
        Args:
            periods: Number of periods to forecast
            granularity: Time granularity for forecasting
            start_date: Start date for forecasting (defaults to now)
            
        Returns:
            List of predicted data points with timestamp and value
        """
        pass
    
    def evaluate(self, actual_data: List[Dict[str, Any]], predicted_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Evaluate model performance by comparing predictions to actual values.
        
        Args:
            actual_data: List of actual data points
            predicted_data: List of predicted data points
            
        Returns:
            Dictionary of evaluation metrics
        """
        if len(actual_data) != len(predicted_data):
            raise ValueError("Actual and predicted data must have the same length")
        
        actual_values = [float(point["value"]) for point in actual_data]
        predicted_values = [float(point["value"]) for point in predicted_data]
        
        # Calculate metrics
        metrics = {}
        
        # Mean Absolute Percentage Error (MAPE)
        mape_sum = 0
        mape_count = 0
        for i, actual in enumerate(actual_values):
            if actual != 0:  # Avoid division by zero
                mape_sum += abs((actual - predicted_values[i]) / actual)
                mape_count += 1
        
        metrics["mape"] = (mape_sum / mape_count * 100) if mape_count > 0 else None
        
        # Root Mean Square Error (RMSE)
        mse = sum((actual - predicted) ** 2 for actual, predicted in zip(actual_values, predicted_values)) / len(actual_values)
        metrics["rmse"] = math.sqrt(mse)
        
        # Mean Absolute Error (MAE)
        metrics["mae"] = sum(abs(actual - predicted) for actual, predicted in zip(actual_values, predicted_values)) / len(actual_values)
        
        # R-squared (coefficient of determination)
        mean_actual = sum(actual_values) / len(actual_values)
        ss_total = sum((actual - mean_actual) ** 2 for actual in actual_values)
        ss_residual = sum((actual - predicted) ** 2 for actual, predicted in zip(actual_values, predicted_values))
        
        metrics["r2"] = 1 - (ss_residual / ss_total) if ss_total != 0 else None
        
        # Update model metrics
        self.metrics = metrics
        self.last_updated = datetime.now()
        
        return metrics
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the forecast model to a dictionary for serialization.
        
        Returns:
            Dict containing all forecast model data
        """
        return {
            "id": self.id,
            "name": self.name,
            "method": self.method.value,
            "config": self.config,
            "creation_date": self.creation_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "last_trained": self.last_trained.isoformat() if self.last_trained else None,
            "metrics": self.metrics
        }

class MovingAverageModel(ForecastModel):
    """
    Moving Average forecast model.
    
    Uses a simple moving average of past values to predict future values.
    """
    
    def __init__(
        self,
        name: str,
        window_size: int = 3,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Moving Average forecast model.
        
        Args:
            name: Name of the forecast model
            window_size: Number of periods to include in the moving average
            config: Additional configuration parameters
        """
        super().__init__(name, ForecastingMethod.MOVING_AVERAGE, config or {})
        self.window_size = window_size
        self.historical_data = []
    
    def train(self, data: List[Dict[str, Any]]) -> None:
        """
        Train the moving average model on historical data.
        
        Args:
            data: List of data points with timestamp and value
        """
        # Sort data by timestamp
        sorted_data = sorted(data, key=lambda x: x["timestamp"])
        
        # Store historical data
        self.historical_data = sorted_data
        
        # Update model metadata
        self.last_trained = datetime.now()
        self.last_updated = datetime.now()
        
        logger.info(f"Trained {self.name} moving average model with {len(data)} data points")
    
    def predict(
        self,
        periods: int,
        granularity: TimeGranularity,
        start_date: Optional[Union[str, datetime]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate predictions using moving average.
        
        Args:
            periods: Number of periods to forecast
            granularity: Time granularity for forecasting
            start_date: Start date for forecasting (defaults to last historical data point)
            
        Returns:
            List of predicted data points with timestamp and value
        """
        if not self.historical_data:
            raise ValueError("Model has not been trained with historical data")
        
        # Convert string date to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        
        # If no start date provided, use the last historical data point
        if start_date is None:
            last_timestamp = max(point["timestamp"] for point in self.historical_data)
            if isinstance(last_timestamp, str):
                last_timestamp = datetime.fromisoformat(last_timestamp)
            start_date = last_timestamp
        
        # Extract values from historical data
        historical_values = [float(point["value"]) for point in self.historical_data]
        
        # Generate predictions
        predictions = []
        
        # Calculate initial moving average
        if len(historical_values) < self.window_size:
            initial_avg = sum(historical_values) / len(historical_values)
        else:
            initial_avg = sum(historical_values[-self.window_size:]) / self.window_size
        
        # Generate future values
        current_date = start_date
        values_window = historical_values[-self.window_size:] if len(historical_values) >= self.window_size else historical_values.copy()
        
        for i in range(periods):
            # Calculate next date based on granularity
            if i > 0:  # Skip first iteration as we start from start_date
                if granularity == TimeGranularity.DAILY:
                    current_date += timedelta(days=1)
                elif granularity == TimeGranularity.WEEKLY:
                    current_date += timedelta(weeks=1)
                elif granularity == TimeGranularity.MONTHLY:
                    # Approximate a month as 30 days
                    current_date += timedelta(days=30)
                elif granularity == TimeGranularity.QUARTERLY:
                    # Approximate a quarter as 90 days
                    current_date += timedelta(days=90)
                elif granularity == TimeGranularity.YEARLY:
                    # Approximate a year as 365 days
                    current_date += timedelta(days=365)
            
            # Calculate moving average
            predicted_value = sum(values_window) / len(values_window)
            
            # Add prediction
            predictions.append({
                "timestamp": current_date.isoformat(),
                "value": predicted_value,
                "confidence_interval": None  # Simple moving average doesn't provide confidence intervals
            })
            
            # Update window for next prediction
            values_window.append(predicted_value)
            if len(values_window) > self.window_size:
                values_window.pop(0)
        
        return predictions

class ExponentialSmoothingModel(ForecastModel):
    """
    Exponential Smoothing forecast model.
    
    Uses exponential smoothing to give more weight to recent observations.
    """
    
    def __init__(
        self,
        name: str,
        alpha: float = 0.3,
        beta: Optional[float] = None,
        gamma: Optional[float] = None,
        seasonal_periods: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an Exponential Smoothing forecast model.
        
        Args:
            name: Name of the forecast model
            alpha: Smoothing factor for level (0-1)
            beta: Smoothing factor for trend (0-1), None for simple exponential smoothing
            gamma: Smoothing factor for seasonality (0-1), None for non-seasonal models
            seasonal_periods: Number of periods in a seasonal cycle, required if gamma is provided
            config: Additional configuration parameters
        """
        super().__init__(name, ForecastingMethod.EXPONENTIAL_SMOOTHING, config or {})
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.seasonal_periods = seasonal_periods
        
        # Model state
        self.level = None
        self.trend = None
        self.seasonals = None
        self.historical_data = []
        
        # Validate parameters
        if gamma is not None and seasonal_periods is None:
            raise ValueError("seasonal_periods must be provided when gamma is specified")
    
    def train(self, data: List[Dict[str, Any]]) -> None:
        """
        Train the exponential smoothing model on historical data.
        
        Args:
            data: List of data points with timestamp and value
        """
        # Sort data by timestamp
        sorted_data = sorted(data, key=lambda x: x["timestamp"])
        
        # Store historical data
        self.historical_data = sorted_data
        
        # Extract values
        values = [float(point["value"]) for point in sorted_data]
        
        if not values:
            raise ValueError("No data provided for training")
        
        # Initialize model components
        if self.gamma is not None:  # Triple exponential smoothing (Holt-Winters)
            if len(values) < 2 * self.seasonal_periods:
                raise ValueError(f"Need at least {2 * self.seasonal_periods} data points for seasonal model")
                
            # Initialize level, trend, and seasonal components
            self.level = values[0]
            self.trend = sum(values[self.seasonal_periods:2*self.seasonal_periods] - values[:self.seasonal_periods]) / (self.seasonal_periods ** 2)
            self.seasonals = [values[i] / self.level for i in range(self.seasonal_periods)]
            
            # Normalize seasonals
            mean_seasonal = sum(self.seasonals) / len(self.seasonals)
            self.seasonals = [s / mean_seasonal for s in self.seasonals]
            
        elif self.beta is not None:  # Double exponential smoothing (Holt's method)
            if len(values) < 2:
                raise ValueError("Need at least 2 data points for trend model")
                
            # Initialize level and trend
            self.level = values[0]
            self.trend = values[1] - values[0]
            
        else:  # Simple exponential smoothing
            # Initialize level
            self.level = values[0]
        
        # Update model metadata
        self.last_trained = datetime.now()
        self.last_updated = datetime.now()
        
        logger.info(f"Trained {self.name} exponential smoothing model with {len(data)} data points")
    
    def predict(
        self,
        periods: int,
        granularity: TimeGranularity,
        start_date: Optional[Union[str, datetime]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate predictions using exponential smoothing.
        
        Args:
            periods: Number of periods to forecast
            granularity: Time granularity for forecasting
            start_date: Start date for forecasting (defaults to last historical data point)
            
        Returns:
            List of predicted data points with timestamp and value
        """
        if self.level is None:
            raise ValueError("Model has not been trained with historical data")
        
        # Convert string date to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        
        # If no start date provided, use the last historical data point
        if start_date is None:
            last_timestamp = max(point["timestamp"] for point in self.historical_data)
            if isinstance(last_timestamp, str):
                last_timestamp = datetime.fromisoformat(last_timestamp)
            start_date = last_timestamp
        
        # Generate predictions
        predictions = []
        current_date = start_date
        
        for i in range(periods):
            # Calculate next date based on granularity
            if i > 0:  # Skip first iteration as we start from start_date
                if granularity == TimeGranularity.DAILY:
                    current_date += timedelta(days=1)
                elif granularity == TimeGranularity.WEEKLY:
                    current_date += timedelta(weeks=1)
                elif granularity == TimeGranularity.MONTHLY:
                    # Approximate a month as 30 days
                    current_date += timedelta(days=30)
                elif granularity == TimeGranularity.QUARTERLY:
                    # Approximate a quarter as 90 days
                    current_date += timedelta(days=90)
                elif granularity == TimeGranularity.YEARLY:
                    # Approximate a year as 365 days
                    current_date += timedelta(days=365)
            
            # Calculate prediction based on model type
            if self.gamma is not None:  # Triple exponential smoothing
                season_idx = i % self.seasonal_periods
                predicted_value = (self.level + i * self.trend) * self.seasonals[season_idx]
            elif self.beta is not None:  # Double exponential smoothing
                predicted_value = self.level + i * self.trend
            else:  # Simple exponential smoothing
                predicted_value = self.level
            
            # Add prediction
            predictions.append({
                "timestamp": current_date.isoformat(),
                "value": predicted_value,
                "confidence_interval": None  # Simple implementation doesn't provide confidence intervals
            })
        
        return predictions

class LinearRegressionModel(ForecastModel):
    """
    Linear Regression forecast model.
    
    Uses linear regression to predict future values based on time.
    """
    
    def __init__(
        self,
        name: str,
        include_seasonality: bool = False,
        seasonal_periods: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Linear Regression forecast model.
        
        Args:
            name: Name of the forecast model
            include_seasonality: Whether to include seasonal components
            seasonal_periods: Number of periods in a seasonal cycle, required if include_seasonality is True
            config: Additional configuration parameters
        """
        super().__init__(name, ForecastingMethod.LINEAR_REGRESSION, config or {})
        self.include_seasonality = include_seasonality
        self.seasonal_periods = seasonal_periods
        
        # Model parameters
        self.slope = None
        self.intercept = None
        self.seasonal_factors = None
        self.historical_data = []
        
        # Validate parameters
        if include_seasonality and seasonal_periods is None:
            raise ValueError("seasonal_periods must be provided when include_seasonality is True")
    
    def train(self, data: List[Dict[str, Any]]) -> None:
        """
        Train the linear regression model on historical data.
        
        Args:
            data: List of data points with timestamp and value
        """
        # Sort data by timestamp
        sorted_data = sorted(data, key=lambda x: x["timestamp"])
        
        # Store historical data
        self.historical_data = sorted_data
        
        # Extract values and convert timestamps to numeric values (days since first timestamp)
        values = [float(point["value"]) for point in sorted_data]
        
        # Convert timestamps to datetime objects if they are strings
        timestamps = []
        for point in sorted_data:
            ts = point["timestamp"]
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            timestamps.append(ts)
        
        # Convert timestamps to numeric values (days since first timestamp)
        first_timestamp = min(timestamps)
        x_values = [(ts - first_timestamp).days for ts in timestamps]
        
        if not values or not x_values:
            raise ValueError("No data provided for training")
        
        if self.include_seasonality:
            # Fit linear trend
            n = len(x_values)
            mean_x = sum(x_values) / n
            mean_y = sum(values) / n
            
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
            denominator = sum((x - mean_x) ** 2 for x in x_values)
            
            if denominator == 0:
                self.slope = 0
            else:
                self.slope = numerator / denominator
                
            self.intercept = mean_y - self.slope * mean_x
            
            # Calculate trend component for each point
            trend_values = [self.intercept + self.slope * x for x in x_values]
            
            # Calculate seasonal factors
            seasonal_deviations = [y - t for y, t in zip(values, trend_values)]
            
            # Group by season and average
            self.seasonal_factors = []
            for i in range(self.seasonal_periods):
                season_values = [seasonal_deviations[j] for j in range(i, n, self.seasonal_periods) if j < n]
                if season_values:
                    self.seasonal_factors.append(sum(season_values) / len(season_values))
                else:
                    self.seasonal_factors.append(0)
            
            # Normalize seasonal factors to sum to zero
            mean_factor = sum(self.seasonal_factors) / len(self.seasonal_factors)
            self.seasonal_factors = [f - mean_factor for f in self.seasonal_factors]
            
        else:
            # Simple linear regression
            n = len(x_values)
            mean_x = sum(x_values) / n
            mean_y = sum(values) / n
            
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
            denominator = sum((x - mean_x) ** 2 for x in x_values)
            
            if denominator == 0:
                self.slope = 0
            else:
                self.slope = numerator / denominator
                
            self.intercept = mean_y - self.slope * mean_x
        
        # Update model metadata
        self.last_trained = datetime.now()
        self.last_updated = datetime.now()
        
        logger.info(f"Trained {self.name} linear regression model with {len(data)} data points")
    
    def predict(
        self,
        periods: int,
        granularity: TimeGranularity,
        start_date: Optional[Union[str, datetime]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate predictions using linear regression.
        
        Args:
            periods: Number of periods to forecast
            granularity: Time granularity for forecasting
            start_date: Start date for forecasting (defaults to last historical data point)
            
        Returns:
            List of predicted data points with timestamp and value
        """
        if self.slope is None or self.intercept is None:
            raise ValueError("Model has not been trained with historical data")
        
        # Convert string date to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        
        # If no start date provided, use the last historical data point
        if start_date is None:
            last_timestamp = max(point["timestamp"] for point in self.historical_data)
            if isinstance(last_timestamp, str):
                last_timestamp = datetime.fromisoformat(last_timestamp)
            start_date = last_timestamp
        
        # Get first timestamp from historical data
        first_timestamp = min(
            datetime.fromisoformat(point["timestamp"]) if isinstance(point["timestamp"], str) else point["timestamp"]
            for point in self.historical_data
        )
        
        # Generate predictions
        predictions = []
        current_date = start_date
        
        for i in range(periods):
            # Calculate next date based on granularity
            if i > 0:  # Skip first iteration as we start from start_date
                if granularity == TimeGranularity.DAILY:
                    current_date += timedelta(days=1)
                elif granularity == TimeGranularity.WEEKLY:
                    current_date += timedelta(weeks=1)
                elif granularity == TimeGranularity.MONTHLY:
                    # Approximate a month as 30 days
                    current_date += timedelta(days=30)
                elif granularity == TimeGranularity.QUARTERLY:
                    # Approximate a quarter as 90 days
                    current_date += timedelta(days=90)
                elif granularity == TimeGranularity.YEARLY:
                    # Approximate a year as 365 days
                    current_date += timedelta(days=365)
            
            # Calculate days since first timestamp
            days_since_first = (current_date - first_timestamp).days
            
            # Calculate trend component
            trend = self.intercept + self.slope * days_since_first
            
            # Add seasonal component if applicable
            if self.include_seasonality and self.seasonal_factors:
                season_idx = i % self.seasonal_periods
                predicted_value = trend + self.seasonal_factors[season_idx]
            else:
                predicted_value = trend
            
            # Add prediction
            predictions.append({
                "timestamp": current_date.isoformat(),
                "value": predicted_value,
                "confidence_interval": None  # Simple implementation doesn't provide confidence intervals
            })
        
        return predictions
