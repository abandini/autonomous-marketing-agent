"""
Authentication Manager for the Autonomous Marketing Agent.

This module handles authentication and credential management for various
marketing platforms and analytics services.
"""

import os
import json
import logging
import base64
import hashlib
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AuthManager:
    """
    Manages authentication and credentials for marketing platforms.
    
    Features:
    1. Secure storage of credentials
    2. OAuth flow management
    3. Token refresh handling
    4. Platform-specific authentication
    """
    
    def __init__(self, config_path: str = "config/auth_config.json"):
        """
        Initialize the Authentication Manager.
        
        Args:
            config_path: Path to the authentication configuration file
        """
        self.config_path = config_path
        self.credentials = {}
        self.tokens = {}
        self.encryption_key = None
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Load credentials if available
        self._load_credentials()
        
        logger.info("Authentication Manager initialized")
        
    def _initialize_encryption(self) -> None:
        """Initialize encryption for secure credential storage."""
        key_path = "config/.encryption_key"
        
        if os.path.exists(key_path):
            # Load existing key
            with open(key_path, 'rb') as file:
                self.encryption_key = file.read()
        else:
            # Generate new key
            self.encryption_key = Fernet.generate_key()
            
            # Save key
            with open(key_path, 'wb') as file:
                file.write(self.encryption_key)
                
            logger.info("Generated new encryption key")
            
    def _encrypt_data(self, data: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data as a string
        """
        if not self.encryption_key:
            self._initialize_encryption()
            
        cipher = Fernet(self.encryption_key)
        encrypted_data = cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
        
    def _decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            Decrypted data as a string
        """
        if not self.encryption_key:
            raise ValueError("Encryption key not initialized")
            
        cipher = Fernet(self.encryption_key)
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted_data = cipher.decrypt(decoded_data)
        return decrypted_data.decode()
        
    def _load_credentials(self) -> None:
        """Load credentials from the configuration file."""
        if not os.path.exists(self.config_path):
            logger.info("No credentials file found")
            return
            
        try:
            with open(self.config_path, 'r') as file:
                encrypted_data = json.load(file)
                
                # Decrypt credentials
                for platform, creds in encrypted_data.get("credentials", {}).items():
                    if "password" in creds and creds["password"]:
                        creds["password"] = self._decrypt_data(creds["password"])
                    if "api_key" in creds and creds["api_key"]:
                        creds["api_key"] = self._decrypt_data(creds["api_key"])
                    if "client_secret" in creds and creds["client_secret"]:
                        creds["client_secret"] = self._decrypt_data(creds["client_secret"])
                        
                    self.credentials[platform] = creds
                    
                # Load tokens
                self.tokens = encrypted_data.get("tokens", {})
                
                logger.info(f"Loaded credentials for {len(self.credentials)} platforms")
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            
    def _save_credentials(self) -> None:
        """Save credentials to the configuration file."""
        try:
            # Create a copy of credentials for encryption
            encrypted_creds = {}
            
            for platform, creds in self.credentials.items():
                encrypted_creds[platform] = creds.copy()
                
                # Encrypt sensitive data
                if "password" in creds and creds["password"]:
                    encrypted_creds[platform]["password"] = self._encrypt_data(creds["password"])
                if "api_key" in creds and creds["api_key"]:
                    encrypted_creds[platform]["api_key"] = self._encrypt_data(creds["api_key"])
                if "client_secret" in creds and creds["client_secret"]:
                    encrypted_creds[platform]["client_secret"] = self._encrypt_data(creds["client_secret"])
                    
            # Prepare data for saving
            data = {
                "credentials": encrypted_creds,
                "tokens": self.tokens,
                "last_updated": datetime.now().isoformat()
            }
            
            # Save to file
            with open(self.config_path, 'w') as file:
                json.dump(data, file, indent=2)
                
            logger.info(f"Saved credentials for {len(self.credentials)} platforms")
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            
    def add_credentials(self, platform: str, credentials: Dict[str, Any]) -> bool:
        """
        Add credentials for a platform.
        
        Args:
            platform: Platform name
            credentials: Credential information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.credentials[platform] = credentials
            self._save_credentials()
            logger.info(f"Added credentials for {platform}")
            return True
        except Exception as e:
            logger.error(f"Error adding credentials for {platform}: {str(e)}")
            return False
            
    def get_credentials(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        Get credentials for a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Dict containing credentials, or None if not found
        """
        return self.credentials.get(platform)
        
    def remove_credentials(self, platform: str) -> bool:
        """
        Remove credentials for a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            True if successful, False otherwise
        """
        if platform in self.credentials:
            try:
                del self.credentials[platform]
                self._save_credentials()
                logger.info(f"Removed credentials for {platform}")
                return True
            except Exception as e:
                logger.error(f"Error removing credentials for {platform}: {str(e)}")
                
        return False
        
    def list_platforms(self) -> List[str]:
        """
        List all platforms with stored credentials.
        
        Returns:
            List of platform names
        """
        return list(self.credentials.keys())
        
    def authenticate(self, platform: str) -> Dict[str, Any]:
        """
        Authenticate with a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Dict containing authentication status and token
        """
        if platform not in self.credentials:
            return {"status": "error", "message": f"No credentials found for {platform}"}
            
        # Check if we have a valid token
        if platform in self.tokens:
            token_info = self.tokens[platform]
            
            # Check if token is expired
            if "expires_at" in token_info:
                expires_at = datetime.fromisoformat(token_info["expires_at"])
                
                if expires_at > datetime.now():
                    # Token is still valid
                    return {"status": "success", "token": token_info["token"]}
                    
        # No valid token, authenticate based on platform type
        auth_method = f"_authenticate_{platform}"
        
        if hasattr(self, auth_method):
            try:
                # Call platform-specific authentication method
                result = getattr(self, auth_method)()
                
                if result["status"] == "success":
                    # Save token
                    self.tokens[platform] = {
                        "token": result["token"],
                        "expires_at": result.get("expires_at", (datetime.now() + timedelta(hours=1)).isoformat())
                    }
                    self._save_credentials()
                    
                return result
            except Exception as e:
                logger.error(f"Error authenticating with {platform}: {str(e)}")
                return {"status": "error", "message": str(e)}
        else:
            # Generic authentication
            return self._authenticate_generic(platform)
            
    def _authenticate_generic(self, platform: str) -> Dict[str, Any]:
        """
        Generic authentication method.
        
        Args:
            platform: Platform name
            
        Returns:
            Dict containing authentication status and token
        """
        creds = self.credentials[platform]
        
        # Simulate authentication
        # In a real implementation, this would make API calls to the platform
        token = hashlib.sha256(f"{platform}:{datetime.now().isoformat()}".encode()).hexdigest()
        
        expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
        
        return {
            "status": "success",
            "token": token,
            "expires_at": expires_at
        }
        
    def _authenticate_google_analytics(self) -> Dict[str, Any]:
        """
        Authenticate with Google Analytics.
        
        Returns:
            Dict containing authentication status and token
        """
        # In a real implementation, this would use OAuth2 flow
        creds = self.credentials.get("google_analytics", {})
        
        if not creds or "client_id" not in creds or "client_secret" not in creds:
            return {"status": "error", "message": "Missing required credentials for Google Analytics"}
            
        # Simulate OAuth token
        token = hashlib.sha256(f"google_analytics:{datetime.now().isoformat()}".encode()).hexdigest()
        
        expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
        
        return {
            "status": "success",
            "token": token,
            "expires_at": expires_at
        }
        
    def _authenticate_facebook(self) -> Dict[str, Any]:
        """
        Authenticate with Facebook.
        
        Returns:
            Dict containing authentication status and token
        """
        # In a real implementation, this would use Facebook's authentication API
        creds = self.credentials.get("facebook", {})
        
        if not creds or "app_id" not in creds or "app_secret" not in creds:
            return {"status": "error", "message": "Missing required credentials for Facebook"}
            
        # Simulate Facebook token
        token = hashlib.sha256(f"facebook:{datetime.now().isoformat()}".encode()).hexdigest()
        
        expires_at = (datetime.now() + timedelta(days=60)).isoformat()
        
        return {
            "status": "success",
            "token": token,
            "expires_at": expires_at
        }
        
    def _authenticate_twitter(self) -> Dict[str, Any]:
        """
        Authenticate with Twitter.
        
        Returns:
            Dict containing authentication status and token
        """
        # In a real implementation, this would use Twitter's OAuth flow
        creds = self.credentials.get("twitter", {})
        
        if not creds or "api_key" not in creds or "api_secret" not in creds:
            return {"status": "error", "message": "Missing required credentials for Twitter"}
            
        # Simulate Twitter token
        token = hashlib.sha256(f"twitter:{datetime.now().isoformat()}".encode()).hexdigest()
        
        expires_at = (datetime.now() + timedelta(days=90)).isoformat()
        
        return {
            "status": "success",
            "token": token,
            "expires_at": expires_at
        }
        
    def refresh_token(self, platform: str) -> Dict[str, Any]:
        """
        Refresh authentication token for a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Dict containing refresh status and new token
        """
        # Force re-authentication
        return self.authenticate(platform)
        
    def validate_credentials(self, platform: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate credentials for a platform.
        
        Args:
            platform: Platform name
            credentials: Credentials to validate
            
        Returns:
            Dict containing validation status
        """
        # Check required fields based on platform
        required_fields = {
            "google_analytics": ["client_id", "client_secret"],
            "facebook": ["app_id", "app_secret"],
            "twitter": ["api_key", "api_secret"],
            "linkedin": ["client_id", "client_secret"],
            "instagram": ["username", "password"],
            "google_ads": ["client_id", "client_secret", "developer_token"],
            "mailchimp": ["api_key"],
            "hubspot": ["api_key"],
            "semrush": ["api_key"],
            "ahrefs": ["api_key"],
            "moz": ["access_id", "secret_key"]
        }
        
        # Default required fields
        default_required = ["username", "password"]
        
        # Get required fields for the platform
        platform_required = required_fields.get(platform, default_required)
        
        # Check if all required fields are present
        missing_fields = [field for field in platform_required if field not in credentials]
        
        if missing_fields:
            return {
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }
            
        return {"status": "success"}
