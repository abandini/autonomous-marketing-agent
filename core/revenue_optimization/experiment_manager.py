"""
Experiment Manager for Continuous Revenue Optimization

This module implements an experiment manager that works with the RL Engine
to design, execute, and evaluate experiments for revenue optimization.
"""

import os
import json
import time
import logging
import uuid
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

class ExperimentManager:
    """
    Experiment Manager for continuous revenue optimization.
    
    This class manages the design, execution, and evaluation of experiments
    for revenue optimization, working in conjunction with the RL Engine.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Experiment Manager.
        
        Args:
            config_path: Path to the configuration file for the Experiment Manager.
                         If None, uses default configuration.
        """
        self.config = self._load_config(config_path)
        self.active_experiments = {}
        self.completed_experiments = []
        self.experiment_results = {}
        
        logger.info("Experiment Manager initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file or use default.
        
        Args:
            config_path: Path to configuration file.
            
        Returns:
            Configuration dictionary.
        """
        default_config = {
            'experiment_duration': {
                'min_hours': 24,
                'max_hours': 168,  # 1 week
                'default_hours': 72  # 3 days
            },
            'significance_threshold': 0.05,
            'min_sample_size': 100,
            'max_concurrent_experiments': 5,
            'experiment_types': {
                'a_b_test': {
                    'enabled': True,
                    'variant_count': 2
                },
                'multivariate_test': {
                    'enabled': True,
                    'max_variants': 4
                },
                'bandit_optimization': {
                    'enabled': True,
                    'arm_count': 3
                }
            },
            'metrics': {
                'primary': 'revenue',
                'secondary': ['conversion_rate', 'profit_margin', 'customer_acquisition_cost']
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
            logger.info("Using default Experiment Manager configuration")
            return default_config
    
    def design_experiment(self, experiment_type: str, action: Dict, context: Dict = None) -> Dict:
        """
        Design an experiment based on the given action and context.
        
        Args:
            experiment_type: Type of experiment to design (a_b_test, multivariate_test, bandit_optimization).
            action: Action dictionary from the RL Engine.
            context: Additional context for experiment design.
            
        Returns:
            Dictionary representing the designed experiment.
        """
        if experiment_type not in self.config['experiment_types'] or not self.config['experiment_types'][experiment_type]['enabled']:
            logger.warning(f"Experiment type {experiment_type} is not enabled. Falling back to a_b_test.")
            experiment_type = 'a_b_test'
        
        experiment_id = str(uuid.uuid4())
        
        # Set experiment duration
        duration_hours = self.config['experiment_duration']['default_hours']
        if context and 'urgency' in context:
            # Adjust duration based on urgency
            if context['urgency'] == 'high':
                duration_hours = self.config['experiment_duration']['min_hours']
            elif context['urgency'] == 'low':
                duration_hours = self.config['experiment_duration']['max_hours']
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        experiment = {
            'id': experiment_id,
            'type': experiment_type,
            'status': 'designed',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'action': action,
            'context': context or {},
            'variants': self._generate_variants(experiment_type, action),
            'metrics': {
                'primary': self.config['metrics']['primary'],
                'secondary': self.config['metrics']['secondary']
            },
            'sample_size_target': self._calculate_sample_size(),
            'results': None
        }
        
        logger.info(f"Designed experiment {experiment_id} of type {experiment_type}")
        return experiment
    
    def _generate_variants(self, experiment_type: str, action: Dict) -> List[Dict]:
        """
        Generate variants for the experiment based on the experiment type and action.
        
        Args:
            experiment_type: Type of experiment.
            action: Base action for the experiment.
            
        Returns:
            List of variant dictionaries.
        """
        variants = []
        
        if experiment_type == 'a_b_test':
            # A/B test: control and one variant
            variants.append({
                'id': 'control',
                'name': 'Control',
                'action': {},  # Empty action represents current state (control)
                'traffic_allocation': 0.5
            })
            
            variants.append({
                'id': 'variant_1',
                'name': 'Variant 1',
                'action': action,
                'traffic_allocation': 0.5
            })
            
        elif experiment_type == 'multivariate_test':
            # Multivariate test: multiple variants with different combinations
            max_variants = self.config['experiment_types']['multivariate_test']['max_variants']
            
            # Control variant
            variants.append({
                'id': 'control',
                'name': 'Control',
                'action': {},
                'traffic_allocation': 1.0 / (max_variants + 1)
            })
            
            # Generate variants by modifying different aspects of the action
            action_keys = list(action.keys())
            for i in range(min(len(action_keys), max_variants)):
                variant_action = action.copy()
                key = action_keys[i]
                
                # Modify the action for this variant
                if isinstance(action[key], (int, float)):
                    # For numeric values, increase or decrease by a percentage
                    modifier = 1.0 + (0.1 * (i % 2 == 0 and 1 or -1) * (i // 2 + 1))
                    variant_action[key] = action[key] * modifier
                elif isinstance(action[key], str) and key in ['content_type', 'seo_tactic', 'affiliate_action']:
                    # For categorical values, we'll keep the original for simplicity
                    pass
                
                variants.append({
                    'id': f'variant_{i+1}',
                    'name': f'Variant {i+1}',
                    'action': variant_action,
                    'traffic_allocation': 1.0 / (max_variants + 1)
                })
            
        elif experiment_type == 'bandit_optimization':
            # Multi-armed bandit: multiple variants with adaptive allocation
            arm_count = self.config['experiment_types']['bandit_optimization']['arm_count']
            
            # Control arm
            variants.append({
                'id': 'arm_0',
                'name': 'Control Arm',
                'action': {},
                'traffic_allocation': 1.0 / arm_count,
                'rewards': []
            })
            
            # Generate arms with variations of the action
            for i in range(1, arm_count):
                variant_action = action.copy()
                
                # Modify the action for this arm
                for key in variant_action:
                    if isinstance(variant_action[key], (int, float)):
                        # For numeric values, apply a random adjustment
                        adjustment = 1.0 + (np.random.random() * 0.4 - 0.2)  # ±20%
                        variant_action[key] = variant_action[key] * adjustment
                
                variants.append({
                    'id': f'arm_{i}',
                    'name': f'Arm {i}',
                    'action': variant_action,
                    'traffic_allocation': 1.0 / arm_count,
                    'rewards': []
                })
        
        return variants
    
    def _calculate_sample_size(self) -> int:
        """
        Calculate the required sample size for statistical significance.
        
        Returns:
            Required sample size.
        """
        # This is a simplified calculation
        # In a real system, you would use power analysis based on effect size
        return self.config['min_sample_size']
    
    def start_experiment(self, experiment: Dict) -> Dict:
        """
        Start the execution of an experiment.
        
        Args:
            experiment: Experiment dictionary.
            
        Returns:
            Updated experiment dictionary.
        """
        if len(self.active_experiments) >= self.config['max_concurrent_experiments']:
            logger.warning("Maximum number of concurrent experiments reached. Cannot start new experiment.")
            return experiment
        
        experiment_id = experiment['id']
        experiment['status'] = 'running'
        experiment['actual_start_time'] = datetime.now().isoformat()
        
        # Initialize results structure
        experiment['results'] = {
            'data_points': 0,
            'variants': {}
        }
        
        for variant in experiment['variants']:
            experiment['results']['variants'][variant['id']] = {
                'data_points': 0,
                'metrics': {
                    experiment['metrics']['primary']: 0.0
                }
            }
            
            for metric in experiment['metrics']['secondary']:
                experiment['results']['variants'][variant['id']]['metrics'][metric] = 0.0
        
        self.active_experiments[experiment_id] = experiment
        
        logger.info(f"Started experiment {experiment_id}")
        return experiment
    
    def record_experiment_data(self, experiment_id: str, variant_id: str, metrics: Dict) -> bool:
        """
        Record data for an experiment variant.
        
        Args:
            experiment_id: ID of the experiment.
            variant_id: ID of the variant.
            metrics: Dictionary of metric values.
            
        Returns:
            True if data was recorded successfully, False otherwise.
        """
        if experiment_id not in self.active_experiments:
            logger.warning(f"Experiment {experiment_id} not found in active experiments.")
            return False
        
        experiment = self.active_experiments[experiment_id]
        
        if variant_id not in experiment['results']['variants']:
            logger.warning(f"Variant {variant_id} not found in experiment {experiment_id}.")
            return False
        
        # Update data points count
        experiment['results']['data_points'] += 1
        experiment['results']['variants'][variant_id]['data_points'] += 1
        
        # Update metrics
        for metric, value in metrics.items():
            if metric in experiment['results']['variants'][variant_id]['metrics']:
                # Running average
                current_value = experiment['results']['variants'][variant_id]['metrics'][metric]
                current_count = experiment['results']['variants'][variant_id]['data_points']
                
                # Update the average
                new_value = ((current_value * (current_count - 1)) + value) / current_count
                experiment['results']['variants'][variant_id]['metrics'][metric] = new_value
        
        # For bandit experiments, update rewards
        if experiment['type'] == 'bandit_optimization':
            primary_metric = experiment['metrics']['primary']
            if primary_metric in metrics:
                for variant in experiment['variants']:
                    if variant['id'] == variant_id:
                        if 'rewards' not in variant:
                            variant['rewards'] = []
                        variant['rewards'].append(metrics[primary_metric])
                        break
        
        logger.info(f"Recorded data for experiment {experiment_id}, variant {variant_id}")
        return True
    
    def update_experiment_allocations(self, experiment_id: str) -> bool:
        """
        Update traffic allocations for an experiment based on performance.
        
        Args:
            experiment_id: ID of the experiment.
            
        Returns:
            True if allocations were updated successfully, False otherwise.
        """
        if experiment_id not in self.active_experiments:
            logger.warning(f"Experiment {experiment_id} not found in active experiments.")
            return False
        
        experiment = self.active_experiments[experiment_id]
        
        # Only update allocations for bandit optimization experiments
        if experiment['type'] != 'bandit_optimization':
            return False
        
        # Calculate new allocations using Thompson Sampling
        primary_metric = experiment['metrics']['primary']
        allocations = self._thompson_sampling(experiment, primary_metric)
        
        # Update variant allocations
        for variant_id, allocation in allocations.items():
            for variant in experiment['variants']:
                if variant['id'] == variant_id:
                    variant['traffic_allocation'] = allocation
                    break
        
        logger.info(f"Updated traffic allocations for experiment {experiment_id}")
        return True
    
    def _thompson_sampling(self, experiment: Dict, metric: str) -> Dict[str, float]:
        """
        Calculate traffic allocations using Thompson Sampling.
        
        Args:
            experiment: Experiment dictionary.
            metric: Primary metric to optimize.
            
        Returns:
            Dictionary mapping variant IDs to traffic allocations.
        """
        allocations = {}
        total_samples = 1000  # Number of samples to draw
        
        # Count successes for each variant
        samples_per_variant = {}
        
        for variant_id, variant_data in experiment['results']['variants'].items():
            # Find the variant in the experiment
            variant = None
            for v in experiment['variants']:
                if v['id'] == variant_id:
                    variant = v
                    break
            
            if variant is None or 'rewards' not in variant or not variant['rewards']:
                # No data yet, use uniform allocation
                samples_per_variant[variant_id] = total_samples / len(experiment['results']['variants'])
                continue
            
            # Get rewards for this variant
            rewards = variant['rewards']
            
            # Calculate alpha and beta for Beta distribution
            # We'll normalize rewards to [0, 1] range for Beta distribution
            normalized_rewards = []
            if rewards:
                min_reward = min(rewards)
                max_reward = max(rewards)
                range_reward = max(max_reward - min_reward, 1e-6)  # Avoid division by zero
                
                normalized_rewards = [(r - min_reward) / range_reward for r in rewards]
            
            # Calculate successes and failures
            successes = sum(normalized_rewards)
            failures = len(normalized_rewards) - successes
            
            # Add 1 to both for Bayesian prior
            alpha = successes + 1
            beta = failures + 1
            
            # Draw samples from Beta distribution
            samples = np.random.beta(alpha, beta, total_samples)
            samples_per_variant[variant_id] = np.sum(samples)
        
        # Calculate allocations proportional to samples
        total_samples = sum(samples_per_variant.values())
        for variant_id, samples in samples_per_variant.items():
            allocations[variant_id] = samples / total_samples
        
        return allocations
    
    def check_experiment_completion(self, experiment_id: str) -> bool:
        """
        Check if an experiment should be completed.
        
        Args:
            experiment_id: ID of the experiment.
            
        Returns:
            True if the experiment should be completed, False otherwise.
        """
        if experiment_id not in self.active_experiments:
            logger.warning(f"Experiment {experiment_id} not found in active experiments.")
            return False
        
        experiment = self.active_experiments[experiment_id]
        
        # Check if end time has been reached
        end_time = datetime.fromisoformat(experiment['end_time'])
        if datetime.now() >= end_time:
            return True
        
        # Check if sample size target has been reached
        if experiment['results']['data_points'] >= experiment['sample_size_target']:
            # Check if we have enough data for each variant
            min_variant_data = min(
                variant_data['data_points'] 
                for variant_data in experiment['results']['variants'].values()
            )
            
            if min_variant_data >= experiment['sample_size_target'] / len(experiment['variants']):
                return True
        
        return False
    
    def complete_experiment(self, experiment_id: str) -> Dict:
        """
        Complete an experiment and analyze results.
        
        Args:
            experiment_id: ID of the experiment.
            
        Returns:
            Dictionary with experiment results and analysis.
        """
        if experiment_id not in self.active_experiments:
            logger.warning(f"Experiment {experiment_id} not found in active experiments.")
            return {}
        
        experiment = self.active_experiments[experiment_id]
        experiment['status'] = 'completed'
        experiment['actual_end_time'] = datetime.now().isoformat()
        
        # Analyze results
        analysis = self._analyze_experiment_results(experiment)
        experiment['analysis'] = analysis
        
        # Move to completed experiments
        self.completed_experiments.append(experiment)
        del self.active_experiments[experiment_id]
        
        # Store results
        self.experiment_results[experiment_id] = {
            'experiment': experiment,
            'analysis': analysis
        }
        
        logger.info(f"Completed experiment {experiment_id}")
        return experiment
    
    def _analyze_experiment_results(self, experiment: Dict) -> Dict:
        """
        Analyze the results of an experiment.
        
        Args:
            experiment: Experiment dictionary.
            
        Returns:
            Dictionary with analysis results.
        """
        analysis = {
            'winner': None,
            'significance': False,
            'lift': {},
            'confidence_intervals': {},
            'recommendations': []
        }
        
        primary_metric = experiment['metrics']['primary']
        control_id = None
        
        # Find control variant
        for variant in experiment['variants']:
            if variant['id'] == 'control' or variant['id'] == 'arm_0':
                control_id = variant['id']
                break
        
        if control_id is None:
            logger.warning(f"No control variant found for experiment {experiment['id']}.")
            return analysis
        
        # Get control performance
        control_performance = experiment['results']['variants'][control_id]['metrics'][primary_metric]
        
        # Compare variants to control
        best_variant_id = control_id
        best_performance = control_performance
        
        for variant_id, variant_data in experiment['results']['variants'].items():
            if variant_id == control_id:
                continue
            
            variant_performance = variant_data['metrics'][primary_metric]
            
            # Calculate lift
            lift = 0
            if control_performance > 0:
                lift = (variant_performance - control_performance) / control_performance
            
            analysis['lift'][variant_id] = lift
            
            # Check if this variant is better than the current best
            if variant_performance > best_performance:
                best_variant_id = variant_id
                best_performance = variant_performance
        
        # Set winner
        analysis['winner'] = best_variant_id
        
        # Generate recommendations
        if best_variant_id != control_id:
            # Find the winning variant
            winning_variant = None
            for variant in experiment['variants']:
                if variant['id'] == best_variant_id:
                    winning_variant = variant
                    break
            
            if winning_variant:
                analysis['recommendations'].append({
                    'type': 'implement_winner',
                    'message': f"Implement the winning variant ({winning_variant['name']}) with a lift of {analysis['lift'][best_variant_id]:.2%}",
                    'action': winning_variant['action']
                })
        else:
            analysis['recommendations'].append({
                'type': 'maintain_control',
                'message': "Maintain the current approach as no variant outperformed the control.",
                'action': {}
            })
        
        # Add recommendation for further experimentation if needed
        if experiment['results']['data_points'] < experiment['sample_size_target']:
            analysis['recommendations'].append({
                'type': 'continue_testing',
                'message': f"Continue testing to reach the target sample size of {experiment['sample_size_target']} (currently {experiment['results']['data_points']})."
            })
        
        return analysis
    
    def get_experiment_status(self, experiment_id: str) -> Dict:
        """
        Get the current status of an experiment.
        
        Args:
            experiment_id: ID of the experiment.
            
        Returns:
            Dictionary with experiment status.
        """
        if experiment_id in self.active_experiments:
            return {
                'status': 'active',
                'experiment': self.active_experiments[experiment_id]
            }
        
        for experiment in self.completed_experiments:
            if experiment['id'] == experiment_id:
                return {
                    'status': 'completed',
                    'experiment': experiment
                }
        
        return {
            'status': 'not_found',
            'experiment': None
        }
    
    def get_active_experiments(self) -> List[Dict]:
        """
        Get a list of all active experiments.
        
        Returns:
            List of active experiment dictionaries.
        """
        return list(self.active_experiments.values())
    
    def get_completed_experiments(self) -> List[Dict]:
        """
        Get a list of all completed experiments.
        
        Returns:
            List of completed experiment dictionaries.
        """
        return self.completed_experiments
    
    def get_experiment_insights(self) -> Dict:
        """
        Get insights from all experiments.
        
        Returns:
            Dictionary with experiment insights.
        """
        insights = {
            'total_experiments': len(self.active_experiments) + len(self.completed_experiments),
            'active_experiments': len(self.active_experiments),
            'completed_experiments': len(self.completed_experiments),
            'success_rate': 0.0,
            'average_lift': 0.0,
            'top_performing_actions': [],
            'experiment_types': {}
        }
        
        # Calculate success rate and average lift
        successful_experiments = 0
        total_lift = 0.0
        lift_count = 0
        
        for experiment in self.completed_experiments:
            if 'analysis' in experiment and experiment['analysis']['winner'] != 'control':
                successful_experiments += 1
            
            if 'analysis' in experiment and 'lift' in experiment['analysis']:
                for variant_id, lift in experiment['analysis']['lift'].items():
                    total_lift += lift
                    lift_count += 1
        
        if len(self.completed_experiments) > 0:
            insights['success_rate'] = successful_experiments / len(self.completed_experiments)
        
        if lift_count > 0:
            insights['average_lift'] = total_lift / lift_count
        
        # Count experiment types
        for experiment in self.active_experiments.values():
            exp_type = experiment['type']
            if exp_type not in insights['experiment_types']:
                insights['experiment_types'][exp_type] = 0
            insights['experiment_types'][exp_type] += 1
        
        for experiment in self.completed_experiments:
            exp_type = experiment['type']
            if exp_type not in insights['experiment_types']:
                insights['experiment_types'][exp_type] = 0
            insights['experiment_types'][exp_type] += 1
        
        # Find top performing actions
        action_performance = {}
        
        for experiment in self.completed_experiments:
            if 'analysis' not in experiment or 'winner' not in experiment['analysis']:
                continue
            
            winner_id = experiment['analysis']['winner']
            
            # Find the winning variant
            winner = None
            for variant in experiment['variants']:
                if variant['id'] == winner_id:
                    winner = variant
                    break
            
            if winner and 'action' in winner:
                action = winner['action']
                
                # Convert action to string for counting
                action_str = json.dumps(action, sort_keys=True)
                
                if action_str not in action_performance:
                    action_performance[action_str] = {
                        'action': action,
                        'wins': 0,
                        'total_lift': 0.0,
                        'experiments': 0
                    }
                
                action_performance[action_str]['wins'] += 1
                
                if 'lift' in experiment['analysis'] and winner_id in experiment['analysis']['lift']:
                    action_performance[action_str]['total_lift'] += experiment['analysis']['lift'][winner_id]
                
                action_performance[action_str]['experiments'] += 1
        
        # Sort actions by wins and then by average lift
        sorted_actions = sorted(
            action_performance.values(),
            key=lambda x: (x['wins'], x['total_lift'] / max(x['experiments'], 1)),
            reverse=True
        )
        
        # Get top 5 actions
        insights['top_performing_actions'] = sorted_actions[:5]
        
        return insights
    
    def save_experiments(self, filepath: str) -> bool:
        """
        Save all experiments to a file.
        
        Args:
            filepath: Path to save the experiments.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            data = {
                'active_experiments': self.active_experiments,
                'completed_experiments': self.completed_experiments,
                'experiment_results': self.experiment_results
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Experiments saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving experiments to {filepath}: {e}")
            return False
    
    def load_experiments(self, filepath: str) -> bool:
        """
        Load experiments from a file.
        
        Args:
            filepath: Path to load the experiments from.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.active_experiments = data.get('active_experiments', {})
            self.completed_experiments = data.get('completed_experiments', [])
            self.experiment_results = data.get('experiment_results', {})
            
            logger.info(f"Experiments loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading experiments from {filepath}: {e}")
            return False
