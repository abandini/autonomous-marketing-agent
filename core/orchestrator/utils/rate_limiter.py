"""
Rate limiter for the orchestrator module.

This module provides rate limiting functionality to prevent overloading
external services and APIs.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for workflow execution and API calls."""
    
    def __init__(self, max_per_minute: int = 60, max_concurrent: int = 10):
        """
        Initialize the rate limiter.
        
        Args:
            max_per_minute: Maximum number of executions per minute
            max_concurrent: Maximum number of concurrent executions
        """
        self.max_per_minute = max_per_minute
        self.max_concurrent = max_concurrent
        self.executions = []
        self.concurrent_count = 0
        self.semaphore = asyncio.Semaphore(max_concurrent)
        logger.info(f"Rate limiter initialized with {max_per_minute} per minute, {max_concurrent} concurrent")
        
    async def acquire(self) -> bool:
        """
        Acquire a rate limit slot.
        
        Returns:
            True if a slot was acquired, False otherwise
        """
        now = datetime.now()
        # Remove executions older than 1 minute
        self.executions = [t for t in self.executions 
                          if now - t < timedelta(minutes=1)]
                          
        if len(self.executions) >= self.max_per_minute:
            logger.warning(f"Rate limit exceeded: {len(self.executions)}/{self.max_per_minute} per minute")
            return False
            
        self.executions.append(now)
        return True
        
    async def execute(self, func, *args, **kwargs):
        """
        Execute a function with rate limiting.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function execution
        """
        if not await self.acquire():
            raise Exception("Rate limit exceeded")
            
        async with self.semaphore:
            self.concurrent_count += 1
            try:
                return await func(*args, **kwargs)
            finally:
                self.concurrent_count -= 1
                
class CategoryRateLimiter:
    """Rate limiter with separate limits for different categories."""
    
    def __init__(self, default_max_per_minute: int = 60, default_max_concurrent: int = 10):
        """
        Initialize the category rate limiter.
        
        Args:
            default_max_per_minute: Default maximum executions per minute
            default_max_concurrent: Default maximum concurrent executions
        """
        self.default_max_per_minute = default_max_per_minute
        self.default_max_concurrent = default_max_concurrent
        self.limiters: Dict[str, RateLimiter] = {}
        logger.info(f"Category rate limiter initialized with defaults: {default_max_per_minute} per minute, {default_max_concurrent} concurrent")
        
    def get_limiter(self, category: str) -> RateLimiter:
        """
        Get or create a rate limiter for a category.
        
        Args:
            category: Category name
            
        Returns:
            Rate limiter for the category
        """
        if category not in self.limiters:
            self.limiters[category] = RateLimiter(
                self.default_max_per_minute,
                self.default_max_concurrent
            )
            
        return self.limiters[category]
        
    def configure_category(self, category: str, max_per_minute: int, max_concurrent: int) -> None:
        """
        Configure rate limits for a category.
        
        Args:
            category: Category name
            max_per_minute: Maximum executions per minute
            max_concurrent: Maximum concurrent executions
        """
        self.limiters[category] = RateLimiter(max_per_minute, max_concurrent)
        logger.info(f"Configured rate limiter for {category}: {max_per_minute} per minute, {max_concurrent} concurrent")
        
    async def execute(self, category: str, func, *args, **kwargs):
        """
        Execute a function with category-based rate limiting.
        
        Args:
            category: Category name
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function execution
        """
        limiter = self.get_limiter(category)
        return await limiter.execute(func, *args, **kwargs)
