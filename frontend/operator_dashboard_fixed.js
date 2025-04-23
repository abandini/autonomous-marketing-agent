/**
 * GAMS Operator Dashboard JavaScript
 * 
 * This file provides the functionality for the operator dashboard,
 * including API calls, data visualization, and user interactions.
 */

// API endpoint base URL
const API_BASE_URL = '/api/operator';

// Configuration
const CONFIG = {
    refreshIntervals: {
        approvals: 60000,      // 1 minute
        financial: 300000,     // 5 minutes
        experiments: 120000,   // 2 minutes
        compliance: 180000,    // 3 minutes
        strategy: 600000,      // 10 minutes
        competitiveIntelligence: 900000  // 15 minutes
    },
    charts: {
        colors: {
            organic: 'rgba(40, 167, 69, 0.7)',
            paid: 'rgba(0, 123, 255, 0.7)',
            email: 'rgba(23, 162, 184, 0.7)',
            affiliate: 'rgba(255, 193, 7, 0.7)',
            revenue: 'rgba(40, 167, 69, 0.7)',
            expenses: 'rgba(220, 53, 69, 0.7)',
            profit: 'rgba(0, 123, 255, 0.7)'
        }
    },
    toastDuration: 5000        // 5 seconds
};

/**
 * Dashboard state object
 */
const dashboardState = {
    pendingApprovals: [],
    activeExperiments: [],
    strategySettings: {},
    complianceIssues: [],
    financialData: {
        current: {
            revenue: 0,
            expenses: 0,
            profit: 0,
            roi: 0
        },
        historical: []
    },
    systemStatus: {
        running: false,
        lastStarted: null,
        uptime: 0,
        version: '1.0.0'
    },
    configuration: {
        general: {
            systemName: 'GAMS',
            operatorEmail: '',
            notificationLevel: 'all',
            refreshInterval: 300000
        },
        api: {
            apiKey: '',
            apiEndpoint: '/api',
            requestTimeout: 30000,
            enableRateLimiting: true
        },
        integrations: {
            enableGoogleAnalytics: false,
            enableGoogleSearchConsole: false,
            enableAhrefs: false,
            enableSemrush: false,
            enableMailchimp: false
        },
        advanced: {
            logLevel: 'info',
            maxConcurrentTasks: 5,
            enableDebugMode: false,
            enablePerformanceMetrics: true
        }
    },
    websiteRepoSettings: {
        websiteUrl: '',
        gitRepoUrl: '',
        gitUsername: '',
        gitToken: ''
    },
    errors: [],
    loading: {
        approvals: false,
        experiments: false,
        strategy: false,
        compliance: false,
        financial: false,
        websiteRepo: false,
        competitiveIntelligence: false
    },
    lastUpdated: {
        approvals: null,
        experiments: null,
        strategy: null,
        compliance: null,
        financial: null,
        websiteRepo: null,
        competitiveIntelligence: null
    }
};

/**
 * Initialize the dashboard
 */
function initializeDashboard() {
    console.log('Initializing dashboard...');
    
    // Set up all event listeners and initialize data
    setupEventListeners();
    
    // Initialize dashboard data
    loadDashboardData();
    updateSystemStatusUI();
    loadWebsiteRepoSettings();
    
    // Set up refresh intervals
    setInterval(() => refreshDashboardData(), CONFIG.refreshIntervals.financial);
    setInterval(() => refreshWebsiteRepoSettings(), CONFIG.refreshIntervals.approvals);
}

/**
 * Set up all event listeners
 */
function setupEventListeners() {
    console.log('Setting up dashboard event listeners...');
    
    // Add event listener for GAMS control button click
    const gamsControlBtn = document.getElementById('gams-control-btn');
    if (gamsControlBtn) {
        console.log('Setting up GAMS control button click handler');
        gamsControlBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('GAMS control button clicked');
            showNotification('Processing GAMS control request...', 'info');
            handleGamsControl();
        });
    } else {
        console.error('GAMS control button not found');
    }
    
    // Add event listener for Competitive Intelligence refresh button
    const refreshCompetitiveIntelligenceBtn = document.getElementById('refresh-competitive-intelligence');
    if (refreshCompetitiveIntelligenceBtn) {
        refreshCompetitiveIntelligenceBtn.addEventListener('click', function(e) {
            e.preventDefault();
            refreshCompetitiveIntelligence();
        });
    }
    
    // Tab change event listeners
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', handleTabChange);
    });
    
    // Website & Repository Settings form
    const websiteRepoForm = document.getElementById('websiteRepoSettingsForm');
    if (websiteRepoForm) {
        websiteRepoForm.addEventListener('submit', handleWebsiteRepoSettings);
    }
    
    // Show Git token button
    const showGitTokenBtn = document.getElementById('showGitToken');
    if (showGitTokenBtn) {
        showGitTokenBtn.addEventListener('click', function() {
            togglePasswordVisibility('gitToken', this);
        });
    }
    
    // Direct test buttons
    const directTestBtn = document.getElementById('direct-test-btn');
    if (directTestBtn) {
        directTestBtn.addEventListener('click', function() {
            testDirectApiCall();
        });
    }
    
    const directApiTestBtn = document.getElementById('direct-api-test');
    if (directApiTestBtn) {
        directApiTestBtn.addEventListener('click', function() {
            directApiTest();
        });
    }
}

