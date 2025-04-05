"""
Operator Interface Module

This module provides an interface for human operators to manage critical oversight
tasks that require human judgment, including strategy definition, approvals,
compliance checks, and financial oversight.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ApprovalStatus(Enum):
    """Enum for approval status values."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"

class ApprovalType(Enum):
    """Enum for types of approvals."""
    STRATEGY = "strategy"
    EXPERIMENT = "experiment"
    CONTENT = "content"
    BUDGET = "budget"
    PRICING = "pricing"
    AFFILIATE = "affiliate"
    COMPLIANCE = "compliance"

class OperatorInterface:
    """
    Interface for human operators to manage critical oversight tasks.
    
    This class provides methods for strategy definition, approvals,
    compliance checks, and financial oversight.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Operator Interface.
        
        Args:
            config_path: Path to the configuration file.
        """
        self.config = self._load_config(config_path)
        self.pending_approvals = []
        self.approval_history = []
        self.strategy_settings = {}
        self.compliance_settings = {}
        self.notification_channels = []
        
        # Create approval directories if they don't exist
        os.makedirs(self.config.get('approval_dir', 'data/approvals'), exist_ok=True)
        os.makedirs(self.config.get('strategy_dir', 'data/strategies'), exist_ok=True)
        os.makedirs(self.config.get('compliance_dir', 'data/compliance'), exist_ok=True)
        
        logger.info("Operator Interface initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file or use default.
        
        Args:
            config_path: Path to configuration file.
            
        Returns:
            Configuration dictionary.
        """
        default_config = {
            'approval_dir': 'data/approvals',
            'strategy_dir': 'data/strategies',
            'compliance_dir': 'data/compliance',
            'notification_channels': ['email', 'dashboard'],
            'approval_thresholds': {
                'budget': 1000,  # Require approval for budgets over $1000
                'pricing_change': 0.15,  # Require approval for price changes over 15%
                'content_risk': 0.7  # Require approval for content with risk score over 0.7
            },
            'compliance_requirements': {
                'gdpr': True,
                'ccpa': True,
                'affiliate_disclosure': True,
                'ad_disclosure': True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with default config
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
            logger.info("Using default Operator Interface configuration")
            return default_config
    
    # Strategy Definition & Setup Methods
    
    def define_revenue_targets(self, targets: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define revenue targets and goals.
        
        Args:
            targets: Dictionary containing revenue targets and goals.
            
        Returns:
            Updated targets dictionary.
        """
        # Save targets to strategy settings
        self.strategy_settings['revenue_targets'] = targets
        
        # Save to file
        strategy_path = os.path.join(self.config['strategy_dir'], 'revenue_targets.json')
        try:
            with open(strategy_path, 'w') as f:
                json.dump(targets, f, indent=2)
            logger.info(f"Revenue targets saved to {strategy_path}")
        except Exception as e:
            logger.error(f"Error saving revenue targets: {e}")
        
        return targets
    
    def configure_affiliate_strategy(self, affiliate_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure affiliate partners and revenue models.
        
        Args:
            affiliate_config: Dictionary containing affiliate configuration.
            
        Returns:
            Updated affiliate configuration.
        """
        # Save affiliate config to strategy settings
        self.strategy_settings['affiliate'] = affiliate_config
        
        # Save to file
        strategy_path = os.path.join(self.config['strategy_dir'], 'affiliate_strategy.json')
        try:
            with open(strategy_path, 'w') as f:
                json.dump(affiliate_config, f, indent=2)
            logger.info(f"Affiliate strategy saved to {strategy_path}")
        except Exception as e:
            logger.error(f"Error saving affiliate strategy: {e}")
        
        return affiliate_config
    
    def define_channel_mix(self, channel_mix: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define initial channel mix and overall marketing strategy.
        
        Args:
            channel_mix: Dictionary containing channel mix configuration.
            
        Returns:
            Updated channel mix configuration.
        """
        # Save channel mix to strategy settings
        self.strategy_settings['channel_mix'] = channel_mix
        
        # Save to file
        strategy_path = os.path.join(self.config['strategy_dir'], 'channel_mix.json')
        try:
            with open(strategy_path, 'w') as f:
                json.dump(channel_mix, f, indent=2)
            logger.info(f"Channel mix saved to {strategy_path}")
        except Exception as e:
            logger.error(f"Error saving channel mix: {e}")
        
        return channel_mix
    
    # System Configuration Methods
    
    def store_api_credentials(self, service_name: str, credentials: Dict[str, str]) -> bool:
        """
        Store API credentials for a service.
        
        Args:
            service_name: Name of the service.
            credentials: Dictionary containing credentials.
            
        Returns:
            True if successful, False otherwise.
        """
        # In a real system, this would use a secure credential store
        # For this example, we'll just log that credentials were stored
        logger.info(f"API credentials for {service_name} stored securely")
        return True
    
    def configure_git_repository(self, git_config: Dict[str, str]) -> bool:
        """
        Configure Git repository settings.
        
        Args:
            git_config: Dictionary containing Git configuration.
            
        Returns:
            True if successful, False otherwise.
        """
        # Save Git config to strategy settings
        self.strategy_settings['git'] = git_config
        
        # Save to file
        strategy_path = os.path.join(self.config['strategy_dir'], 'git_config.json')
        try:
            with open(strategy_path, 'w') as f:
                json.dump(git_config, f, indent=2)
            logger.info(f"Git configuration saved to {strategy_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving Git configuration: {e}")
            return False
    
    # Approval Methods
    
    def request_approval(self, 
                        approval_type: ApprovalType, 
                        data: Dict[str, Any], 
                        description: str,
                        urgency: str = "normal") -> str:
        """
        Request approval from a human operator.
        
        Args:
            approval_type: Type of approval being requested.
            data: Data related to the approval request.
            description: Description of what is being approved.
            urgency: Urgency level ("low", "normal", "high", "critical").
            
        Returns:
            Approval ID.
        """
        # Generate approval ID
        approval_id = f"{approval_type.value}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create approval request
        approval_request = {
            "id": approval_id,
            "type": approval_type.value,
            "data": data,
            "description": description,
            "urgency": urgency,
            "status": ApprovalStatus.PENDING.value,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": None,
            "approved_by": None,
            "comments": None
        }
        
        # Add to pending approvals
        self.pending_approvals.append(approval_request)
        
        # Save to file
        approval_path = os.path.join(self.config['approval_dir'], f"{approval_id}.json")
        try:
            with open(approval_path, 'w') as f:
                json.dump(approval_request, f, indent=2)
            logger.info(f"Approval request {approval_id} saved to {approval_path}")
        except Exception as e:
            logger.error(f"Error saving approval request: {e}")
        
        # Send notification
        self._send_approval_notification(approval_request)
        
        return approval_id
    
    def get_pending_approvals(self, approval_type: ApprovalType = None) -> List[Dict[str, Any]]:
        """
        Get list of pending approvals.
        
        Args:
            approval_type: Optional filter by approval type.
            
        Returns:
            List of pending approval requests.
        """
        if approval_type:
            return [a for a in self.pending_approvals if a['type'] == approval_type.value]
        else:
            return self.pending_approvals
    
    def process_approval(self, 
                        approval_id: str, 
                        status: ApprovalStatus, 
                        operator_id: str,
                        comments: str = None,
                        modified_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process an approval request.
        
        Args:
            approval_id: ID of the approval request.
            status: New status for the request.
            operator_id: ID of the operator processing the request.
            comments: Optional comments from the operator.
            modified_data: Optional modified data if the operator made changes.
            
        Returns:
            Updated approval request.
        """
        # Find the approval request
        approval_request = None
        for i, request in enumerate(self.pending_approvals):
            if request['id'] == approval_id:
                approval_request = request
                break
        
        if not approval_request:
            logger.error(f"Approval request {approval_id} not found")
            return None
        
        # Update the approval request
        approval_request['status'] = status.value
        approval_request['updated_at'] = datetime.datetime.now().isoformat()
        approval_request['approved_by'] = operator_id
        
        if comments:
            approval_request['comments'] = comments
        
        if modified_data and status == ApprovalStatus.MODIFIED:
            approval_request['modified_data'] = modified_data
        
        # If approved or rejected, move from pending to history
        if status != ApprovalStatus.PENDING:
            self.pending_approvals.remove(approval_request)
            self.approval_history.append(approval_request)
        
        # Save to file
        approval_path = os.path.join(self.config['approval_dir'], f"{approval_id}.json")
        try:
            with open(approval_path, 'w') as f:
                json.dump(approval_request, f, indent=2)
            logger.info(f"Approval request {approval_id} updated in {approval_path}")
        except Exception as e:
            logger.error(f"Error updating approval request: {e}")
        
        return approval_request
    
    def _send_approval_notification(self, approval_request: Dict[str, Any]) -> None:
        """
        Send notification about an approval request.
        
        Args:
            approval_request: The approval request.
        """
        # In a real system, this would send emails, push notifications, etc.
        logger.info(f"Notification sent for approval request {approval_request['id']}")
    
    # Compliance Methods
    
    def configure_compliance_settings(self, compliance_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure compliance settings.
        
        Args:
            compliance_settings: Dictionary containing compliance settings.
            
        Returns:
            Updated compliance settings.
        """
        # Save compliance settings
        self.compliance_settings = compliance_settings
        
        # Save to file
        compliance_path = os.path.join(self.config['compliance_dir'], 'compliance_settings.json')
        try:
            with open(compliance_path, 'w') as f:
                json.dump(compliance_settings, f, indent=2)
            logger.info(f"Compliance settings saved to {compliance_path}")
        except Exception as e:
            logger.error(f"Error saving compliance settings: {e}")
        
        return compliance_settings
    
    def check_compliance(self, content_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check content for compliance issues.
        
        Args:
            content_type: Type of content being checked.
            content: Content data.
            
        Returns:
            Compliance check results.
        """
        # In a real system, this would perform actual compliance checks
        # For this example, we'll return a simple result
        result = {
            "compliant": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check for required disclosures
        if content_type == "affiliate":
            if "disclosure" not in content or not content["disclosure"]:
                result["compliant"] = False
                result["issues"].append("Missing affiliate disclosure")
                result["recommendations"].append("Add affiliate disclosure to content")
        
        # Check for privacy compliance
        if content_type == "email":
            if "unsubscribe_link" not in content or not content["unsubscribe_link"]:
                result["compliant"] = False
                result["issues"].append("Missing unsubscribe link")
                result["recommendations"].append("Add unsubscribe link to email")
        
        return result
    
    def report_compliance_issue(self, issue_type: str, details: Dict[str, Any]) -> str:
        """
        Report a compliance issue for operator review.
        
        Args:
            issue_type: Type of compliance issue.
            details: Details of the issue.
            
        Returns:
            Issue ID.
        """
        # Generate issue ID
        issue_id = f"compliance_{issue_type}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create issue report
        issue_report = {
            "id": issue_id,
            "type": issue_type,
            "details": details,
            "status": "open",
            "created_at": datetime.datetime.now().isoformat(),
            "resolved_at": None,
            "resolution": None
        }
        
        # Save to file
        issue_path = os.path.join(self.config['compliance_dir'], f"{issue_id}.json")
        try:
            with open(issue_path, 'w') as f:
                json.dump(issue_report, f, indent=2)
            logger.info(f"Compliance issue {issue_id} saved to {issue_path}")
        except Exception as e:
            logger.error(f"Error saving compliance issue: {e}")
        
        # Request approval for compliance issue
        self.request_approval(
            ApprovalType.COMPLIANCE,
            issue_report,
            f"Compliance issue: {issue_type}",
            "high"
        )
        
        return issue_id
    
    # Financial & Strategic Oversight Methods
    
    def generate_financial_summary(self, 
                                  period: str = "weekly", 
                                  start_date: str = None, 
                                  end_date: str = None) -> Dict[str, Any]:
        """
        Generate a financial summary for operator review.
        
        Args:
            period: Period for the summary ("daily", "weekly", "monthly").
            start_date: Optional start date (ISO format).
            end_date: Optional end date (ISO format).
            
        Returns:
            Financial summary.
        """
        # In a real system, this would generate an actual financial summary
        # For this example, we'll return a placeholder
        summary = {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "generated_at": datetime.datetime.now().isoformat(),
            "revenue": {
                "total": 10000,
                "by_channel": {
                    "organic": 3000,
                    "paid": 4000,
                    "affiliate": 2000,
                    "email": 1000
                }
            },
            "expenses": {
                "total": 5000,
                "by_category": {
                    "advertising": 3000,
                    "content": 1000,
                    "tools": 500,
                    "other": 500
                }
            },
            "profit": 5000,
            "roi": 1.0,
            "key_metrics": {
                "cac": 25,
                "ltv": 150,
                "conversion_rate": 0.03
            }
        }
        
        return summary
    
    def update_strategic_direction(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update strategic direction based on operator input.
        
        Args:
            updates: Dictionary containing strategic updates.
            
        Returns:
            Updated strategy.
        """
        # Load current strategy
        current_strategy = {}
        strategy_path = os.path.join(self.config['strategy_dir'], 'marketing_strategy.json')
        if os.path.exists(strategy_path):
            try:
                with open(strategy_path, 'r') as f:
                    current_strategy = json.load(f)
            except Exception as e:
                logger.error(f"Error loading current strategy: {e}")
        
        # Update strategy
        for key, value in updates.items():
            if isinstance(value, dict) and key in current_strategy and isinstance(current_strategy[key], dict):
                # Deep merge dictionaries
                current_strategy[key].update(value)
            else:
                # Simple update
                current_strategy[key] = value
        
        # Save updated strategy
        try:
            with open(strategy_path, 'w') as f:
                json.dump(current_strategy, f, indent=2)
            logger.info(f"Updated marketing strategy saved to {strategy_path}")
        except Exception as e:
            logger.error(f"Error saving updated strategy: {e}")
        
        return current_strategy
    
    def handle_exception(self, exception_type: str, details: Dict[str, Any]) -> str:
        """
        Handle an exception that requires operator attention.
        
        Args:
            exception_type: Type of exception.
            details: Details of the exception.
            
        Returns:
            Exception ID.
        """
        # Generate exception ID
        exception_id = f"exception_{exception_type}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create exception report
        exception_report = {
            "id": exception_id,
            "type": exception_type,
            "details": details,
            "status": "open",
            "created_at": datetime.datetime.now().isoformat(),
            "resolved_at": None,
            "resolution": None
        }
        
        # Save to file
        exception_path = os.path.join(self.config['approval_dir'], f"{exception_id}.json")
        try:
            with open(exception_path, 'w') as f:
                json.dump(exception_report, f, indent=2)
            logger.info(f"Exception {exception_id} saved to {exception_path}")
        except Exception as e:
            logger.error(f"Error saving exception: {e}")
        
        # Request approval for exception handling
        urgency = "critical" if exception_type in ["customer_complaint", "pr_issue"] else "high"
        self.request_approval(
            ApprovalType.STRATEGY,
            exception_report,
            f"Exception requiring attention: {exception_type}",
            urgency
        )
        
        return exception_id
