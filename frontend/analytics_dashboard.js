/**
 * GAMS Analytics Dashboard Integration
 * 
 * This file provides integration between the GAMS Operator Dashboard
 * and the Analytics Engine, displaying key performance metrics and
 * recommendations.
 */

// API endpoint base URL
const ANALYTICS_API_BASE_URL = '/api/operator/analytics';

// Analytics Dashboard Configuration
const ANALYTICS_CONFIG = {
    refreshIntervals: {
        metrics: 60000,         // 1 minute
        recommendations: 300000, // 5 minutes
        contentPerformance: 180000, // 3 minutes
    },
    charts: {
        colors: {
            pageViews: 'rgba(40, 167, 69, 0.7)',
            conversions: 'rgba(0, 123, 255, 0.7)',
            engagement: 'rgba(23, 162, 184, 0.7)',
            revenue: 'rgba(255, 193, 7, 0.7)'
        }
    }
};

// Analytics Dashboard State
const analyticsDashboardState = {
    metrics: {},
    contentPerformance: {},
    recommendations: [],
    performanceReport: {},
    loading: {
        metrics: false,
        contentPerformance: false,
        recommendations: false,
        performanceReport: false
    },
    lastUpdated: {
        metrics: null,
        contentPerformance: null,
        recommendations: null,
        performanceReport: null
    },
    charts: {}
};

/**
 * Initialize the analytics dashboard integration
 */
function initializeAnalyticsDashboard() {
    console.log('Initializing analytics dashboard integration...');
    
    // Set up event listeners
    setupAnalyticsEventListeners();
    
    // Load initial data
    loadAnalyticsData();
    
    // Set up refresh intervals
    setInterval(() => refreshAnalyticsMetrics(), ANALYTICS_CONFIG.refreshIntervals.metrics);
    setInterval(() => refreshContentPerformance(), ANALYTICS_CONFIG.refreshIntervals.contentPerformance);
    setInterval(() => refreshRecommendations(), ANALYTICS_CONFIG.refreshIntervals.recommendations);
}

/**
 * Set up event listeners for analytics dashboard
 */
function setupAnalyticsEventListeners() {
    console.log('Setting up analytics dashboard event listeners...');
    
    // Refresh buttons
    const refreshMetricsBtn = document.getElementById('refresh-metrics-btn');
    if (refreshMetricsBtn) {
        refreshMetricsBtn.addEventListener('click', function() {
            refreshAnalyticsMetrics();
        });
    }
    
    const refreshContentBtn = document.getElementById('refresh-content-btn');
    if (refreshContentBtn) {
        refreshContentBtn.addEventListener('click', function() {
            refreshContentPerformance();
        });
    }
    
    const refreshRecommendationsBtn = document.getElementById('refresh-recommendations-btn');
    if (refreshRecommendationsBtn) {
        refreshRecommendationsBtn.addEventListener('click', function() {
            refreshRecommendations();
        });
    }
    
    // Date range selector for performance report
    const generateReportBtn = document.getElementById('generate-report-btn');
    if (generateReportBtn) {
        generateReportBtn.addEventListener('click', function() {
            const startDate = document.getElementById('report-start-date').value;
            const endDate = document.getElementById('report-end-date').value;
            generatePerformanceReport(startDate, endDate);
        });
    }
}

/**
 * Load all analytics data
 */
function loadAnalyticsData() {
    console.log('Loading analytics data...');
    
    refreshAnalyticsMetrics();
    refreshContentPerformance();
    refreshRecommendations();
    
    // Set default dates for report generation
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    const reportStartDateInput = document.getElementById('report-start-date');
    const reportEndDateInput = document.getElementById('report-end-date');
    
    if (reportStartDateInput && reportEndDateInput) {
        reportStartDateInput.valueAsDate = thirtyDaysAgo;
        reportEndDateInput.valueAsDate = today;
    }
}

/**
 * Refresh analytics metrics
 */
function refreshAnalyticsMetrics() {
    console.log('Refreshing analytics metrics...');
    analyticsDashboardState.loading.metrics = true;
    updateLoadingState('metrics', true);
    
    fetch(`${ANALYTICS_API_BASE_URL}/metrics`)
        .then(response => response.json())
        .then(data => {
            console.log('Received metrics data:', data);
            analyticsDashboardState.metrics = data;
            analyticsDashboardState.lastUpdated.metrics = new Date();
            updateMetricsUI(data);
            updateLoadingState('metrics', false);
            showNotification('Analytics metrics refreshed', 'success');
        })
        .catch(error => {
            console.error('Error fetching metrics:', error);
            updateLoadingState('metrics', false);
            showNotification('Failed to refresh analytics metrics', 'error');
        });
}

