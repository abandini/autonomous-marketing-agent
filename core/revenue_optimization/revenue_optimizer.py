"""
Revenue Optimization Manager

This module implements a revenue optimization manager that coordinates
the RL Engine and Experiment Manager to continuously optimize revenue.
"""

import os
import json
import time
import logging
import threading
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union

from core.revenue_optimization.rl_engine import RLEngine
from core.revenue_optimization.experiment_manager import ExperimentManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RevenueOptimizer:
    """
    Revenue Optimization Manager for continuous revenue optimization.
    
    This class coordinates the RL Engine and Experiment Manager to
    continuously optimize revenue through reinforcement learning and
    experimentation.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Revenue Optimizer.
        
        Args:
            config_path: Path to the configuration file for the Revenue Optimizer.
                         If None, uses default configuration.
        """
        self.config = self._load_config(config_path)
        self.rl_engine = RLEngine(self.config.get('rl_engine_config'))
        self.experiment_manager = ExperimentManager(self.config.get('experiment_manager_config'))
        self.running = False
        self.optimization_thread = None
        self.last_state_update = None
        self.last_experiment_check = None
        self.last_model_save = None
        self.data_sources = {}
        self.action_handlers = {}
        
        logger.info("Revenue Optimizer initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file or use default.
        
        Args:
            config_path: Path to configuration file.
            
        Returns:
            Configuration dictionary.
        """
        default_config = {
            'optimization_interval': 3600,  # 1 hour
            'state_update_interval': 900,   # 15 minutes
            'experiment_check_interval': 1800,  # 30 minutes
            'model_save_interval': 86400,   # 24 hours
            'model_save_path': 'models/revenue_optimization',
            'experiment_save_path': 'data/experiments',
            'max_optimization_iterations': 1000,
            'data_sources': {
                'analytics': True,
                'financial': True,
                'marketing': True,
                'content': True,
                'affiliate': True
            },
            'action_handlers': {
                'content': True,
                'pricing': True,
                'advertising': True,
                'seo': True,
                'affiliate': True
            },
            'constraints': {
                'max_budget_per_day': 1000,
                'min_profit_margin': 0.2,
                'max_risk_level': 0.5
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
            logger.info("Using default Revenue Optimizer configuration")
            return default_config
    
    def register_data_source(self, name: str, data_source_func) -> bool:
        """
        Register a data source function.
        
        Args:
            name: Name of the data source.
            data_source_func: Function that returns data from the source.
            
        Returns:
            True if successful, False otherwise.
        """
        if name in self.data_sources:
            logger.warning(f"Data source {name} already registered. Overwriting.")
        
        self.data_sources[name] = data_source_func
        logger.info(f"Registered data source: {name}")
        return True
    
    def register_action_handler(self, name: str, action_handler_func) -> bool:
        """
        Register an action handler function.
        
        Args:
            name: Name of the action handler.
            action_handler_func: Function that handles actions.
            
        Returns:
            True if successful, False otherwise.
        """
        if name in self.action_handlers:
            logger.warning(f"Action handler {name} already registered. Overwriting.")
        
        self.action_handlers[name] = action_handler_func
        logger.info(f"Registered action handler: {name}")
        return True
    
    def start(self) -> bool:
        """
        Start the revenue optimization process.
        
        Returns:
            True if started successfully, False otherwise.
        """
        if self.running:
            logger.warning("Revenue Optimizer is already running.")
            return False
        
        self.running = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop)
        self.optimization_thread.daemon = True
        self.optimization_thread.start()
        
        logger.info("Revenue Optimizer started successfully")
        return True
    
    def stop(self) -> bool:
        """
        Stop the revenue optimization process.
        
        Returns:
            True if stopped successfully, False otherwise.
        """
        if not self.running:
            logger.warning("Revenue Optimizer is not running.")
            return False
        
        self.running = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=30)
            if self.optimization_thread.is_alive():
                logger.warning("Optimization thread did not terminate gracefully.")
        
        logger.info("Revenue Optimizer stopped successfully")
        return True
    
    def _optimization_loop(self):
        """
        Main optimization loop that runs continuously.
        """
        iteration = 0
        
        while self.running and iteration < self.config['max_optimization_iterations']:
            try:
                # Update state from data sources
                self._update_state()
                
                # Select action using RL Engine
                action = self.rl_engine.select_action()
                
                # Design experiment for the action
                experiment_type = self._determine_experiment_type(action)
                experiment = self.experiment_manager.design_experiment(experiment_type, action)
                
                # Start the experiment
                experiment = self.experiment_manager.start_experiment(experiment)
                
                # Execute the action through action handlers
                self._execute_action(action, experiment['id'])
                
                # Check and process experiments
                self._check_experiments()
                
                # Save model periodically
                self._save_model_if_needed()
                
                # Sleep for the optimization interval
                time.sleep(self.config['optimization_interval'])
                
                iteration += 1
                
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                time.sleep(60)  # Sleep for a minute before retrying
    
    def _update_state(self):
        """
        Update the state from all registered data sources.
        """
        current_time = datetime.now()
        
        # Check if it's time to update the state
        if (self.last_state_update is None or 
            (current_time - self.last_state_update).total_seconds() >= self.config['state_update_interval']):
            
            state_data = {}
            
            # Collect data from all registered data sources
            for name, data_source_func in self.data_sources.items():
                try:
                    data = data_source_func()
                    if data:
                        state_data[name] = data
                except Exception as e:
                    logger.error(f"Error collecting data from {name}: {e}")
            
            # Update the RL Engine state
            if state_data:
                self.rl_engine.update_state(state_data)
                self.last_state_update = current_time
                logger.info("Updated state from data sources")
    
    def _determine_experiment_type(self, action: Dict) -> str:
        """
        Determine the appropriate experiment type for an action.
        
        Args:
            action: Action dictionary.
            
        Returns:
            Experiment type string.
        """
        # This is a simplified implementation
        # In a real system, you would use more sophisticated logic
        
        # If multiple action dimensions are being modified, use multivariate test
        if len(action) > 1:
            return 'multivariate_test'
        
        # If it's a pricing or budget action, use bandit optimization
        if 'pricing' in action or 'ad_spend' in action:
            return 'bandit_optimization'
        
        # Default to A/B test
        return 'a_b_test'
    
    def _execute_action(self, action: Dict, experiment_id: str):
        """
        Execute an action through registered action handlers.
        
        Args:
            action: Action dictionary.
            experiment_id: ID of the associated experiment.
        """
        # Determine which action handlers to use based on the action
        handlers_to_use = []
        
        if 'content_type' in action and 'content' in self.action_handlers:
            handlers_to_use.append('content')
        
        if 'pricing' in action and 'pricing' in self.action_handlers:
            handlers_to_use.append('pricing')
        
        if 'ad_spend' in action and 'advertising' in self.action_handlers:
            handlers_to_use.append('advertising')
        
        if 'seo_tactic' in action and 'seo' in self.action_handlers:
            handlers_to_use.append('seo')
        
        if 'affiliate_action' in action and 'affiliate' in self.action_handlers:
            handlers_to_use.append('affiliate')
        
        # Execute the action using the appropriate handlers
        for handler_name in handlers_to_use:
            try:
                handler_func = self.action_handlers[handler_name]
                result = handler_func(action, experiment_id)
                logger.info(f"Executed action using {handler_name} handler: {result}")
            except Exception as e:
                logger.error(f"Error executing action with {handler_name} handler: {e}")
    
    def _check_experiments(self):
        """
        Check and process active experiments.
        """
        current_time = datetime.now()
        
        # Check if it's time to check experiments
        if (self.last_experiment_check is None or 
            (current_time - self.last_experiment_check).total_seconds() >= self.config['experiment_check_interval']):
            
            # Get all active experiments
            active_experiments = self.experiment_manager.get_active_experiments()
            
            for experiment in active_experiments:
                experiment_id = experiment['id']
                
                # Check if the experiment should be completed
                if self.experiment_manager.check_experiment_completion(experiment_id):
                    # Complete the experiment
                    completed_experiment = self.experiment_manager.complete_experiment(experiment_id)
                    
                    # Process the results
                    self._process_experiment_results(completed_experiment)
                else:
                    # For bandit experiments, update allocations
                    if experiment['type'] == 'bandit_optimization':
                        self.experiment_manager.update_experiment_allocations(experiment_id)
            
            self.last_experiment_check = current_time
            logger.info("Checked and processed experiments")
    
    def _process_experiment_results(self, experiment: Dict):
        """
        Process the results of a completed experiment.
        
        Args:
            experiment: Completed experiment dictionary.
        """
        if 'analysis' not in experiment or 'winner' not in experiment['analysis']:
            logger.warning(f"Experiment {experiment['id']} has no analysis or winner.")
            return
        
        winner_id = experiment['analysis']['winner']
        
        # Find the winning variant
        winner = None
        for variant in experiment['variants']:
            if variant['id'] == winner_id:
                winner = variant
                break
        
        if winner is None:
            logger.warning(f"Winner variant {winner_id} not found in experiment {experiment['id']}.")
            return
        
        # Calculate reward based on the experiment results
        reward_data = self._calculate_reward_from_experiment(experiment, winner)
        
        # Send reward to RL Engine
        self.rl_engine.receive_reward(winner['action'], reward_data)
        
        logger.info(f"Processed results for experiment {experiment['id']}, winner: {winner_id}")
    
    def _calculate_reward_from_experiment(self, experiment: Dict, winner: Dict) -> Dict:
        """
        Calculate reward data from experiment results.
        
        Args:
            experiment: Completed experiment dictionary.
            winner: Winning variant dictionary.
            
        Returns:
            Dictionary with reward data.
        """
        reward_data = {}
        
        # Get primary metric
        primary_metric = experiment['metrics']['primary']
        
        # Find control variant
        control_id = None
        for variant in experiment['variants']:
            if variant['id'] == 'control' or variant['id'] == 'arm_0':
                control_id = variant['id']
                break
        
        if control_id is None:
            logger.warning(f"No control variant found for experiment {experiment['id']}.")
            return reward_data
        
        # Get metrics for control and winner
        control_metrics = experiment['results']['variants'][control_id]['metrics']
        winner_metrics = experiment['results']['variants'][winner['id']]['metrics']
        
        # Calculate revenue component (primary metric)
        if primary_metric in winner_metrics and primary_metric in control_metrics:
            winner_value = winner_metrics[primary_metric]
            control_value = control_metrics[primary_metric]
            
            # Normalize to [0, 1] range for reward
            if winner_value > control_value:
                # Positive lift
                reward_data['revenue'] = min(1.0, (winner_value - control_value) / control_value)
            else:
                # Negative or zero lift
                reward_data['revenue'] = 0.0
        
        # Calculate profit component (if available)
        profit_metric = 'profit_margin'
        if profit_metric in winner_metrics and profit_metric in control_metrics:
            winner_value = winner_metrics[profit_metric]
            control_value = control_metrics[profit_metric]
            
            # Normalize to [0, 1] range for reward
            if winner_value > control_value:
                # Positive lift
                reward_data['profit'] = min(1.0, (winner_value - control_value) / max(0.01, control_value))
            else:
                # Negative or zero lift
                reward_data['profit'] = 0.0
        
        # Calculate growth component (if available)
        growth_metric = 'conversion_rate'
        if growth_metric in winner_metrics and growth_metric in control_metrics:
            winner_value = winner_metrics[growth_metric]
            control_value = control_metrics[growth_metric]
            
            # Normalize to [0, 1] range for reward
            if winner_value > control_value:
                # Positive lift
                reward_data['growth'] = min(1.0, (winner_value - control_value) / max(0.01, control_value))
            else:
                # Negative or zero lift
                reward_data['growth'] = 0.0
        
        return reward_data
    
    def _save_model_if_needed(self):
        """
        Save the RL model if it's time to do so.
        """
        current_time = datetime.now()
        
        # Check if it's time to save the model
        if (self.last_model_save is None or 
            (current_time - self.last_model_save).total_seconds() >= self.config['model_save_interval']):
            
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(self.config['model_save_path']), exist_ok=True)
            os.makedirs(os.path.dirname(self.config['experiment_save_path']), exist_ok=True)
            
            # Save RL model
            model_path = f"{self.config['model_save_path']}/model_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
            self.rl_engine.save_model(model_path)
            
            # Save experiments
            experiment_path = f"{self.config['experiment_save_path']}/experiments_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
            self.experiment_manager.save_experiments(experiment_path)
            
            self.last_model_save = current_time
            logger.info(f"Saved model to {model_path} and experiments to {experiment_path}")
    
    def get_optimization_status(self) -> Dict:
        """
        Get the current status of the revenue optimization process.
        
        Returns:
            Dictionary with optimization status.
        """
        status = {
            'running': self.running,
            'last_state_update': self.last_state_update.isoformat() if self.last_state_update else None,
            'last_experiment_check': self.last_experiment_check.isoformat() if self.last_experiment_check else None,
            'last_model_save': self.last_model_save.isoformat() if self.last_model_save else None,
            'active_experiments': len(self.experiment_manager.get_active_experiments()),
            'completed_experiments': len(self.experiment_manager.get_completed_experiments()),
            'rl_performance': self.rl_engine.get_performance_metrics(),
            'experiment_insights': self.experiment_manager.get_experiment_insights()
        }
        
        return status
    
    def get_revenue_insights(self) -> Dict:
        """
        Get insights into revenue optimization.
        
        Returns:
            Dictionary with revenue insights.
        """
        insights = {
            'top_actions': [],
            'experiment_success_rate': 0.0,
            'average_lift': 0.0,
            'optimization_recommendations': []
        }
        
        # Get RL policy insights
        rl_insights = self.rl_engine.get_policy_insights()
        if 'top_actions' in rl_insights:
            insights['top_actions'] = rl_insights['top_actions']
        
        # Get experiment insights
        experiment_insights = self.experiment_manager.get_experiment_insights()
        if 'success_rate' in experiment_insights:
            insights['experiment_success_rate'] = experiment_insights['success_rate']
        if 'average_lift' in experiment_insights:
            insights['average_lift'] = experiment_insights['average_lift']
        if 'top_performing_actions' in experiment_insights:
            # Merge with RL insights
            for action_info in experiment_insights['top_performing_actions']:
                if 'action' in action_info:
                    insights['top_actions'].append({
                        'action': action_info['action'],
                        'wins': action_info.get('wins', 0),
                        'average_lift': action_info.get('total_lift', 0) / max(1, action_info.get('experiments', 1))
                    })
        
        # Generate recommendations
        insights['optimization_recommendations'] = self._generate_recommendations()
        
        return insights
    
    def _generate_recommendations(self) -> List[Dict]:
        """
        Generate recommendations for revenue optimization.
        
        Returns:
            List of recommendation dictionaries.
        """
        recommendations = []
        
        # Get experiment insights
        experiment_insights = self.experiment_manager.get_experiment_insights()
        
        # Get RL policy insights
        rl_insights = self.rl_engine.get_policy_insights()
        
        # Recommend top-performing actions
        if 'top_actions' in rl_insights and rl_insights['top_actions']:
            for i, action_info in enumerate(rl_insights['top_actions'][:3]):
                if 'action' in action_info:
                    recommendations.append({
                        'type': 'implement_action',
                        'priority': i + 1,
                        'message': f"Implement high-performing action with estimated value {action_info.get('average_q_value', 0):.2f}",
                        'action': action_info['action']
                    })
        
        # Recommend experiment types based on success rates
        if 'experiment_types' in experiment_insights:
            best_type = None
            best_rate = 0.0
            
            for exp_type, count in experiment_insights['experiment_types'].items():
                # Calculate success rate for this type
                success_count = 0
                for experiment in self.experiment_manager.get_completed_experiments():
                    if experiment['type'] == exp_type and 'analysis' in experiment and experiment['analysis']['winner'] != 'control':
                        success_count += 1
                
                if count > 0:
                    rate = success_count / count
                    if rate > best_rate:
                        best_rate = rate
                        best_type = exp_type
            
            if best_type:
                recommendations.append({
                    'type': 'experiment_strategy',
                    'priority': 4,
                    'message': f"Focus on {best_type} experiments which have shown a {best_rate:.2%} success rate"
                })
        
        # Add general recommendation if we don't have enough data
        if not recommendations:
            recommendations.append({
                'type': 'general',
                'priority': 1,
                'message': "Continue collecting data through diverse experiments to build a stronger optimization model"
            })
        
        return recommendations
    
    def manual_optimization(self, action: Dict) -> Dict:
        """
        Manually trigger an optimization action.
        
        Args:
            action: Action dictionary to execute.
            
        Returns:
            Dictionary with optimization results.
        """
        try:
            # Update state from data sources
            self._update_state()
            
            # Design experiment for the action
            experiment_type = self._determine_experiment_type(action)
            experiment = self.experiment_manager.design_experiment(experiment_type, action)
            
            # Start the experiment
            experiment = self.experiment_manager.start_experiment(experiment)
            
            # Execute the action through action handlers
            self._execute_action(action, experiment['id'])
            
            return {
                'status': 'success',
                'message': f"Manual optimization action executed successfully",
                'experiment_id': experiment['id'],
                'experiment_type': experiment_type,
                'action': action
            }
        except Exception as e:
            logger.error(f"Error in manual optimization: {e}")
            return {
                'status': 'error',
                'message': f"Error in manual optimization: {str(e)}",
                'action': action
            }
