"""
Pattern Recognition for Competitive Intelligence

This module provides tools for detecting patterns in competitor behavior,
including pricing patterns, release cycles, marketing patterns, and seasonal patterns.
"""

import logging
import json
import datetime
import random
import math
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field

from .monitoring import CompetitorMonitor

logger = logging.getLogger(__name__)

@dataclass
class PatternData:
    """Data structure for detected patterns"""
    pattern_id: str
    name: str
    description: str
    pattern_type: str  # pricing, release, marketing, seasonal
    competitors: List[str]
    confidence: float  # 0.0 to 1.0
    occurrences: List[Dict] = field(default_factory=list)
    first_detected: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_detected: datetime.datetime = field(default_factory=datetime.datetime.now)
    status: str = "active"  # active, fading, inactive
    expected_next_occurrence: Optional[datetime.datetime] = None
    
    def add_occurrence(self, data: Dict):
        """Add a new occurrence of the pattern"""
        self.occurrences.append(data)
        self.last_detected = datetime.datetime.now()
        
        # Update status based on recency
        days_since_first = (self.last_detected - self.first_detected).days
        if days_since_first > 180:  # More than 6 months of history
            self.status = "active"
        elif days_since_first > 90:  # 3-6 months of history
            self.status = "emerging"
            
        # Update confidence based on number of occurrences
        self.confidence = min(0.95, 0.5 + (len(self.occurrences) * 0.05))


