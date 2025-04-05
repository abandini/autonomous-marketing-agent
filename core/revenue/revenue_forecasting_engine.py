"""
Revenue Forecasting Engine for the Autonomous Marketing Agent.

This module implements the Revenue Forecasting Engine component of the Revenue Optimization Framework,
predicting future revenue, modeling scenarios, and detecting seasonal patterns.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
import os
import uuid
import asyncio
from enum import Enum

# Import forecast models
from core.revenue.forecast_models import (
    ForecastModel, MovingAverageModel, ExponentialSmoothingModel, LinearRegressionModel,
    ForecastingMethod, ScenarioType, TimeGranularity
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RevenueForecastingEngine:
    """
    Engine for predicting future revenue, modeling scenarios, and detecting seasonal patterns.
    
    This engine is responsible for:
    - Generating time-series forecasts for revenue prediction
    - Modeling impact of various marketing scenarios
    - Detecting and forecasting seasonal trends
    - Providing channel-specific forecasting
    - Creating early warning systems for revenue shortfalls
    - Identifying revenue opportunity gaps
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        default_method: ForecastingMethod = ForecastingMethod.EXPONENTIAL_SMOOTHING,
        default_granularity: TimeGranularity = TimeGranularity.MONTHLY
    ):
        """
        Initialize the Revenue Forecasting Engine.
        
        Args:
            storage_path: Optional path to store forecasting data and models
            default_method: Default forecasting method to use
            default_granularity: Default time granularity for forecasting
        """
        self.storage_path = storage_path
        self.default_method = default_method
        self.default_granularity = default_granularity
        
        # Model registry
        self.models = {}  # Dictionary of forecast models by ID
        
        # Historical data
        self.historical_data = {}  # Dictionary of historical data by channel/segment
        
        # Forecasts
        self.forecasts = {}  # Dictionary of forecasts by ID
        
        # Scenarios
        self.scenarios = {}  # Dictionary of scenarios by ID
        
        # Early warnings
        self.warnings = {}  # Dictionary of warnings by ID
        
        # Create storage directory if it doesn't exist
        if storage_path and not os.path.exists(os.path.dirname(storage_path)):
            os.makedirs(os.path.dirname(storage_path))
        
        logger.info(f"Revenue Forecasting Engine initialized with {default_method.value} method")
    
    async def register_model(
        self,
        name: str,
        method: ForecastingMethod,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a new forecasting model.
        
        Args:
            name: Name of the forecast model
            method: Forecasting method to use
            config: Configuration parameters for the model
            
        Returns:
            Dict containing the model data
        """
        # Create model based on method
        if method == ForecastingMethod.MOVING_AVERAGE:
            window_size = config.get("window_size", 3) if config else 3
            model = MovingAverageModel(name=name, window_size=window_size, config=config)
            
        elif method == ForecastingMethod.EXPONENTIAL_SMOOTHING:
            alpha = config.get("alpha", 0.3) if config else 0.3
            beta = config.get("beta") if config else None
            gamma = config.get("gamma") if config else None
            seasonal_periods = config.get("seasonal_periods") if config else None
            
            model = ExponentialSmoothingModel(
                name=name,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
                seasonal_periods=seasonal_periods,
                config=config
            )
            
        elif method == ForecastingMethod.LINEAR_REGRESSION:
            include_seasonality = config.get("include_seasonality", False) if config else False
            seasonal_periods = config.get("seasonal_periods") if config else None
            
            model = LinearRegressionModel(
                name=name,
                include_seasonality=include_seasonality,
                seasonal_periods=seasonal_periods,
                config=config
            )
            
        else:
            raise ValueError(f"Unsupported forecasting method: {method.value}")
        
        # Register model
        self.models[model.id] = model
        
        # Save data
        self._save_data()
        
        logger.info(f"Registered {method.value} forecast model: {name}")
        return model.to_dict()
    
    async def load_historical_data(
        self,
        data: List[Dict[str, Any]],
        channel: Optional[str] = None,
        segment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load historical revenue data.
        
        Args:
            data: List of data points with timestamp and value
            channel: Optional channel name for segmentation
            segment: Optional segment name for segmentation
            
        Returns:
            Dict containing information about the loaded data
        """
        # Create key for this data set
        key = f"{channel or 'all'}:{segment or 'all'}"
        
        # Validate data
        validated_data = []
        for point in data:
            if "timestamp" not in point or "value" not in point:
                logger.warning(f"Skipping invalid data point: {point}")
                continue
                
            # Ensure timestamp is in ISO format
            if isinstance(point["timestamp"], datetime):
                point["timestamp"] = point["timestamp"].isoformat()
                
            # Ensure value is numeric
            try:
                point["value"] = float(point["value"])
                validated_data.append(point)
            except (ValueError, TypeError):
                logger.warning(f"Skipping non-numeric value: {point}")
        
        # Store data
        self.historical_data[key] = validated_data
        
        # Save data
        self._save_data()
        
        logger.info(f"Loaded {len(validated_data)} historical data points for {key}")
        return {
            "key": key,
            "points": len(validated_data),
            "date_range": {
                "start": min(point["timestamp"] for point in validated_data) if validated_data else None,
                "end": max(point["timestamp"] for point in validated_data) if validated_data else None
            }
        }
    
    async def train_models(
        self,
        model_ids: Optional[List[str]] = None,
        channel: Optional[str] = None,
        segment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Train forecast models on historical data.
        
        Args:
            model_ids: Optional list of model IDs to train (defaults to all)
            channel: Optional channel name for data selection
            segment: Optional segment name for data selection
            
        Returns:
            Dict containing training results
        """
        # Get data key
        key = f"{channel or 'all'}:{segment or 'all'}"
        
        # Check if data exists
        if key not in self.historical_data or not self.historical_data[key]:
            return {
                "status": "error",
                "message": f"No historical data found for {key}"
            }
        
        # Get models to train
        models_to_train = []
        if model_ids:
            for model_id in model_ids:
                if model_id in self.models:
                    models_to_train.append(self.models[model_id])
                else:
                    logger.warning(f"Model not found: {model_id}")
        else:
            models_to_train = list(self.models.values())
        
        if not models_to_train:
            return {
                "status": "error",
                "message": "No models to train"
            }
        
        # Train models
        results = {}
        for model in models_to_train:
            try:
                model.train(self.historical_data[key])
                results[model.id] = {
                    "status": "success",
                    "name": model.name,
                    "method": model.method.value
                }
            except Exception as e:
                logger.error(f"Error training model {model.name}: {e}")
                results[model.id] = {
                    "status": "error",
                    "name": model.name,
                    "method": model.method.value,
                    "error": str(e)
                }
        
        # Save data
        self._save_data()
        
        logger.info(f"Trained {len(models_to_train)} models on {key} data")
        return {
            "status": "success",
            "data_key": key,
            "data_points": len(self.historical_data[key]),
            "models_trained": len(models_to_train),
            "results": results
        }
    
    async def predict_revenue(
        self,
        periods: int,
        model_id: Optional[str] = None,
        granularity: Optional[TimeGranularity] = None,
        start_date: Optional[Union[str, datetime]] = None,
        channel: Optional[str] = None,
        segment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate revenue predictions.
        
        Args:
            periods: Number of periods to forecast
            model_id: ID of the model to use (defaults to best performing model)
            granularity: Time granularity for forecasting
            start_date: Start date for forecasting (defaults to last historical data point)
            channel: Optional channel name for data selection
            segment: Optional segment name for data selection
            
        Returns:
            Dict containing forecast data
        """
        # Use default granularity if not specified
        if granularity is None:
            granularity = self.default_granularity
        
        # Get data key
        key = f"{channel or 'all'}:{segment or 'all'}"
        
        # Check if data exists
        if key not in self.historical_data or not self.historical_data[key]:
            return {
                "status": "error",
                "message": f"No historical data found for {key}"
            }
        
        # Get model to use
        model = None
        if model_id:
            if model_id in self.models:
                model = self.models[model_id]
            else:
                return {
                    "status": "error",
                    "message": f"Model not found: {model_id}"
                }
        else:
            # Use default model or create one if none exists
            if self.models:
                # Use first model (in a real implementation, would select best model)
                model = next(iter(self.models.values()))
            else:
                # Create default model
                model_name = f"Default {self.default_method.value} Model"
                if self.default_method == ForecastingMethod.MOVING_AVERAGE:
                    model = MovingAverageModel(name=model_name)
                elif self.default_method == ForecastingMethod.EXPONENTIAL_SMOOTHING:
                    model = ExponentialSmoothingModel(name=model_name)
                elif self.default_method == ForecastingMethod.LINEAR_REGRESSION:
                    model = LinearRegressionModel(name=model_name)
                else:
                    return {
                        "status": "error",
                        "message": f"Unsupported default forecasting method: {self.default_method.value}"
                    }
                
                # Register model
                self.models[model.id] = model
                
                # Train model
                model.train(self.historical_data[key])
        
        # Generate predictions
        try:
            predictions = model.predict(
                periods=periods,
                granularity=granularity,
                start_date=start_date
            )
        except Exception as e:
            logger.error(f"Error generating predictions with model {model.name}: {e}")
            return {
                "status": "error",
                "message": f"Error generating predictions: {e}"
            }
        
        # Create forecast
        forecast_id = str(uuid.uuid4())
        forecast = {
            "id": forecast_id,
            "timestamp": datetime.now().isoformat(),
            "model": {
                "id": model.id,
                "name": model.name,
                "method": model.method.value
            },
            "parameters": {
                "periods": periods,
                "granularity": granularity.value,
                "start_date": start_date.isoformat() if isinstance(start_date, datetime) else start_date,
                "channel": channel,
                "segment": segment
            },
            "predictions": predictions,
            "metadata": {
                "data_key": key,
                "data_points": len(self.historical_data[key])
            }
        }
        
        # Store forecast
        self.forecasts[forecast_id] = forecast
        
        # Save data
        self._save_data()
        
        logger.info(f"Generated {periods} {granularity.value} revenue predictions using {model.name}")
        return forecast
    
    async def create_scenario(
        self,
        name: str,
        scenario_type: ScenarioType,
        base_forecast_id: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a revenue scenario based on a forecast.
        
        Args:
            name: Name of the scenario
            scenario_type: Type of scenario
            base_forecast_id: ID of the base forecast to modify
            parameters: Parameters for scenario modification
            
        Returns:
            Dict containing scenario data
        """
        # Check if base forecast exists
        if base_forecast_id not in self.forecasts:
            return {
                "status": "error",
                "message": f"Base forecast not found: {base_forecast_id}"
            }
        
        base_forecast = self.forecasts[base_forecast_id]
        
        # Create modified predictions based on scenario type and parameters
        modified_predictions = []
        
        if scenario_type == ScenarioType.BASELINE:
            # Baseline scenario is just the original forecast
            modified_predictions = base_forecast["predictions"]
            
        elif scenario_type == ScenarioType.OPTIMISTIC:
            # Optimistic scenario increases values by a percentage
            growth_factor = parameters.get("growth_factor", 1.1)  # Default: 10% growth
            
            for prediction in base_forecast["predictions"]:
                modified_predictions.append({
                    "timestamp": prediction["timestamp"],
                    "value": prediction["value"] * growth_factor,
                    "confidence_interval": prediction.get("confidence_interval")
                })
                
        elif scenario_type == ScenarioType.PESSIMISTIC:
            # Pessimistic scenario decreases values by a percentage
            decline_factor = parameters.get("decline_factor", 0.9)  # Default: 10% decline
            
            for prediction in base_forecast["predictions"]:
                modified_predictions.append({
                    "timestamp": prediction["timestamp"],
                    "value": prediction["value"] * decline_factor,
                    "confidence_interval": prediction.get("confidence_interval")
                })
                
        elif scenario_type == ScenarioType.SEASONAL:
            # Seasonal scenario adds seasonal factors
            seasonal_factors = parameters.get("seasonal_factors", [])
            
            if not seasonal_factors:
                return {
                    "status": "error",
                    "message": "Seasonal factors not provided for seasonal scenario"
                }
                
            for i, prediction in enumerate(base_forecast["predictions"]):
                season_idx = i % len(seasonal_factors)
                modified_predictions.append({
                    "timestamp": prediction["timestamp"],
                    "value": prediction["value"] * seasonal_factors[season_idx],
                    "confidence_interval": prediction.get("confidence_interval")
                })
                
        elif scenario_type == ScenarioType.CAMPAIGN:
            # Campaign scenario adds campaign impact
            campaign_start = parameters.get("campaign_start", 0)  # Index of start period
            campaign_duration = parameters.get("campaign_duration", 3)  # Number of periods
            campaign_impact = parameters.get("campaign_impact", 1.2)  # Impact factor
            
            for i, prediction in enumerate(base_forecast["predictions"]):
                if i >= campaign_start and i < campaign_start + campaign_duration:
                    # Apply campaign impact
                    modified_predictions.append({
                        "timestamp": prediction["timestamp"],
                        "value": prediction["value"] * campaign_impact,
                        "confidence_interval": prediction.get("confidence_interval")
                    })
                else:
                    # No change
                    modified_predictions.append(prediction)
                    
        elif scenario_type == ScenarioType.MARKET_SHIFT:
            # Market shift scenario applies a permanent shift after a certain point
            shift_start = parameters.get("shift_start", 0)  # Index of start period
            shift_factor = parameters.get("shift_factor", 1.15)  # Shift factor
            
            for i, prediction in enumerate(base_forecast["predictions"]):
                if i >= shift_start:
                    # Apply market shift
                    modified_predictions.append({
                        "timestamp": prediction["timestamp"],
                        "value": prediction["value"] * shift_factor,
                        "confidence_interval": prediction.get("confidence_interval")
                    })
                else:
                    # No change
                    modified_predictions.append(prediction)
                    
        elif scenario_type == ScenarioType.COMPETITOR_ACTION:
            # Competitor action scenario applies a temporary impact
            action_start = parameters.get("action_start", 0)  # Index of start period
            action_duration = parameters.get("action_duration", 3)  # Number of periods
            action_impact = parameters.get("action_impact", 0.9)  # Impact factor
            recovery_rate = parameters.get("recovery_rate", 0.05)  # Recovery per period
            
            for i, prediction in enumerate(base_forecast["predictions"]):
                if i >= action_start and i < action_start + action_duration:
                    # Full competitor impact
                    impact_factor = action_impact
                elif i >= action_start + action_duration:
                    # Gradual recovery
                    periods_since_end = i - (action_start + action_duration)
                    recovery_amount = periods_since_end * recovery_rate
                    impact_factor = min(1.0, action_impact + recovery_amount)
                else:
                    # No change
                    impact_factor = 1.0
                    
                modified_predictions.append({
                    "timestamp": prediction["timestamp"],
                    "value": prediction["value"] * impact_factor,
                    "confidence_interval": prediction.get("confidence_interval")
                })
                
        elif scenario_type == ScenarioType.CUSTOM:
            # Custom scenario applies user-defined modifications
            modifications = parameters.get("modifications", [])
            
            if not modifications:
                return {
                    "status": "error",
                    "message": "Modifications not provided for custom scenario"
                }
                
            for i, prediction in enumerate(base_forecast["predictions"]):
                if i < len(modifications):
                    modified_predictions.append({
                        "timestamp": prediction["timestamp"],
                        "value": prediction["value"] * modifications[i],
                        "confidence_interval": prediction.get("confidence_interval")
                    })
                else:
                    modified_predictions.append(prediction)
        
        else:
            return {
                "status": "error",
                "message": f"Unsupported scenario type: {scenario_type.value}"
            }
        
        # Create scenario
        scenario_id = str(uuid.uuid4())
        scenario = {
            "id": scenario_id,
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "type": scenario_type.value,
            "base_forecast_id": base_forecast_id,
            "parameters": parameters,
            "predictions": modified_predictions,
            "metadata": {
                "model": base_forecast["model"],
                "original_parameters": base_forecast["parameters"]
            }
        }
        
        # Store scenario
        self.scenarios[scenario_id] = scenario
        
        # Save data
        self._save_data()
        
        logger.info(f"Created {scenario_type.value} scenario: {name}")
        return scenario