/**
 * Handle GAMS control button click
 */
function handleGamsControl() {
    console.log('Handling GAMS control request');
    
    // Disable the button to prevent multiple clicks
    const controlBtn = document.getElementById('gams-control-btn');
    if (controlBtn) controlBtn.disabled = true;
    
    // Determine action based on current system status
    const action = dashboardState.systemStatus.running ? 'stop' : 'start';
    console.log(`Attempting to ${action} GAMS system`);
    
    // Send the request using fetch API
    fetch(`${API_BASE_URL}/system/control`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        
        // Update the system status if available
        if (data.system_status) {
            dashboardState.systemStatus = data.system_status;
            
            // Make sure lastStarted is set for the updateSystemStatusUI function
            if (data.system_status.running && data.system_status.start_time) {
                dashboardState.systemStatus.lastStarted = data.system_status.start_time;
            }
            
            updateSystemStatusUI();
            showNotification(`GAMS system ${action}ed successfully`, 'success');
        } else {
            // Update UI manually if system_status is not in the response
            updateSystemStatusManually(action);
            showNotification(`GAMS system ${action}ed successfully`, 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(`Error controlling GAMS: ${error.message}`, 'error');
    })
    .finally(() => {
        // Re-enable the button
        if (controlBtn) controlBtn.disabled = false;
    });
}

/**
 * Update system status UI manually based on action
 */
function updateSystemStatusManually(action) {
    const statusBadge = document.getElementById('system-status-badge');
    const statusText = document.getElementById('system-status-text');
    const controlBtn = document.getElementById('gams-control-btn');
    
    if (statusBadge && statusText && controlBtn) {
        if (action === 'start') {
            dashboardState.systemStatus.running = true;
            dashboardState.systemStatus.lastStarted = new Date().toISOString();
            statusBadge.className = 'badge bg-success';
            statusBadge.textContent = 'Running';
            statusText.textContent = `Running since ${new Date().toLocaleString()}`;
            controlBtn.innerHTML = '<i class="bi bi-stop-fill me-1"></i> Stop GAMS';
            controlBtn.className = 'btn btn-danger btn-lg';
        } else {
            dashboardState.systemStatus.running = false;
            statusBadge.className = 'badge bg-danger';
            statusBadge.textContent = 'Stopped';
            statusText.textContent = 'System is currently stopped';
            controlBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i> Start GAMS';
            controlBtn.className = 'btn btn-success btn-lg';
        }
    }
}

/**
 * Update system status UI
 */
function updateSystemStatusUI() {
    const statusBadge = document.getElementById('system-status-badge');
    const statusText = document.getElementById('system-status-text');
    const controlBtn = document.getElementById('gams-control-btn');
    
    if (statusBadge && statusText && controlBtn) {
        if (dashboardState.systemStatus.running) {
            statusBadge.className = 'badge bg-success';
            statusBadge.textContent = 'Running';
            statusText.textContent = `Running since ${new Date(dashboardState.systemStatus.lastStarted).toLocaleString()}`;
            controlBtn.innerHTML = '<i class="bi bi-stop-fill me-1"></i> Stop GAMS';
            controlBtn.className = 'btn btn-danger btn-lg';
        } else {
            statusBadge.className = 'badge bg-danger';
            statusBadge.textContent = 'Stopped';
            statusText.textContent = 'System is currently stopped';
            controlBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i> Start GAMS';
            controlBtn.className = 'btn btn-success btn-lg';
        }
    }
}

/**
 * Show a notification to the user
 */
function showNotification(message, type = 'info') {
    console.log(`Notification (${type}): ${message}`);
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // Create toast content
    const toastContent = document.createElement('div');
    toastContent.className = 'd-flex';
    
    const toastBody = document.createElement('div');
    toastBody.className = 'toast-body';
    toastBody.textContent = message;
    
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close btn-close-white me-2 m-auto';
    closeButton.setAttribute('data-bs-dismiss', 'toast');
    closeButton.setAttribute('aria-label', 'Close');
    
    // Assemble toast
    toastContent.appendChild(toastBody);
    toastContent.appendChild(closeButton);
    toast.appendChild(toastContent);
    
    // Add to toast container
    const toastContainer = document.getElementById('toast-container');
    if (toastContainer) {
        toastContainer.appendChild(toast);
        
        // Initialize and show the toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: CONFIG.toastDuration
        });
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    } else {
        // Fallback if toast container not found
        alert(`${type.toUpperCase()}: ${message}`);
    }
}

/**
 * Show an error message
 */
