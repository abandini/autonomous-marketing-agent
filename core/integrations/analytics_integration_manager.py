#!/usr/bin/env python3
"""
Analytics Integration Manager for GAMS

This module manages the integration between external analytics services
(like Google Analytics) and the GAMS Analytics Engine.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Union

# Import Google Analytics connector
from core.integrations.google_analytics_connector import GoogleAnalyticsConnector

# Try to import Analytics Engine components
try:
    from core.analytics.analytics_engine import AnalyticsEngine
    from core.analytics.metrics_collector import MetricsCollector
    ANALYTICS_ENGINE_AVAILABLE = True
except ImportError:
    ANALYTICS_ENGINE_AVAILABLE = False
    logging.warning("Analytics Engine not available. Some functionality will be limited.")

# Set up logging
logger = logging.getLogger(__name__)

class AnalyticsIntegrationManager:
    """
    Manages integration between external analytics services and the GAMS Analytics Engine.
    
    This class provides methods to:
    - Connect to external analytics services
    - Retrieve data from these services
    - Process and transform the data
    - Feed the data into the GAMS Analytics Engine
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Analytics Integration Manager.
        
        Args:
            config_path: Path to the configuration file. If None, will check
                         standard locations.
        """
        self.config = {}
        self.ga_connector = None
        self.analytics_engine = None
        self.metrics_collector = None
        
        # Load configuration
        self._load_config(config_path)
        
        # Initialize components
        self._initialize_components()
    
    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file. If None, will check
                         standard locations.
        """
        # Default paths to check for config
        default_paths = [
            os.path.join(os.getcwd(), 'config', 'analytics_integration.json'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                         'config', 'analytics_integration.json'),
            os.path.expanduser('~/.gams/analytics_integration.json')
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
                    logger.info(f"Loaded analytics integration configuration from {path}")
                    break
                except Exception as e:
                    logger.error(f"Error loading analytics integration configuration from {path}: {e}")
        
        # If no config was loaded, use default config
        if not self.config:
            logger.warning("No analytics integration configuration found. Using default configuration.")
            self.config = {
                "google_analytics": {
                    "enabled": True,
                    "config_path": None
                },
                "sync_interval": 3600,  # Sync every hour by default
                "data_retention_days": 90,  # Keep 90 days of data by default
                "metrics_mapping": {
                    "website_traffic": {
                        "ga:users": "users",
                        "ga:sessions": "sessions",
                        "ga:pageviews": "pageviews",
                        "activeUsers": "users",
                        "sessions": "sessions",
                        "screenPageViews": "pageviews"
                    },
                    "conversions": {
                        "ga:goalCompletionsAll": "conversions",
                        "ga:goalConversionRateAll": "conversion_rate",
                        "conversions": "conversions",
                        "conversionRate": "conversion_rate"
                    }
                }
            }
    
    def _initialize_components(self) -> None:
        """Initialize the required components based on configuration."""
        # Initialize Google Analytics connector if enabled
        if self.config.get('google_analytics', {}).get('enabled', False):
            try:
                ga_config_path = self.config['google_analytics'].get('config_path')
                self.ga_connector = GoogleAnalyticsConnector(ga_config_path)
                logger.info("Google Analytics connector initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Google Analytics connector: {e}")
        
        # Initialize Analytics Engine components if available
        if ANALYTICS_ENGINE_AVAILABLE:
            try:
                self.analytics_engine = AnalyticsEngine()
                self.metrics_collector = MetricsCollector()
                logger.info("Analytics Engine components initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Analytics Engine components: {e}")
    
    def sync_google_analytics_data(self, date_range_days: int = 30) -> Dict[str, Any]:
        """
        Sync data from Google Analytics to the GAMS Analytics Engine.
        
        Args:
            date_range_days: Number of days of data to sync
            
        Returns:
            Dictionary containing the sync results
        """
        if not self.ga_connector:
            logger.error("Google Analytics connector not initialized")
            return {"status": "error", "message": "Google Analytics connector not initialized"}
        
        sync_results = {
            "status": "success",
            "timestamp": datetime.datetime.now().isoformat(),
            "data_sources": ["google_analytics"],
            "metrics_synced": [],
            "errors": []
        }
        
        try:
            # Get website traffic data
            traffic_data = self.ga_connector.get_website_traffic(date_range_days)
            if traffic_data and 'rows' in traffic_data:
                self._process_and_store_traffic_data(traffic_data)
                sync_results["metrics_synced"].append("website_traffic")
            
            # Get conversion data
            conversion_data = self.ga_connector.get_conversion_data(date_range_days)
            if conversion_data and 'rows' in conversion_data:
                self._process_and_store_conversion_data(conversion_data)
                sync_results["metrics_synced"].append("conversions")
            
            # Get content performance data
            content_data = self.ga_connector.get_content_performance()
            if content_data and 'rows' in content_data:
                self._process_and_store_content_data(content_data)
                sync_results["metrics_synced"].append("content_performance")
            
            # Get traffic sources data
            sources_data = self.ga_connector.get_traffic_sources()
            if sources_data and 'rows' in sources_data:
                self._process_and_store_sources_data(sources_data)
                sync_results["metrics_synced"].append("traffic_sources")
            
            # Get device breakdown data
            device_data = self.ga_connector.get_device_breakdown()
            if device_data and 'rows' in device_data:
                self._process_and_store_device_data(device_data)
                sync_results["metrics_synced"].append("device_breakdown")
            
            logger.info(f"Successfully synced Google Analytics data: {', '.join(sync_results['metrics_synced'])}")
            
        except Exception as e:
            error_msg = f"Error syncing Google Analytics data: {str(e)}"
            logger.error(error_msg)
            sync_results["status"] = "partial"
            sync_results["errors"].append(error_msg)
        
        return sync_results
    
    def _process_and_store_traffic_data(self, traffic_data: Dict[str, Any]) -> None:
        """
        Process and store website traffic data.
        
        Args:
            traffic_data: Traffic data from Google Analytics
        """
        if not ANALYTICS_ENGINE_AVAILABLE or not self.analytics_engine:
            logger.warning("Analytics Engine not available. Cannot store traffic data.")
            return
        
        try:
            # Map GA metrics to our internal metrics
            metrics_mapping = self.config.get('metrics_mapping', {}).get('website_traffic', {})
            
            # Process each row (typically each day)
            for row in traffic_data.get('rows', []):
                # Get date from the row
                date_str = row.get('date', datetime.datetime.now().strftime('%Y%m%d'))
                try:
                    # Convert YYYYMMDD to datetime
                    date = datetime.datetime.strptime(date_str, '%Y%m%d').date()
                except ValueError:
                    # If date is not in expected format, use current date
                    date = datetime.datetime.now().date()
                
                # Map and store metrics
                metrics = {}
                for ga_metric, internal_metric in metrics_mapping.items():
                    if ga_metric in row:
                        try:
                            # Convert to appropriate type (int or float)
                            value = row[ga_metric]
                            if '.' in value:
                                metrics[internal_metric] = float(value)
                            else:
                                metrics[internal_metric] = int(value)
                        except (ValueError, TypeError):
                            # If conversion fails, store as string
                            metrics[internal_metric] = row[ga_metric]
                
                # Store in Analytics Engine
                self.analytics_engine.update_metrics(
                    category="website_traffic",
                    date=date,
                    metrics=metrics,
                    source="google_analytics"
                )
            
            logger.info(f"Processed and stored {len(traffic_data.get('rows', []))} traffic data points")
            
        except Exception as e:
            logger.error(f"Error processing traffic data: {e}")
    
    def _process_and_store_conversion_data(self, conversion_data: Dict[str, Any]) -> None:
        """
        Process and store conversion data.
        
        Args:
            conversion_data: Conversion data from Google Analytics
        """
        if not ANALYTICS_ENGINE_AVAILABLE or not self.analytics_engine:
            logger.warning("Analytics Engine not available. Cannot store conversion data.")
            return
        
        try:
            # Map GA metrics to our internal metrics
            metrics_mapping = self.config.get('metrics_mapping', {}).get('conversions', {})
            
            # Process each row (typically each day)
            for row in conversion_data.get('rows', []):
                # Get date from the row
                date_str = row.get('date', datetime.datetime.now().strftime('%Y%m%d'))
                try:
                    # Convert YYYYMMDD to datetime
                    date = datetime.datetime.strptime(date_str, '%Y%m%d').date()
                except ValueError:
                    # If date is not in expected format, use current date
                    date = datetime.datetime.now().date()
                
                # Map and store metrics
                metrics = {}
                for ga_metric, internal_metric in metrics_mapping.items():
                    if ga_metric in row:
                        try:
                            # Convert to appropriate type (int or float)
                            value = row[ga_metric]
                            if '.' in value or internal_metric == 'conversion_rate':
                                metrics[internal_metric] = float(value)
                            else:
                                metrics[internal_metric] = int(value)
                        except (ValueError, TypeError):
                            # If conversion fails, store as string
                            metrics[internal_metric] = row[ga_metric]
                
                # Store in Analytics Engine
                self.analytics_engine.update_metrics(
                    category="conversions",
                    date=date,
                    metrics=metrics,
                    source="google_analytics"
                )
            
            logger.info(f"Processed and stored {len(conversion_data.get('rows', []))} conversion data points")
            
        except Exception as e:
            logger.error(f"Error processing conversion data: {e}")
    
    def _process_and_store_content_data(self, content_data: Dict[str, Any]) -> None:
        """
        Process and store content performance data.
        
        Args:
            content_data: Content performance data from Google Analytics
        """
        if not ANALYTICS_ENGINE_AVAILABLE or not self.analytics_engine:
            logger.warning("Analytics Engine not available. Cannot store content data.")
            return
        
        try:
            # Process each row (each page)
            for row in content_data.get('rows', []):
                # Get page path
                page_path = row.get('pagePath', '') or row.get('page', '')
                if not page_path:
                    continue
                
                # Extract metrics
                metrics = {}
                
                # Handle different metric names between GA4 and UA
                if 'screenPageViews' in row:
                    metrics['pageviews'] = int(row['screenPageViews'])
                elif 'pageviews' in row:
                    metrics['pageviews'] = int(row['pageviews'])
                
                if 'averageSessionDuration' in row:
                    metrics['avg_time_on_page'] = float(row['averageSessionDuration'])
                elif 'avgTimeOnPage' in row:
                    metrics['avg_time_on_page'] = float(row['avgTimeOnPage'])
                
                if 'bounceRate' in row:
                    metrics['bounce_rate'] = float(row['bounceRate'])
                
                # Store in Analytics Engine
                self.analytics_engine.update_content_metrics(
                    content_id=page_path,
                    metrics=metrics,
                    source="google_analytics"
                )
            
            logger.info(f"Processed and stored performance data for {len(content_data.get('rows', []))} content pages")
            
        except Exception as e:
            logger.error(f"Error processing content data: {e}")
    
    def _process_and_store_sources_data(self, sources_data: Dict[str, Any]) -> None:
        """
        Process and store traffic sources data.
        
        Args:
            sources_data: Traffic sources data from Google Analytics
        """
        if not ANALYTICS_ENGINE_AVAILABLE or not self.analytics_engine:
            logger.warning("Analytics Engine not available. Cannot store sources data.")
            return
        
        try:
            # Process each row (each source/medium)
            for row in sources_data.get('rows', []):
                # Get source and medium
                source = row.get('source', '') or row.get('sessionSource', '')
                medium = row.get('medium', '') or row.get('sessionMedium', '')
                if not source:
                    continue
                
                # Create a source identifier
                source_id = f"{source}/{medium}" if medium else source
                
                # Extract metrics
                metrics = {}
                
                if 'sessions' in row:
                    metrics['sessions'] = int(row['sessions'])
                
                if 'activeUsers' in row:
                    metrics['users'] = int(row['activeUsers'])
                elif 'users' in row:
                    metrics['users'] = int(row['users'])
                
                # Store in Analytics Engine
                self.analytics_engine.update_source_metrics(
                    source_id=source_id,
                    metrics=metrics,
                    source="google_analytics"
                )
            
            logger.info(f"Processed and stored data for {len(sources_data.get('rows', []))} traffic sources")
            
        except Exception as e:
            logger.error(f"Error processing sources data: {e}")
    
    def _process_and_store_device_data(self, device_data: Dict[str, Any]) -> None:
        """
        Process and store device breakdown data.
        
        Args:
            device_data: Device breakdown data from Google Analytics
        """
        if not ANALYTICS_ENGINE_AVAILABLE or not self.analytics_engine:
            logger.warning("Analytics Engine not available. Cannot store device data.")
            return
        
        try:
            # Process each row (each device category)
            for row in device_data.get('rows', []):
                # Get device category
                device = row.get('deviceCategory', '')
                if not device:
                    continue
                
                # Extract metrics
                metrics = {}
                
                if 'sessions' in row:
                    metrics['sessions'] = int(row['sessions'])
                
                if 'activeUsers' in row:
                    metrics['users'] = int(row['activeUsers'])
                elif 'users' in row:
                    metrics['users'] = int(row['users'])
                
                if 'screenPageViews' in row:
                    metrics['pageviews'] = int(row['screenPageViews'])
                elif 'pageviews' in row:
                    metrics['pageviews'] = int(row['pageviews'])
                
                # Store in Analytics Engine
                self.analytics_engine.update_segment_metrics(
                    segment_type="device",
                    segment_id=device,
                    metrics=metrics,
                    source="google_analytics"
                )
            
            logger.info(f"Processed and stored data for {len(device_data.get('rows', []))} device categories")
            
        except Exception as e:
            logger.error(f"Error processing device data: {e}")
    
    def get_analytics_data_for_dashboard(self) -> Dict[str, Any]:
        """
        Get analytics data formatted for the dashboard.
        
        Returns:
            Dictionary containing formatted analytics data
        """
        dashboard_data = {
            "website_traffic": {
                "labels": [],
                "website_traffic": [],
                "conversions": [],
                "bounce_rate": [],
                "avg_session_duration": []
            },
            "content_performance": [],
            "traffic_sources": [],
            "device_breakdown": []
        }
        
        # If Analytics Engine is not available, try to get data directly from GA
        if not ANALYTICS_ENGINE_AVAILABLE or not self.analytics_engine:
            if self.ga_connector:
                # Get traffic data
                traffic_data = self.ga_connector.get_website_traffic(30)
                if traffic_data and 'rows' in traffic_data:
                    # Sort by date
                    rows = sorted(traffic_data['rows'], 
                                 key=lambda x: x.get('date', ''))
                    
                    # Extract data for chart
                    for row in rows:
                        date_str = row.get('date', '')
                        if date_str:
                            # Format date as MMM DD
                            try:
                                date = datetime.datetime.strptime(date_str, '%Y%m%d')
                                dashboard_data["website_traffic"]["labels"].append(
                                    date.strftime('%b %d')
                                )
                            except ValueError:
                                dashboard_data["website_traffic"]["labels"].append(date_str)
                        
                        # Extract metrics
                        if 'activeUsers' in row:
                            dashboard_data["website_traffic"]["website_traffic"].append(
                                int(row['activeUsers'])
                            )
                        elif 'users' in row:
                            dashboard_data["website_traffic"]["website_traffic"].append(
                                int(row['users'])
                            )
                
                # Get conversion data
                conversion_data = self.ga_connector.get_conversion_data(30)
                if conversion_data and 'rows' in conversion_data:
                    # Sort by date
                    rows = sorted(conversion_data['rows'], 
                                 key=lambda x: x.get('date', ''))
                    
                    # Extract data for chart
                    for row in rows:
                        if 'conversions' in row:
                            dashboard_data["website_traffic"]["conversions"].append(
                                int(row['conversions'])
                            )
                        elif 'goalCompletionsAll' in row:
                            dashboard_data["website_traffic"]["conversions"].append(
                                int(row['goalCompletionsAll'])
                            )
                
                # Get content performance data
                content_data = self.ga_connector.get_content_performance(10)
                if content_data and 'rows' in content_data:
                    for row in content_data['rows']:
                        page_path = row.get('pagePath', '') or row.get('page', '')
                        if not page_path:
                            continue
                        
                        content_item = {
                            "page": page_path,
                            "pageviews": 0,
                            "avg_time_on_page": 0,
                            "bounce_rate": 0
                        }
                        
                        if 'screenPageViews' in row:
                            content_item["pageviews"] = int(row['screenPageViews'])
                        elif 'pageviews' in row:
                            content_item["pageviews"] = int(row['pageviews'])
                        
                        if 'averageSessionDuration' in row:
                            content_item["avg_time_on_page"] = float(row['averageSessionDuration'])
                        elif 'avgTimeOnPage' in row:
                            content_item["avg_time_on_page"] = float(row['avgTimeOnPage'])
                        
                        if 'bounceRate' in row:
                            content_item["bounce_rate"] = float(row['bounceRate'])
                        
                        dashboard_data["content_performance"].append(content_item)
                
                # Get traffic sources data
                sources_data = self.ga_connector.get_traffic_sources(5)
                if sources_data and 'rows' in sources_data:
                    for row in sources_data['rows']:
                        source = row.get('source', '') or row.get('sessionSource', '')
                        medium = row.get('medium', '') or row.get('sessionMedium', '')
                        if not source:
                            continue
                        
                        source_item = {
                            "source": f"{source}/{medium}" if medium else source,
                            "sessions": 0,
                            "users": 0
                        }
                        
                        if 'sessions' in row:
                            source_item["sessions"] = int(row['sessions'])
                        
                        if 'activeUsers' in row:
                            source_item["users"] = int(row['activeUsers'])
                        elif 'users' in row:
                            source_item["users"] = int(row['users'])
                        
                        dashboard_data["traffic_sources"].append(source_item)
                
                # Get device breakdown data
                device_data = self.ga_connector.get_device_breakdown()
                if device_data and 'rows' in device_data:
                    for row in device_data['rows']:
                        device = row.get('deviceCategory', '')
                        if not device:
                            continue
                        
                        device_item = {
                            "device": device,
                            "sessions": 0,
                            "users": 0
                        }
                        
                        if 'sessions' in row:
                            device_item["sessions"] = int(row['sessions'])
                        
                        if 'activeUsers' in row:
                            device_item["users"] = int(row['activeUsers'])
                        elif 'users' in row:
                            device_item["users"] = int(row['users'])
                        
                        dashboard_data["device_breakdown"].append(device_item)
            
            return dashboard_data
        
        # If Analytics Engine is available, get data from it
        try:
            # Get traffic data for the last 30 days
            end_date = datetime.datetime.now().date()
            start_date = end_date - datetime.timedelta(days=30)
            
            traffic_data = self.analytics_engine.get_metrics(
                category="website_traffic",
                start_date=start_date,
                end_date=end_date
            )
            
            # Process traffic data
            dates = []
            traffic_values = []
            conversion_values = []
            bounce_rate_values = []
            duration_values = []
            
            for date_str, metrics in traffic_data.items():
                try:
                    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                    dates.append(date.strftime('%b %d'))
                except ValueError:
                    dates.append(date_str)
                
                traffic_values.append(metrics.get('users', 0))
                
                # Get conversion data for the same date
                conversion_metrics = self.analytics_engine.get_metrics(
                    category="conversions",
                    start_date=date,
                    end_date=date
                )
                
                if date_str in conversion_metrics:
                    conversion_values.append(conversion_metrics[date_str].get('conversions', 0))
                    bounce_rate_values.append(metrics.get('bounce_rate', 0))
                    duration_values.append(metrics.get('avg_session_duration', 0))
                else:
                    conversion_values.append(0)
                    bounce_rate_values.append(0)
                    duration_values.append(0)
            
            # Add to dashboard data
            dashboard_data["website_traffic"]["labels"] = dates
            dashboard_data["website_traffic"]["website_traffic"] = traffic_values
            dashboard_data["website_traffic"]["conversions"] = conversion_values
            dashboard_data["website_traffic"]["bounce_rate"] = bounce_rate_values
            dashboard_data["website_traffic"]["avg_session_duration"] = duration_values
            
            # Get content performance data
            content_metrics = self.analytics_engine.get_content_metrics()
            for content_id, metrics in content_metrics.items():
                content_item = {
                    "page": content_id,
                    "pageviews": metrics.get('pageviews', 0),
                    "avg_time_on_page": metrics.get('avg_time_on_page', 0),
                    "bounce_rate": metrics.get('bounce_rate', 0)
                }
                dashboard_data["content_performance"].append(content_item)
            
            # Sort content by pageviews (descending)
            dashboard_data["content_performance"].sort(
                key=lambda x: x["pageviews"], reverse=True
            )
            
            # Limit to top 10
            dashboard_data["content_performance"] = dashboard_data["content_performance"][:10]
            
            # Get traffic sources data
            source_metrics = self.analytics_engine.get_source_metrics()
            for source_id, metrics in source_metrics.items():
                source_item = {
                    "source": source_id,
                    "sessions": metrics.get('sessions', 0),
                    "users": metrics.get('users', 0)
                }
                dashboard_data["traffic_sources"].append(source_item)
            
            # Sort sources by sessions (descending)
            dashboard_data["traffic_sources"].sort(
                key=lambda x: x["sessions"], reverse=True
            )
            
            # Limit to top 5
            dashboard_data["traffic_sources"] = dashboard_data["traffic_sources"][:5]
            
            # Get device breakdown data
            device_metrics = self.analytics_engine.get_segment_metrics(segment_type="device")
            for device_id, metrics in device_metrics.items():
                device_item = {
                    "device": device_id,
                    "sessions": metrics.get('sessions', 0),
                    "users": metrics.get('users', 0)
                }
                dashboard_data["device_breakdown"].append(device_item)
            
        except Exception as e:
            logger.error(f"Error getting analytics data for dashboard: {e}")
        
        return dashboard_data


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create integration manager
    manager = AnalyticsIntegrationManager()
    
    # Sync Google Analytics data
    sync_results = manager.sync_google_analytics_data(7)
    print("Sync Results:")
    print(json.dumps(sync_results, indent=2))
    
    # Get dashboard data
    dashboard_data = manager.get_analytics_data_for_dashboard()
    print("\nDashboard Data:")
    print(json.dumps(dashboard_data, indent=2))
