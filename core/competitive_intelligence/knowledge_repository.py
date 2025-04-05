"""
Knowledge Repository for Competitive Intelligence

This module provides tools for storing, retrieving, and managing
competitive intelligence insights and historical data.
"""

import logging
import json
import datetime
import os
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class CompetitiveEvent:
    """Data structure for competitive events"""
    event_id: str
    competitor_id: str
    event_type: str  # product_launch, price_change, marketing_campaign, etc.
    title: str
    description: str
    date: datetime.datetime
    impact_level: str  # high, medium, low
    sources: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    related_events: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class CompetitiveInsight:
    """Data structure for competitive insights"""
    insight_id: str
    title: str
    description: str
    category: str  # strategy, product, marketing, etc.
    importance: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    competitors: List[str] = field(default_factory=list)
    related_events: List[str] = field(default_factory=list)
    related_insights: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    status: str = "active"  # active, archived, invalidated


class KnowledgeRepository:
    """
    Knowledge Repository
    
    Stores, retrieves, and manages competitive intelligence insights
    and historical data.
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize the knowledge repository"""
        self.events: Dict[str, CompetitiveEvent] = {}
        self.insights: Dict[str, CompetitiveInsight] = {}
        self.competitor_events: Dict[str, List[str]] = {}  # competitor_id -> list of event_ids
        self.competitor_insights: Dict[str, List[str]] = {}  # competitor_id -> list of insight_ids
        self.category_insights: Dict[str, List[str]] = {}  # category -> list of insight_ids
        self.storage_dir = storage_dir
        logger.info("KnowledgeRepository initialized")
        
    def add_event(self, event: CompetitiveEvent) -> str:
        """
        Add a competitive event to the repository
        
        Parameters:
        - event: The event to add
        
        Returns event_id
        """
        logger.info(f"Adding event: {event.title}")
        
        # Store the event
        self.events[event.event_id] = event
        
        # Update competitor events index
        if event.competitor_id not in self.competitor_events:
            self.competitor_events[event.competitor_id] = []
            
        if event.event_id not in self.competitor_events[event.competitor_id]:
            self.competitor_events[event.competitor_id].append(event.event_id)
            
        return event.event_id
        
    def add_insight(self, insight: CompetitiveInsight) -> str:
        """
        Add a competitive insight to the repository
        
        Parameters:
        - insight: The insight to add
        
        Returns insight_id
        """
        logger.info(f"Adding insight: {insight.title}")
        
        # Store the insight
        self.insights[insight.id] = insight
        
        # Update category insights index
        if insight.insight_type not in self.category_insights:
            self.category_insights[insight.insight_type] = []
            
        if insight.id not in self.category_insights[insight.insight_type]:
            self.category_insights[insight.insight_type].append(insight.id)
            
        # Update competitor insights index
        for competitor_id in insight.related_competitors:
            if competitor_id not in self.competitor_insights:
                self.competitor_insights[competitor_id] = []
                
            if insight.id not in self.competitor_insights[competitor_id]:
                self.competitor_insights[competitor_id].append(insight.id)
                
        return insight.id
        
    def get_event(self, event_id: str) -> Optional[CompetitiveEvent]:
        """
        Get a specific event by ID
        
        Parameters:
        - event_id: ID of the event to retrieve
        
        Returns the event or None if not found
        """
        return self.events.get(event_id)
        
    def get_insight(self, insight_id: str) -> Optional[CompetitiveInsight]:
        """
        Get a specific insight by ID
        
        Parameters:
        - insight_id: ID of the insight to retrieve
        
        Returns the insight or None if not found
        """
        return self.insights.get(insight_id)
        
    def get_competitor_events(self, competitor_id: str, 
                             event_type: Optional[str] = None,
                             limit: int = 10,
                             sort_by_date: bool = True) -> List[CompetitiveEvent]:
        """
        Get events for a specific competitor
        
        Parameters:
        - competitor_id: ID of the competitor
        - event_type: Optional filter by event type
        - limit: Maximum number of events to return
        - sort_by_date: Whether to sort by date (newest first)
        
        Returns list of events
        """
        logger.info(f"Getting events for competitor {competitor_id}")
        
        # Get event IDs for the competitor
        event_ids = self.competitor_events.get(competitor_id, [])
        
        # Get the actual events
        events = []
        for event_id in event_ids:
            event = self.events.get(event_id)
            if event and (not event_type or event.event_type == event_type):
                events.append(event)
                
        # Sort by date if requested
        if sort_by_date:
            events.sort(key=lambda e: e.date, reverse=True)
            
        # Apply limit
        return events[:limit]
        
    def get_competitor_insights(self, competitor_id: str,
                               category: Optional[str] = None,
                               min_importance: float = 0.0,
                               limit: int = 10) -> List[CompetitiveInsight]:
        """
        Get insights for a specific competitor
        
        Parameters:
        - competitor_id: ID of the competitor
        - category: Optional filter by category
        - min_importance: Minimum importance threshold
        - limit: Maximum number of insights to return
        
        Returns list of insights
        """
        logger.info(f"Getting insights for competitor {competitor_id}")
        
        # Get insight IDs for the competitor
        insight_ids = self.competitor_insights.get(competitor_id, [])
        
        # Get the actual insights
        insights = []
        for insight_id in insight_ids:
            insight = self.insights.get(insight_id)
            if (insight and 
                insight.priority >= int(min_importance * 5) and
                (not category or insight.insight_type == category)):
                insights.append(insight)
                
        # Sort by priority
        insights.sort(key=lambda i: i.priority, reverse=True)
            
        # Apply limit
        return insights[:limit]
        
    def get_category_insights(self, category: str,
                             min_importance: float = 0.0,
                             limit: int = 10) -> List[CompetitiveInsight]:
        """
        Get insights for a specific category
        
        Parameters:
        - category: Category to filter by
        - min_importance: Minimum importance threshold
        - limit: Maximum number of insights to return
        
        Returns list of insights
        """
        logger.info(f"Getting insights for category {category}")
        
        # Get insight IDs for the category
        insight_ids = self.category_insights.get(category, [])
        
        # Get the actual insights
        insights = []
        for insight_id in insight_ids:
            insight = self.insights.get(insight_id)
            if insight and insight.status == "active" and insight.importance >= min_importance:
                insights.append(insight)
                
        # Sort by importance
        insights.sort(key=lambda i: i.importance, reverse=True)
            
        # Apply limit
        return insights[:limit]
        
    def search_events(self, query: str, limit: int = 10) -> List[CompetitiveEvent]:
        """
        Search for events matching a query
        
        Parameters:
        - query: Search query
        - limit: Maximum number of events to return
        
        Returns list of matching events
        """
        logger.info(f"Searching events with query: {query}")
        
        query = query.lower()
        matching_events = []
        
        for event in self.events.values():
            # Check for matches in title, description, or tags
            if (query in event.title.lower() or
                query in event.description.lower() or
                any(query in tag.lower() for tag in event.tags)):
                matching_events.append(event)
                
        # Sort by date (newest first)
        matching_events.sort(key=lambda e: e.date, reverse=True)
        
        # Apply limit
        return matching_events[:limit]
        
    def search_insights(self, query: str, limit: int = 10) -> List[CompetitiveInsight]:
        """
        Search for insights matching a query
        
        Parameters:
        - query: Search query
        - limit: Maximum number of insights to return
        
        Returns list of matching insights
        """
        logger.info(f"Searching insights with query: {query}")
        
        query = query.lower()
        matching_insights = []
        
        for insight in self.insights.values():
            # Skip archived or invalidated insights
            if insight.status != "active":
                continue
                
            # Check for matches in title, description, or tags
            if (query in insight.title.lower() or
                query in insight.description.lower() or
                any(query in tag.lower() for tag in insight.tags)):
                matching_insights.append(insight)
                
        # Sort by importance
        matching_insights.sort(key=lambda i: i.importance, reverse=True)
        
        # Apply limit
        return matching_insights[:limit]
        
    def get_related_insights(self, insight_id: str, limit: int = 5) -> List[CompetitiveInsight]:
        """
        Get insights related to a specific insight
        
        Parameters:
        - insight_id: ID of the insight
        - limit: Maximum number of related insights to return
        
        Returns list of related insights
        """
        logger.info(f"Getting related insights for {insight_id}")
        
        insight = self.insights.get(insight_id)
        if not insight:
            logger.warning(f"Insight {insight_id} not found")
            return []
            
        # Get directly related insights
        related_ids = insight.related_insights.copy()
        
        # Get insights with shared competitors
        for competitor_id in insight.competitors:
            for related_id in self.competitor_insights.get(competitor_id, []):
                if related_id != insight_id and related_id not in related_ids:
                    related_ids.append(related_id)
                    
        # Get insights with shared tags
        for tag in insight.tags:
            for other_insight in self.insights.values():
                if (other_insight.insight_id != insight_id and 
                    other_insight.insight_id not in related_ids and
                    tag in other_insight.tags):
                    related_ids.append(other_insight.insight_id)
                    
        # Get the actual insights
        related_insights = []
        for related_id in related_ids:
            related = self.insights.get(related_id)
            if related and related.status == "active":
                related_insights.append(related)
                
        # Sort by importance
        related_insights.sort(key=lambda i: i.importance, reverse=True)
        
        # Apply limit
        return related_insights[:limit]
        
    def get_related_events(self, event_id: str, limit: int = 5) -> List[CompetitiveEvent]:
        """
        Get events related to a specific event
        
        Parameters:
        - event_id: ID of the event
        - limit: Maximum number of related events to return
        
        Returns list of related events
        """
        logger.info(f"Getting related events for {event_id}")
        
        event = self.events.get(event_id)
        if not event:
            logger.warning(f"Event {event_id} not found")
            return []
            
        # Get directly related events
        related_ids = event.related_events.copy()
        
        # Get events from the same competitor
        for other_id in self.competitor_events.get(event.competitor_id, []):
            if other_id != event_id and other_id not in related_ids:
                related_ids.append(other_id)
                
        # Get events with shared tags
        for tag in event.tags:
            for other_event in self.events.values():
                if (other_event.event_id != event_id and 
                    other_event.event_id not in related_ids and
                    tag in other_event.tags):
                    related_ids.append(other_event.event_id)
                    
        # Get the actual events
        related_events = []
        for related_id in related_ids:
            related = self.events.get(related_id)
            if related:
                related_events.append(related)
                
        # Sort by date (newest first)
        related_events.sort(key=lambda e: e.date, reverse=True)
        
        # Apply limit
        return related_events[:limit]
        
    def update_insight(self, insight_id: str, 
                      updates: Dict[str, Any]) -> Optional[CompetitiveInsight]:
        """
        Update an existing insight
        
        Parameters:
        - insight_id: ID of the insight to update
        - updates: Dictionary of fields to update
        
        Returns updated insight or None if not found
        """
        logger.info(f"Updating insight {insight_id}")
        
        insight = self.insights.get(insight_id)
        if not insight:
            logger.warning(f"Insight {insight_id} not found")
            return None
            
        # Update fields
        for field, value in updates.items():
            if hasattr(insight, field):
                setattr(insight, field, value)
                
        # Always update the updated_at timestamp
        insight.updated_at = datetime.datetime.now()
        
        return insight
        
    def archive_insight(self, insight_id: str) -> bool:
        """
        Archive an insight
        
        Parameters:
        - insight_id: ID of the insight to archive
        
        Returns success flag
        """
        logger.info(f"Archiving insight {insight_id}")
        
        insight = self.insights.get(insight_id)
        if not insight:
            logger.warning(f"Insight {insight_id} not found")
            return False
            
        insight.status = "archived"
        insight.updated_at = datetime.datetime.now()
        
        return True
        
    def invalidate_insight(self, insight_id: str) -> bool:
        """
        Invalidate an insight
        
        Parameters:
        - insight_id: ID of the insight to invalidate
        
        Returns success flag
        """
        logger.info(f"Invalidating insight {insight_id}")
        
        insight = self.insights.get(insight_id)
        if not insight:
            logger.warning(f"Insight {insight_id} not found")
            return False
            
        insight.status = "invalidated"
        insight.updated_at = datetime.datetime.now()
        
        return True
        
    def create_event_timeline(self, competitor_id: str, 
                             start_date: Optional[datetime.datetime] = None,
                             end_date: Optional[datetime.datetime] = None) -> List[Dict]:
        """
        Create a timeline of events for a competitor
        
        Parameters:
        - competitor_id: ID of the competitor
        - start_date: Optional start date for the timeline
        - end_date: Optional end date for the timeline
        
        Returns timeline of events
        """
        logger.info(f"Creating event timeline for competitor {competitor_id}")
        
        # Get all events for the competitor
        events = self.get_competitor_events(competitor_id, limit=100, sort_by_date=True)
        
        # Filter by date range if specified
        if start_date or end_date:
            filtered_events = []
            for event in events:
                if start_date and event.date < start_date:
                    continue
                if end_date and event.date > end_date:
                    continue
                filtered_events.append(event)
            events = filtered_events
            
        # Create timeline entries
        timeline = []
        for event in events:
            timeline.append({
                "event_id": event.event_id,
                "date": event.date,
                "title": event.title,
                "description": event.description,
                "event_type": event.event_type,
                "impact_level": event.impact_level
            })
            
        return timeline
        
    def generate_competitor_summary(self, competitor_id: str) -> Dict:
        """
        Generate a summary of knowledge about a competitor
        
        Parameters:
        - competitor_id: ID of the competitor
        
        Returns competitor summary
        """
        logger.info(f"Generating summary for competitor {competitor_id}")
        
        # Get recent events
        recent_events = self.get_competitor_events(competitor_id, limit=5)
        
        # Get important insights
        important_insights = self.get_competitor_insights(competitor_id, min_importance=0.7, limit=5)
        
        # Count events by type
        event_counts = {}
        for event in self.get_competitor_events(competitor_id, limit=100):
            event_type = event.event_type
            if event_type not in event_counts:
                event_counts[event_type] = 0
            event_counts[event_type] += 1
            
        # Count insights by type
        insight_counts = {}
        for insight in self.get_competitor_insights(competitor_id, limit=100):
            insight_type = insight.insight_type
            if insight_type not in insight_counts:
                insight_counts[insight_type] = 0
            insight_counts[insight_type] += 1
            
        return {
            "competitor_id": competitor_id,
            "total_events": len(self.competitor_events.get(competitor_id, [])),
            "total_insights": len(self.competitor_insights.get(competitor_id, [])),
            "recent_events": [
                {"date": e.date, "title": e.title, "type": e.event_type}
                for e in recent_events
            ],
            "key_insights": [
                {"title": i.title, "priority": i.priority, "type": i.insight_type}
                for i in important_insights
            ],
            "event_type_distribution": event_counts,
            "insight_type_distribution": insight_counts
        }
        
    def export_repository(self, output_dir: Optional[str] = None) -> Dict[str, int]:
        """
        Export the repository to JSON files
        
        Parameters:
        - output_dir: Directory to export to (defaults to self.storage_dir)
        
        Returns counts of exported items
        """
        logger.info("Exporting repository")
        
        dir_path = output_dir or self.storage_dir
        if not dir_path:
            logger.error("No export directory specified")
            return {"error": "No export directory specified"}
            
        # Create directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)
        
        # Export events
        events_path = os.path.join(dir_path, "events.json")
        events_data = {}
        for event_id, event in self.events.items():
            events_data[event_id] = {
                "event_id": event.event_id,
                "competitor_id": event.competitor_id,
                "event_type": event.event_type,
                "title": event.title,
                "description": event.description,
                "date": event.date.isoformat(),
                "impact_level": event.impact_level,
                "sources": event.sources,
                "tags": event.tags,
                "related_events": event.related_events,
                "metadata": event.metadata,
                "created_at": event.created_at.isoformat()
            }
            
        with open(events_path, 'w') as f:
            json.dump(events_data, f, indent=2)
            
        # Export insights
        insights_path = os.path.join(dir_path, "insights.json")
        insights_data = {}
        for insight_id, insight in self.insights.items():
            insights_data[insight_id] = {
                "id": insight.id,
                "title": insight.title,
                "description": insight.description,
                "insight_type": insight.insight_type,
                "priority": insight.priority,
                "source_type": insight.source_type,
                "source_id": insight.source_id,
                "related_competitors": insight.related_competitors,
                "created_at": insight.created_at.isoformat(),
                "tags": insight.tags if hasattr(insight, 'tags') else []
            }
            
        with open(insights_path, 'w') as f:
            json.dump(insights_data, f, indent=2)
            
        # Export indexes
        indexes_path = os.path.join(dir_path, "indexes.json")
        indexes_data = {
            "competitor_events": self.competitor_events,
            "competitor_insights": self.competitor_insights,
            "category_insights": self.category_insights
        }
            
        with open(indexes_path, 'w') as f:
            json.dump(indexes_data, f, indent=2)
            
        return {
            "events": len(self.events),
            "insights": len(self.insights),
            "export_path": dir_path
        }
        
    def import_repository(self, input_dir: Optional[str] = None) -> Dict[str, int]:
        """
        Import the repository from JSON files
        
        Parameters:
        - input_dir: Directory to import from (defaults to self.storage_dir)
        
        Returns counts of imported items
        """
        logger.info("Importing repository")
        
        dir_path = input_dir or self.storage_dir
        if not dir_path:
            logger.error("No import directory specified")
            return {"error": "No import directory specified"}
            
        # Check if directory exists
        if not os.path.isdir(dir_path):
            logger.error(f"Directory not found: {dir_path}")
            return {"error": f"Directory not found: {dir_path}"}
            
        # Import events
        events_path = os.path.join(dir_path, "events.json")
        if os.path.isfile(events_path):
            with open(events_path, 'r') as f:
                events_data = json.load(f)
                
            for event_id, event_dict in events_data.items():
                event = CompetitiveEvent(
                    event_id=event_dict["event_id"],
                    competitor_id=event_dict["competitor_id"],
                    event_type=event_dict["event_type"],
                    title=event_dict["title"],
                    description=event_dict["description"],
                    date=datetime.datetime.fromisoformat(event_dict["date"]),
                    impact_level=event_dict["impact_level"],
                    sources=event_dict["sources"],
                    tags=event_dict["tags"],
                    related_events=event_dict["related_events"],
                    metadata=event_dict["metadata"],
                    created_at=datetime.datetime.fromisoformat(event_dict["created_at"])
                )
                self.events[event_id] = event
                
        # Import insights
        insights_path = os.path.join(dir_path, "insights.json")
        if os.path.isfile(insights_path):
            with open(insights_path, 'r') as f:
                insights_data = json.load(f)
                
            for insight_id, insight_dict in insights_data.items():
                insight = CompetitiveInsight(
                    insight_id=insight_dict["insight_id"],
                    title=insight_dict["title"],
                    description=insight_dict["description"],
                    category=insight_dict["category"],
                    importance=insight_dict["importance"],
                    confidence=insight_dict["confidence"],
                    competitors=insight_dict["competitors"],
                    related_events=insight_dict["related_events"],
                    related_insights=insight_dict["related_insights"],
                    tags=insight_dict["tags"],
                    created_at=datetime.datetime.fromisoformat(insight_dict["created_at"]),
                    updated_at=datetime.datetime.fromisoformat(insight_dict["updated_at"]),
                    status=insight_dict["status"]
                )
                self.insights[insight_id] = insight
                
        # Import indexes
        indexes_path = os.path.join(dir_path, "indexes.json")
        if os.path.isfile(indexes_path):
            with open(indexes_path, 'r') as f:
                indexes_data = json.load(f)
                
            self.competitor_events = indexes_data.get("competitor_events", {})
            self.competitor_insights = indexes_data.get("competitor_insights", {})
            self.category_insights = indexes_data.get("category_insights", {})
            
        return {
            "events": len(self.events),
            "insights": len(self.insights)
        }
