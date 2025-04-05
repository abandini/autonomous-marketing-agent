"""
Competitive Intelligence Module for GAMS

This module provides comprehensive competitive intelligence capabilities including:
1. Comprehensive Monitoring System
   - Real-Time Competitor Tracking
   - Market Positioning Analysis
   - Competitive Benchmark Alerts
2. Strategic Response System 
   - Countermeasure Development
   - Opportunity Gap Exploitation
   - War Gaming Simulation
3. Insight Integration
   - Cross-Team Intelligence Distribution
   - AI-Powered Competitive Analysis
   - Knowledge Repository Management

The module enables GAMS to monitor the competitive landscape and proactively 
generate strategic responses to maintain or enhance market position.
"""

from .monitoring import CompetitorMonitor, MarketPositionAnalyzer, BenchmarkAlertSystem
from .response import CountermeasureEngine
from .opportunity import OpportunityAnalyzer
from .wargaming import WarGamingSimulator
from .insights import CrossTeamDistributor, CompetitiveInsight
from .ai_analysis import SentimentAnalyzer
from .pattern_recognizer import PatternRecognizer, PatternData
from .predictive_modeler import PredictiveModeler, PredictionData
from .trend_analyzer import TrendAnalyzer, TrendData
from .knowledge_repository import KnowledgeRepository, CompetitiveEvent, CompetitiveInsight
from .manager import CompetitiveIntelligenceManager

__all__ = [
    # Monitoring System
    'CompetitorMonitor', 
    'MarketPositionAnalyzer', 
    'BenchmarkAlertSystem',

    # Strategic Response System
    'CountermeasureEngine', 
    'OpportunityAnalyzer', 
    'WarGamingSimulator',

    # Insight Integration
    'CrossTeamDistributor',
    'CompetitiveInsight',
    'SentimentAnalyzer',

    # Pattern Recognition
    'PatternRecognizer',
    'PatternData',

    # Predictive Modeling
    'PredictiveModeler',
    'PredictionData',

    # Trend Analysis
    'TrendAnalyzer',
    'TrendData',

    # Knowledge Management
    'KnowledgeRepository',
    'CompetitiveEvent',
    'CompetitiveInsight',

    # Integration Manager
    'CompetitiveIntelligenceManager'
]
