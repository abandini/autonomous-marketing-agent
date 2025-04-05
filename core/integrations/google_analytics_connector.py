#!/usr/bin/env python3
"""
Google Analytics Connector for GAMS

This module provides integration with Google Analytics, allowing GAMS to retrieve
analytics data for marketing decision-making and performance tracking.

It supports both Universal Analytics (GA3) and Google Analytics 4 (GA4).
"""

import os
import json
import datetime
import logging
from typing import Dict, List, Any, Optional, Union

# Google API libraries
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric, 
        OrderBy, OrderBy, MetricType
    )
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GA_LIBRARIES_AVAILABLE = True
except ImportError:
    GA_LIBRARIES_AVAILABLE = False
    logging.warning("Google Analytics libraries not available. Install with: "
                   "pip install google-analytics-data google-api-python-client google-auth")

# Set up logging
logger = logging.getLogger(__name__)

class GoogleAnalyticsConnector:
    """
    Connector for Google Analytics API integration with GAMS.
    
    This class provides methods to authenticate with Google Analytics
    and retrieve various metrics and dimensions for analysis.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Google Analytics connector.
        
        Args:
            config_path: Path to the Google Analytics configuration file.
                         If None, will look for config in standard locations.
        """
        self.ga4_client = None
        self.ua_service = None
        self.config = {}
        self.credentials = None
        self.is_ga4 = False
        self.is_ua = False
        
        # Check if Google Analytics libraries are available
        if not GA_LIBRARIES_AVAILABLE:
            logger.warning("Google Analytics libraries not available. Running in mock mode.")
            return
        
        # Load configuration
        self._load_config(config_path)
        
        # Initialize clients based on configuration
        self._initialize_clients()
    
    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        Load Google Analytics configuration from a file.
        
        Args:
            config_path: Path to the configuration file. If None, will check
                         standard locations.
        """
        # Default paths to check for config
        default_paths = [
            os.path.join(os.getcwd(), 'config', 'google_analytics.json'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                         'config', 'google_analytics.json'),
            os.path.expanduser('~/.gams/google_analytics.json')
        ]
        
        # If config_path is provided, check it first
        if config_path:
            default_paths.insert(0, config_path)
        
        # Try to load from each path
        for path in default_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        self.config = json.load(f)
                    logger.info(f"Loaded Google Analytics configuration from {path}")
                    break
                except Exception as e:
                    logger.error(f"Error loading Google Analytics configuration from {path}: {e}")
        
        # If no config was loaded, use empty config
        if not self.config:
            logger.warning("No Google Analytics configuration found. Using default empty configuration.")
            self.config = {
                "ga4": {
                    "enabled": False,
                    "property_id": "",
                    "credentials_file": ""
                },
                "universal_analytics": {
                    "enabled": False,
                    "view_id": "",
                    "credentials_file": ""
                }
            }
    
    def _initialize_clients(self) -> None:
        """Initialize Google Analytics clients based on configuration."""
        # Initialize GA4 client if enabled
        if self.config.get('ga4', {}).get('enabled', False):
            try:
                credentials_file = self.config['ga4']['credentials_file']
                if os.path.exists(credentials_file):
                    self.credentials = Credentials.from_service_account_file(
                        credentials_file,
                        scopes=['https://www.googleapis.com/auth/analytics.readonly']
                    )
                    self.ga4_client = BetaAnalyticsDataClient(credentials=self.credentials)
                    self.is_ga4 = True
                    logger.info("GA4 client initialized successfully")
                else:
                    logger.error(f"GA4 credentials file not found: {credentials_file}")
            except Exception as e:
                logger.error(f"Error initializing GA4 client: {e}")
        
        # Initialize Universal Analytics client if enabled
        if self.config.get('universal_analytics', {}).get('enabled', False):
            try:
                credentials_file = self.config['universal_analytics']['credentials_file']
                if os.path.exists(credentials_file):
                    self.credentials = Credentials.from_service_account_file(
                        credentials_file,
                        scopes=['https://www.googleapis.com/auth/analytics.readonly']
                    )
                    self.ua_service = build('analyticsreporting', 'v4', credentials=self.credentials)
                    self.is_ua = True
                    logger.info("Universal Analytics client initialized successfully")
                else:
                    logger.error(f"Universal Analytics credentials file not found: {credentials_file}")
            except Exception as e:
                logger.error(f"Error initializing Universal Analytics client: {e}")
    
    def get_ga4_report(self, 
                      metrics: List[str], 
                      dimensions: List[str] = None, 
                      date_range_days: int = 30,
                      limit: int = 100) -> Dict[str, Any]:
        """
        Get a report from Google Analytics 4.
        
        Args:
            metrics: List of metrics to retrieve (e.g., ['activeUsers', 'sessions'])
            dimensions: Optional list of dimensions (e.g., ['date', 'country'])
            date_range_days: Number of days to include in the report
            limit: Maximum number of rows to return
            
        Returns:
            Dictionary containing the report data
        """
        if not self.is_ga4:
            return self._get_mock_data(metrics, dimensions, date_range_days)
        
        try:
            property_id = self.config['ga4']['property_id']
            
            # Create dimension objects
            dimension_objects = []
            if dimensions:
                for dimension in dimensions:
                    dimension_objects.append(Dimension(name=dimension))
            
            # Create metric objects
            metric_objects = []
            for metric in metrics:
                metric_objects.append(Metric(name=metric))
            
            # Create date range
            end_date = datetime.datetime.now().date()
            start_date = end_date - datetime.timedelta(days=date_range_days)
            date_range = DateRange(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            # Create the request
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=dimension_objects,
                metrics=metric_objects,
                date_ranges=[date_range],
                limit=limit
            )
            
            # Make the request
            response = self.ga4_client.run_report(request)
            
            # Process the response
            result = {
                'report_type': 'ga4',
                'dimensions': dimensions or [],
                'metrics': metrics,
                'rows': []
            }
            
            # Extract dimension and metric headers
            dimension_headers = [header.name for header in response.dimension_headers]
            metric_headers = [header.name for header in response.metric_headers]
            
            # Extract rows
            for row in response.rows:
                row_data = {}
                
                # Add dimensions
                for i, dimension_value in enumerate(row.dimension_values):
                    row_data[dimension_headers[i]] = dimension_value.value
                
                # Add metrics
                for i, metric_value in enumerate(row.metric_values):
                    row_data[metric_headers[i]] = metric_value.value
                
                result['rows'].append(row_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting GA4 report: {e}")
            return self._get_mock_data(metrics, dimensions, date_range_days)
    
    def get_ua_report(self, 
                     metrics: List[str], 
                     dimensions: List[str] = None, 
                     date_range_days: int = 30,
                     limit: int = 100) -> Dict[str, Any]:
        """
        Get a report from Universal Analytics.
        
        Args:
            metrics: List of metrics to retrieve (e.g., ['ga:users', 'ga:sessions'])
            dimensions: Optional list of dimensions (e.g., ['ga:date', 'ga:country'])
            date_range_days: Number of days to include in the report
            limit: Maximum number of rows to return
            
        Returns:
            Dictionary containing the report data
        """
        if not self.is_ua:
            return self._get_mock_data(metrics, dimensions, date_range_days, prefix='ga:')
        
        try:
            view_id = self.config['universal_analytics']['view_id']
            
            # Create date range
            end_date = datetime.datetime.now().date()
            start_date = end_date - datetime.timedelta(days=date_range_days)
            
            # Ensure metrics have ga: prefix
            metrics_list = [{'expression': m if m.startswith('ga:') else f'ga:{m}'} 
                           for m in metrics]
            
            # Ensure dimensions have ga: prefix if provided
            dimensions_list = []
            if dimensions:
                dimensions_list = [{'name': d if d.startswith('ga:') else f'ga:{d}'} 
                                  for d in dimensions]
            
            # Create the request body
            request_body = {
                'reportRequests': [{
                    'viewId': view_id,
                    'dateRanges': [{'startDate': start_date.strftime('%Y-%m-%d'), 
                                   'endDate': end_date.strftime('%Y-%m-%d')}],
                    'metrics': metrics_list,
                    'pageSize': limit
                }]
            }
            
            # Add dimensions if provided
            if dimensions_list:
                request_body['reportRequests'][0]['dimensions'] = dimensions_list
            
            # Make the request
            response = self.ua_service.reports().batchGet(body=request_body).execute()
            
            # Process the response
            result = {
                'report_type': 'universal_analytics',
                'dimensions': dimensions or [],
                'metrics': metrics,
                'rows': []
            }
            
            # Extract report data
            for report in response.get('reports', []):
                column_header = report.get('columnHeader', {})
                dimension_headers = []
                if 'dimensions' in column_header:
                    dimension_headers = [h.replace('ga:', '') for h in column_header['dimensions']]
                
                metric_headers = []
                if 'metricHeader' in column_header:
                    metric_headers = [h['name'].replace('ga:', '') 
                                     for h in column_header['metricHeader']['metricHeaderEntries']]
                
                # Extract rows
                for row in report.get('data', {}).get('rows', []):
                    row_data = {}
                    
                    # Add dimensions
                    dimensions = row.get('dimensions', [])
                    for i, dimension in enumerate(dimensions):
                        row_data[dimension_headers[i]] = dimension
                    
                    # Add metrics
                    metrics = row.get('metrics', [])[0].get('values', [])
                    for i, metric in enumerate(metrics):
                        row_data[metric_headers[i]] = metric
                    
                    result['rows'].append(row_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting Universal Analytics report: {e}")
            return self._get_mock_data(metrics, dimensions, date_range_days, prefix='ga:')
    
    def get_report(self, 
                  metrics: List[str], 
                  dimensions: List[str] = None, 
                  date_range_days: int = 30,
                  limit: int = 100,
                  prefer_ga4: bool = True) -> Dict[str, Any]:
        """
        Get a report from the preferred Google Analytics property.
        
        This method will try to use GA4 first if prefer_ga4 is True,
        otherwise it will try Universal Analytics first. If the preferred
        method fails, it will fall back to the other method.
        
        Args:
            metrics: List of metrics to retrieve
            dimensions: Optional list of dimensions
            date_range_days: Number of days to include in the report
            limit: Maximum number of rows to return
            prefer_ga4: Whether to prefer GA4 over Universal Analytics
            
        Returns:
            Dictionary containing the report data
        """
        if prefer_ga4 and self.is_ga4:
            return self.get_ga4_report(metrics, dimensions, date_range_days, limit)
        elif self.is_ua:
            return self.get_ua_report(metrics, dimensions, date_range_days, limit)
        elif self.is_ga4:
            return self.get_ga4_report(metrics, dimensions, date_range_days, limit)
        else:
            return self._get_mock_data(metrics, dimensions, date_range_days)
    
    def get_website_traffic(self, date_range_days: int = 30) -> Dict[str, Any]:
        """
        Get website traffic data.
        
        Args:
            date_range_days: Number of days to include in the report
            
        Returns:
            Dictionary containing traffic data
        """
        if self.is_ga4:
            metrics = ['activeUsers', 'sessions', 'screenPageViews']
            dimensions = ['date']
        else:
            metrics = ['ga:users', 'ga:sessions', 'ga:pageviews']
            dimensions = ['ga:date']
        
        return self.get_report(metrics, dimensions, date_range_days)
    
    def get_conversion_data(self, date_range_days: int = 30) -> Dict[str, Any]:
        """
        Get conversion data.
        
        Args:
            date_range_days: Number of days to include in the report
            
        Returns:
            Dictionary containing conversion data
        """
        if self.is_ga4:
            metrics = ['conversions', 'conversionRate']
            dimensions = ['date']
        else:
            metrics = ['ga:goalCompletionsAll', 'ga:goalConversionRateAll']
            dimensions = ['ga:date']
        
        return self.get_report(metrics, dimensions, date_range_days)
    
    def get_content_performance(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get performance data for content pages.
        
        Args:
            limit: Maximum number of pages to return
            
        Returns:
            Dictionary containing content performance data
        """
        if self.is_ga4:
            metrics = ['screenPageViews', 'averageSessionDuration', 'bounceRate']
            dimensions = ['pagePath']
        else:
            metrics = ['ga:pageviews', 'ga:avgTimeOnPage', 'ga:bounceRate']
            dimensions = ['ga:pagePath']
        
        return self.get_report(metrics, dimensions, 30, limit)
    
    def get_traffic_sources(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get traffic source data.
        
        Args:
            limit: Maximum number of sources to return
            
        Returns:
            Dictionary containing traffic source data
        """
        if self.is_ga4:
            metrics = ['sessions', 'activeUsers']
            dimensions = ['sessionSource', 'sessionMedium']
        else:
            metrics = ['ga:sessions', 'ga:users']
            dimensions = ['ga:source', 'ga:medium']
        
        return self.get_report(metrics, dimensions, 30, limit)
    
    def get_keyword_performance(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get performance data for keywords.
        
        Note: This data is limited in GA4 and may require Search Console integration
        for comprehensive keyword data.
        
        Args:
            limit: Maximum number of keywords to return
            
        Returns:
            Dictionary containing keyword performance data
        """
        if self.is_ga4:
            # GA4 doesn't provide keyword data directly
            # This is a simplified approach that uses query parameters
            metrics = ['sessions', 'conversions']
            dimensions = ['queryParameter']
        else:
            metrics = ['ga:sessions', 'ga:goalCompletionsAll']
            dimensions = ['ga:keyword']
        
        return self.get_report(metrics, dimensions, 30, limit)
    
    def get_device_breakdown(self) -> Dict[str, Any]:
        """
        Get breakdown of traffic by device category.
        
        Returns:
            Dictionary containing device breakdown data
        """
        if self.is_ga4:
            metrics = ['activeUsers', 'sessions', 'screenPageViews']
            dimensions = ['deviceCategory']
        else:
            metrics = ['ga:users', 'ga:sessions', 'ga:pageviews']
            dimensions = ['ga:deviceCategory']
        
        return self.get_report(metrics, dimensions, 30, 10)
    
    def _get_mock_data(self, 
                      metrics: List[str], 
                      dimensions: List[str] = None, 
                      date_range_days: int = 30,
                      prefix: str = '') -> Dict[str, Any]:
        """
        Generate mock data for testing when Google Analytics is not available.
        
        Args:
            metrics: List of metrics
            dimensions: Optional list of dimensions
            date_range_days: Number of days to include
            prefix: Prefix for metrics and dimensions (e.g., 'ga:')
            
        Returns:
            Dictionary containing mock data
        """
        import random
        
        # Clean metric names (remove prefix if present)
        clean_metrics = [m.replace(prefix, '') for m in metrics]
        
        # Clean dimension names (remove prefix if present)
        clean_dimensions = []
        if dimensions:
            clean_dimensions = [d.replace(prefix, '') for d in dimensions]
        
        result = {
            'report_type': 'mock',
            'dimensions': clean_dimensions,
            'metrics': clean_metrics,
            'rows': []
        }
        
        # Generate mock data based on dimensions
        if dimensions and 'date' in clean_dimensions or 'yearMonth' in clean_dimensions:
            # Generate time-series data
            end_date = datetime.datetime.now().date()
            
            for i in range(date_range_days):
                date = end_date - datetime.timedelta(days=i)
                row = {}
                
                # Add date dimension
                date_str = date.strftime('%Y%m%d')
                if 'date' in clean_dimensions:
                    row['date'] = date_str
                if 'yearMonth' in clean_dimensions:
                    row['yearMonth'] = date_str[:6]
                
                # Add other dimensions with mock values
                for dim in clean_dimensions:
                    if dim not in ['date', 'yearMonth']:
                        row[dim] = f"mock_{dim}_{random.randint(1, 5)}"
                
                # Add metrics with realistic mock values
                for metric in clean_metrics:
                    if 'users' in metric or 'activeUsers' in metric:
                        row[metric] = str(random.randint(500, 2000))
                    elif 'sessions' in metric:
                        row[metric] = str(random.randint(800, 3000))
                    elif 'pageviews' in metric or 'screenPageViews' in metric:
                        row[metric] = str(random.randint(2000, 8000))
                    elif 'bounceRate' in metric:
                        row[metric] = str(random.uniform(20, 60))
                    elif 'conversionRate' in metric:
                        row[metric] = str(random.uniform(1, 10))
                    elif 'conversions' in metric or 'goalCompletions' in metric:
                        row[metric] = str(random.randint(10, 100))
                    elif 'duration' in metric.lower() or 'timeOnPage' in metric.lower():
                        row[metric] = str(random.randint(30, 300))
                    else:
                        row[metric] = str(random.randint(1, 1000))
                
                result['rows'].append(row)
            
            # Sort by date (newest first)
            result['rows'].sort(key=lambda x: x.get('date', ''), reverse=True)
            
        elif dimensions and ('pagePath' in clean_dimensions or 'page' in clean_dimensions):
            # Generate page-specific data
            pages = [
                '/home', '/about', '/products', '/services', '/blog',
                '/blog/post-1', '/blog/post-2', '/contact', '/pricing',
                '/products/product-1', '/products/product-2', '/products/product-3'
            ]
            
            for page in pages[:min(len(pages), 20)]:
                row = {}
                
                # Add page dimension
                if 'pagePath' in clean_dimensions:
                    row['pagePath'] = page
                if 'page' in clean_dimensions:
                    row['page'] = page
                
                # Add other dimensions with mock values
                for dim in clean_dimensions:
                    if dim not in ['pagePath', 'page']:
                        row[dim] = f"mock_{dim}_{random.randint(1, 5)}"
                
                # Add metrics with realistic mock values
                for metric in clean_metrics:
                    if 'pageviews' in metric or 'screenPageViews' in metric:
                        row[metric] = str(random.randint(100, 2000))
                    elif 'bounceRate' in metric:
                        row[metric] = str(random.uniform(20, 60))
                    elif 'duration' in metric.lower() or 'timeOnPage' in metric.lower():
                        row[metric] = str(random.randint(30, 300))
                    else:
                        row[metric] = str(random.randint(1, 500))
                
                result['rows'].append(row)
                
        elif dimensions and any(dim in clean_dimensions for dim in ['source', 'medium', 'sessionSource', 'sessionMedium']):
            # Generate traffic source data
            sources = [
                {'source': 'google', 'medium': 'organic'},
                {'source': 'direct', 'medium': 'none'},
                {'source': 'facebook', 'medium': 'social'},
                {'source': 'twitter', 'medium': 'social'},
                {'source': 'email', 'medium': 'email'},
                {'source': 'bing', 'medium': 'organic'},
                {'source': 'linkedin', 'medium': 'social'},
                {'source': 'referral', 'medium': 'referral'}
            ]
            
            for source_data in sources:
                row = {}
                
                # Add source/medium dimensions
                if 'source' in clean_dimensions:
                    row['source'] = source_data['source']
                if 'sessionSource' in clean_dimensions:
                    row['sessionSource'] = source_data['source']
                if 'medium' in clean_dimensions:
                    row['medium'] = source_data['medium']
                if 'sessionMedium' in clean_dimensions:
                    row['sessionMedium'] = source_data['medium']
                
                # Add other dimensions with mock values
                for dim in clean_dimensions:
                    if dim not in ['source', 'medium', 'sessionSource', 'sessionMedium']:
                        row[dim] = f"mock_{dim}_{random.randint(1, 5)}"
                
                # Add metrics with realistic mock values
                for metric in clean_metrics:
                    if 'users' in metric or 'activeUsers' in metric:
                        row[metric] = str(random.randint(100, 1000))
                    elif 'sessions' in metric:
                        row[metric] = str(random.randint(150, 1500))
                    else:
                        row[metric] = str(random.randint(1, 500))
                
                result['rows'].append(row)
        
        else:
            # Generate generic data
            for i in range(min(20, date_range_days)):
                row = {}
                
                # Add dimensions with mock values
                if dimensions:
                    for dim in clean_dimensions:
                        row[dim] = f"mock_{dim}_{random.randint(1, 5)}"
                
                # Add metrics with mock values
                for metric in clean_metrics:
                    row[metric] = str(random.randint(1, 1000))
                
                result['rows'].append(row)
        
        return result


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create connector
    connector = GoogleAnalyticsConnector()
    
    # Get website traffic
    traffic_data = connector.get_website_traffic(7)
    print("Website Traffic Data:")
    print(json.dumps(traffic_data, indent=2))
    
    # Get conversion data
    conversion_data = connector.get_conversion_data(7)
    print("\nConversion Data:")
    print(json.dumps(conversion_data, indent=2))
    
    # Get content performance
    content_data = connector.get_content_performance(5)
    print("\nContent Performance Data:")
    print(json.dumps(content_data, indent=2))
