"""
Revenue Attribution Agent Implementation for the Autonomous Marketing Agent.

This module implements the main RevenueAttributionAgent class that uses the data models
defined in revenue_attribution_agent.py.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import os
import uuid
import asyncio
from enum import Enum

# Import models from the base file
from core.revenue.revenue_attribution_agent import (
    AttributionModel, TouchPoint, CustomerJourney
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RevenueAttributionAgent:
    """
    Agent for tracking multi-touch attribution across marketing channels.
    
    This agent is responsible for:
    - Tracking multi-touch attribution across marketing channels
    - Assigning revenue value to each customer touchpoint
    - Calculating customer acquisition cost by channel
    - Determining lifetime value projections for customer segments
    - Providing revenue impact analysis for all marketing activities
    - Identifying highest-ROI tactics and channels for resource allocation
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        default_attribution_model: AttributionModel = AttributionModel.DATA_DRIVEN
    ):
        """
        Initialize the Revenue Attribution Agent.
        
        Args:
            storage_path: Optional path to store attribution data
            default_attribution_model: Default attribution model to use
        """
        self.journeys = {}  # Dictionary of customer journeys by ID
        self.storage_path = storage_path
        self.default_attribution_model = default_attribution_model
        self.channel_metrics = {}  # Metrics by channel
        self.campaign_metrics = {}  # Metrics by campaign
        self.content_metrics = {}  # Metrics by content
        
        # Create storage directory if it doesn't exist
        if storage_path and not os.path.exists(os.path.dirname(storage_path)):
            os.makedirs(os.path.dirname(storage_path))
        
        logger.info(f"Revenue Attribution Agent initialized with {default_attribution_model.value} model")
    
    async def record_touchpoint(
        self,
        customer_id: str,
        channel: str,
        campaign: Optional[str] = None,
        content: Optional[str] = None,
        interaction_type: Optional[str] = None,
        cost: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a customer touchpoint.
        
        Args:
            customer_id: Unique identifier for the customer
            channel: Marketing channel
            campaign: Optional campaign name
            content: Optional content identifier
            interaction_type: Type of interaction
            cost: Cost associated with this touchpoint
            metadata: Additional data about the touchpoint
            
        Returns:
            Dict containing the touchpoint data
        """
        # Create touchpoint
        touchpoint = TouchPoint(
            channel=channel,
            campaign=campaign,
            content=content,
            interaction_type=interaction_type,
            cost=cost,
            metadata=metadata
        )
        
        # Get or create customer journey
        journey = self._get_or_create_journey(customer_id)
        
        # Add touchpoint to journey
        journey.add_touchpoint(touchpoint)
        
        # Save data
        self._save_data()
        
        logger.info(f"Recorded touchpoint for customer {customer_id} on channel {channel}")
        return touchpoint.to_dict()
    
    async def record_conversion(
        self,
        customer_id: str,
        value: float,
        date: Optional[Union[str, datetime]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a conversion for a customer.
        
        Args:
            customer_id: Unique identifier for the customer
            value: Conversion value
            date: Conversion date (defaults to now)
            metadata: Additional data about the conversion
            
        Returns:
            Dict containing the updated journey data
        """
        # Get or create customer journey
        journey = self._get_or_create_journey(customer_id)
        
        # Set conversion
        journey.set_conversion(value, date)
        
        # Update journey metadata
        if metadata:
            journey.metadata.update(metadata)
        
        # Attribute revenue to touchpoints
        await self._attribute_revenue(journey)
        
        # Save data
        self._save_data()
        
        logger.info(f"Recorded conversion of ${value} for customer {customer_id}")
        return journey.to_dict()
    
    async def get_customer_journey(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a customer's journey.
        
        Args:
            customer_id: Unique identifier for the customer
            
        Returns:
            Dict containing the journey data or None if not found
        """
        # Check if journey exists
        for journey_id, journey in self.journeys.items():
            if journey.customer_id == customer_id:
                return journey.to_dict()
        
        return None
    
    async def get_channel_metrics(
        self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get metrics by channel.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Dict containing metrics by channel
        """
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        
        # Initialize metrics
        metrics = {}
        
        # Process all journeys
        for journey in self.journeys.values():
            # Filter by date if specified
            if start_date and journey.conversion_date and journey.conversion_date < start_date:
                continue
            if end_date and journey.conversion_date and journey.conversion_date > end_date:
                continue
            
            # Process touchpoints
            for touchpoint in journey.touchpoints:
                # Filter by date if specified
                if start_date and touchpoint.timestamp < start_date:
                    continue
                if end_date and touchpoint.timestamp > end_date:
                    continue
                
                # Initialize channel metrics if needed
                if touchpoint.channel not in metrics:
                    metrics[touchpoint.channel] = {
                        "touchpoints": 0,
                        "cost": 0.0,
                        "revenue_contribution": 0.0,
                        "conversions": 0,
                        "conversion_rate": 0.0,
                        "roi": 0.0,
                        "cac": 0.0
                    }
                
                # Update metrics
                metrics[touchpoint.channel]["touchpoints"] += 1
                metrics[touchpoint.channel]["cost"] += touchpoint.cost
                metrics[touchpoint.channel]["revenue_contribution"] += touchpoint.revenue_contribution
                
                # Count conversions (only once per journey)
                if journey.conversion_date and touchpoint == journey.touchpoints[-1]:
                    metrics[touchpoint.channel]["conversions"] += 1
        
        # Calculate derived metrics
        for channel, channel_metrics in metrics.items():
            # Calculate conversion rate
            if channel_metrics["touchpoints"] > 0:
                channel_metrics["conversion_rate"] = (
                    channel_metrics["conversions"] / channel_metrics["touchpoints"] * 100
                )
            
            # Calculate ROI
            if channel_metrics["cost"] > 0:
                channel_metrics["roi"] = (
                    (channel_metrics["revenue_contribution"] - channel_metrics["cost"]) / 
                    channel_metrics["cost"] * 100
                )
            
            # Calculate CAC
            if channel_metrics["conversions"] > 0:
                channel_metrics["cac"] = channel_metrics["cost"] / channel_metrics["conversions"]
        
        return metrics
    
    async def get_campaign_metrics(
        self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get metrics by campaign.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Dict containing metrics by campaign
        """
        # Similar implementation to get_channel_metrics but grouped by campaign
        # This is a simplified version for brevity
        metrics = {}
        
        # Process all journeys with campaign information
        for journey in self.journeys.values():
            for touchpoint in journey.touchpoints:
                if not touchpoint.campaign:
                    continue
                    
                # Filter by date if specified
                if start_date and isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date)
                if end_date and isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date)
                    
                if start_date and touchpoint.timestamp < start_date:
                    continue
                if end_date and touchpoint.timestamp > end_date:
                    continue
                
                # Initialize campaign metrics if needed
                if touchpoint.campaign not in metrics:
                    metrics[touchpoint.campaign] = {
                        "touchpoints": 0,
                        "cost": 0.0,
                        "revenue_contribution": 0.0,
                        "conversions": 0,
                        "channels": set()
                    }
                
                # Update metrics
                metrics[touchpoint.campaign]["touchpoints"] += 1
                metrics[touchpoint.campaign]["cost"] += touchpoint.cost
                metrics[touchpoint.campaign]["revenue_contribution"] += touchpoint.revenue_contribution
                metrics[touchpoint.campaign]["channels"].add(touchpoint.channel)
                
                # Count conversions (only once per journey)
                if journey.conversion_date and touchpoint == journey.touchpoints[-1]:
                    metrics[touchpoint.campaign]["conversions"] += 1
        
        # Convert sets to lists for JSON serialization
        for campaign, campaign_metrics in metrics.items():
            campaign_metrics["channels"] = list(campaign_metrics["channels"])
            
            # Calculate derived metrics
            if campaign_metrics["touchpoints"] > 0:
                campaign_metrics["conversion_rate"] = (
                    campaign_metrics["conversions"] / campaign_metrics["touchpoints"] * 100
                )
            else:
                campaign_metrics["conversion_rate"] = 0
                
            if campaign_metrics["cost"] > 0:
                campaign_metrics["roi"] = (
                    (campaign_metrics["revenue_contribution"] - campaign_metrics["cost"]) / 
                    campaign_metrics["cost"] * 100
                )
            else:
                campaign_metrics["roi"] = 0
                
            if campaign_metrics["conversions"] > 0:
                campaign_metrics["cac"] = campaign_metrics["cost"] / campaign_metrics["conversions"]
            else:
                campaign_metrics["cac"] = 0
        
        return metrics
    
    async def calculate_customer_ltv(
        self,
        customer_id: str,
        prediction_months: int = 12
    ) -> Dict[str, Any]:
        """
        Calculate lifetime value projection for a customer.
        
        Args:
            customer_id: Unique identifier for the customer
            prediction_months: Number of months to project
            
        Returns:
            Dict containing LTV projection data
        """
        # Get customer journey
        journey_data = await self.get_customer_journey(customer_id)
        if not journey_data:
            return {
                "status": "error",
                "message": f"Customer {customer_id} not found"
            }
        
        # Calculate basic LTV based on conversion value
        # In a real implementation, this would use more sophisticated models
        conversion_value = journey_data["conversion_value"]
        
        # Simple LTV model: conversion value * estimated repeat purchases
        # This is a very simplified model for demonstration purposes
        estimated_repeat_rate = 0.3  # 30% chance of repeat purchase
        estimated_churn_rate = 0.1   # 10% monthly churn
        
        monthly_value = conversion_value * estimated_repeat_rate
        ltv = conversion_value  # Initial conversion
        
        # Calculate cumulative LTV over prediction months
        monthly_values = [conversion_value]  # First month is the initial conversion
        remaining_customers = 1.0  # Start with 100% of customers
        
        for month in range(1, prediction_months):
            remaining_customers *= (1 - estimated_churn_rate)  # Apply churn
            month_value = monthly_value * remaining_customers
            ltv += month_value
            monthly_values.append(month_value)
        
        return {
            "status": "success",
            "customer_id": customer_id,
            "initial_conversion_value": conversion_value,
            "ltv_projection": ltv,
            "prediction_months": prediction_months,
            "monthly_values": monthly_values,
            "model_parameters": {
                "estimated_repeat_rate": estimated_repeat_rate,
                "estimated_churn_rate": estimated_churn_rate
            }
        }
    
    async def identify_high_roi_channels(self) -> Dict[str, Any]:
        """
        Identify channels with the highest ROI.
        
        Returns:
            Dict containing high-ROI channel data
        """
        # Get channel metrics
        channel_metrics = await self.get_channel_metrics()
        
        # Sort channels by ROI
        sorted_channels = sorted(
            channel_metrics.items(),
            key=lambda x: x[1]["roi"],
            reverse=True
        )
        
        # Format results
        results = {
            "high_roi_channels": [
                {
                    "channel": channel,
                    "roi": metrics["roi"],
                    "revenue_contribution": metrics["revenue_contribution"],
                    "cost": metrics["cost"],
                    "conversion_rate": metrics["conversion_rate"]
                }
                for channel, metrics in sorted_channels
                if metrics["roi"] > 0  # Only include positive ROI channels
            ],
            "low_roi_channels": [
                {
                    "channel": channel,
                    "roi": metrics["roi"],
                    "revenue_contribution": metrics["revenue_contribution"],
                    "cost": metrics["cost"],
                    "conversion_rate": metrics["conversion_rate"]
                }
                for channel, metrics in sorted_channels
                if metrics["roi"] <= 0  # Only include negative or zero ROI channels
            ]
        }
        
        # Add recommendations
        results["recommendations"] = []
        
        # Recommend increasing investment in high-ROI channels
        if results["high_roi_channels"]:
            for channel_data in results["high_roi_channels"][:3]:  # Top 3 channels
                results["recommendations"].append({
                    "action": "increase_investment",
                    "channel": channel_data["channel"],
                    "reason": f"High ROI of {channel_data['roi']:.2f}%",
                    "potential_impact": "Increase revenue while maintaining efficiency"
                })
        
        # Recommend optimizing or reducing investment in low-ROI channels
        if results["low_roi_channels"]:
            for channel_data in results["low_roi_channels"]:
                if channel_data["conversion_rate"] > 0:
                    results["recommendations"].append({
                        "action": "optimize",
                        "channel": channel_data["channel"],
                        "reason": f"Low ROI of {channel_data['roi']:.2f}% despite conversions",
                        "potential_impact": "Improve efficiency and ROI"
                    })
                else:
                    results["recommendations"].append({
                        "action": "reduce_investment",
                        "channel": channel_data["channel"],
                        "reason": f"Negative ROI of {channel_data['roi']:.2f}% with no conversions",
                        "potential_impact": "Reduce waste and reallocate budget"
                    })
        
        return results
    
    async def generate_attribution_report(
        self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None,
        attribution_model: Optional[AttributionModel] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive attribution report.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            attribution_model: Attribution model to use (defaults to agent's default model)
            
        Returns:
            Dict containing the attribution report
        """
        # Use specified attribution model or default
        model = attribution_model or self.default_attribution_model
        
        # Get metrics
        channel_metrics = await self.get_channel_metrics(start_date, end_date)
        campaign_metrics = await self.get_campaign_metrics(start_date, end_date)
        
        # Calculate total metrics
        total_revenue = sum(metrics["revenue_contribution"] for metrics in channel_metrics.values())
        total_cost = sum(metrics["cost"] for metrics in channel_metrics.values())
        total_conversions = sum(metrics["conversions"] for metrics in channel_metrics.values())
        
        # Calculate overall ROI
        overall_roi = 0
        if total_cost > 0:
            overall_roi = (total_revenue - total_cost) / total_cost * 100
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "date_range": {
                "start_date": start_date.isoformat() if isinstance(start_date, datetime) else start_date,
                "end_date": end_date.isoformat() if isinstance(end_date, datetime) else end_date
            },
            "attribution_model": model.value,
            "summary": {
                "total_revenue": total_revenue,
                "total_cost": total_cost,
                "total_conversions": total_conversions,
                "overall_roi": overall_roi
            },
            "channel_attribution": channel_metrics,
            "campaign_attribution": campaign_metrics,
            "customer_journeys": {
                journey.customer_id: {
                    "touchpoints": len(journey.touchpoints),
                    "channels_used": list(set(tp.channel for tp in journey.touchpoints)),
                    "conversion_value": journey.conversion_value,
                    "journey_duration_days": journey.get_journey_duration().days if journey.get_journey_duration() else None
                }
                for journey in self.journeys.values()
                if journey.conversion_date  # Only include converted journeys
            }
        }
        
        # Add recommendations
        high_roi_channels = await self.identify_high_roi_channels()
        report["recommendations"] = high_roi_channels["recommendations"]
        
        return report
    
    def _get_or_create_journey(self, customer_id: str) -> CustomerJourney:
        """
        Get an existing customer journey or create a new one.
        
        Args:
            customer_id: Unique identifier for the customer
            
        Returns:
            CustomerJourney instance
        """
        # Check if journey exists
        for journey in self.journeys.values():
            if journey.customer_id == customer_id:
                return journey
        
        # Create new journey
        journey = CustomerJourney(customer_id=customer_id)
        self.journeys[journey.id] = journey
        return journey
    
    async def _attribute_revenue(self, journey: CustomerJourney) -> None:
        """
        Attribute revenue to touchpoints based on the attribution model.
        
        Args:
            journey: CustomerJourney to attribute revenue for
        """
        if not journey.touchpoints or journey.conversion_value <= 0:
            return
        
        # Apply attribution model
        if self.default_attribution_model == AttributionModel.FIRST_TOUCH:
            # First touch gets 100% credit
            journey.touchpoints[0].revenue_contribution = journey.conversion_value
            
        elif self.default_attribution_model == AttributionModel.LAST_TOUCH:
            # Last touch gets 100% credit
            journey.touchpoints[-1].revenue_contribution = journey.conversion_value
            
        elif self.default_attribution_model == AttributionModel.LINEAR:
            # Equal distribution across all touchpoints
            per_touchpoint = journey.conversion_value / len(journey.touchpoints)
            for touchpoint in journey.touchpoints:
                touchpoint.revenue_contribution = per_touchpoint
                
        elif self.default_attribution_model == AttributionModel.TIME_DECAY:
            # More recent touchpoints get more credit
            # Simple implementation: credit increases linearly with recency
            total_weight = sum(range(1, len(journey.touchpoints) + 1))
            for i, touchpoint in enumerate(journey.touchpoints):
                weight = i + 1  # 1-based index
                touchpoint.revenue_contribution = (weight / total_weight) * journey.conversion_value
                
        elif self.default_attribution_model == AttributionModel.POSITION_BASED:
            # First and last touchpoints get 40% each, others share 20%
            if len(journey.touchpoints) == 1:
                journey.touchpoints[0].revenue_contribution = journey.conversion_value
            else:
                journey.touchpoints[0].revenue_contribution = 0.4 * journey.conversion_value
                journey.touchpoints[-1].revenue_contribution = 0.4 * journey.conversion_value
                
                if len(journey.touchpoints) > 2:
                    middle_share = 0.2 * journey.conversion_value
                    per_middle = middle_share / (len(journey.touchpoints) - 2)
                    for i in range(1, len(journey.touchpoints) - 1):
                        journey.touchpoints[i].revenue_contribution = per_middle
                        
        elif self.default_attribution_model == AttributionModel.DATA_DRIVEN:
            # In a real implementation, this would use machine learning models
            # For this example, we'll use a simplified heuristic based on interaction type
            total_weight = 0
            weights = []
            
            for touchpoint in journey.touchpoints:
                weight = 1.0  # Default weight
                
                # Adjust weight based on interaction type
                if touchpoint.interaction_type == "view":
                    weight = 0.5
                elif touchpoint.interaction_type == "click":
                    weight = 1.0
                elif touchpoint.interaction_type == "engagement":
                    weight = 2.0
                elif touchpoint.interaction_type == "add_to_cart":
                    weight = 3.0
                
                weights.append(weight)
                total_weight += weight
            
            # Attribute revenue based on weights
            if total_weight > 0:
                for i, touchpoint in enumerate(journey.touchpoints):
                    touchpoint.revenue_contribution = (weights[i] / total_weight) * journey.conversion_value
            else:
                # Fallback to linear if no weights
                per_touchpoint = journey.conversion_value / len(journey.touchpoints)
                for touchpoint in journey.touchpoints:
                    touchpoint.revenue_contribution = per_touchpoint
        
        else:  # Custom or unknown model
            # Fallback to linear attribution
            per_touchpoint = journey.conversion_value / len(journey.touchpoints)
            for touchpoint in journey.touchpoints:
                touchpoint.revenue_contribution = per_touchpoint
    
    def _save_data(self) -> None:
        """Save attribution data to storage if a storage path is configured."""
        if not self.storage_path:
            return
            
        try:
            data = {
                "journeys": {
                    journey_id: journey.to_dict()
                    for journey_id, journey in self.journeys.items()
                },
                "attribution_model": self.default_attribution_model.value
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved attribution data to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving attribution data: {e}")
    
    def load_data(self) -> bool:
        """
        Load attribution data from storage.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.storage_path:
            logger.warning("No storage path configured, cannot load attribution data")
            return False
            
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            # Load journeys
            self.journeys = {
                journey_id: CustomerJourney.from_dict(journey_data)
                for journey_id, journey_data in data["journeys"].items()
            }
            
            # Load attribution model
            if "attribution_model" in data:
                self.default_attribution_model = AttributionModel(data["attribution_model"])
                
            logger.info(f"Loaded {len(self.journeys)} customer journeys from {self.storage_path}")
            return True
        except FileNotFoundError:
            logger.warning(f"Attribution data file not found: {self.storage_path}")
            return False
        except Exception as e:
            logger.error(f"Error loading attribution data: {e}")
            return False
