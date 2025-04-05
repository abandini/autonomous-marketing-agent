"""
Insight Integration

This module provides tools for cross-team intelligence distribution, AI-powered
competitive analysis, and knowledge repository management.
"""

import logging
import json
import datetime
import os
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass

from .monitoring import CompetitorMonitor, MarketPositionAnalyzer, BenchmarkAlertSystem, CompetitiveAlert
from .response import CountermeasureEngine, StrategicResponse
from .opportunity import OpportunityAnalyzer, MarketOpportunity
from .wargaming import WarGamingSimulator, WarGameScenario

logger = logging.getLogger(__name__)

@dataclass
class CompetitiveInsight:
    """Data structure for competitive insights"""
    id: str
    title: str
    description: str
    insight_type: str  # market, competitor, strategy, opportunity, threat
    source_type: str  # alert, response, opportunity, wargame, analysis
    source_id: str
    related_competitors: List[str]
    priority: int  # 1-5 scale
    created_at: datetime.datetime
    expiration_date: Optional[datetime.datetime] = None
    tags: List[str] = None
    distribution_targets: List[str] = None  # teams/departments
    viewed_by: List[str] = None
    actions_taken: List[Dict] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.distribution_targets is None:
            self.distribution_targets = []
        if self.viewed_by is None:
            self.viewed_by = []
        if self.actions_taken is None:
            self.actions_taken = []


