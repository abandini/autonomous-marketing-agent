"""
Affiliate Marketing Agent for the Autonomous Marketing Agent.

This module implements the specialized agent for affiliate marketing,
focusing on product selection, revenue optimization, and continuous improvement.
"""

import logging
import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from core.agents.base_agent import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AffiliateAgent(BaseAgent):
    """
    Specialized agent for affiliate marketing.
    
    Features:
    1. Product selection and analysis
    2. Commission optimization
    3. Revenue tracking and reporting
    4. Continuous improvement cycle management
    5. A/B testing for affiliate content
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Affiliate Marketing Agent.
        
        Args:
            config: Configuration for the agent
        """
        super().__init__("affiliate", config)
        
        # Initialize affiliate platforms
        self.platforms = {}
        self.products = {}
        self.revenue_data = {}
        self.conversion_data = {}
        
        # Register actions
        self._register_actions()
        
        logger.info("Affiliate Marketing Agent initialized")
        
    def _register_actions(self) -> None:
        """Register agent-specific actions."""
        self.register_action("search_products", self.search_products)
        self.register_action("analyze_product", self.analyze_product)
        self.register_action("track_revenue", self.track_revenue)
        self.register_action("optimize_commissions", self.optimize_commissions)
        self.register_action("generate_affiliate_links", self.generate_affiliate_links)
        self.register_action("analyze_conversion_funnel", self.analyze_conversion_funnel)
        self.register_action("generate_product_recommendations", self.generate_product_recommendations)
        self.register_action("create_ab_test", self.create_ab_test)
        self.register_action("analyze_ab_test_results", self.analyze_ab_test_results)
        
    async def connect_platform(self, platform_name: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Connect to an affiliate marketing platform.
        
        Args:
            platform_name: Name of the platform (e.g., 'clickbank', 'amazon')
            credentials: Credentials for the platform
            
        Returns:
            Dict containing connection status
        """
        # Validate required credentials
        required_fields = {
            "clickbank": ["api_key", "user_id"],
            "amazon": ["access_key", "secret_key", "associate_tag"],
            "shareasale": ["api_token", "affiliate_id"],
            "cj": ["api_key", "website_id"]
        }
        
        if platform_name not in required_fields:
            return {
                "status": "error",
                "message": f"Unsupported platform: {platform_name}"
            }
            
        missing_fields = [field for field in required_fields[platform_name] if field not in credentials]
        
        if missing_fields:
            return {
                "status": "error",
                "message": f"Missing required credentials: {', '.join(missing_fields)}"
            }
            
        # Store platform credentials
        self.platforms[platform_name] = {
            "credentials": credentials,
            "connected_at": datetime.now().isoformat(),
            "status": "connected"
        }
        
        logger.info(f"Connected to {platform_name} affiliate platform")
        
        return {
            "status": "success",
            "message": f"Successfully connected to {platform_name}"
        }
        
    async def search_products(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Search for affiliate products based on criteria.
        
        Args:
            params: Search parameters
                - platform: Platform to search (e.g., 'clickbank', 'amazon')
                - category: Product category
                - keywords: Keywords to search for
                - min_commission: Minimum commission rate
                - max_price: Maximum product price
                - sort_by: Sort criteria (e.g., 'popularity', 'commission')
                
        Returns:
            Dict containing search results
        """
        if not params:
            return {
                "status": "error",
                "message": "No search parameters provided"
            }
            
        platform = params.get("platform")
        
        if not platform:
            return {
                "status": "error",
                "message": "No platform specified"
            }
            
        if platform not in self.platforms:
            return {
                "status": "error",
                "message": f"Not connected to platform: {platform}"
            }
            
        # In a real implementation, this would call the platform's API
        # For now, we'll simulate search results
        
        # Simulate search delay
        await asyncio.sleep(0.5)
        
        # Generate simulated results
        results = []
        categories = ["health", "fitness", "wealth", "relationships", "self-help", "tech"]
        
        category = params.get("category")
        keywords = params.get("keywords", "")
        min_commission = float(params.get("min_commission", 0))
        max_price = float(params.get("max_price", 1000))
        
        # Filter by category if specified
        if category and category not in categories:
            return {
                "status": "error",
                "message": f"Invalid category: {category}"
            }
            
        # Generate random products
        for i in range(10):
            product_category = category if category else random.choice(categories)
            commission_rate = random.uniform(5, 50)
            price = random.uniform(10, 200)
            
            # Apply filters
            if commission_rate < min_commission or price > max_price:
                continue
                
            # Check keywords match
            if keywords and keywords.lower() not in product_category.lower():
                continue
                
            product_id = f"{platform}_{product_category}_{i}"
            
            product = {
                "id": product_id,
                "name": f"{product_category.title()} Product {i}",
                "description": f"This is a great {product_category} product with many benefits.",
                "price": price,
                "commission_rate": commission_rate,
                "commission_type": "percentage",
                "category": product_category,
                "platform": platform,
                "url": f"https://{platform}.com/product/{product_id}",
                "popularity": random.uniform(1, 10),
                "conversion_rate": random.uniform(1, 5),
                "gravity": random.randint(10, 100) if platform == "clickbank" else None
            }
            
            results.append(product)
            
            # Store product data
            self.products[product_id] = product
            
        # Sort results if specified
        sort_by = params.get("sort_by")
        
        if sort_by == "popularity":
            results.sort(key=lambda x: x["popularity"], reverse=True)
        elif sort_by == "commission":
            results.sort(key=lambda x: x["commission_rate"], reverse=True)
        elif sort_by == "price":
            results.sort(key=lambda x: x["price"])
        elif sort_by == "conversion":
            results.sort(key=lambda x: x["conversion_rate"], reverse=True)
            
        return {
            "status": "success",
            "platform": platform,
            "count": len(results),
            "results": results
        }
        
    async def analyze_product(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze an affiliate product in detail.
        
        Args:
            params: Analysis parameters
                - product_id: ID of the product to analyze
                - include_competition: Whether to include competition analysis
                - include_trends: Whether to include trend analysis
                
        Returns:
            Dict containing product analysis
        """
        if not params:
            return {
                "status": "error",
                "message": "No parameters provided"
            }
            
        product_id = params.get("product_id")
        
        if not product_id:
            return {
                "status": "error",
                "message": "No product ID specified"
            }
            
        if product_id not in self.products:
            return {
                "status": "error",
                "message": f"Product not found: {product_id}"
            }
            
        product = self.products[product_id]
        
        # Basic analysis
        analysis = {
            "product": product,
            "potential_revenue": product["price"] * (product["commission_rate"] / 100) * product["conversion_rate"],
            "competition_level": random.choice(["low", "medium", "high"]),
            "recommendation": random.choice(["highly recommended", "recommended", "neutral", "not recommended"]),
            "strengths": [
                "High commission rate" if product["commission_rate"] > 30 else None,
                "Good conversion rate" if product["conversion_rate"] > 3 else None,
                "Popular product" if product["popularity"] > 7 else None
            ],
            "weaknesses": [
                "Low commission rate" if product["commission_rate"] < 15 else None,
                "Poor conversion rate" if product["conversion_rate"] < 2 else None,
                "Low popularity" if product["popularity"] < 3 else None
            ]
        }
        
        # Filter out None values
        analysis["strengths"] = [s for s in analysis["strengths"] if s]
        analysis["weaknesses"] = [w for w in analysis["weaknesses"] if w]
        
        # Add competition analysis if requested
        if params.get("include_competition"):
            analysis["competition"] = {
                "similar_products": [
                    {
                        "id": f"{product['platform']}_{product['category']}_{random.randint(100, 999)}",
                        "name": f"Competitor {product['category'].title()} Product {i}",
                        "price": product["price"] * random.uniform(0.8, 1.2),
                        "commission_rate": product["commission_rate"] * random.uniform(0.8, 1.2),
                        "popularity": product["popularity"] * random.uniform(0.8, 1.2)
                    }
                    for i in range(3)
                ],
                "market_saturation": random.choice(["low", "medium", "high"]),
                "competitive_advantage": "Higher commission rate" if product["commission_rate"] > 25 else "Lower price point"
            }
            
        # Add trend analysis if requested
        if params.get("include_trends"):
            analysis["trends"] = {
                "popularity_trend": random.choice(["increasing", "stable", "decreasing"]),
                "seasonal_factors": random.choice([None, "summer peak", "winter peak", "holiday season peak"]),
                "forecast": random.choice(["positive", "neutral", "negative"])
            }
            
        return {
            "status": "success",
            "analysis": analysis
        }
        
    async def track_revenue(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Track revenue from affiliate products.
        
        Args:
            params: Tracking parameters
                - product_id: ID of the product (optional)
                - platform: Platform to track (optional)
                - start_date: Start date for tracking period
                - end_date: End date for tracking period
                
        Returns:
            Dict containing revenue data
        """
        if not params:
            return {
                "status": "error",
                "message": "No parameters provided"
            }
            
        product_id = params.get("product_id")
        platform = params.get("platform")
        start_date = params.get("start_date", (datetime.now() - timedelta(days=30)).isoformat())
        end_date = params.get("end_date", datetime.now().isoformat())
        
        # Convert dates to datetime objects
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid date format"
            }
            
        # Generate simulated revenue data
        revenue_data = []
        
        # If product_id is specified, track for that product only
        if product_id:
            if product_id not in self.products:
                return {
                    "status": "error",
                    "message": f"Product not found: {product_id}"
                }
                
            product = self.products[product_id]
            
            # Generate daily revenue data
            current_date = start_dt
            while current_date <= end_dt:
                daily_sales = random.randint(0, 10)
                daily_revenue = daily_sales * product["price"] * (product["commission_rate"] / 100)
                
                revenue_data.append({
                    "date": current_date.isoformat(),
                    "product_id": product_id,
                    "platform": product["platform"],
                    "sales": daily_sales,
                    "revenue": daily_revenue
                })
                
                current_date += timedelta(days=1)
                
        # If platform is specified, track for that platform only
        elif platform:
            if platform not in self.platforms:
                return {
                    "status": "error",
                    "message": f"Not connected to platform: {platform}"
                }
                
            # Get all products for the platform
            platform_products = [p for p in self.products.values() if p["platform"] == platform]
            
            # Generate daily revenue data
            current_date = start_dt
            while current_date <= end_dt:
                daily_platform_revenue = 0
                daily_platform_sales = 0
                
                for product in platform_products:
                    daily_sales = random.randint(0, 5)
                    daily_revenue = daily_sales * product["price"] * (product["commission_rate"] / 100)
                    
                    daily_platform_sales += daily_sales
                    daily_platform_revenue += daily_revenue
                
                revenue_data.append({
                    "date": current_date.isoformat(),
                    "platform": platform,
                    "sales": daily_platform_sales,
                    "revenue": daily_platform_revenue
                })
                
                current_date += timedelta(days=1)
                
        # Otherwise, track for all platforms
        else:
            # Generate daily revenue data
            current_date = start_dt
            while current_date <= end_dt:
                daily_total_revenue = 0
                daily_total_sales = 0
                platform_data = {}
                
                for platform_name in self.platforms:
                    platform_products = [p for p in self.products.values() if p["platform"] == platform_name]
                    
                    daily_platform_revenue = 0
                    daily_platform_sales = 0
                    
                    for product in platform_products:
                        daily_sales = random.randint(0, 3)
                        daily_revenue = daily_sales * product["price"] * (product["commission_rate"] / 100)
                        
                        daily_platform_sales += daily_sales
                        daily_platform_revenue += daily_revenue
                    
                    platform_data[platform_name] = {
                        "sales": daily_platform_sales,
                        "revenue": daily_platform_revenue
                    }
                    
                    daily_total_sales += daily_platform_sales
                    daily_total_revenue += daily_platform_revenue
                
                revenue_data.append({
                    "date": current_date.isoformat(),
                    "total_sales": daily_total_sales,
                    "total_revenue": daily_total_revenue,
                    "platforms": platform_data
                })
                
                current_date += timedelta(days=1)
                
        # Store revenue data
        self.revenue_data[datetime.now().isoformat()] = {
            "start_date": start_date,
            "end_date": end_date,
            "product_id": product_id,
            "platform": platform,
            "data": revenue_data
        }
        
        # Calculate summary metrics
        total_revenue = sum(day["revenue"] if "revenue" in day else day["total_revenue"] for day in revenue_data)
        total_sales = sum(day["sales"] if "sales" in day else day["total_sales"] for day in revenue_data)
        
        daily_avg_revenue = total_revenue / len(revenue_data) if revenue_data else 0
        
        return {
            "status": "success",
            "start_date": start_date,
            "end_date": end_date,
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "daily_average_revenue": daily_avg_revenue,
            "data": revenue_data
        }
        
    async def optimize_commissions(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optimize commission rates for affiliate products.
        
        Args:
            params: Optimization parameters
                - platform: Platform to optimize
                - target_metric: Metric to optimize for (e.g., 'revenue', 'conversion')
                - optimization_strategy: Strategy to use (e.g., 'balanced', 'aggressive')
                
        Returns:
            Dict containing optimization recommendations
        """
        if not params:
            return {
                "status": "error",
                "message": "No parameters provided"
            }
            
        platform = params.get("platform")
        target_metric = params.get("target_metric", "revenue")
        optimization_strategy = params.get("optimization_strategy", "balanced")
        
        if not platform:
            return {
                "status": "error",
                "message": "No platform specified"
            }
            
        if platform not in self.platforms:
            return {
                "status": "error",
                "message": f"Not connected to platform: {platform}"
            }
            
        # Get all products for the platform
        platform_products = [p for p in self.products.values() if p["platform"] == platform]
        
        if not platform_products:
            return {
                "status": "error",
                "message": f"No products found for platform: {platform}"
            }
            
        # Define optimization strategies
        strategies = {
            "balanced": {
                "min_commission": 10,
                "max_commission": 40,
                "revenue_weight": 0.5,
                "conversion_weight": 0.5
            },
            "aggressive": {
                "min_commission": 5,
                "max_commission": 50,
                "revenue_weight": 0.7,
                "conversion_weight": 0.3
            },
            "conservative": {
                "min_commission": 15,
                "max_commission": 35,
                "revenue_weight": 0.3,
                "conversion_weight": 0.7
            }
        }
        
        if optimization_strategy not in strategies:
            return {
                "status": "error",
                "message": f"Invalid optimization strategy: {optimization_strategy}"
            }
            
        strategy = strategies[optimization_strategy]
        
        # Generate optimization recommendations
        recommendations = []
        
        for product in platform_products:
            current_commission = product["commission_rate"]
            current_revenue = product["price"] * (current_commission / 100) * product["conversion_rate"]
            
            # Simulate different commission rates
            test_rates = []
            for rate in range(int(strategy["min_commission"]), int(strategy["max_commission"]) + 1, 5):
                # Simulate conversion rate change based on commission rate
                # Higher commission might lead to lower conversion rate
                conversion_factor = 1.0
                if rate > current_commission:
                    conversion_factor = 0.95 - (rate - current_commission) * 0.01
                elif rate < current_commission:
                    conversion_factor = 1.05 + (current_commission - rate) * 0.005
                    
                simulated_conversion = product["conversion_rate"] * conversion_factor
                simulated_revenue = product["price"] * (rate / 100) * simulated_conversion
                
                # Calculate score based on weights
                revenue_score = simulated_revenue / current_revenue if current_revenue > 0 else 0
                conversion_score = simulated_conversion / product["conversion_rate"]
                
                weighted_score = (revenue_score * strategy["revenue_weight"] + 
                                 conversion_score * strategy["conversion_weight"])
                
                test_rates.append({
                    "commission_rate": rate,
                    "simulated_conversion": simulated_conversion,
                    "simulated_revenue": simulated_revenue,
                    "score": weighted_score
                })
                
            # Find optimal rate
            optimal_rate = max(test_rates, key=lambda x: x["score"])
            
            # Generate recommendation
            recommendation = {
                "product_id": product["id"],
                "product_name": product["name"],
                "current_commission_rate": current_commission,
                "recommended_commission_rate": optimal_rate["commission_rate"],
                "expected_revenue_change": (optimal_rate["simulated_revenue"] - current_revenue) / current_revenue * 100 if current_revenue > 0 else 0,
                "confidence": "high" if optimal_rate["score"] > 1.2 else "medium" if optimal_rate["score"] > 1.05 else "low"
            }
            
            recommendations.append(recommendation)
            
        return {
            "status": "success",
            "platform": platform,
            "target_metric": target_metric,
            "optimization_strategy": optimization_strategy,
            "recommendations": recommendations
        }
        
    async def generate_affiliate_links(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate affiliate links for products.
        
        Args:
            params: Link generation parameters
                - product_ids: List of product IDs to generate links for
                - tracking_id: Tracking ID to include in links
                - utm_params: UTM parameters to include in links
                
        Returns:
            Dict containing generated links
        """
        if not params:
            return {
                "status": "error",
                "message": "No parameters provided"
            }
            
        product_ids = params.get("product_ids", [])
        tracking_id = params.get("tracking_id", "default")
        utm_params = params.get("utm_params", {})
        
        if not product_ids:
            return {
                "status": "error",
                "message": "No product IDs specified"
            }
            
        # Validate product IDs
        invalid_ids = [pid for pid in product_ids if pid not in self.products]
        
        if invalid_ids:
            return {
                "status": "error",
                "message": f"Invalid product IDs: {', '.join(invalid_ids)}"
            }
            
        # Generate UTM string
        utm_string = ""
        if utm_params:
            utm_string = "&" + "&".join([f"utm_{key}={value}" for key, value in utm_params.items()])
            
        # Generate links
        links = []
        
        for product_id in product_ids:
            product = self.products[product_id]
            platform = product["platform"]
            
            # Generate platform-specific link
            if platform == "clickbank":
                link = f"https://vendor.clickbank.net/{tracking_id}/{product_id}{utm_string}"
            elif platform == "amazon":
                link = f"https://amazon.com/dp/{product_id}?tag={tracking_id}{utm_string}"
            elif platform == "shareasale":
                link = f"https://shareasale.com/r.cfm?b={product_id}&u={tracking_id}{utm_string}"
            else:
                link = f"{product['url']}?tracking={tracking_id}{utm_string}"
                
            links.append({
                "product_id": product_id,
                "product_name": product["name"],
                "platform": platform,
                "affiliate_link": link,
                "tracking_id": tracking_id
            })
            
        return {
            "status": "success",
            "count": len(links),
            "links": links
        }
        
    async def analyze_conversion_funnel(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze the conversion funnel for affiliate products.
        
        Args:
            params: Analysis parameters
                - product_id: ID of the product to analyze
                - start_date: Start date for analysis period
                - end_date: End date for analysis period
                
        Returns:
            Dict containing funnel analysis
        """
        if not params:
            return {
                "status": "error",
                "message": "No parameters provided"
            }
            
        product_id = params.get("product_id")
        start_date = params.get("start_date", (datetime.now() - timedelta(days=30)).isoformat())
        end_date = params.get("end_date", datetime.now().isoformat())
        
        if not product_id:
            return {
                "status": "error",
                "message": "No product ID specified"
            }
            
        if product_id not in self.products:
            return {
                "status": "error",
                "message": f"Product not found: {product_id}"
            }
            
        product = self.products[product_id]
        
        # Generate simulated funnel data
        impressions = random.randint(1000, 10000)
        clicks = int(impressions * random.uniform(0.02, 0.1))
        add_to_carts = int(clicks * random.uniform(0.1, 0.3))
        checkouts = int(add_to_carts * random.uniform(0.3, 0.6))
        purchases = int(checkouts * random.uniform(0.5, 0.9))
        
        # Calculate conversion rates
        ctr = clicks / impressions if impressions > 0 else 0
        add_to_cart_rate = add_to_carts / clicks if clicks > 0 else 0
        checkout_rate = checkouts / add_to_carts if add_to_carts > 0 else 0
        purchase_rate = purchases / checkouts if checkouts > 0 else 0
        overall_conversion = purchases / impressions if impressions > 0 else 0
        
        # Generate funnel stages
        funnel_stages = [
            {"stage": "impressions", "count": impressions, "drop_off": 0, "conversion_rate": 1.0},
            {"stage": "clicks", "count": clicks, "drop_off": impressions - clicks, "conversion_rate": ctr},
            {"stage": "add_to_carts", "count": add_to_carts, "drop_off": clicks - add_to_carts, "conversion_rate": add_to_cart_rate},
            {"stage": "checkouts", "count": checkouts, "drop_off": add_to_carts - checkouts, "conversion_rate": checkout_rate},
            {"stage": "purchases", "count": purchases, "drop_off": checkouts - purchases, "conversion_rate": purchase_rate}
        ]
        
        # Generate bottleneck analysis
        bottleneck_stage = min(funnel_stages[1:], key=lambda x: x["conversion_rate"])
        
        # Generate recommendations based on bottleneck
        recommendations = []
        
        if bottleneck_stage["stage"] == "clicks":
            recommendations = [
                "Improve ad copy and creative to increase click-through rate",
                "Test different headlines and images to find what resonates with your audience",
                "Refine targeting to reach more relevant potential customers"
            ]
        elif bottleneck_stage["stage"] == "add_to_carts":
            recommendations = [
                "Enhance product landing page to better showcase benefits",
                "Add more compelling product images and descriptions",
                "Include customer testimonials and social proof"
            ]
        elif bottleneck_stage["stage"] == "checkouts":
            recommendations = [
                "Simplify the checkout process to reduce abandonment",
                "Add trust signals and security badges",
                "Implement exit-intent popups with special offers"
            ]
        elif bottleneck_stage["stage"] == "purchases":
            recommendations = [
                "Review pricing strategy and consider limited-time offers",
                "Add guarantees to reduce purchase anxiety",
                "Implement abandoned cart email sequences"
            ]
            
        # Store conversion data
        self.conversion_data[product_id] = {
            "timestamp": datetime.now().isoformat(),
            "start_date": start_date,
            "end_date": end_date,
            "funnel_stages": funnel_stages,
            "overall_conversion": overall_conversion
        }
        
        return {
            "status": "success",
            "product_id": product_id,
            "product_name": product["name"],
            "start_date": start_date,
            "end_date": end_date,
            "funnel_stages": funnel_stages,
            "overall_conversion_rate": overall_conversion,
            "bottleneck_stage": bottleneck_stage["stage"],
            "recommendations": recommendations
        }
        
    async def generate_product_recommendations(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate product recommendations based on criteria.
        
        Args:
            params: Recommendation parameters
                - niche: Target niche
                - budget: Maximum budget
                - platform_preference: Preferred platform
                - count: Number of recommendations to generate
                
        Returns:
            Dict containing product recommendations
        """
        if not params:
            return {
                "status": "error",
                "message": "No parameters provided"
            }
            
        niche = params.get("niche")
        budget = float(params.get("budget", 1000))
        platform_preference = params.get("platform_preference")
        count = int(params.get("count", 5))
        
        # Filter products based on criteria
        filtered_products = list(self.products.values())
        
        # Filter by niche if specified
        if niche:
            filtered_products = [p for p in filtered_products if p["category"] == niche]
            
        # Filter by budget if specified
        if budget:
            filtered_products = [p for p in filtered_products if p["price"] <= budget]
            
        # Filter by platform if specified
        if platform_preference:
            filtered_products = [p for p in filtered_products if p["platform"] == platform_preference]
            
        if not filtered_products:
            return {
                "status": "error",
                "message": "No products match the specified criteria"
            }
            
        # Score products based on potential revenue and conversion rate
        scored_products = []
        
        for product in filtered_products:
            potential_revenue = product["price"] * (product["commission_rate"] / 100) * product["conversion_rate"]
            popularity_score = product["popularity"]
            
            # Calculate overall score
            overall_score = (potential_revenue * 0.6) + (popularity_score * 0.4)
            
            scored_products.append({
                "product": product,
                "score": overall_score
            })
            
        # Sort by score and take top N
        scored_products.sort(key=lambda x: x["score"], reverse=True)
        top_products = scored_products[:count]
        
        recommendations = []
        
        for idx, item in enumerate(top_products):
            product = item["product"]
            score = item["score"]
            
            recommendation = {
                "rank": idx + 1,
                "product_id": product["id"],
                "product_name": product["name"],
                "platform": product["platform"],
                "price": product["price"],
                "commission_rate": product["commission_rate"],
                "potential_revenue": product["price"] * (product["commission_rate"] / 100) * product["conversion_rate"],
                "recommendation_score": score,
                "reason": "High commission rate" if product["commission_rate"] > 30 else "Good conversion rate" if product["conversion_rate"] > 3 else "Popular product"
            }
            
            recommendations.append(recommendation)
            
        return {
            "status": "success",
            "count": len(recommendations),
            "recommendations": recommendations
        }
        
    async def create_ab_test(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create an A/B test for affiliate marketing content or strategy.
        
        Args:
            params: Test parameters
                - test_name: Name of the test
                - test_type: Type of test (e.g., 'content', 'landing_page', 'call_to_action')
                - variants: List of variants to test
                - duration_days: Duration of the test in days
                
        Returns:
            Dict containing test configuration
        """
        if not params:
            return {
                "status": "error",
                "message": "No parameters provided"
            }
            
        test_name = params.get("test_name")
        test_type = params.get("test_type")
        variants = params.get("variants", [])
        duration_days = int(params.get("duration_days", 14))
        
        if not test_name:
            return {
                "status": "error",
                "message": "No test name specified"
            }
            
        if not test_type:
            return {
                "status": "error",
                "message": "No test type specified"
            }
            
        if not variants or len(variants) < 2:
            return {
                "status": "error",
                "message": "At least two variants are required for an A/B test"
            }
            
        # Generate test ID
        test_id = f"test_{test_name.lower().replace(' ', '_')}_{int(time.time())}"
        
        # Configure test
        test_config = {
            "id": test_id,
            "name": test_name,
            "type": test_type,
            "variants": variants,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=duration_days)).isoformat(),
            "status": "running",
            "metrics": {},
            "winner": None
        }
        
        # Initialize metrics for each variant
        for variant in variants:
            variant_id = variant.get("id", f"variant_{variants.index(variant) + 1}")
            test_config["metrics"][variant_id] = {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "revenue": 0.0,
                "ctr": 0.0,
                "conversion_rate": 0.0
            }
            
        # Store test configuration
        if not hasattr(self, "ab_tests"):
            self.ab_tests = {}
            
        self.ab_tests[test_id] = test_config
        
        return {
            "status": "success",
            "test_id": test_id,
            "test_config": test_config
        }
        
    async def update_ab_test_metrics(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update metrics for an A/B test.
        
        Args:
            params: Update parameters
                - test_id: ID of the test to update
                - variant_id: ID of the variant to update
                - metrics: Metrics to update
                
        Returns:
            Dict containing update status
        """
        if not params:
            return {
                "status": "error",
                "message": "No parameters provided"
            }
            
        test_id = params.get("test_id")
        variant_id = params.get("variant_id")
        metrics = params.get("metrics", {})
        
        if not test_id:
            return {
                "status": "error",
                "message": "No test ID specified"
            }
            
        if not hasattr(self, "ab_tests") or test_id not in self.ab_tests:
            return {
                "status": "error",
                "message": f"Test not found: {test_id}"
            }
            
        test = self.ab_tests[test_id]
        
        if test["status"] != "running":
            return {
                "status": "error",
                "message": f"Test is not running: {test_id}"
            }
            
        if not variant_id:
            return {
                "status": "error",
                "message": "No variant ID specified"
            }
            
        if variant_id not in test["metrics"]:
            return {
                "status": "error",
                "message": f"Variant not found: {variant_id}"
            }
            
        # Update metrics
        for key, value in metrics.items():
            if key in test["metrics"][variant_id]:
                test["metrics"][variant_id][key] += value
                
        # Recalculate derived metrics
        variant_metrics = test["metrics"][variant_id]
        
        if variant_metrics["impressions"] > 0:
            variant_metrics["ctr"] = variant_metrics["clicks"] / variant_metrics["impressions"]
            
        if variant_metrics["clicks"] > 0:
            variant_metrics["conversion_rate"] = variant_metrics["conversions"] / variant_metrics["clicks"]
            
        return {
            "status": "success",
            "test_id": test_id,
            "variant_id": variant_id,
            "updated_metrics": test["metrics"][variant_id]
        }
        
    async def analyze_ab_test_results(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze the results of an A/B test.
        
        Args:
            params: Analysis parameters
                - test_id: ID of the test to analyze
                - confidence_level: Confidence level for statistical significance (default: 0.95)
                
        Returns:
            Dict containing test results and analysis
        """
        if not params:
            return {
                "status": "error",
                "message": "No parameters provided"
            }
            
        test_id = params.get("test_id")
        confidence_level = float(params.get("confidence_level", 0.95))
        
        if not test_id:
            return {
                "status": "error",
                "message": "No test ID specified"
            }
            
        if not hasattr(self, "ab_tests") or test_id not in self.ab_tests:
            return {
                "status": "error",
                "message": f"Test not found: {test_id}"
            }
            
        test = self.ab_tests[test_id]
        
        # Extract metrics for all variants
        variants_metrics = test["metrics"]
        
        if not variants_metrics:
            return {
                "status": "error",
                "message": f"No metrics recorded for test: {test_id}"
            }
            
        # Find variant with highest conversion rate
        best_variant = max(variants_metrics.items(), key=lambda x: x[1]["conversion_rate"])
        best_variant_id = best_variant[0]
        best_variant_metrics = best_variant[1]
        
        # Calculate statistical significance (simplified)
        # In a real implementation, this would use proper statistical tests
        significant = True
        for variant_id, metrics in variants_metrics.items():
            if variant_id == best_variant_id:
                continue
                
            # Simple check: if the difference is less than 20%, consider it not significant
            if best_variant_metrics["conversion_rate"] > 0 and metrics["conversion_rate"] > 0:
                difference = (best_variant_metrics["conversion_rate"] - metrics["conversion_rate"]) / metrics["conversion_rate"]
                if difference < 0.2:
                    significant = False
                    break
                    
        # Update test status
        test["status"] = "completed"
        test["completion_date"] = datetime.now().isoformat()
        test["winner"] = best_variant_id if significant else None
        test["significant"] = significant
        
        # Generate insights
        insights = []
        
        if significant:
            insights.append(f"Variant {best_variant_id} is the clear winner with a conversion rate of {best_variant_metrics['conversion_rate']:.2%}")
            insights.append(f"The winning variant generated {best_variant_metrics['revenue']:.2f} in revenue")
        else:
            insights.append("No statistically significant difference between variants")
            insights.append("Consider running the test longer or with more traffic")
            
        # Generate recommendations
        recommendations = []
        
        if significant:
            recommendations.append(f"Implement variant {best_variant_id} as the new standard")
            recommendations.append("Apply learnings from the winning variant to other marketing materials")
        else:
            recommendations.append("Refine test variants to create more differentiation")
            recommendations.append("Analyze user segments to see if certain audiences prefer different variants")
            
        return {
            "status": "success",
            "test_id": test_id,
            "test_name": test["name"],
            "test_type": test["type"],
            "start_date": test["start_date"],
            "end_date": test["completion_date"],
            "variants": test["variants"],
            "metrics": variants_metrics,
            "winner": test["winner"],
            "statistically_significant": significant,
            "confidence_level": confidence_level,
            "insights": insights,
            "recommendations": recommendations
        }
