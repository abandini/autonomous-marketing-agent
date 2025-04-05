"""
Event Manager for the Background Execution Framework.

This module provides event-driven architecture capabilities,
allowing components to publish and subscribe to events.
"""

import logging
import asyncio
from typing import Dict, List, Callable, Any, Optional, Set
from datetime import datetime
import json
import uuid

# Import analytics components for integration
from core.analytics.analytics_engine import AnalyticsEngine

logger = logging.getLogger(__name__)

class EventManager:
    """
    Manages events for the Background Execution Framework.
    
    This class provides a publish-subscribe pattern implementation,
    allowing components to communicate through events without direct coupling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the event manager.
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or {}
        self.subscribers = {}  # Event name -> list of subscribers
        self.event_history = {}  # Event name -> list of recent events
        self.history_limit = self.config.get('event_history_limit', 100)
        self.analytics_engine = None
        
        # Initialize analytics engine if configured
        if self.config.get('analytics_integration', {}).get('enabled', True):
            self._init_analytics_engine()
            
        logger.info("Event Manager initialized")
        
    def _init_analytics_engine(self):
        """Initialize analytics engine for event tracking."""
        try:
            self.analytics_engine = AnalyticsEngine()
            logger.info("Analytics Engine initialized for event tracking")
        except Exception as e:
            logger.error(f"Error initializing Analytics Engine: {e}")
            
    def subscribe(self, event_name: str, callback: Callable, 
                 subscriber_id: Optional[str] = None) -> str:
        """
        Subscribe to an event.
        
        Args:
            event_name: Name of the event to subscribe to
            callback: Function to call when the event occurs
            subscriber_id: Unique identifier for the subscriber (optional)
            
        Returns:
            Subscriber ID
        """
        if not subscriber_id:
            subscriber_id = str(uuid.uuid4())
            
        if event_name not in self.subscribers:
            self.subscribers[event_name] = {}
            
        self.subscribers[event_name][subscriber_id] = callback
        logger.info(f"Subscribed {subscriber_id} to event: {event_name}")
        
        return subscriber_id
        
    def unsubscribe(self, event_name: str, subscriber_id: str) -> bool:
        """
        Unsubscribe from an event.
        
        Args:
            event_name: Name of the event
            subscriber_id: ID of the subscriber
            
        Returns:
            True if unsubscription successful, False otherwise
        """
        if (event_name not in self.subscribers or 
            subscriber_id not in self.subscribers[event_name]):
            logger.warning(f"Subscriber {subscriber_id} not found for event: {event_name}")
            return False
            
        del self.subscribers[event_name][subscriber_id]
        
        # Clean up empty event entries
        if not self.subscribers[event_name]:
            del self.subscribers[event_name]
            
        logger.info(f"Unsubscribed {subscriber_id} from event: {event_name}")
        return True
        
    async def publish(self, event_name: str, event_data: Any = None,
                    publisher_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Publish an event.
        
        Args:
            event_name: Name of the event
            event_data: Data associated with the event
            publisher_id: ID of the publisher (optional)
            
        Returns:
            Dictionary with results of event processing
        """
        event = {
            'name': event_name,
            'data': event_data,
            'publisher_id': publisher_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in event history
        if event_name not in self.event_history:
            self.event_history[event_name] = []
            
        self.event_history[event_name].append(event)
        
        # Trim history if needed
        if len(self.event_history[event_name]) > self.history_limit:
            self.event_history[event_name] = self.event_history[event_name][-self.history_limit:]
            
        # Track event in analytics if available
        if self.analytics_engine:
            try:
                self._track_event_in_analytics(event)
            except Exception as e:
                logger.error(f"Error tracking event in analytics: {e}")
                
        # Notify subscribers
        results = {}
        if event_name in self.subscribers:
            for subscriber_id, callback in self.subscribers[event_name].items():
                try:
                    logger.debug(f"Notifying subscriber {subscriber_id} of event: {event_name}")
                    
                    if asyncio.iscoroutinefunction(callback):
                        result = await callback(event)
                    else:
                        result = callback(event)
                        
                    results[subscriber_id] = {
                        'status': 'success',
                        'result': result
                    }
                except Exception as e:
                    logger.error(f"Error notifying subscriber {subscriber_id}: {e}")
                    results[subscriber_id] = {
                        'status': 'error',
                        'message': str(e)
                    }
                    
        # Also notify wildcard subscribers
        if '*' in self.subscribers:
            for subscriber_id, callback in self.subscribers['*'].items():
                try:
                    logger.debug(f"Notifying wildcard subscriber {subscriber_id} of event: {event_name}")
                    
                    if asyncio.iscoroutinefunction(callback):
                        result = await callback(event)
                    else:
                        result = callback(event)
                        
                    results[subscriber_id] = {
                        'status': 'success',
                        'result': result
                    }
                except Exception as e:
                    logger.error(f"Error notifying wildcard subscriber {subscriber_id}: {e}")
                    results[subscriber_id] = {
                        'status': 'error',
                        'message': str(e)
                    }
                    
        logger.info(f"Published event: {event_name}, notified {len(results)} subscribers")
        return {
            'event': event,
            'results': results
        }
        
    def _track_event_in_analytics(self, event: Dict[str, Any]):
        """
        Track an event in the analytics engine.
        
        Args:
            event: Event dictionary
        """
        if not self.analytics_engine:
            return
            
        # Add event as a data source
        source_name = f"event_{event['name']}"
        source_type = "event"
        
        self.analytics_engine.add_data_source({
            "name": source_name,
            "type": source_type,
            "event": event
        })
        
        # Collect metrics for this event
        self.analytics_engine.collect_metrics(source_name)
        
    def get_event_history(self, event_name: Optional[str] = None, 
                         limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the history of events.
        
        Args:
            event_name: Name of the event to get history for (optional)
            limit: Maximum number of events to return per event type
            
        Returns:
            Dictionary of event names to lists of events
        """
        if event_name:
            if event_name not in self.event_history:
                return {event_name: []}
            return {event_name: self.event_history[event_name][-limit:]}
            
        # Return history for all events
        result = {}
        for name, events in self.event_history.items():
            result[name] = events[-limit:]
            
        return result
        
    def get_subscriber_count(self, event_name: Optional[str] = None) -> Dict[str, int]:
        """
        Get the number of subscribers for events.
        
        Args:
            event_name: Name of the event to get subscriber count for (optional)
            
        Returns:
            Dictionary of event names to subscriber counts
        """
        if event_name:
            if event_name not in self.subscribers:
                return {event_name: 0}
            return {event_name: len(self.subscribers[event_name])}
            
        # Return counts for all events
        return {name: len(subscribers) for name, subscribers in self.subscribers.items()}
        
    def clear_event_history(self, event_name: Optional[str] = None):
        """
        Clear the event history.
        
        Args:
            event_name: Name of the event to clear history for (optional)
        """
        if event_name:
            if event_name in self.event_history:
                self.event_history[event_name] = []
                logger.info(f"Cleared history for event: {event_name}")
        else:
            self.event_history = {}
            logger.info("Cleared all event history")
            
    async def register_analytics_events(self):
        """Register standard events related to analytics."""
        if not self.analytics_engine:
            logger.warning("Analytics Engine not available for event registration")
            return
            
        # Define standard analytics events
        standard_events = [
            "content_performance_change",
            "traffic_spike",
            "conversion_rate_change",
            "keyword_ranking_change",
            "competitor_activity",
            "social_media_mention",
            "revenue_goal_achieved",
            "strategy_performance_update"
        ]
        
        # Register handlers for these events
        for event_name in standard_events:
            self.subscribe(
                event_name=event_name,
                callback=self._handle_analytics_event,
                subscriber_id=f"analytics_{event_name}"
            )
            
        logger.info(f"Registered {len(standard_events)} standard analytics events")
        
    async def _handle_analytics_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle analytics-related events.
        
        Args:
            event: Event dictionary
            
        Returns:
            Result of handling the event
        """
        event_name = event['name']
        event_data = event['data']
        
        logger.info(f"Handling analytics event: {event_name}")
        
        # Process different types of analytics events
        if event_name == "content_performance_change":
            return await self._handle_content_performance_change(event_data)
        elif event_name == "traffic_spike":
            return await self._handle_traffic_spike(event_data)
        elif event_name == "conversion_rate_change":
            return await self._handle_conversion_rate_change(event_data)
        elif event_name == "keyword_ranking_change":
            return await self._handle_keyword_ranking_change(event_data)
        elif event_name == "competitor_activity":
            return await self._handle_competitor_activity(event_data)
        elif event_name == "social_media_mention":
            return await self._handle_social_media_mention(event_data)
        elif event_name == "revenue_goal_achieved":
            return await self._handle_revenue_goal_achieved(event_data)
        elif event_name == "strategy_performance_update":
            return await self._handle_strategy_performance_update(event_data)
        else:
            logger.warning(f"No specific handler for analytics event: {event_name}")
            return {"status": "unhandled", "event": event_name}
            
    async def _handle_content_performance_change(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle content performance change events.
        
        Args:
            event_data: Event data
            
        Returns:
            Result of handling the event
        """
        logger.info("Processing content performance change")
        
        # In a real implementation, this would analyze the performance change
        # and potentially trigger website updates via Git integration
        
        # For now, just return a placeholder result
        return {
            "status": "processed",
            "action": "content_performance_analysis",
            "result": "Content performance change detected and analyzed"
        }
        
    async def _handle_traffic_spike(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle traffic spike events."""
        logger.info("Processing traffic spike")
        return {
            "status": "processed",
            "action": "traffic_analysis",
            "result": "Traffic spike detected and analyzed"
        }
        
    async def _handle_conversion_rate_change(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle conversion rate change events."""
        logger.info("Processing conversion rate change")
        return {
            "status": "processed",
            "action": "conversion_analysis",
            "result": "Conversion rate change detected and analyzed"
        }
        
    async def _handle_keyword_ranking_change(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle keyword ranking change events."""
        logger.info("Processing keyword ranking change")
        return {
            "status": "processed",
            "action": "keyword_analysis",
            "result": "Keyword ranking change detected and analyzed"
        }
        
    async def _handle_competitor_activity(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle competitor activity events."""
        logger.info("Processing competitor activity")
        return {
            "status": "processed",
            "action": "competitor_analysis",
            "result": "Competitor activity detected and analyzed"
        }
        
    async def _handle_social_media_mention(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle social media mention events."""
        logger.info("Processing social media mention")
        return {
            "status": "processed",
            "action": "social_media_analysis",
            "result": "Social media mention detected and analyzed"
        }
        
    async def _handle_revenue_goal_achieved(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle revenue goal achieved events."""
        logger.info("Processing revenue goal achievement")
        return {
            "status": "processed",
            "action": "revenue_goal_analysis",
            "result": "Revenue goal achievement detected and analyzed"
        }
        
    async def _handle_strategy_performance_update(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle strategy performance update events."""
        logger.info("Processing strategy performance update")
        return {
            "status": "processed",
            "action": "strategy_performance_analysis",
            "result": "Strategy performance update detected and analyzed"
        }
