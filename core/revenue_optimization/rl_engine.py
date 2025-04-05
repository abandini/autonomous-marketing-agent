"""
Reinforcement Learning Engine for Continuous Revenue Optimization

This module implements a reinforcement learning (RL) agent that autonomously 
conducts experiments and optimizes actions to maximize revenue and profitability.
"""

import os
import json
import time
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RLEngine:
    """
    Reinforcement Learning Engine for revenue optimization.
    
    This class implements a reinforcement learning agent that continuously
    experiments with and optimizes various marketing actions to maximize
    revenue and profitability.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the RL Engine.
        
        Args:
            config_path: Path to the configuration file for the RL Engine.
                         If None, uses default configuration.
        """
        self.config = self._load_config(config_path)
        self.state = None
        self.action_history = []
        self.reward_history = []
        self.policy = None
        self.exploration_strategy = self._initialize_exploration_strategy()
        self.constraints = self.config.get('constraints', {})
        self.action_space = self._initialize_action_space()
        self.state_space = self._initialize_state_space()
        self.model = self._initialize_model()
        
        logger.info("RL Engine initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file or use default.
        
        Args:
            config_path: Path to configuration file.
            
        Returns:
            Configuration dictionary.
        """
        default_config = {
            'learning_rate': 0.01,
            'discount_factor': 0.95,
            'exploration_strategy': {
                'type': 'epsilon_greedy',
                'initial_epsilon': 0.3,
                'min_epsilon': 0.05,
                'decay_rate': 0.001
            },
            'constraints': {
                'max_budget': 10000,
                'min_profit_margin': 0.2,
                'max_risk_level': 0.5
            },
            'reward_weights': {
                'revenue': 0.6,
                'profit': 0.3,
                'growth': 0.1
            },
            'action_space': {
                'content_type': ['blog', 'video', 'infographic', 'ebook', 'case_study'],
                'pricing': {
                    'min': 0.0,
                    'max': 1000.0,
                    'step': 5.0
                },
                'ad_spend': {
                    'min': 0.0,
                    'max': 5000.0,
                    'step': 50.0
                },
                'seo_tactics': ['keyword_optimization', 'backlink_building', 'content_refresh', 'technical_seo'],
                'affiliate_products': ['add', 'remove', 'replace', 'adjust_commission']
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with default config to ensure all required fields exist
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict) and isinstance(config[key], dict):
                            for subkey, subvalue in value.items():
                                if subkey not in config[key]:
                                    config[key][subkey] = subvalue
                return config
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {e}")
                return default_config
        else:
            logger.info("Using default RL Engine configuration")
            return default_config
    
    def _initialize_exploration_strategy(self) -> Dict:
        """
        Initialize the exploration strategy based on configuration.
        
        Returns:
            Dictionary containing exploration strategy parameters.
        """
        strategy_config = self.config.get('exploration_strategy', {})
        strategy_type = strategy_config.get('type', 'epsilon_greedy')
        
        if strategy_type == 'epsilon_greedy':
            return {
                'type': 'epsilon_greedy',
                'epsilon': strategy_config.get('initial_epsilon', 0.3),
                'min_epsilon': strategy_config.get('min_epsilon', 0.05),
                'decay_rate': strategy_config.get('decay_rate', 0.001)
            }
        elif strategy_type == 'ucb':
            return {
                'type': 'ucb',
                'c': strategy_config.get('confidence_level', 2.0)
            }
        elif strategy_type == 'thompson_sampling':
            return {
                'type': 'thompson_sampling',
                'alpha': strategy_config.get('alpha', 1.0),
                'beta': strategy_config.get('beta', 1.0)
            }
        else:
            logger.warning(f"Unknown exploration strategy: {strategy_type}. Using epsilon-greedy.")
            return {
                'type': 'epsilon_greedy',
                'epsilon': 0.3,
                'min_epsilon': 0.05,
                'decay_rate': 0.001
            }
    
    def _initialize_action_space(self) -> Dict:
        """
        Initialize the action space based on configuration.
        
        Returns:
            Dictionary representing the action space.
        """
        return self.config.get('action_space', {})
    
    def _initialize_state_space(self) -> Dict:
        """
        Initialize the state space for the RL agent.
        
        Returns:
            Dictionary representing the state space.
        """
        return {
            'traffic': {
                'organic': 0,
                'paid': 0,
                'social': 0,
                'referral': 0,
                'direct': 0
            },
            'conversion_rates': {
                'overall': 0.0,
                'by_channel': {}
            },
            'revenue': {
                'total': 0.0,
                'by_channel': {},
                'by_product': {}
            },
            'costs': {
                'total': 0.0,
                'fixed': 0.0,
                'variable': 0.0,
                'by_channel': {}
            },
            'market_conditions': {
                'competition_level': 0.5,
                'seasonality': 0.5,
                'trend': 0.0
            }
        }
    
    def _initialize_model(self) -> Any:
        """
        Initialize the RL model.
        
        Returns:
            Initialized model object.
        """
        # For now, we'll use a simple Q-learning model
        # This could be replaced with more sophisticated models like DQN, PPO, etc.
        return {
            'q_table': {},
            'learning_rate': self.config.get('learning_rate', 0.01),
            'discount_factor': self.config.get('discount_factor', 0.95)
        }
    
    def update_state(self, new_state_data: Dict) -> Dict:
        """
        Update the current state with new data.
        
        Args:
            new_state_data: Dictionary containing new state information.
            
        Returns:
            Updated state dictionary.
        """
        if self.state is None:
            self.state = self._initialize_state_space()
        
        # Deep merge the new state data with the current state
        self._deep_update(self.state, new_state_data)
        
        logger.info("State updated successfully")
        return self.state
    
    def _deep_update(self, d: Dict, u: Dict) -> Dict:
        """
        Recursively update a dictionary.
        
        Args:
            d: Dictionary to update.
            u: Dictionary with updates.
            
        Returns:
            Updated dictionary.
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
        return d
    
    def select_action(self, state: Optional[Dict] = None) -> Dict:
        """
        Select an action based on the current state and exploration strategy.
        
        Args:
            state: Current state. If None, uses self.state.
            
        Returns:
            Dictionary representing the selected action.
        """
        if state is None:
            state = self.state
        
        if state is None:
            logger.warning("No state available. Initializing default state.")
            state = self._initialize_state_space()
            self.state = state
        
        # Convert state to a hashable representation for Q-table lookup
        state_key = self._state_to_key(state)
        
        # Exploration strategy
        strategy = self.exploration_strategy
        
        if strategy['type'] == 'epsilon_greedy':
            # Epsilon-greedy strategy
            if np.random.random() < strategy['epsilon']:
                # Explore: select a random action
                action = self._generate_random_action()
                logger.info("Exploring: Selected random action")
            else:
                # Exploit: select the best action according to the Q-table
                action = self._get_best_action(state_key)
                logger.info("Exploiting: Selected best known action")
            
            # Decay epsilon
            new_epsilon = max(
                strategy['min_epsilon'],
                strategy['epsilon'] * (1 - strategy['decay_rate'])
            )
            self.exploration_strategy['epsilon'] = new_epsilon
            
        elif strategy['type'] == 'ucb':
            # Upper Confidence Bound strategy
            action = self._select_ucb_action(state_key)
            
        elif strategy['type'] == 'thompson_sampling':
            # Thompson Sampling strategy
            action = self._select_thompson_sampling_action(state_key)
            
        else:
            # Default to random action if strategy is unknown
            action = self._generate_random_action()
        
        # Apply constraints to ensure the action is valid
        action = self._apply_constraints(action)
        
        # Record the action
        self.action_history.append({
            'timestamp': datetime.now().isoformat(),
            'state': state,
            'action': action
        })
        
        return action
    
    def _state_to_key(self, state: Dict) -> str:
        """
        Convert a state dictionary to a hashable key for Q-table lookup.
        
        Args:
            state: State dictionary.
            
        Returns:
            String key representing the state.
        """
        # For simplicity, we'll use a JSON string as the key
        # In a production system, you might want a more efficient representation
        return json.dumps(self._discretize_state(state), sort_keys=True)
    
    def _discretize_state(self, state: Dict) -> Dict:
        """
        Discretize continuous values in the state to make it suitable for Q-table.
        
        Args:
            state: State dictionary with potentially continuous values.
            
        Returns:
            Discretized state dictionary.
        """
        # This is a simplified implementation
        # In a real system, you would use more sophisticated discretization
        discretized = {}
        
        for key, value in state.items():
            if isinstance(value, dict):
                discretized[key] = self._discretize_state(value)
            elif isinstance(value, float):
                # Discretize floats to 2 decimal places
                discretized[key] = round(value, 2)
            else:
                discretized[key] = value
        
        return discretized
    
    def _generate_random_action(self) -> Dict:
        """
        Generate a random action within the action space.
        
        Returns:
            Dictionary representing a random action.
        """
        action = {}
        action_space = self.action_space
        
        # Select random content type
        if 'content_type' in action_space:
            action['content_type'] = np.random.choice(action_space['content_type'])
        
        # Select random pricing
        if 'pricing' in action_space:
            pricing_config = action_space['pricing']
            min_price = pricing_config.get('min', 0.0)
            max_price = pricing_config.get('max', 1000.0)
            step = pricing_config.get('step', 5.0)
            possible_prices = np.arange(min_price, max_price + step, step)
            action['pricing'] = float(np.random.choice(possible_prices))
        
        # Select random ad spend
        if 'ad_spend' in action_space:
            ad_spend_config = action_space['ad_spend']
            min_spend = ad_spend_config.get('min', 0.0)
            max_spend = ad_spend_config.get('max', 5000.0)
            step = ad_spend_config.get('step', 50.0)
            possible_spends = np.arange(min_spend, max_spend + step, step)
            action['ad_spend'] = float(np.random.choice(possible_spends))
        
        # Select random SEO tactic
        if 'seo_tactics' in action_space:
            action['seo_tactic'] = np.random.choice(action_space['seo_tactics'])
        
        # Select random affiliate product action
        if 'affiliate_products' in action_space:
            action['affiliate_action'] = np.random.choice(action_space['affiliate_products'])
        
        return action
    
    def _get_best_action(self, state_key: str) -> Dict:
        """
        Get the best action for a given state according to the Q-table.
        
        Args:
            state_key: Hashable key representing the state.
            
        Returns:
            Dictionary representing the best action.
        """
        # If state not in Q-table, return a random action
        if state_key not in self.model['q_table']:
            return self._generate_random_action()
        
        # Find action with highest Q-value
        q_values = self.model['q_table'][state_key]
        if not q_values:
            return self._generate_random_action()
        
        best_action_key = max(q_values, key=q_values.get)
        
        try:
            # Convert the action key back to a dictionary
            best_action = json.loads(best_action_key)
            return best_action
        except:
            logger.error(f"Failed to parse best action key: {best_action_key}")
            return self._generate_random_action()
    
    def _select_ucb_action(self, state_key: str) -> Dict:
        """
        Select an action using Upper Confidence Bound algorithm.
        
        Args:
            state_key: Hashable key representing the state.
            
        Returns:
            Dictionary representing the selected action.
        """
        # Not implemented yet - would require tracking action counts
        # For now, fall back to epsilon-greedy
        return self._get_best_action(state_key)
    
    def _select_thompson_sampling_action(self, state_key: str) -> Dict:
        """
        Select an action using Thompson Sampling algorithm.
        
        Args:
            state_key: Hashable key representing the state.
            
        Returns:
            Dictionary representing the selected action.
        """
        # Not implemented yet - would require tracking success/failure for each action
        # For now, fall back to epsilon-greedy
        return self._get_best_action(state_key)
    
    def _apply_constraints(self, action: Dict) -> Dict:
        """
        Apply constraints to ensure the action is valid.
        
        Args:
            action: Dictionary representing an action.
            
        Returns:
            Dictionary representing the constrained action.
        """
        constrained_action = action.copy()
        
        # Apply budget constraint
        if 'ad_spend' in constrained_action:
            max_budget = self.constraints.get('max_budget', float('inf'))
            constrained_action['ad_spend'] = min(constrained_action['ad_spend'], max_budget)
        
        # Apply other constraints as needed
        
        return constrained_action
    
    def receive_reward(self, action: Dict, reward_data: Dict) -> float:
        """
        Process reward data and update the RL model.
        
        Args:
            action: The action that was taken.
            reward_data: Dictionary containing reward information.
            
        Returns:
            Calculated reward value.
        """
        # Calculate the reward based on the reward data and weights
        reward = self._calculate_reward(reward_data)
        
        # Record the reward
        self.reward_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'reward_data': reward_data,
            'reward': reward
        })
        
        # Update the Q-table
        if self.state is not None:
            state_key = self._state_to_key(self.state)
            action_key = json.dumps(action, sort_keys=True)
            
            # Initialize state in Q-table if not present
            if state_key not in self.model['q_table']:
                self.model['q_table'][state_key] = {}
            
            # Initialize action in Q-table if not present
            if action_key not in self.model['q_table'][state_key]:
                self.model['q_table'][state_key][action_key] = 0.0
            
            # Q-learning update
            # Q(s,a) = Q(s,a) + α * (r + γ * max(Q(s',a')) - Q(s,a))
            # For now, we'll use a simplified update without the next state
            current_q = self.model['q_table'][state_key][action_key]
            learning_rate = self.model['learning_rate']
            
            # Update Q-value
            new_q = current_q + learning_rate * (reward - current_q)
            self.model['q_table'][state_key][action_key] = new_q
            
            logger.info(f"Updated Q-value for state-action pair: {new_q}")
        
        return reward
    
    def _calculate_reward(self, reward_data: Dict) -> float:
        """
        Calculate the reward based on reward data and weights.
        
        Args:
            reward_data: Dictionary containing reward information.
            
        Returns:
            Calculated reward value.
        """
        reward_weights = self.config.get('reward_weights', {
            'revenue': 0.6,
            'profit': 0.3,
            'growth': 0.1
        })
        
        reward = 0.0
        
        # Revenue component
        if 'revenue' in reward_data:
            reward += reward_data['revenue'] * reward_weights.get('revenue', 0.6)
        
        # Profit component
        if 'profit' in reward_data:
            reward += reward_data['profit'] * reward_weights.get('profit', 0.3)
        
        # Growth component
        if 'growth' in reward_data:
            reward += reward_data['growth'] * reward_weights.get('growth', 0.1)
        
        # Apply any penalties for constraint violations
        if 'penalties' in reward_data:
            reward -= reward_data['penalties']
        
        return reward
    
    def save_model(self, filepath: str) -> bool:
        """
        Save the RL model to a file.
        
        Args:
            filepath: Path to save the model.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            model_data = {
                'q_table': self.model['q_table'],
                'learning_rate': self.model['learning_rate'],
                'discount_factor': self.model['discount_factor'],
                'exploration_strategy': self.exploration_strategy,
                'action_history': self.action_history,
                'reward_history': self.reward_history
            }
            
            with open(filepath, 'w') as f:
                json.dump(model_data, f, indent=2)
            
            logger.info(f"Model saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving model to {filepath}: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """
        Load the RL model from a file.
        
        Args:
            filepath: Path to load the model from.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(filepath, 'r') as f:
                model_data = json.load(f)
            
            self.model['q_table'] = model_data.get('q_table', {})
            self.model['learning_rate'] = model_data.get('learning_rate', 0.01)
            self.model['discount_factor'] = model_data.get('discount_factor', 0.95)
            self.exploration_strategy = model_data.get('exploration_strategy', self.exploration_strategy)
            self.action_history = model_data.get('action_history', [])
            self.reward_history = model_data.get('reward_history', [])
            
            logger.info(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading model from {filepath}: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict:
        """
        Get performance metrics for the RL agent.
        
        Returns:
            Dictionary containing performance metrics.
        """
        metrics = {
            'total_actions': len(self.action_history),
            'total_rewards': len(self.reward_history),
            'average_reward': 0.0,
            'recent_average_reward': 0.0,
            'exploration_rate': self.exploration_strategy.get('epsilon', 0.0),
            'q_table_size': len(self.model['q_table'])
        }
        
        # Calculate average reward
        if self.reward_history:
            rewards = [entry['reward'] for entry in self.reward_history]
            metrics['average_reward'] = sum(rewards) / len(rewards)
            
            # Calculate recent average reward (last 10 rewards)
            recent_rewards = rewards[-10:] if len(rewards) >= 10 else rewards
            metrics['recent_average_reward'] = sum(recent_rewards) / len(recent_rewards)
        
        return metrics
    
    def get_policy_insights(self) -> Dict:
        """
        Get insights into the learned policy.
        
        Returns:
            Dictionary containing policy insights.
        """
        insights = {
            'top_actions': [],
            'state_coverage': len(self.model['q_table']),
            'action_preferences': {}
        }
        
        # Find top actions across all states
        all_actions = {}
        
        for state_key, actions in self.model['q_table'].items():
            for action_key, q_value in actions.items():
                if action_key not in all_actions:
                    all_actions[action_key] = []
                all_actions[action_key].append(q_value)
        
        # Calculate average Q-value for each action
        avg_q_values = {}
        for action_key, q_values in all_actions.items():
            avg_q_values[action_key] = sum(q_values) / len(q_values)
        
        # Sort actions by average Q-value
        sorted_actions = sorted(avg_q_values.items(), key=lambda x: x[1], reverse=True)
        
        # Get top 5 actions
        for action_key, avg_q_value in sorted_actions[:5]:
            try:
                action = json.loads(action_key)
                insights['top_actions'].append({
                    'action': action,
                    'average_q_value': avg_q_value
                })
            except:
                logger.error(f"Failed to parse action key: {action_key}")
        
        # Analyze action preferences
        for action_type in ['content_type', 'seo_tactic', 'affiliate_action']:
            preferences = {}
            counts = {}
            
            for action_entry in self.action_history:
                action = action_entry['action']
                if action_type in action:
                    value = action[action_type]
                    if value not in preferences:
                        preferences[value] = 0
                        counts[value] = 0
                    
                    # Find corresponding reward
                    timestamp = action_entry['timestamp']
                    for reward_entry in self.reward_history:
                        if reward_entry['timestamp'] >= timestamp:
                            preferences[value] += reward_entry['reward']
                            counts[value] += 1
                            break
            
            # Calculate average reward for each value
            avg_preferences = {}
            for value, total_reward in preferences.items():
                count = counts[value]
                if count > 0:
                    avg_preferences[value] = total_reward / count
            
            insights['action_preferences'][action_type] = avg_preferences
        
        return insights
