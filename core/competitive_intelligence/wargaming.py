"""
War Gaming Simulation

This module provides tools for simulating competitive responses and modeling
what-if scenarios to test strategic options.
"""

import logging
import json
import datetime
import random
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass

from .monitoring import CompetitorMonitor, MarketPositionAnalyzer, CompetitorProfile
from .response import WarGameScenario, StrategicResponse

logger = logging.getLogger(__name__)

class WarGamingSimulator:
    """
    War Gaming Simulation
    
    Simulates competitive responses to strategic moves and models
    what-if scenarios to evaluate potential outcomes.
    """
    
    def __init__(self, competitor_monitor: CompetitorMonitor, 
                 position_analyzer: MarketPositionAnalyzer):
        """Initialize with references to other components"""
        self.competitor_monitor = competitor_monitor
        self.position_analyzer = position_analyzer
        self.scenarios: List[WarGameScenario] = []
        self.simulation_runs: Dict[str, List[Dict]] = {}  # scenario_id -> list of simulation results
        logger.info("WarGamingSimulator initialized")
        
    def create_scenario(self, name: str, description: str, 
                       our_strategy: Dict[str, Any],
                       primary_competitors: List[str]) -> WarGameScenario:
        """
        Create a new war gaming scenario
        
        Parameters:
        - name: Scenario name
        - description: Scenario description
        - our_strategy: Dictionary describing our strategic approach
        - primary_competitors: List of competitor IDs to include in simulation
        
        Returns the created scenario
        """
        logger.info(f"Creating war gaming scenario: {name}")
        
        now = datetime.datetime.now()
        scenario_id = f"scenario_{now.strftime('%Y%m%d%H%M%S')}"
        
        # Initialize empty competitor responses
        competitor_responses = {}
        for competitor_id in primary_competitors:
            competitor_responses[competitor_id] = []
            
        # Initialize with default market conditions
        market_conditions = {
            "growth_rate": 0.05,  # 5% annual growth
            "disruption_level": 0.2,  # Low disruption
            "price_sensitivity": 0.5,  # Moderate price sensitivity
            "switching_costs": 0.4,  # Moderate switching costs
            "regulatory_factors": []
        }
        
        # Initialize with empty outcomes
        outcomes = {
            "market_share_impact": {},
            "revenue_impact": {},
            "customer_retention": {},
            "brand_perception": {},
            "competitive_position": {}
        }
        
        # Initialize risk assessment
        risk_assessment = {
            "execution_risk": 0.3,  # Moderate execution risk
            "market_risk": 0.4,  # Moderate market risk
            "competitive_risk": 0.5,  # Moderate competitive risk
            "financial_risk": 0.3,  # Moderate financial risk
            "overall_risk": 0.4  # Moderate overall risk
        }
        
        scenario = WarGameScenario(
            id=scenario_id,
            name=name,
            description=description,
            primary_competitors=primary_competitors,
            our_strategy=our_strategy,
            competitor_responses=competitor_responses,
            market_conditions=market_conditions,
            outcomes=outcomes,
            probability=0.5,  # Default 50% probability
            created_at=now,
            risk_assessment=risk_assessment
        )
        
        self.scenarios.append(scenario)
        return scenario
        
    def model_competitor_responses(self, scenario_id: str) -> Dict[str, List[Dict]]:
        """
        Model likely responses from competitors based on historical behavior
        
        Parameters:
        - scenario_id: ID of the scenario to model
        
        Returns dictionary of competitor_id -> list of potential responses
        """
        logger.info(f"Modeling competitor responses for scenario {scenario_id}")
        
        # Find the scenario
        scenario = next((s for s in self.scenarios if s.id == scenario_id), None)
        if not scenario:
            logger.warning(f"Scenario {scenario_id} not found")
            return {}
            
        # Model responses for each competitor
        for competitor_id in scenario.primary_competitors:
            profile = self.competitor_monitor.competitors.get(competitor_id)
            if not profile:
                continue
                
            # Clear previous responses
            scenario.competitor_responses[competitor_id] = []
            
            # Model potential responses based on competitor profile and our strategy
            # In a real implementation, this would use historical data and competitor behavior patterns
            
            # Determine response types based on our strategy
            response_types = []
            if scenario.our_strategy.get("type") == "price_change":
                response_types.append("price_match")
                response_types.append("value_proposition")
                
            elif scenario.our_strategy.get("type") == "product_launch":
                response_types.append("accelerate_roadmap")
                response_types.append("marketing_counter")
                
            elif scenario.our_strategy.get("type") == "market_expansion":
                response_types.append("defend_territory")
                response_types.append("partnership")
                
            else:
                # Default responses for any strategy
                response_types.append("marketing_counter")
                response_types.append("price_adjustment")
                
            # Generate 2-3 potential responses per competitor
            num_responses = random.randint(2, 3)
            for i in range(num_responses):
                response_type = response_types[i % len(response_types)]
                
                # Determine probability based on competitor profile
                # In a real implementation, this would be based on historical behavior
                probability = 0.3 + (random.random() * 0.5)  # 30-80% probability
                
                # Determine time frame
                time_frame = {
                    "min_days": 14 + (i * 7),  # 2-4 weeks
                    "max_days": 30 + (i * 14)  # 1-2 months
                }
                
                # Determine impact
                impact = {
                    "market_share": -0.02 + (random.random() * 0.04),  # -2% to +2%
                    "revenue": -0.03 + (random.random() * 0.06),  # -3% to +3%
                    "customer_retention": -0.01 + (random.random() * 0.02)  # -1% to +1%
                }
                
                response = {
                    "type": response_type,
                    "description": f"{profile.name} {self._get_response_description(response_type)}",
                    "probability": probability,
                    "time_frame": time_frame,
                    "impact": impact
                }
                
                scenario.competitor_responses[competitor_id].append(response)
                
        return scenario.competitor_responses
        
    def _get_response_description(self, response_type: str) -> str:
        """Helper method to get description for a response type"""
        descriptions = {
            "price_match": "matches our pricing strategy",
            "value_proposition": "emphasizes value proposition over price",
            "accelerate_roadmap": "accelerates their product roadmap",
            "marketing_counter": "launches counter-marketing campaign",
            "defend_territory": "increases focus on defending their territory",
            "partnership": "forms strategic partnership to strengthen position",
            "price_adjustment": "adjusts pricing to maintain competitive position"
        }
        return descriptions.get(response_type, "responds with a strategic adjustment")
        
    def run_what_if_simulation(self, scenario_id: str, num_simulations: int = 100) -> List[Dict]:
        """
        Run what-if simulations to test scenario outcomes
        
        Parameters:
        - scenario_id: ID of the scenario to simulate
        - num_simulations: Number of simulation runs
        
        Returns list of simulation results
        """
        logger.info(f"Running {num_simulations} what-if simulations for scenario {scenario_id}")
        
        # Find the scenario
        scenario = next((s for s in self.scenarios if s.id == scenario_id), None)
        if not scenario:
            logger.warning(f"Scenario {scenario_id} not found")
            return []
            
        # Ensure competitor responses are modeled
        if not any(scenario.competitor_responses.values()):
            self.model_competitor_responses(scenario_id)
            
        # Run simulations
        simulation_results = []
        
        for i in range(num_simulations):
            # Initialize simulation state
            sim_state = {
                "market_share": 0.2,  # Starting market share (20%)
                "revenue": 10000000,  # Starting revenue ($10M)
                "customer_retention": 0.85,  # Starting retention rate (85%)
                "brand_perception": 0.7,  # Starting brand perception (0-1 scale)
                "competitive_position": 0.6  # Starting competitive position (0-1 scale)
            }
            
            # Apply our strategy impact
            strategy_impact = self._calculate_strategy_impact(scenario.our_strategy)
            for metric, impact in strategy_impact.items():
                if metric in sim_state:
                    sim_state[metric] += impact
                    
            # Determine which competitor responses occur in this simulation
            active_responses = []
            for competitor_id, responses in scenario.competitor_responses.items():
                for response in responses:
                    # Check if response occurs based on probability
                    if random.random() < response["probability"]:
                        # Clone response and add competitor ID
                        active_response = response.copy()
                        active_response["competitor_id"] = competitor_id
                        active_responses.append(active_response)
                        
            # Sort responses by timing
            for response in active_responses:
                time_frame = response["time_frame"]
                response["activation_day"] = random.randint(time_frame["min_days"], time_frame["max_days"])
                
            active_responses.sort(key=lambda r: r["activation_day"])
            
            # Apply response impacts sequentially
            for response in active_responses:
                for metric, impact in response["impact"].items():
                    if metric in sim_state:
                        sim_state[metric] += impact
                        
            # Apply market condition effects
            market_impact = self._calculate_market_impact(scenario.market_conditions)
            for metric, impact in market_impact.items():
                if metric in sim_state:
                    sim_state[metric] += impact
                    
            # Ensure values are within reasonable bounds
            sim_state["market_share"] = max(0.01, min(1.0, sim_state["market_share"]))
            sim_state["customer_retention"] = max(0.5, min(0.99, sim_state["customer_retention"]))
            sim_state["brand_perception"] = max(0.1, min(1.0, sim_state["brand_perception"]))
            sim_state["competitive_position"] = max(0.1, min(1.0, sim_state["competitive_position"]))
            
            # Add simulation result
            simulation_results.append({
                "simulation_id": i,
                "active_responses": active_responses,
                "final_state": sim_state
            })
            
        # Store simulation results
        self.simulation_runs[scenario_id] = simulation_results
        
        # Update scenario outcomes based on average results
        self._update_scenario_outcomes(scenario, simulation_results)
        
        return simulation_results
        
    def _calculate_strategy_impact(self, strategy: Dict[str, Any]) -> Dict[str, float]:
        """Calculate the impact of our strategy on key metrics"""
        # In a real implementation, this would use more sophisticated models
        
        impact = {
            "market_share": 0.0,
            "revenue": 0.0,
            "customer_retention": 0.0,
            "brand_perception": 0.0,
            "competitive_position": 0.0
        }
        
        strategy_type = strategy.get("type", "")
        intensity = strategy.get("intensity", 0.5)  # 0-1 scale
        
        if strategy_type == "price_change":
            direction = strategy.get("direction", "decrease")
            if direction == "decrease":
                impact["market_share"] = 0.03 * intensity
                impact["revenue"] = -0.05 * intensity
                impact["customer_retention"] = 0.02 * intensity
            else:
                impact["market_share"] = -0.02 * intensity
                impact["revenue"] = 0.04 * intensity
                impact["customer_retention"] = -0.01 * intensity
                
        elif strategy_type == "product_launch":
            impact["market_share"] = 0.05 * intensity
            impact["revenue"] = 0.07 * intensity
            impact["brand_perception"] = 0.04 * intensity
            impact["competitive_position"] = 0.06 * intensity
            
        elif strategy_type == "market_expansion":
            impact["market_share"] = 0.04 * intensity
            impact["revenue"] = 0.06 * intensity
            impact["competitive_position"] = 0.03 * intensity
            
        elif strategy_type == "marketing_campaign":
            impact["brand_perception"] = 0.05 * intensity
            impact["market_share"] = 0.02 * intensity
            
        return impact
        
    def _calculate_market_impact(self, market_conditions: Dict[str, Any]) -> Dict[str, float]:
        """Calculate the impact of market conditions on key metrics"""
        # In a real implementation, this would use more sophisticated models
        
        impact = {
            "market_share": 0.0,
            "revenue": 0.0,
            "customer_retention": 0.0,
            "brand_perception": 0.0,
            "competitive_position": 0.0
        }
        
        growth_rate = market_conditions.get("growth_rate", 0.05)
        disruption_level = market_conditions.get("disruption_level", 0.2)
        price_sensitivity = market_conditions.get("price_sensitivity", 0.5)
        
        # Apply growth rate effect
        impact["market_share"] += growth_rate * 0.1  # Small positive effect
        impact["revenue"] += growth_rate * 0.2  # Larger positive effect
        
        # Apply disruption effect (usually negative)
        impact["market_share"] -= disruption_level * 0.05
        impact["competitive_position"] -= disruption_level * 0.1
        
        # Apply price sensitivity effect
        if price_sensitivity > 0.7:  # High price sensitivity
            impact["customer_retention"] -= 0.02
            
        return impact
        
    def _update_scenario_outcomes(self, scenario: WarGameScenario, simulation_results: List[Dict]):
        """Update scenario outcomes based on simulation results"""
        if not simulation_results:
            return
            
        # Calculate average outcomes
        avg_outcomes = {
            "market_share_impact": 0.0,
            "revenue_impact": 0.0,
            "customer_retention": 0.0,
            "brand_perception": 0.0,
            "competitive_position": 0.0
        }
        
        # Starting values (assumed)
        base_values = {
            "market_share": 0.2,
            "revenue": 10000000,
            "customer_retention": 0.85,
            "brand_perception": 0.7,
            "competitive_position": 0.6
        }
        
        # Sum final states
        for result in simulation_results:
            final_state = result["final_state"]
            for metric in avg_outcomes:
                simple_metric = metric.replace("_impact", "")
                if simple_metric in final_state:
                    avg_outcomes[metric] += final_state[simple_metric]
                    
        # Calculate averages
        num_sims = len(simulation_results)
        for metric in avg_outcomes:
            avg_outcomes[metric] /= num_sims
            
        # Convert to impacts for market_share and revenue
        avg_outcomes["market_share_impact"] -= base_values["market_share"]
        avg_outcomes["revenue_impact"] = (avg_outcomes["revenue_impact"] - base_values["revenue"]) / base_values["revenue"]
        
        # Update scenario outcomes
        scenario.outcomes = {
            "market_share_impact": avg_outcomes["market_share_impact"],
            "revenue_impact": avg_outcomes["revenue_impact"],
            "customer_retention": avg_outcomes["customer_retention"],
            "brand_perception": avg_outcomes["brand_perception"],
            "competitive_position": avg_outcomes["competitive_position"],
            "simulation_count": num_sims
        }
        
        # Update scenario probability based on positive outcomes
        positive_outcomes = sum(1 for metric, value in avg_outcomes.items() 
                              if (metric.endswith("_impact") and value > 0) or 
                                 (not metric.endswith("_impact") and value > base_values.get(metric, 0)))
                                 
        scenario.probability = min(0.9, max(0.1, positive_outcomes / len(avg_outcomes)))
        
        # Update risk assessment
        scenario.risk_assessment = self._calculate_risk_assessment(scenario, simulation_results)
        
    def _calculate_risk_assessment(self, scenario: WarGameScenario, simulation_results: List[Dict]) -> Dict[str, float]:
        """Calculate risk assessment based on simulation variability"""
        if not simulation_results:
            return scenario.risk_assessment
            
        # Calculate variance in outcomes
        variances = {
            "market_share": 0.0,
            "revenue": 0.0,
            "customer_retention": 0.0,
            "brand_perception": 0.0,
            "competitive_position": 0.0
        }
        
        # Calculate means
        means = {metric: 0.0 for metric in variances}
        for result in simulation_results:
            for metric in means:
                means[metric] += result["final_state"].get(metric, 0)
                
        for metric in means:
            means[metric] /= len(simulation_results)
            
        # Calculate variances
        for result in simulation_results:
            for metric in variances:
                value = result["final_state"].get(metric, 0)
                variances[metric] += (value - means[metric]) ** 2
                
        for metric in variances:
            variances[metric] /= len(simulation_results)
            
        # Convert variances to risk scores (higher variance = higher risk)
        risk_assessment = {
            "execution_risk": 0.3,  # Base execution risk
            "market_risk": 0.3 + (variances["market_share"] * 5),  # Scale variance to 0-1 range
            "competitive_risk": 0.3 + (variances["competitive_position"] * 5),
            "financial_risk": 0.3 + (variances["revenue"] / 1000000)  # Scale based on revenue variance
        }
        
        # Cap risk values
        for key in risk_assessment:
            risk_assessment[key] = min(0.9, max(0.1, risk_assessment[key]))
            
        # Calculate overall risk
        risk_assessment["overall_risk"] = sum(risk_assessment.values()) / len(risk_assessment)
        
        return risk_assessment
        
    def evaluate_scenario_outcomes(self, scenario_id: str) -> Dict:
        """
        Evaluate outcomes and risks of a simulated scenario
        
        Parameters:
        - scenario_id: ID of the scenario to evaluate
        
        Returns evaluation results
        """
        logger.info(f"Evaluating outcomes for scenario {scenario_id}")
        
        # Find the scenario
        scenario = next((s for s in self.scenarios if s.id == scenario_id), None)
        if not scenario:
            logger.warning(f"Scenario {scenario_id} not found")
            return {}
            
        # Check if simulations have been run
        if scenario_id not in self.simulation_runs:
            logger.warning(f"No simulation runs found for scenario {scenario_id}")
            return {}
            
        # Evaluate outcomes
        evaluation = {
            "scenario_name": scenario.name,
            "outcomes": scenario.outcomes,
            "risk_assessment": scenario.risk_assessment,
            "probability": scenario.probability,
            "recommendation": self._generate_recommendation(scenario)
        }
        
        return evaluation
        
    def _generate_recommendation(self, scenario: WarGameScenario) -> Dict:
        """Generate a recommendation based on scenario outcomes and risks"""
        outcomes = scenario.outcomes
        risks = scenario.risk_assessment
        
        # Determine if outcomes are generally positive
        positive_outcomes = (
            outcomes.get("market_share_impact", 0) > 0 and
            outcomes.get("revenue_impact", 0) > 0 and
            outcomes.get("competitive_position", 0) > 0.5
        )
        
        # Determine if risks are acceptable
        acceptable_risk = risks.get("overall_risk", 1.0) < 0.6
        
        # Generate recommendation
        if positive_outcomes and acceptable_risk:
            recommendation = {
                "action": "proceed",
                "confidence": min(0.9, scenario.probability + 0.1),
                "rationale": "Positive expected outcomes with acceptable risk levels",
                "modifications": []
            }
        elif positive_outcomes:
            recommendation = {
                "action": "proceed_with_caution",
                "confidence": scenario.probability,
                "rationale": "Positive expected outcomes but significant risks",
                "modifications": [
                    "Implement risk mitigation measures",
                    "Phase implementation to allow for adjustments"
                ]
            }
        elif acceptable_risk:
            recommendation = {
                "action": "modify",
                "confidence": scenario.probability - 0.1,
                "rationale": "Low risk but limited positive outcomes",
                "modifications": [
                    "Increase strategy intensity",
                    "Combine with complementary initiatives"
                ]
            }
        else:
            recommendation = {
                "action": "reconsider",
                "confidence": max(0.1, scenario.probability - 0.2),
                "rationale": "High risk with limited positive outcomes",
                "modifications": [
                    "Fundamentally redesign strategy",
                    "Consider alternative approaches"
                ]
            }
            
        return recommendation
        
    def compare_scenarios(self, scenario_ids: List[str]) -> Dict:
        """
        Compare multiple scenarios to identify optimal approach
        
        Parameters:
        - scenario_ids: List of scenario IDs to compare
        
        Returns comparison results
        """
        logger.info(f"Comparing {len(scenario_ids)} scenarios")
        
        # Get scenarios
        scenarios = [s for s in self.scenarios if s.id in scenario_ids]
        if not scenarios:
            logger.warning("No valid scenarios found for comparison")
            return {}
            
        # Ensure all scenarios have been simulated
        for scenario in scenarios:
            if scenario.id not in self.simulation_runs:
                logger.warning(f"Scenario {scenario.id} has not been simulated")
                return {}
                
        # Compare key metrics
        comparison = {
            "scenarios": [{"id": s.id, "name": s.name} for s in scenarios],
            "market_share_impact": {s.id: s.outcomes.get("market_share_impact", 0) for s in scenarios},
            "revenue_impact": {s.id: s.outcomes.get("revenue_impact", 0) for s in scenarios},
            "risk_levels": {s.id: s.risk_assessment.get("overall_risk", 0) for s in scenarios},
            "probabilities": {s.id: s.probability for s in scenarios}
        }
        
        # Calculate combined score (outcome * probability / risk)
        scores = {}
        for scenario in scenarios:
            outcome_score = (
                scenario.outcomes.get("market_share_impact", 0) * 5 +  # Weight market share higher
                scenario.outcomes.get("revenue_impact", 0) * 3 +       # Weight revenue
                scenario.outcomes.get("competitive_position", 0)        # Include competitive position
            ) / 9  # Normalize
            
            risk = max(0.1, scenario.risk_assessment.get("overall_risk", 0.5))
            scores[scenario.id] = (outcome_score * scenario.probability) / risk
            
        comparison["scores"] = scores
        
        # Identify optimal scenario
        if scores:
            optimal_id = max(scores.items(), key=lambda x: x[1])[0]
            optimal_scenario = next(s for s in scenarios if s.id == optimal_id)
            
            comparison["optimal_scenario"] = {
                "id": optimal_id,
                "name": optimal_scenario.name,
                "score": scores[optimal_id],
                "recommendation": self._generate_recommendation(optimal_scenario)
            }
            
        return comparison
        
    def get_scenarios(self) -> List[Dict]:
        """
        Get summary information for all scenarios
        
        Returns list of scenario summaries
        """
        return [
            {
                "id": scenario.id,
                "name": scenario.name,
                "description": scenario.description,
                "created_at": scenario.created_at,
                "num_competitors": len(scenario.primary_competitors),
                "has_simulations": scenario.id in self.simulation_runs,
                "probability": scenario.probability,
                "overall_risk": scenario.risk_assessment.get("overall_risk", 0)
            }
            for scenario in self.scenarios
        ]