function showError(message) {
    showNotification(message, 'danger');
}

/**
 * Load dashboard data from API
 */
function loadDashboardData() {
    console.log('Loading dashboard data...');
    
    // For demonstration purposes, we'll use mock data
    // In a real application, this would make API calls to fetch data
    
    // Update system status
    getSystemStatus();
    
    // Update financial data
    getFinancialData();
    
    // Update pending approvals
    getPendingApprovals();
    
    // Update active experiments
    getActiveExperiments();
    
    // Update compliance issues
    getComplianceIssues();
    
    // Update strategy settings
    getStrategySettings();
    
    // Update competitive intelligence
    getCompetitiveIntelligence();
}

/**
 * Refresh dashboard data
 */
function refreshDashboardData() {
    console.log('Refreshing dashboard data...');
    loadDashboardData();
}

/**
 * Get system status from API
 */
function getSystemStatus() {
    console.log('Getting system status...');
    
    // In a real application, this would make an API call
    // For demonstration, we'll use mock data
    
    // Simulate API call
    setTimeout(() => {
        // Mock response data
        const data = {
            running: false,
            lastStarted: null,
            uptime: 0,
            version: '1.0.0'
        };
        
        // Update dashboard state
        dashboardState.systemStatus = data;
        
        // Update UI
        updateSystemStatusUI();
    }, 500);
}

/**
 * Handle tab change
 */
function handleTabChange(event) {
    const tabId = event.target.getAttribute('href').substring(1);
    console.log(`Tab changed to: ${tabId}`);
    
    // Perform actions based on the selected tab
    switch (tabId) {
        case 'approvals':
            refreshApprovals();
            break;
        case 'financial':
            refreshFinancialData();
            break;
        case 'experiments':
            refreshExperiments();
            break;
        case 'compliance':
            refreshComplianceIssues();
            break;
        case 'strategy':
            refreshStrategySettings();
            break;
        case 'competitive-intelligence':
            refreshCompetitiveIntelligence();
            break;
    }
}

/**
 * Refresh competitive intelligence data
 */
function refreshCompetitiveIntelligence() {
    console.log('Refreshing competitive intelligence data...');
    
    // Set loading state
    dashboardState.loading.competitiveIntelligence = true;
    
    // Get the competitive intelligence iframe
    const ciFrame = document.getElementById('competitive-intelligence-frame');
    
    if (ciFrame) {
        // Reload the iframe
        ciFrame.src = ciFrame.src;
        
        // Show notification
        showNotification('Competitive Intelligence data refreshed', 'success');
    } else {
        console.error('Competitive Intelligence iframe not found');
        showError('Failed to refresh Competitive Intelligence data');
    }
    
    // Update loading state
    dashboardState.loading.competitiveIntelligence = false;
}

/**
 * Direct test function for GAMS control
 */
function testDirectApiCall() {
    console.log('Testing direct API call');
    showNotification('Testing direct API call to /api/operator/system/control', 'info');
    
    const action = dashboardState.systemStatus.running ? 'stop' : 'start';
    
    fetch(`${API_BASE_URL}/system/control`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
    })
    .then(response => {
        console.log('Response status:', response.status);
        showNotification(`Response status: ${response.status}`, 'info');
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        showNotification(`Response data: ${JSON.stringify(data)}`, 'success');
        
        // Update the system status if available
        if (data.system_status) {
            dashboardState.systemStatus = data.system_status;
            updateSystemStatusUI();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(`Error: ${error.message}`, 'error');
    });
}

/**
 * Direct API test using XMLHttpRequest
 */
function directApiTest() {
    console.log('Direct API test called');
    showNotification('Testing API directly with XMLHttpRequest...', 'info');
    
    const xhr = new XMLHttpRequest();
    const url = `${API_BASE_URL}/system/control`;
    const action = dashboardState.systemStatus.running ? 'stop' : 'start';
    
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            console.log('XHR status:', xhr.status);
            console.log('XHR response:', xhr.responseText);
            
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    console.log('Parsed data:', data);
                    
                    if (data.system_status) {
                        dashboardState.systemStatus = data.system_status;
                        updateSystemStatusUI();
                    }
                    
                    showNotification(`Direct API test successful: ${action}ed GAMS`, 'success');
                } catch (e) {
                    console.error('Error parsing response:', e);
                    showNotification('Error parsing API response', 'error');
                }
            } else {
                showNotification(`API error: ${xhr.status} ${xhr.statusText}`, 'error');
            }
        }
    };
    
    xhr.onerror = function() {
        console.error('XHR error');
        showNotification('Network error during API test', 'error');
    };
    
    const data = JSON.stringify({ action });
    console.log('Sending data:', data);
    xhr.send(data);
}

// Initialize the dashboard when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initializeDashboard);

// Make functions globally accessible
window.testDirectApiCall = testDirectApiCall;
window.directApiTest = directApiTest;
window.handleGamsControl = handleGamsControl;
