"""
Revenue Attribution Agent for the Autonomous Marketing Agent.

This module implements the Revenue Attribution Agent component of the Revenue Optimization Framework,
tracking multi-touch attribution across marketing channels and providing revenue impact analysis.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AttributionModel(Enum):
    """Enumeration of attribution model types."""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"
    CUSTOM = "custom"

class TouchPoint:
    """
    Represents a customer touchpoint in the marketing journey.
    """
    
    def __init__(
        self,
        channel: str,
        campaign: Optional[str] = None,
        content: Optional[str] = None,
        timestamp: Optional[Union[str, datetime]] = None,
        interaction_type: Optional[str] = None,
        revenue_contribution: float = 0.0,
        cost: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a touchpoint.
        
        Args:
            channel: Marketing channel (e.g., 'email', 'social', 'search')
            campaign: Optional campaign name
            content: Optional content identifier
            timestamp: When the touchpoint occurred
            interaction_type: Type of interaction (e.g., 'click', 'view', 'conversion')
            revenue_contribution: Attributed revenue contribution
            cost: Cost associated with this touchpoint
            metadata: Additional data about the touchpoint
        """
        self.id = str(uuid.uuid4())
        self.channel = channel
        self.campaign = campaign
        self.content = content
        self.interaction_type = interaction_type
        self.revenue_contribution = float(revenue_contribution)
        self.cost = float(cost)
        self.metadata = metadata or {}
        
        # Set timestamp
        if timestamp is None:
            self.timestamp = datetime.now()
        elif isinstance(timestamp, str):
            self.timestamp = datetime.fromisoformat(timestamp)
        else:
            self.timestamp = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the touchpoint to a dictionary for serialization.
        
        Returns:
            Dict containing all touchpoint data
        """
        return {
            "id": self.id,
            "channel": self.channel,
            "campaign": self.campaign,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "interaction_type": self.interaction_type,
            "revenue_contribution": self.revenue_contribution,
            "cost": self.cost,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TouchPoint':
        """
        Create a TouchPoint instance from a dictionary.
        
        Args:
            data: Dictionary containing touchpoint data
            
        Returns:
            TouchPoint instance
        """
        touchpoint = cls(
            channel=data["channel"],
            campaign=data.get("campaign"),
            content=data.get("content"),
            timestamp=data["timestamp"],
            interaction_type=data.get("interaction_type"),
            revenue_contribution=data.get("revenue_contribution", 0.0),
            cost=data.get("cost", 0.0),
            metadata=data.get("metadata", {})
        )
        
        # Restore ID
        touchpoint.id = data["id"]
        
        return touchpoint

class CustomerJourney:
    """
    Represents a customer's journey through multiple touchpoints.
    """
    
    def __init__(
        self,
        customer_id: str,
        touchpoints: Optional[List[TouchPoint]] = None,
        conversion_value: float = 0.0,
        conversion_date: Optional[Union[str, datetime]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a customer journey.
        
        Args:
            customer_id: Unique identifier for the customer
            touchpoints: List of touchpoints in the journey
            conversion_value: Total value of the conversion
            conversion_date: When the conversion occurred
            metadata: Additional data about the customer or journey
        """
        self.id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.touchpoints = touchpoints or []
        self.conversion_value = float(conversion_value)
        self.metadata = metadata or {}
        self.creation_date = datetime.now()
        self.last_updated = datetime.now()
        
        # Set conversion date
        if conversion_date is None:
            self.conversion_date = None
        elif isinstance(conversion_date, str):
            self.conversion_date = datetime.fromisoformat(conversion_date)
        else:
            self.conversion_date = conversion_date
    
    def add_touchpoint(self, touchpoint: TouchPoint) -> None:
        """
        Add a touchpoint to the journey.
        
        Args:
            touchpoint: Touchpoint to add
        """
        self.touchpoints.append(touchpoint)
        self.touchpoints.sort(key=lambda tp: tp.timestamp)
        self.last_updated = datetime.now()
    
    def set_conversion(self, value: float, date: Optional[Union[str, datetime]] = None) -> None:
        """
        Set the conversion value and date.
        
        Args:
            value: Conversion value
            date: Conversion date (defaults to now)
        """
        self.conversion_value = float(value)
        
        if date is None:
            self.conversion_date = datetime.now()
        elif isinstance(date, str):
            self.conversion_date = datetime.fromisoformat(date)
        else:
            self.conversion_date = date
            
        self.last_updated = datetime.now()
    
    def get_journey_duration(self) -> Optional[timedelta]:
        """
        Get the duration of the customer journey.
        
        Returns:
            Duration from first touchpoint to conversion or None if no conversion
        """
        if not self.touchpoints or self.conversion_date is None:
            return None
            
        first_touchpoint = min(self.touchpoints, key=lambda tp: tp.timestamp)
        return self.conversion_date - first_touchpoint.timestamp
    
    def get_channel_count(self) -> Dict[str, int]:
        """
        Get the count of touchpoints by channel.
        
        Returns:
            Dictionary mapping channels to touchpoint counts
        """
        channel_count = {}
        for touchpoint in self.touchpoints:
            channel_count[touchpoint.channel] = channel_count.get(touchpoint.channel, 0) + 1
        return channel_count
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the customer journey to a dictionary for serialization.
        
        Returns:
            Dict containing all customer journey data
        """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "touchpoints": [tp.to_dict() for tp in self.touchpoints],
            "conversion_value": self.conversion_value,
            "conversion_date": self.conversion_date.isoformat() if self.conversion_date else None,
            "metadata": self.metadata,
            "creation_date": self.creation_date.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomerJourney':
        """
        Create a CustomerJourney instance from a dictionary.
        
        Args:
            data: Dictionary containing customer journey data
            
        Returns:
            CustomerJourney instance
        """
        journey = cls(
            customer_id=data["customer_id"],
            touchpoints=[TouchPoint.from_dict(tp) for tp in data["touchpoints"]],
            conversion_value=data["conversion_value"],
            conversion_date=data.get("conversion_date"),
            metadata=data.get("metadata", {})
        )
        
        # Restore additional properties
        journey.id = data["id"]
        journey.creation_date = datetime.fromisoformat(data["creation_date"])
        journey.last_updated = datetime.fromisoformat(data["last_updated"])
        
        return journey