/**
 * Refresh content performance data
 */
function refreshContentPerformance() {
    console.log('Refreshing content performance data...');
    analyticsDashboardState.loading.contentPerformance = true;
    updateLoadingState('contentPerformance', true);
    
    fetch(`${ANALYTICS_API_BASE_URL}/content-performance`)
        .then(response => response.json())
        .then(data => {
            console.log('Received content performance data:', data);
            analyticsDashboardState.contentPerformance = data;
            analyticsDashboardState.lastUpdated.contentPerformance = new Date();
            updateContentPerformanceUI(data);
            updateLoadingState('contentPerformance', false);
            showNotification('Content performance data refreshed', 'success');
        })
        .catch(error => {
            console.error('Error fetching content performance:', error);
            updateLoadingState('contentPerformance', false);
            showNotification('Failed to refresh content performance data', 'error');
        });
}

/**
 * Refresh recommendations
 */
function refreshRecommendations() {
    console.log('Refreshing recommendations...');
    analyticsDashboardState.loading.recommendations = true;
    updateLoadingState('recommendations', true);
    
    fetch(`${ANALYTICS_API_BASE_URL}/recommendations`)
        .then(response => response.json())
        .then(data => {
            console.log('Received recommendations data:', data);
            analyticsDashboardState.recommendations = data;
            analyticsDashboardState.lastUpdated.recommendations = new Date();
            updateRecommendationsUI(data);
            updateLoadingState('recommendations', false);
            showNotification('Recommendations refreshed', 'success');
        })
        .catch(error => {
            console.error('Error fetching recommendations:', error);
            updateLoadingState('recommendations', false);
            showNotification('Failed to refresh recommendations', 'error');
        });
}

/**
 * Generate performance report for a specific date range
 */
function generatePerformanceReport(startDate, endDate) {
    console.log(`Generating performance report from ${startDate} to ${endDate}...`);
    analyticsDashboardState.loading.performanceReport = true;
    updateLoadingState('performanceReport', true);
    
    fetch(`${ANALYTICS_API_BASE_URL}/performance-report`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            start_date: startDate,
            end_date: endDate
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Received performance report:', data);
            analyticsDashboardState.performanceReport = data;
            analyticsDashboardState.lastUpdated.performanceReport = new Date();
            updatePerformanceReportUI(data);
            updateLoadingState('performanceReport', false);
            showNotification('Performance report generated', 'success');
        })
        .catch(error => {
            console.error('Error generating performance report:', error);
            updateLoadingState('performanceReport', false);
            showNotification('Failed to generate performance report', 'error');
        });
}

/**
 * Update metrics UI with latest data
 */
function updateMetricsUI(metricsData) {
    // Update metrics cards
    updateMetricCard('page-views-metric', metricsData.website?.page_views || 0);
    updateMetricCard('conversions-metric', metricsData.website?.conversions || 0);
    updateMetricCard('revenue-metric', formatCurrency(metricsData.website?.revenue || 0));
    updateMetricCard('engagement-metric', formatPercentage(metricsData.website?.engagement_rate || 0));
    
    // Update metrics chart if it exists
    if (document.getElementById('metrics-chart')) {
        createOrUpdateMetricsChart(metricsData);
    }
    
    // Update last updated timestamp
    updateLastUpdatedTimestamp('metrics-last-updated', analyticsDashboardState.lastUpdated.metrics);
}

/**
 * Update content performance UI with latest data
 */