class CrossTeamDistributor:
    """
    Cross-Team Intelligence Distribution
    
    Distributes competitive insights to relevant teams, formats intelligence
    for different stakeholders, and tracks usage and impact.
    """
    
    def __init__(self, competitor_monitor: CompetitorMonitor,
                 alert_system: BenchmarkAlertSystem,
                 countermeasure_engine: CountermeasureEngine,
                 opportunity_analyzer: OpportunityAnalyzer,
                 wargaming_simulator: WarGamingSimulator):
        """Initialize with references to other components"""
        self.competitor_monitor = competitor_monitor
        self.alert_system = alert_system
        self.countermeasure_engine = countermeasure_engine
        self.opportunity_analyzer = opportunity_analyzer
        self.wargaming_simulator = wargaming_simulator
        self.insights: List[CompetitiveInsight] = []
        self.teams = ["marketing", "product", "sales", "executive", "r&d", "customer_success"]
        self.distribution_rules = self._load_distribution_rules()
        logger.info("CrossTeamDistributor initialized")
        
    def _load_distribution_rules(self) -> Dict[str, List[str]]:
        """Load rules for which teams should receive which types of insights"""
        # In a real implementation, these would be loaded from a configuration file
        return {
            "market": ["marketing", "executive", "sales"],
            "competitor": ["marketing", "product", "sales", "executive"],
            "strategy": ["executive", "marketing", "product"],
            "opportunity": ["product", "marketing", "sales", "r&d"],
            "threat": ["executive", "marketing", "product", "sales"]
        }
        
    def generate_insights_from_alerts(self) -> List[CompetitiveInsight]:
        """
        Generate insights from competitive alerts
        
        Returns list of new insights
        """
        logger.info("Generating insights from alerts")
        
        new_insights = []
        now = datetime.datetime.now()
        
        # Get active alerts
        active_alerts = self.alert_system.get_active_alerts()
        
        for alert in active_alerts:
            # Check if we already have an insight for this alert
            if any(i for i in self.insights if i.source_type == "alert" and i.source_id == alert.id):
                continue
                
            # Map alert types to insight types
            insight_type_map = {
                "performance": "competitor",
                "strategy": "competitor",
                "emerging": "market",
                "threat": "threat",
                "disruption": "market"
            }
            
            insight_type = insight_type_map.get(alert.alert_type, "competitor")
            
            # Determine distribution targets based on insight type
            distribution_targets = self.distribution_rules.get(insight_type, [])
            
            # Create insight
            insight_id = f"insight_alert_{alert.id}"
            
            insight = CompetitiveInsight(
                id=insight_id,
                title=f"Alert: {alert.description}",
                description=f"Competitive alert detected: {alert.description}. Severity: {alert.severity}/5.",
                insight_type=insight_type,
                source_type="alert",
                source_id=alert.id,
                related_competitors=[alert.competitor_id],
                priority=alert.severity,
                created_at=now,
                expiration_date=now + datetime.timedelta(days=30),
                distribution_targets=distribution_targets
            )
            
            new_insights.append(insight)
            
        self.insights.extend(new_insights)
        return new_insights
        
    def generate_insights_from_responses(self) -> List[CompetitiveInsight]:
        """
        Generate insights from strategic responses
        
        Returns list of new insights
        """
        logger.info("Generating insights from strategic responses")
        
        new_insights = []
        now = datetime.datetime.now()
        
        # Get high-priority responses
        responses = self.countermeasure_engine.get_responses(min_priority=0.7)
        
        for response in responses:
            # Check if we already have an insight for this response
            if any(i for i in self.insights if i.source_type == "response" and i.source_id == response.id):
                continue
                
            # Map response types to insight types
            insight_type_map = {
                "defensive": "strategy",
                "offensive": "strategy",
                "preemptive": "strategy",
                "differentiation": "opportunity",
                "pivot": "strategy"
            }
            
            insight_type = insight_type_map.get(response.response_type, "strategy")
            
            # Determine distribution targets based on insight type
            distribution_targets = self.distribution_rules.get(insight_type, [])
            
            # Convert priority score (0-1) to priority level (1-5)
            priority = min(5, max(1, int(response.priority_score * 5)))
            
            # Create insight
            insight_id = f"insight_response_{response.id}"
            
            insight = CompetitiveInsight(
                id=insight_id,
                title=f"Strategic Response: {response.name}",
                description=f"Recommended strategic response: {response.description}. Priority: {priority}/5.",
                insight_type=insight_type,
                source_type="response",
                source_id=response.id,
                related_competitors=response.target_competitors,
                priority=priority,
                created_at=now,
                expiration_date=now + datetime.timedelta(days=90),
                distribution_targets=distribution_targets
            )
            
            new_insights.append(insight)
            
        self.insights.extend(new_insights)
        return new_insights
        
    def generate_insights_from_opportunities(self) -> List[CompetitiveInsight]:
        """
        Generate insights from market opportunities
        
        Returns list of new insights
        """
        logger.info("Generating insights from opportunities")
        
        new_insights = []
        now = datetime.datetime.now()
        
        # Get opportunities
        opportunities = self.opportunity_analyzer.get_opportunities()
        
        for opportunity in opportunities:
            # Check if we already have an insight for this opportunity
            if any(i for i in self.insights if i.source_type == "opportunity" and i.source_id == opportunity.id):
                continue
                
            # Determine priority based on opportunity value and difficulty
            # Higher value, lower difficulty = higher priority
            value_factor = min(5, int((opportunity.estimated_value or 1000000) / 1000000))
            difficulty_factor = 5 - min(5, max(1, int(opportunity.difficulty * 5)))
            priority = min(5, max(1, (value_factor + difficulty_factor) // 2))
            
            # Create insight
            insight_id = f"insight_opportunity_{opportunity.id}"
            
            insight = CompetitiveInsight(
                id=insight_id,
                title=f"Market Opportunity: {opportunity.name}",
                description=f"Identified market opportunity: {opportunity.description}. Priority: {priority}/5.",
                insight_type="opportunity",
                source_type="opportunity",
                source_id=opportunity.id,
                related_competitors=opportunity.related_competitors,
                priority=priority,
                created_at=now,
                expiration_date=now + datetime.timedelta(days=180),
                distribution_targets=self.distribution_rules.get("opportunity", [])
            )
            
            new_insights.append(insight)
            
        self.insights.extend(new_insights)
        return new_insights
        
    def generate_insights_from_wargames(self) -> List[CompetitiveInsight]:
        """
        Generate insights from war gaming simulations
        
        Returns list of new insights
        """
        logger.info("Generating insights from war gaming simulations")
        
        new_insights = []
        now = datetime.datetime.now()
        
        # Get scenarios
        scenarios = self.wargaming_simulator.scenarios
        
        for scenario in scenarios:
            # Check if we already have an insight for this scenario
            if any(i for i in self.insights if i.source_type == "wargame" and i.source_id == scenario.id):
                continue
                
            # Only create insights for scenarios that have been simulated
            if scenario.id not in self.wargaming_simulator.simulation_runs:
                continue
                
            # Determine priority based on scenario probability and risk
            probability_factor = min(5, max(1, int(scenario.probability * 5)))
            risk_factor = min(5, max(1, int(scenario.risk_assessment.get("overall_risk", 0.5) * 5)))
            priority = min(5, max(1, (probability_factor + risk_factor) // 2))
            
            # Create insight
            insight_id = f"insight_wargame_{scenario.id}"
            
            # Create description based on recommendation
            recommendation = self._generate_recommendation(scenario)
            
            insight = CompetitiveInsight(
                id=insight_id,
                title=f"War Game Simulation: {scenario.name}",
                description=f"War game simulation results for '{scenario.name}': {recommendation}. Priority: {priority}/5.",
                insight_type="strategy",
                source_type="wargame",
                source_id=scenario.id,
                related_competitors=scenario.primary_competitors,
                priority=priority,
                created_at=now,
                expiration_date=now + datetime.timedelta(days=90),
                distribution_targets=self.distribution_rules.get("strategy", [])
            )
            
            new_insights.append(insight)
            
        self.insights.extend(new_insights)
        return new_insights
        
    def _generate_recommendation(self, scenario: WarGameScenario) -> str:
        """Generate a recommendation string based on scenario outcomes"""
        outcomes = scenario.outcomes
        
        market_share_impact = outcomes.get("market_share_impact", 0)
        revenue_impact = outcomes.get("revenue_impact", 0)
        
        if market_share_impact > 0 and revenue_impact > 0:
            return f"Positive outcomes expected with {scenario.probability:.0%} probability. Recommend proceeding."
        elif market_share_impact > 0 or revenue_impact > 0:
            return f"Mixed outcomes expected with {scenario.probability:.0%} probability. Proceed with caution."
        else:
            return f"Negative outcomes likely with {scenario.probability:.0%} probability. Recommend reconsidering."
        
    def format_insight_for_team(self, insight: CompetitiveInsight, team: str) -> Dict:
        """
        Format an insight for a specific team's needs and perspective
        
        Parameters:
        - insight: The insight to format
        - team: The target team
        
        Returns formatted insight
        """
        # Base formatted insight
        formatted = {
            "id": insight.id,
            "title": insight.title,
            "description": insight.description,
            "priority": insight.priority,
            "created_at": insight.created_at,
            "expiration_date": insight.expiration_date
        }
        
        # Add team-specific formatting
        if team == "executive":
            # Executives need high-level strategic implications
            formatted["title"] = f"EXECUTIVE BRIEF: {insight.title}"
            formatted["strategic_implications"] = self._generate_strategic_implications(insight)
            formatted["financial_impact"] = self._estimate_financial_impact(insight)
            
        elif team == "marketing":
            # Marketing needs messaging and positioning implications
            formatted["title"] = f"MARKETING INSIGHT: {insight.title}"
            formatted["messaging_implications"] = self._generate_messaging_implications(insight)
            formatted["campaign_opportunities"] = self._identify_campaign_opportunities(insight)
            
        elif team == "product":
            # Product needs feature and roadmap implications
            formatted["title"] = f"PRODUCT INSIGHT: {insight.title}"
            formatted["feature_implications"] = self._generate_feature_implications(insight)
            formatted["roadmap_impact"] = self._assess_roadmap_impact(insight)
            
        elif team == "sales":
            # Sales needs competitive positioning and objection handling
            formatted["title"] = f"SALES INSIGHT: {insight.title}"
            formatted["competitive_positioning"] = self._generate_competitive_positioning(insight)
            formatted["objection_handling"] = self._generate_objection_handling(insight)
            
        return formatted
        
    def _generate_strategic_implications(self, insight: CompetitiveInsight) -> str:
        """Generate strategic implications for executive team"""
        # Placeholder implementation
        if insight.insight_type == "threat":
            return "This represents a significant competitive threat that may impact market position and revenue growth if not addressed."
        elif insight.insight_type == "opportunity":
            return "This opportunity could strengthen our competitive position and open new revenue streams if properly executed."
        else:
            return "This insight has implications for our overall market strategy and competitive positioning."
            
    def _estimate_financial_impact(self, insight: CompetitiveInsight) -> Dict:
        """Estimate financial impact for executive team"""
        # Placeholder implementation
        return {
            "revenue_impact": f"{(insight.priority * 2)}% potential change",
            "market_share_impact": f"{insight.priority}% potential change",
            "confidence": "medium"
        }
        
    def _generate_messaging_implications(self, insight: CompetitiveInsight) -> str:
        """Generate messaging implications for marketing team"""
        # Placeholder implementation
        if insight.insight_type == "competitor":
            return "Adjust messaging to highlight our strengths against competitor's recent moves."
        elif insight.insight_type == "opportunity":
            return "Develop messaging that emphasizes our unique ability to address this market need."
        else:
            return "Consider how this insight should influence our brand positioning and marketing messages."
            
    def _identify_campaign_opportunities(self, insight: CompetitiveInsight) -> List[str]:
        """Identify campaign opportunities for marketing team"""
        # Placeholder implementation
        if insight.insight_type == "competitor":
            return ["Comparative campaign highlighting differentiators", "Customer testimonial campaign"]
        elif insight.insight_type == "opportunity":
            return ["Thought leadership campaign on emerging needs", "Solution spotlight campaign"]
        else:
            return ["Brand awareness campaign", "Value proposition campaign"]
            
    def _generate_feature_implications(self, insight: CompetitiveInsight) -> str:
        """Generate feature implications for product team"""
        # Placeholder implementation
        if insight.insight_type == "competitor":
            return "Evaluate our feature set against competitor's recent changes to identify gaps or opportunities."
        elif insight.insight_type == "opportunity":
            return "Consider new features or enhancements that would address this market opportunity."
        else:
            return "Review product roadmap to ensure alignment with this competitive insight."
            
    def _assess_roadmap_impact(self, insight: CompetitiveInsight) -> Dict:
        """Assess roadmap impact for product team"""
        # Placeholder implementation
        if insight.priority >= 4:
            return {
                "impact_level": "high",
                "recommendation": "Consider reprioritizing roadmap",
                "affected_areas": ["Feature development", "UX improvements"]
            }
        elif insight.priority >= 2:
            return {
                "impact_level": "medium",
                "recommendation": "Monitor closely for roadmap implications",
                "affected_areas": ["Feature enhancements"]
            }
        else:
            return {
                "impact_level": "low",
                "recommendation": "No immediate roadmap changes needed",
                "affected_areas": []
            }
            
    def _generate_competitive_positioning(self, insight: CompetitiveInsight) -> List[str]:
        """Generate competitive positioning points for sales team"""
        # Placeholder implementation
        return [
            "Emphasize our superior customer support and implementation services",
            "Highlight our more comprehensive feature set in key areas",
            "Focus on our stronger integration capabilities and ecosystem"
        ]
        
    def _generate_objection_handling(self, insight: CompetitiveInsight) -> Dict[str, str]:
        """Generate objection handling guidance for sales team"""
        # Placeholder implementation
        return {
            "competitor_has_lower_price": "Focus on total cost of ownership and ROI rather than upfront cost",
            "competitor_has_specific_feature": "Emphasize our roadmap and the comprehensive nature of our solution",
            "competitor_claims_faster_implementation": "Highlight our proven implementation methodology and success stories"
        }
        
    def distribute_insights(self) -> Dict[str, List[Dict]]:
        """
        Distribute insights to relevant teams
        
        Returns dictionary of team -> list of formatted insights
        """
        logger.info("Distributing insights to teams")
        
        # Generate new insights from all sources
        self.generate_insights_from_alerts()
        self.generate_insights_from_responses()
        self.generate_insights_from_opportunities()
        self.generate_insights_from_wargames()
        
        # Distribute to teams
        distribution = {team: [] for team in self.teams}
        
        for insight in self.insights:
            for team in insight.distribution_targets:
                if team in self.teams:
                    formatted_insight = self.format_insight_for_team(insight, team)
                    distribution[team].append(formatted_insight)
                    
        logger.info(f"Distributed {len(self.insights)} insights to {len(self.teams)} teams")
        return distribution
        
    def create_insight_report(self, team: str, format_type: str = "html") -> str:
        """
        Create a formatted report of insights for a specific team
        
        Parameters:
        - team: Target team
        - format_type: Report format (html, markdown, plain)
        
        Returns formatted report
        """
        logger.info(f"Creating {format_type} insight report for {team}")
        
        # Get insights for team
        team_insights = []
        for insight in self.insights:
            if team in insight.distribution_targets:
                formatted_insight = self.format_insight_for_team(insight, team)
                team_insights.append(formatted_insight)
                
        # Sort by priority (highest first)
        team_insights.sort(key=lambda x: x["priority"], reverse=True)
        
        # Generate report based on format type
        if format_type == "html":
            return self._generate_html_report(team, team_insights)
        elif format_type == "markdown":
            return self._generate_markdown_report(team, team_insights)
        else:
            return self._generate_plain_report(team, team_insights)
            
    def _generate_html_report(self, team: str, insights: List[Dict]) -> str:
        """Generate HTML report"""
        # Placeholder implementation
        html = f"""
        <html>
        <head>
            <title>Competitive Intelligence Report for {team.capitalize()} Team</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                .insight {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
                .priority-5 {{ border-left: 5px solid #e74c3c; }}
                .priority-4 {{ border-left: 5px solid #e67e22; }}
                .priority-3 {{ border-left: 5px solid #f1c40f; }}
                .priority-2 {{ border-left: 5px solid #3498db; }}
                .priority-1 {{ border-left: 5px solid #2ecc71; }}
                .insight-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .insight-description {{ margin-bottom: 15px; }}
                .insight-meta {{ color: #7f8c8d; font-size: 14px; }}
                .section {{ margin-top: 15px; }}
                .section-title {{ font-weight: bold; margin-bottom: 5px; }}
            </style>
        </head>
        <body>
            <h1>Competitive Intelligence Report for {team.capitalize()} Team</h1>
            <p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            
            <h2>Summary</h2>
            <p>This report contains {len(insights)} competitive insights relevant to your team.</p>
            
            <h2>Insights</h2>
        """
        
        for insight in insights:
            html += f"""
            <div class="insight priority-{insight['priority']}">
                <div class="insight-title">{insight['title']}</div>
                <div class="insight-description">{insight['description']}</div>
                <div class="insight-meta">Priority: {insight['priority']}/5 | Created: {insight['created_at'].strftime('%Y-%m-%d')}</div>
            """
            
            # Add team-specific sections
            for key, value in insight.items():
                if key not in ["id", "title", "description", "priority", "created_at", "expiration_date"]:
                    html += f"""
                    <div class="section">
                        <div class="section-title">{key.replace('_', ' ').title()}:</div>
                    """
                    
                    if isinstance(value, list):
                        html += "<ul>"
                        for item in value:
                            html += f"<li>{item}</li>"
                        html += "</ul>"
                    elif isinstance(value, dict):
                        html += "<ul>"
                        for k, v in value.items():
                            html += f"<li><strong>{k.replace('_', ' ').title()}:</strong> {v}</li>"
                        html += "</ul>"
                    else:
                        html += f"<p>{value}</p>"
                        
                    html += "</div>"
                    
            html += "</div>"
            
        html += """
        </body>
        </html>
        """
        
        return html
        
    def _generate_markdown_report(self, team: str, insights: List[Dict]) -> str:
        """Generate Markdown report"""
        # Placeholder implementation
        markdown = f"""
# Competitive Intelligence Report for {team.capitalize()} Team

Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary

This report contains {len(insights)} competitive insights relevant to your team.

## Insights

"""
        
        for insight in insights:
            markdown += f"""
### {insight['title']}

{insight['description']}

**Priority:** {insight['priority']}/5 | **Created:** {insight['created_at'].strftime('%Y-%m-%d')}
"""
            
            # Add team-specific sections
            for key, value in insight.items():
                if key not in ["id", "title", "description", "priority", "created_at", "expiration_date"]:
                    markdown += f"""
#### {key.replace('_', ' ').title()}:

"""
                    
                    if isinstance(value, list):
                        for item in value:
                            markdown += f"- {item}\n"
                    elif isinstance(value, dict):
                        for k, v in value.items():
                            markdown += f"- **{k.replace('_', ' ').title()}:** {v}\n"
                    else:
                        markdown += f"{value}\n"
                        
            markdown += "\n---\n"
            
        return markdown
        
    def _generate_plain_report(self, team: str, insights: List[Dict]) -> str:
        """Generate plain text report"""
        # Placeholder implementation
        text = f"""
COMPETITIVE INTELLIGENCE REPORT FOR {team.upper()} TEAM
Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

SUMMARY
This report contains {len(insights)} competitive insights relevant to your team.

INSIGHTS
"""
        
        for i, insight in enumerate(insights, 1):
            text += f"""
{i}. {insight['title']}
   {insight['description']}
   Priority: {insight['priority']}/5 | Created: {insight['created_at'].strftime('%Y-%m-%d')}
"""
            
            # Add team-specific sections
            for key, value in insight.items():
                if key not in ["id", "title", "description", "priority", "created_at", "expiration_date"]:
                    text += f"""
   {key.replace('_', ' ').title()}:
"""
                    
                    if isinstance(value, list):
                        for item in value:
                            text += f"   - {item}\n"
                    elif isinstance(value, dict):
                        for k, v in value.items():
                            text += f"   - {k.replace('_', ' ').title()}: {v}\n"
                    else:
                        text += f"   {value}\n"
                        
            text += "\n" + "-" * 50 + "\n"
            
        return text
        
    def track_insight_usage(self, insight_id: str, user: str, action: str) -> bool:
        """
        Track usage of an insight
        
        Parameters:
        - insight_id: ID of the insight
        - user: User who viewed/used the insight
        - action: Action taken (viewed, shared, implemented)
        
        Returns success flag
        """
        for insight in self.insights:
            if insight.id == insight_id:
                # Track viewing
                if action == "viewed" and user not in insight.viewed_by:
                    insight.viewed_by.append(user)
                    
                # Track actions
                if action in ["shared", "implemented"]:
                    insight.actions_taken.append({
                        "user": user,
                        "action": action,
                        "timestamp": datetime.datetime.now()
                    })
                    
                logger.info(f"Tracked {action} action for insight {insight_id} by {user}")
                return True
                
        logger.warning(f"Insight {insight_id} not found for tracking")
        return False
        
    def get_insight_metrics(self) -> Dict:
        """
        Get metrics on insight distribution and usage
        
        Returns metrics dictionary
        """
        metrics = {
            "total_insights": len(self.insights),
            "by_type": {},
            "by_priority": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "by_team": {team: 0 for team in self.teams},
            "viewed_rate": 0,
            "action_rate": 0
        }
        
        # Count by type
        for insight in self.insights:
            # By type
            if insight.insight_type not in metrics["by_type"]:
                metrics["by_type"][insight.insight_type] = 0
            metrics["by_type"][insight.insight_type] += 1
            
            # By priority
            metrics["by_priority"][insight.priority] += 1
            
            # By team
            for team in insight.distribution_targets:
                if team in metrics["by_team"]:
                    metrics["by_team"][team] += 1
                    
        # Calculate view and action rates
        total_potential_views = sum(len(insight.distribution_targets) for insight in self.insights)
        total_actual_views = sum(len(insight.viewed_by) for insight in self.insights)
        total_actions = sum(len(insight.actions_taken) for insight in self.insights)
        
        if total_potential_views > 0:
            metrics["viewed_rate"] = total_actual_views / total_potential_views
            
        if total_actual_views > 0:
            metrics["action_rate"] = total_actions / total_actual_views
            
        return metrics