class PatternRecognizer:
    """
    Pattern Recognition
    
    Identifies patterns in competitor behavior, including pricing patterns,
    release cycles, marketing patterns, and seasonal patterns.
    """
    
    def __init__(self, competitor_monitor: CompetitorMonitor):
        """Initialize with reference to competitor monitor"""
        self.competitor_monitor = competitor_monitor
        self.patterns: Dict[str, PatternData] = {}  # pattern_id -> pattern
        self.competitor_patterns: Dict[str, List[str]] = {}  # competitor_id -> list of pattern_ids
        logger.info("PatternRecognizer initialized")
        
    def detect_pricing_patterns(self, competitor_id: str) -> List[PatternData]:
        """
        Detect patterns in competitor pricing
        
        Parameters:
        - competitor_id: ID of the competitor to analyze
        
        Returns list of detected patterns
        """
        logger.info(f"Detecting pricing patterns for competitor {competitor_id}")
        
        # Placeholder implementation
        # In a real system, this would analyze historical pricing data
        
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            logger.warning(f"Competitor {competitor_id} not found")
            return []
            
        detected_patterns = []
        
        # Generate some sample patterns
        pattern_types = ["seasonal_discount", "competitive_response", "cost_based_adjustment"]
        
        # Use competitor_id to deterministically select a pattern type
        pattern_index = hash(competitor_id) % len(pattern_types)
        pattern_type = pattern_types[pattern_index]
        
        # Create pattern based on type
        if pattern_type == "seasonal_discount":
            # Seasonal discount pattern
            pattern_id = f"pricing_seasonal_{competitor_id}"
            
            if pattern_id not in self.patterns:
                # Create new pattern
                pattern = PatternData(
                    pattern_id=pattern_id,
                    name="Seasonal Discount Pattern",
                    description=f"{profile.name} consistently offers discounts during specific seasons",
                    pattern_type="pricing",
                    competitors=[competitor_id],
                    confidence=0.7
                )
                
                # Add sample occurrences
                now = datetime.datetime.now()
                
                # Create past occurrences for the last 2 years
                for year_offset in range(2):
                    for month in [11, 12]:  # November and December
                        date = datetime.datetime(now.year - year_offset, month, 15)
                        pattern.add_occurrence({
                            "date": date,
                            "description": f"Holiday season discount of {15 + random.randint(0, 10)}%",
                            "magnitude": random.uniform(0.15, 0.25)
                        })
                        
                # Predict next occurrence
                next_holiday = datetime.datetime(now.year, 11, 15)
                if now > next_holiday:
                    next_holiday = datetime.datetime(now.year + 1, 11, 15)
                    
                pattern.expected_next_occurrence = next_holiday
                
                self.patterns[pattern_id] = pattern
                detected_patterns.append(pattern)
                
            else:
                # Return existing pattern
                detected_patterns.append(self.patterns[pattern_id])
                
        elif pattern_type == "competitive_response":
            # Competitive response pattern
            pattern_id = f"pricing_response_{competitor_id}"
            
            if pattern_id not in self.patterns:
                # Create new pattern
                pattern = PatternData(
                    pattern_id=pattern_id,
                    name="Competitive Response Pattern",
                    description=f"{profile.name} adjusts pricing in response to competitor changes",
                    pattern_type="pricing",
                    competitors=[competitor_id],
                    confidence=0.65
                )
                
                # Add sample occurrences
                now = datetime.datetime.now()
                
                # Create past occurrences
                for month_offset in range(1, 13, 3):  # Every 3 months for the past year
                    date = now - datetime.timedelta(days=30 * month_offset)
                    pattern.add_occurrence({
                        "date": date,
                        "description": f"Price adjustment following competitor change",
                        "magnitude": random.uniform(-0.1, 0.1),
                        "response_time_days": random.randint(7, 21)
                    })
                    
                # No specific prediction for next occurrence
                
                self.patterns[pattern_id] = pattern
                detected_patterns.append(pattern)
                
            else:
                # Return existing pattern
                detected_patterns.append(self.patterns[pattern_id])
                
        else:  # cost_based_adjustment
            # Cost-based adjustment pattern
            pattern_id = f"pricing_cost_{competitor_id}"
            
            if pattern_id not in self.patterns:
                # Create new pattern
                pattern = PatternData(
                    pattern_id=pattern_id,
                    name="Cost-Based Adjustment Pattern",
                    description=f"{profile.name} adjusts pricing based on cost changes",
                    pattern_type="pricing",
                    competitors=[competitor_id],
                    confidence=0.8
                )
                
                # Add sample occurrences
                now = datetime.datetime.now()
                
                # Create past occurrences
                for month_offset in [3, 9]:  # Twice a year
                    date = now - datetime.timedelta(days=30 * month_offset)
                    pattern.add_occurrence({
                        "date": date,
                        "description": f"Price adjustment citing cost increases",
                        "magnitude": random.uniform(0.03, 0.08)
                    })
                    
                # Predict next occurrence
                next_adjustment = now + datetime.timedelta(days=90)  # 3 months from now
                pattern.expected_next_occurrence = next_adjustment
                
                self.patterns[pattern_id] = pattern
                detected_patterns.append(pattern)
                
            else:
                # Return existing pattern
                detected_patterns.append(self.patterns[pattern_id])
                
        # Update competitor patterns index
        if competitor_id not in self.competitor_patterns:
            self.competitor_patterns[competitor_id] = []
            
        for pattern in detected_patterns:
            if pattern.pattern_id not in self.competitor_patterns[competitor_id]:
                self.competitor_patterns[competitor_id].append(pattern.pattern_id)
                
        return detected_patterns
        
    def detect_release_cycles(self, competitor_id: str) -> List[PatternData]:
        """
        Detect patterns in competitor product/feature releases
        
        Parameters:
        - competitor_id: ID of the competitor to analyze
        
        Returns list of detected patterns
        """
        logger.info(f"Detecting release cycles for competitor {competitor_id}")
        
        # Placeholder implementation
        # In a real system, this would analyze historical release data
        
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            logger.warning(f"Competitor {competitor_id} not found")
            return []
            
        detected_patterns = []
        
        # Generate a sample release cycle pattern
        pattern_id = f"release_cycle_{competitor_id}"
        
        if pattern_id not in self.patterns:
            # Determine cycle length based on competitor_id
            cycle_options = [30, 60, 90, 180, 365]  # Days
            cycle_index = hash(competitor_id) % len(cycle_options)
            cycle_length = cycle_options[cycle_index]
            
            # Create new pattern
            pattern = PatternData(
                pattern_id=pattern_id,
                name=f"{cycle_length}-Day Release Cycle",
                description=f"{profile.name} releases product updates approximately every {cycle_length // 30} month(s)",
                pattern_type="release",
                competitors=[competitor_id],
                confidence=0.75
            )
            
            # Add sample occurrences
            now = datetime.datetime.now()
            
            # Create past occurrences
            for i in range(1, 5):  # Last 4 releases
                date = now - datetime.timedelta(days=cycle_length * i)
                
                # Add some randomness to the cycle
                date += datetime.timedelta(days=random.randint(-10, 10))
                
                pattern.add_occurrence({
                    "date": date,
                    "description": f"Version {2023 - i}.{random.randint(1, 3)} release",
                    "major_release": random.random() > 0.7
                })
                
            # Predict next occurrence
            last_release = max(occ["date"] for occ in pattern.occurrences)
            next_release = last_release + datetime.timedelta(days=cycle_length)
            
            # Add some randomness to the prediction
            next_release += datetime.timedelta(days=random.randint(-5, 5))
            
            pattern.expected_next_occurrence = next_release
            
            self.patterns[pattern_id] = pattern
            detected_patterns.append(pattern)
            
        else:
            # Return existing pattern
            detected_patterns.append(self.patterns[pattern_id])
            
        # Update competitor patterns index
        if competitor_id not in self.competitor_patterns:
            self.competitor_patterns[competitor_id] = []
            
        for pattern in detected_patterns:
            if pattern.pattern_id not in self.competitor_patterns[competitor_id]:
                self.competitor_patterns[competitor_id].append(pattern.pattern_id)
                
        return detected_patterns
        
    def detect_marketing_patterns(self, competitor_id: str) -> List[PatternData]:
        """
        Detect patterns in competitor marketing campaigns
        
        Parameters:
        - competitor_id: ID of the competitor to analyze
        
        Returns list of detected patterns
        """
        logger.info(f"Detecting marketing patterns for competitor {competitor_id}")
        
        # Placeholder implementation
        # In a real system, this would analyze historical marketing data
        
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            logger.warning(f"Competitor {competitor_id} not found")
            return []
            
        detected_patterns = []
        
        # Generate some sample patterns
        pattern_types = ["event_based", "quarterly_campaign", "competitor_response"]
        
        # Use competitor_id to deterministically select a pattern type
        pattern_index = hash(competitor_id + "marketing") % len(pattern_types)
        pattern_type = pattern_types[pattern_index]
        
        # Create pattern based on type
        if pattern_type == "event_based":
            # Event-based marketing pattern
            pattern_id = f"marketing_event_{competitor_id}"
            
            if pattern_id not in self.patterns:
                # Create new pattern
                pattern = PatternData(
                    pattern_id=pattern_id,
                    name="Event-Based Marketing Pattern",
                    description=f"{profile.name} launches major marketing campaigns around industry events",
                    pattern_type="marketing",
                    competitors=[competitor_id],
                    confidence=0.8
                )
                
                # Add sample occurrences
                now = datetime.datetime.now()
                
                # Create past occurrences
                events = ["Industry Conference", "Trade Show", "Product Launch"]
                
                for month_offset in [2, 6, 10]:  # Three times per year
                    date = now - datetime.timedelta(days=30 * month_offset)
                    event = random.choice(events)
                    
                    pattern.add_occurrence({
                        "date": date,
                        "description": f"Campaign around {event}",
                        "event": event,
                        "duration_days": random.randint(14, 30)
                    })
                    
                # Predict next occurrence
                next_event = now + datetime.timedelta(days=60)  # 2 months from now
                pattern.expected_next_occurrence = next_event
                
                self.patterns[pattern_id] = pattern
                detected_patterns.append(pattern)
                
            else:
                # Return existing pattern
                detected_patterns.append(self.patterns[pattern_id])
                
        elif pattern_type == "quarterly_campaign":
            # Quarterly campaign pattern
            pattern_id = f"marketing_quarterly_{competitor_id}"
            
            if pattern_id not in self.patterns:
                # Create new pattern
                pattern = PatternData(
                    pattern_id=pattern_id,
                    name="Quarterly Campaign Pattern",
                    description=f"{profile.name} runs major marketing campaigns on a quarterly basis",
                    pattern_type="marketing",
                    competitors=[competitor_id],
                    confidence=0.85
                )
                
                # Add sample occurrences
                now = datetime.datetime.now()
                
                # Create past occurrences for the last year
                for quarter in range(4):
                    month = quarter * 3 + 1  # Jan, Apr, Jul, Oct
                    date = datetime.datetime(now.year - 1, month, 15)
                    
                    if date < now:
                        pattern.add_occurrence({
                            "date": date,
                            "description": f"Q{quarter + 1} marketing campaign",
                            "budget_level": random.choice(["high", "medium", "high"]),
                            "duration_days": random.randint(30, 45)
                        })
                        
                # Predict next occurrence
                current_month = now.month
                next_quarter_month = ((current_month - 1) // 3 + 1) * 3 + 1
                
                if next_quarter_month > 12:
                    next_quarter_month = 1
                    next_quarter_year = now.year + 1
                else:
                    next_quarter_year = now.year
                    
                next_campaign = datetime.datetime(next_quarter_year, next_quarter_month, 15)
                pattern.expected_next_occurrence = next_campaign
                
                self.patterns[pattern_id] = pattern
                detected_patterns.append(pattern)
                
            else:
                # Return existing pattern
                detected_patterns.append(self.patterns[pattern_id])
                
        else:  # competitor_response
            # Competitor response pattern
            pattern_id = f"marketing_response_{competitor_id}"
            
            if pattern_id not in self.patterns:
                # Create new pattern
                pattern = PatternData(
                    pattern_id=pattern_id,
                    name="Marketing Counter-Response Pattern",
                    description=f"{profile.name} launches counter-campaigns in response to competitor marketing",
                    pattern_type="marketing",
                    competitors=[competitor_id],
                    confidence=0.7
                )
                
                # Add sample occurrences
                now = datetime.datetime.now()
                
                # Create past occurrences
                for month_offset in range(2, 12, 3):  # Every 3 months for the past year
                    date = now - datetime.timedelta(days=30 * month_offset)
                    
                    pattern.add_occurrence({
                        "date": date,
                        "description": "Counter-campaign launched",
                        "trigger": "Competitor campaign",
                        "response_time_days": random.randint(5, 15)
                    })
                    
                # No specific prediction for next occurrence
                
                self.patterns[pattern_id] = pattern
                detected_patterns.append(pattern)
                
            else:
                # Return existing pattern
                detected_patterns.append(self.patterns[pattern_id])
                
        # Update competitor patterns index
        if competitor_id not in self.competitor_patterns:
            self.competitor_patterns[competitor_id] = []
            
        for pattern in detected_patterns:
            if pattern.pattern_id not in self.competitor_patterns[competitor_id]:
                self.competitor_patterns[competitor_id].append(pattern.pattern_id)
                
        return detected_patterns
        
    def detect_seasonal_patterns(self, competitor_id: str) -> List[PatternData]:
        """
        Detect seasonal patterns in competitor behavior
        
        Parameters:
        - competitor_id: ID of the competitor to analyze
        
        Returns list of detected patterns
        """
        logger.info(f"Detecting seasonal patterns for competitor {competitor_id}")
        
        # Placeholder implementation
        # In a real system, this would analyze historical data across multiple years
        
        profile = self.competitor_monitor.competitors.get(competitor_id)
        if not profile:
            logger.warning(f"Competitor {competitor_id} not found")
            return []
            
        detected_patterns = []
        
        # Generate a sample seasonal pattern
        pattern_id = f"seasonal_{competitor_id}"
        
        if pattern_id not in self.patterns:
            # Determine season based on competitor_id
            season_options = ["holiday", "summer", "back-to-school", "end-of-year"]
            season_index = hash(competitor_id + "seasonal") % len(season_options)
            season = season_options[season_index]
            
            # Create pattern description based on season
            if season == "holiday":
                name = "Holiday Season Pattern"
                description = f"{profile.name} shows increased activity during the holiday season (November-December)"
                months = [11, 12]
            elif season == "summer":
                name = "Summer Season Pattern"
                description = f"{profile.name} shows increased activity during summer months (June-August)"
                months = [6, 7, 8]
            elif season == "back-to-school":
                name = "Back-to-School Pattern"
                description = f"{profile.name} shows increased activity during back-to-school season (August-September)"
                months = [8, 9]
            else:  # end-of-year
                name = "End-of-Year Pattern"
                description = f"{profile.name} shows increased activity at the end of fiscal year"
                months = [3, 12]  # Assuming fiscal year ends in March or December
                
            # Create new pattern
            pattern = PatternData(
                pattern_id=pattern_id,
                name=name,
                description=description,
                pattern_type="seasonal",
                competitors=[competitor_id],
                confidence=0.85
            )
            
            # Add sample occurrences
            now = datetime.datetime.now()
            
            # Create past occurrences for the last 2 years
            for year_offset in range(2):
                for month in months:
                    # Skip future months in current year
                    if year_offset == 0 and month > now.month:
                        continue
                        
                    date = datetime.datetime(now.year - year_offset, month, 15)
                    
                    pattern.add_occurrence({
                        "date": date,
                        "description": f"Increased activity in {date.strftime('%B %Y')}",
                        "activity_increase": f"{random.randint(20, 50)}%",
                        "areas": random.sample(["marketing", "sales", "product", "pricing"], k=2)
                    })
                    
            # Predict next occurrence
            next_month = None
            for month in sorted(months):
                if month > now.month:
                    next_month = month
                    break
                    
            if next_month:
                next_occurrence = datetime.datetime(now.year, next_month, 15)
            else:
                next_occurrence = datetime.datetime(now.year + 1, months[0], 15)
                
            pattern.expected_next_occurrence = next_occurrence
            
            self.patterns[pattern_id] = pattern
            detected_patterns.append(pattern)
            
        else:
            # Return existing pattern
            detected_patterns.append(self.patterns[pattern_id])
            
        # Update competitor patterns index
        if competitor_id not in self.competitor_patterns:
            self.competitor_patterns[competitor_id] = []
            
        for pattern in detected_patterns:
            if pattern.pattern_id not in self.competitor_patterns[competitor_id]:
                self.competitor_patterns[competitor_id].append(pattern.pattern_id)
                
        return detected_patterns
        
    def get_active_patterns(self, competitor_id: Optional[str] = None) -> List[PatternData]:
        """
        Get all active patterns
        
        Parameters:
        - competitor_id: Optional competitor ID to filter by
        
        Returns list of active patterns
        """
        logger.info(f"Getting active patterns{f' for {competitor_id}' if competitor_id else ''}")
        
        if competitor_id:
            # Get patterns for specific competitor
            pattern_ids = self.competitor_patterns.get(competitor_id, [])
            patterns = [self.patterns[pid] for pid in pattern_ids if pid in self.patterns]
        else:
            # Get all patterns
            patterns = list(self.patterns.values())
            
        # Filter for active patterns
        active_patterns = [p for p in patterns if p.status in ["active", "emerging"]]
        
        return active_patterns
        
    def get_upcoming_pattern_events(self, days_ahead: int = 90) -> List[Dict]:
        """
        Get upcoming pattern-based events
        
        Parameters:
        - days_ahead: Number of days to look ahead
        
        Returns list of upcoming events
        """
        logger.info(f"Getting upcoming pattern events for next {days_ahead} days")
        
        upcoming_events = []
        now = datetime.datetime.now()
        cutoff = now + datetime.timedelta(days=days_ahead)
        
        for pattern in self.patterns.values():
            if pattern.expected_next_occurrence and now <= pattern.expected_next_occurrence <= cutoff:
                # Get competitor name
                competitor_id = pattern.competitors[0] if pattern.competitors else None
                competitor_name = "Unknown"
                
                if competitor_id:
                    profile = self.competitor_monitor.competitors.get(competitor_id)
                    if profile:
                        competitor_name = profile.name
                        
                event = {
                    "pattern_id": pattern.pattern_id,
                    "pattern_name": pattern.name,
                    "pattern_type": pattern.pattern_type,
                    "competitor_id": competitor_id,
                    "competitor_name": competitor_name,
                    "expected_date": pattern.expected_next_occurrence,
                    "days_until": (pattern.expected_next_occurrence - now).days,
                    "confidence": pattern.confidence,
                    "description": f"Expected {pattern.pattern_type} activity based on historical pattern"
                }
                
                upcoming_events.append(event)
                
        # Sort by date
        upcoming_events.sort(key=lambda x: x["expected_date"])
        
        return upcoming_events
        
    def detect_all_patterns(self, competitor_id: str) -> Dict[str, List[PatternData]]:
        """
        Detect all types of patterns for a competitor
        
        Parameters:
        - competitor_id: ID of the competitor to analyze
        
        Returns dictionary of pattern types to lists of patterns
        """
        logger.info(f"Detecting all patterns for competitor {competitor_id}")
        
        pricing_patterns = self.detect_pricing_patterns(competitor_id)
        release_patterns = self.detect_release_cycles(competitor_id)
        marketing_patterns = self.detect_marketing_patterns(competitor_id)
        seasonal_patterns = self.detect_seasonal_patterns(competitor_id)
        
        return {
            "pricing": pricing_patterns,
            "release": release_patterns,
            "marketing": marketing_patterns,
            "seasonal": seasonal_patterns
        }
        
    def run_pattern_detection(self) -> Dict[str, Dict]:
        """
        Run pattern detection for all competitors
        
        Returns results by competitor
        """
        logger.info("Running pattern detection for all competitors")
        
        results = {}
        
        for competitor_id in self.competitor_monitor.competitors:
            patterns = self.detect_all_patterns(competitor_id)
            
            total_patterns = sum(len(p) for p in patterns.values())
            
            results[competitor_id] = {
                "total_patterns": total_patterns,
                "patterns_by_type": {k: len(v) for k, v in patterns.items()}
            }
            
        # Get upcoming events
        upcoming_events = self.get_upcoming_pattern_events()
        
        return {
            "competitor_results": results,
            "total_patterns": len(self.patterns),
            "upcoming_events": len(upcoming_events)
        }