function updateContentPerformanceUI(contentData) {
    const contentTableBody = document.getElementById('content-performance-table-body');
    if (!contentTableBody) return;
    
    // Clear existing rows
    contentTableBody.innerHTML = '';
    
    // Add new rows
    if (contentData.top_content && contentData.top_content.length > 0) {
        contentData.top_content.forEach(content => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${content.url}</td>
                <td>${content.page_views}</td>
                <td>${formatPercentage(content.bounce_rate)}</td>
                <td>${content.average_time_on_page}s</td>
                <td>${formatPercentage(content.conversion_rate)}</td>
                <td>${formatPercentage(content.engagement_rate)}</td>
            `;
            contentTableBody.appendChild(row);
        });
    } else {
        // No data
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="6" class="text-center">No content performance data available</td>
        `;
        contentTableBody.appendChild(row);
    }
    
    // Update summary metrics
    updateMetricCard('total-page-views', contentData.total_page_views || 0);
    updateMetricCard('avg-bounce-rate', formatPercentage(contentData.average_bounce_rate || 0));
    updateMetricCard('avg-conversion-rate', formatPercentage(contentData.average_conversion_rate || 0));
    updateMetricCard('avg-engagement-rate', formatPercentage(contentData.average_engagement_rate || 0));
    
    // Update last updated timestamp
    updateLastUpdatedTimestamp('content-last-updated', analyticsDashboardState.lastUpdated.contentPerformance);
}

/**
 * Update recommendations UI with latest data
 */
function updateRecommendationsUI(recommendationsData) {
    const recommendationsContainer = document.getElementById('recommendations-container');
    if (!recommendationsContainer) return;
    
    // Clear existing recommendations
    recommendationsContainer.innerHTML = '';
    
    // Add new recommendations
    if (recommendationsData && recommendationsData.length > 0) {
        recommendationsData.forEach(recommendation => {
            const card = document.createElement('div');
            card.className = 'card mb-3';
            
            // Determine card color based on recommendation type
            let cardHeaderClass = 'bg-primary';
            let icon = 'bi-lightbulb';
            
            switch (recommendation.type) {
                case 'content':
                    cardHeaderClass = 'bg-info';
                    icon = 'bi-file-text';
                    break;
                case 'seo':
                    cardHeaderClass = 'bg-success';
                    icon = 'bi-search';
                    break;
                case 'conversion':
                    cardHeaderClass = 'bg-warning';
                    icon = 'bi-graph-up';
                    break;
            }
            
            card.innerHTML = `
                <div class="card-header ${cardHeaderClass} text-white">
                    <i class="bi ${icon} me-2"></i>
                    ${recommendation.type.toUpperCase()} Recommendation
                </div>
                <div class="card-body">
                    <h5 class="card-title">${recommendation.target}</h5>
                    <p class="card-text"><strong>Issue:</strong> ${recommendation.issue}</p>
                    <p class="card-text">${recommendation.recommendation}</p>
                    <p class="card-text text-success"><strong>Expected Impact:</strong> ${recommendation.expected_impact}</p>
                </div>
            `;
            
            recommendationsContainer.appendChild(card);
        });
    } else {
        // No recommendations
        recommendationsContainer.innerHTML = `
            <div class="alert alert-info">
                No recommendations available at this time.
            </div>
        `;
    }
    
    // Update last updated timestamp
    updateLastUpdatedTimestamp('recommendations-last-updated', analyticsDashboardState.lastUpdated.recommendations);
}

/**
 * Update performance report UI with latest data
 */
function updatePerformanceReportUI(reportData) {
    // Update report summary
    const reportSummary = document.getElementById('report-summary');
    if (reportSummary) {
        reportSummary.innerHTML = `
            <h5>Report Summary</h5>
            <p>Period: ${formatDate(reportData.start_date)} to ${formatDate(reportData.end_date)}</p>
            <p>Generated: ${formatDateTime(reportData.generated_at)}</p>
        `;
    }
    
    // Update summary metrics
    const summaryMetrics = reportData.summary || {};
    
    // Website Traffic
    updateReportMetric('traffic-summary', summaryMetrics.website_traffic);
    
    // Conversions
    updateReportMetric('conversions-summary', summaryMetrics.conversions);
    
    // Engagement
    updateReportMetric('engagement-summary', summaryMetrics.engagement);
    
    // Revenue
    updateReportMetric('revenue-summary', summaryMetrics.revenue);
    
    // Create or update performance chart
    if (document.getElementById('performance-chart')) {
        createOrUpdatePerformanceChart(reportData);
    }
    
    // Update last updated timestamp
    updateLastUpdatedTimestamp('report-last-updated', analyticsDashboardState.lastUpdated.performanceReport);
}

/**
 * Update a metric card with new value
 */
function updateMetricCard(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

/**
 * Update a report metric section
 */
function updateReportMetric(elementId, metricData) {
    const element = document.getElementById(elementId);
    if (!element || !metricData) return;
    
    if (metricData.available) {
        element.innerHTML = `
            <div class="metric-value">${metricData.total}</div>
            <div class="metric-details">
                <div>Average: ${metricData.average}</div>
                <div>Min: ${metricData.min}</div>
                <div>Max: ${metricData.max}</div>
            </div>
        `;
    } else {
        element.innerHTML = `
            <div class="alert alert-warning">
                ${metricData.message || 'No data available'}
            </div>
        `;
    }
}

/**
 * Create or update metrics chart
 */
function createOrUpdateMetricsChart(metricsData) {
    const ctx = document.getElementById('metrics-chart').getContext('2d');
    
    // Prepare data
    const labels = ['Page Views', 'Visitors', 'Conversions', 'Engagement'];
    const data = [
        metricsData.website?.page_views || 0,
        metricsData.website?.unique_visitors || 0,
        metricsData.website?.conversions || 0,
        (metricsData.website?.engagement_rate || 0) * 100
    ];
    
    // Create or update chart
    if (analyticsDashboardState.charts.metrics) {
        // Update existing chart
        analyticsDashboardState.charts.metrics.data.labels = labels;
        analyticsDashboardState.charts.metrics.data.datasets[0].data = data;
        analyticsDashboardState.charts.metrics.update();
    } else {
        // Create new chart
        analyticsDashboardState.charts.metrics = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Website Metrics',
                    data: data,
                    backgroundColor: [
                        ANALYTICS_CONFIG.charts.colors.pageViews,
                        ANALYTICS_CONFIG.charts.colors.conversions,
                        ANALYTICS_CONFIG.charts.colors.engagement,
                        ANALYTICS_CONFIG.charts.colors.revenue
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

/**
 * Create or update performance chart
 */
function createOrUpdatePerformanceChart(reportData) {
    const ctx = document.getElementById('performance-chart').getContext('2d');
    
    // Prepare data (this is simplified - in a real implementation, you'd use time-series data)
    const metrics = reportData.metrics || {};
    const labels = Object.keys(metrics);
    const pageViewsData = [];
    const conversionsData = [];
    
    labels.forEach(source => {
        pageViewsData.push(metrics[source].page_views || 0);
        conversionsData.push(metrics[source].conversions || 0);
    });
    
    // Create or update chart
    if (analyticsDashboardState.charts.performance) {
        // Update existing chart
        analyticsDashboardState.charts.performance.data.labels = labels;
        analyticsDashboardState.charts.performance.data.datasets[0].data = pageViewsData;
        analyticsDashboardState.charts.performance.data.datasets[1].data = conversionsData;
        analyticsDashboardState.charts.performance.update();
    } else {
        // Create new chart
        analyticsDashboardState.charts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Page Views',
                        data: pageViewsData,
                        backgroundColor: ANALYTICS_CONFIG.charts.colors.pageViews,
                        borderColor: ANALYTICS_CONFIG.charts.colors.pageViews,
                        borderWidth: 2,
                        fill: false
                    },
                    {
                        label: 'Conversions',
                        data: conversionsData,
                        backgroundColor: ANALYTICS_CONFIG.charts.colors.conversions,
                        borderColor: ANALYTICS_CONFIG.charts.colors.conversions,
                        borderWidth: 2,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

/**
 * Update loading state for a specific section
 */
function updateLoadingState(section, isLoading) {
    analyticsDashboardState.loading[section] = isLoading;
    
    // Update UI loading indicators
    const loadingIndicator = document.getElementById(`${section}-loading`);
    if (loadingIndicator) {
        loadingIndicator.style.display = isLoading ? 'inline-block' : 'none';
    }
}

/**
 * Update last updated timestamp
 */
function updateLastUpdatedTimestamp(elementId, timestamp) {
    const element = document.getElementById(elementId);
    if (element && timestamp) {
        element.textContent = formatDateTime(timestamp);
    }
}

/**
 * Format date as YYYY-MM-DD
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
}

/**
 * Format date and time
 */
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleString();
}

/**
 * Format currency
 */
function formatCurrency(value) {
    return '$' + value.toFixed(2);
}

/**
 * Format percentage
 */
function formatPercentage(value) {
    return (value * 100).toFixed(1) + '%';
}

// Initialize the analytics dashboard when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the analytics tab
    if (document.getElementById('analytics')) {
        initializeAnalyticsDashboard();
    }
});

// Make functions globally accessible
window.refreshAnalyticsMetrics = refreshAnalyticsMetrics;
window.refreshContentPerformance = refreshContentPerformance;
window.refreshRecommendations = refreshRecommendations;
window.generatePerformanceReport = generatePerformanceReport;
