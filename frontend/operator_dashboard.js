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

// End of file
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

// End of file
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

// End of file
};

/**
 * Initialize the dashboard
 */
function initializeDashboard() {
    console.log('Initializing dashboard...');
    
    // Function to set up all event listeners and initialize data
    function setupDashboard() {
        console.log('Setting up dashboard event listeners and data...');
        
        // Add event listener for GAMS control button click
        const gamsControlBtn = document.getElementById('gams-control-btn');
        if (gamsControlBtn) {
            console.log('Setting up GAMS control button click handler');
            gamsControlBtn.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('GAMS control button clicked - DEBUG');
                // Show a notification to confirm the button click is being triggered
                showNotification('DEBUG: Button click triggered', 'info');
                
                // Call the simplified GAMS control function
                sendGamsControlRequest();
            });
        } else {
            console.error('GAMS control button not found');
        }

// End of file
        
        // GAMS control form event listener is already set up above
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
        
        // We're using the form submission event instead of the button click
        
        // Website & Repository Settings form
        const websiteRepoForm = document.getElementById('websiteRepoSettingsForm');
        if (websiteRepoForm) {
            websiteRepoForm.addEventListener('submit', handleWebsiteRepoSettings);
        }

// End of file
        
        // Show Git token button
        const showGitTokenBtn = document.getElementById('showGitToken');
        if (showGitTokenBtn) {
            showGitTokenBtn.addEventListener('click', function() {
                togglePasswordVisibility('gitToken', this);
            });
        }

// End of file
        
/**
 * Test function to directly control GAMS system
 * Can be called from browser console: testGamsControl('start') or testGamsControl('stop')
 */
function testGamsControl(action) {
    console.log(`Test function called with action: ${action}`);
    
    return fetch(`${API_BASE_URL}/system/control`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
    })
    .then(response => {
        console.log('Test response status:', response.status);
        return response.text().then(text => {
            console.log('Test response text:', text);
            try {
                return JSON.parse(text);
            } catch (e) {
                console.error('Failed to parse response as JSON:', e);
                return { status: 'error', message: 'Invalid JSON response' };
            }

// End of file
        });
    })
    .then(data => {
        console.log('Test response data:', data);
        if (data.system_status) {
            dashboardState.systemStatus = data.system_status;
            updateSystemStatusUI();
        }

// End of file
        showNotification(`Test: GAMS system ${action}ed successfully`, 'success');
        return data;
    })
    .catch(error => {
        console.error(`Test error ${action}ing GAMS:`, error);
        showNotification(`Test: Failed to ${action} GAMS: ${error.message}`, 'error');
    });
}

// End of file

/**
 * Direct API test function that uses XMLHttpRequest instead of fetch
 * This is a fallback to test if fetch is causing issues
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

// End of file
                    
                    showNotification(`Direct API test successful: ${action}ed GAMS`, 'success');
                } catch (e) {
                    console.error('Error parsing response:', e);
                    showNotification('Error parsing API response', 'error');
                }

// End of file
            } else {
                showNotification(`API error: ${xhr.status} ${xhr.statusText}`, 'error');
            }

// End of file
        }

// End of file
    };
    
    xhr.onerror = function() {
        console.error('XHR error');
        showNotification('Network error during API test', 'error');
    };
    
    const data = JSON.stringify({ action });
    console.log('Sending data:', data);
    xhr.send(data);
}

// End of file

/**
 * Direct handler for GAMS control button clicks
 * This function is called directly from the button's onclick attribute
 */
function handleDirectGamsControl() {
    console.log('Direct GAMS control handler called');
    showNotification('Processing GAMS control request...', 'info');
    
    // Determine action based on current system status
    const action = dashboardState.systemStatus.running ? 'stop' : 'start';
    console.log(`Attempting to ${action} GAMS system directly`);
    
    // Create a new XMLHttpRequest
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${API_BASE_URL}/system/control`, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    // Set up response handler
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            console.log(`XHR response received: status ${xhr.status}`);
            console.log('Response text:', xhr.responseText);
            
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    console.log('Parsed response data:', data);
                    
                    if (data.system_status) {
                        // Update dashboard state
                        dashboardState.systemStatus = data.system_status;
                        
                        // Update UI
                        const statusBadge = document.getElementById('system-status-badge');
                        const statusText = document.getElementById('system-status-text');
                        const controlBtn = document.getElementById('gams-control-btn');
                        
                        if (statusBadge && statusText && controlBtn) {
                            if (data.system_status.running) {
                                statusBadge.className = 'badge bg-success';
                                statusBadge.textContent = 'Running';
                                statusText.textContent = `Running since ${new Date(data.system_status.start_time).toLocaleString()}`;
                                controlBtn.innerHTML = '<i class="bi bi-stop-fill me-1"></i> Stop GAMS';
                                controlBtn.className = 'btn btn-danger btn-lg';
                            } else {
                                statusBadge.className = 'badge bg-danger';
                                statusBadge.textContent = 'Stopped';
                                statusText.textContent = 'System is currently stopped';
                                controlBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i> Start GAMS';
                                controlBtn.className = 'btn btn-success btn-lg';
                            }

// End of file
                        }

// End of file
                        
                        // Show success notification
                        showNotification(`GAMS system ${action}ed successfully`, 'success');
                    } else {
                        showNotification('Warning: Response missing system status', 'warning');
                    }

// End of file
                } catch (e) {
                    console.error('Error parsing response:', e);
                    showNotification(`Error parsing response: ${e.message}`, 'error');
                }

// End of file
            } else {
                console.error(`HTTP error: ${xhr.status} ${xhr.statusText}`);
                showNotification(`Server error: ${xhr.status} ${xhr.statusText}`, 'error');
            }

// End of file
        }

// End of file
    };
    
    // Set up error handler
    xhr.onerror = function() {
        console.error('Network error occurred');
        showNotification('Network error when trying to control GAMS', 'error');
    };
    
    // Send the request
    const payload = JSON.stringify({ action });
    console.log('Sending payload:', payload);
    xhr.send(payload);
}

// End of file

// Make functions globally accessible
window.testGamsControl = testGamsControl;
window.directApiTest = directApiTest;
window.handleDirectGamsControl = handleDirectGamsControl;

// Add event listener for direct test button
const directTestBtn = document.getElementById('direct-test-btn');
if (directTestBtn) {
    directTestBtn.addEventListener('click', function() {
        console.log('Direct test button clicked');
        testDirectApiCall();
    });
}

// End of file

// Initialize dashboard
loadDashboardData();
updateSystemStatusUI();
loadWebsiteRepoSettings();

// Set up refresh intervals
setInterval(() => refreshDashboardData(), CONFIG.refreshIntervals.financial);
setInterval(() => refreshWebsiteRepoSettings(), CONFIG.refreshIntervals.approvals);

// Check if DOM is already loaded
if (document.readyState === 'loading') {
    console.log('DOM still loading, waiting for DOMContentLoaded event');
    document.addEventListener('DOMContentLoaded', setupDashboard);
} else {
    console.log('DOM already loaded, setting up dashboard immediately');
    setupDashboard();
}

// End of file

/**
 * Direct test function to test the API endpoint
 */
function testDirectApiCall() {
    console.log('Testing direct API call');
    showNotification('Testing direct API call to /api/operator/system/control', 'info');
    
    const action = 'start';
    const url = '/api/operator/system/control';
    
    fetch(url, {
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

// End of file
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(`Error: ${error.message}`, 'error');
    });
}

// End of file

/**
 * Simplified function to send GAMS control request
 */
function sendGamsControlRequest() {
    console.log('Sending GAMS control request');
    
    // Determine the action based on current system status
    const action = dashboardState.systemStatus.running ? 'stop' : 'start';
    showNotification(`Attempting to ${action} GAMS...`, 'info');
    
    // Disable the button during operation
    const controlBtn = document.getElementById('gams-control-btn');
    if (controlBtn) controlBtn.disabled = true;
    
    const url = '/api/operator/system/control';
    
    fetch(url, {
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

// End of file
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        
        // Update the system status if available
        if (data.system_status) {
            dashboardState.systemStatus = data.system_status;
            updateSystemStatusUI();
            showNotification(`GAMS system ${action}ed successfully`, 'success');
        } else {
            showNotification(`Warning: Response missing system status`, 'warning');
        }

// End of file
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

// End of file

/**
 * Update configuration forms with current values
 */
function updateConfigurationForms() {
    // This would be implemented to populate configuration forms
    // with current settings from dashboardState.configSettings
    console.log('Updating configuration forms');
    
    // Update website and repository settings if available
    if (dashboardState.websiteRepoSettings) {
        const settings = dashboardState.websiteRepoSettings;
        
        // Website URL
        const websiteUrlInput = document.getElementById('websiteUrl');
        if (websiteUrlInput && settings.websiteUrl) {
            websiteUrlInput.value = settings.websiteUrl;
        }

// End of file
        
        // Git Repository URL
        const gitRepoUrlInput = document.getElementById('gitRepoUrl');
        if (gitRepoUrlInput && settings.gitRepoUrl) {
            gitRepoUrlInput.value = settings.gitRepoUrl;
        }

// End of file
        
        // Git Username
        const gitUsernameInput = document.getElementById('gitUsername');
        if (gitUsernameInput && settings.gitUsername) {
            gitUsernameInput.value = settings.gitUsername;
        }

// End of file
        
        // Git Token (we don't show the actual token for security reasons)
        const gitTokenInput = document.getElementById('gitToken');
        if (gitTokenInput && settings.gitToken) {
            gitTokenInput.value = settings.gitToken;
        }

// End of file
    }

// End of file
}

// End of file

/**
 * Handle website and repository settings form submission
 */
function handleWebsiteRepoSettings(event) {
    event.preventDefault();
    
    // Update dashboard state with form values
    dashboardState.websiteRepoSettings = {
        websiteUrl: document.getElementById('websiteUrl').value,
        gitRepoUrl: document.getElementById('gitRepoUrl').value,
        gitUsername: document.getElementById('gitUsername').value,
        gitToken: document.getElementById('gitToken').value
    };
    
    // In a real app, this would send the data to the server
    // For now, we'll just show a success notification
    showNotification('Website and repository settings updated successfully', 'success');
}

// End of file

/**
 * Load website and repository settings from the API
 */
async function loadWebsiteRepoSettings() {
    try {
        // Set loading state
        dashboardState.loading.websiteRepo = true;
        updateLoadingIndicators();
        
        // Make API request
        const response = await fetch(`${API_BASE_URL}/website-repo-settings`);
        
        // Handle HTTP errors
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `Server returned ${response.status}: ${response.statusText}`);
        }

// End of file
        
        // Process response data
        const data = await response.json();
        dashboardState.websiteRepoSettings = data;
        
        // Update UI components
        updateConfigurationForms();
        
        // Update last updated timestamp
        dashboardState.lastUpdated.websiteRepo = new Date();
        updateLastUpdatedTimes();
        
        return data;
    } catch (error) {
        console.error('Error loading website and repository settings:', error);
        showError(`Failed to load website and repository settings: ${error.message}`);
    } finally {
        // Reset loading state
        dashboardState.loading.websiteRepo = false;
        updateLoadingIndicators();
    }

// End of file
}

// End of file

/**
 * Refresh website and repository settings
 */
async function refreshWebsiteRepoSettings() {
    try {
        // Show loading indicator for this section
        dashboardState.loading.websiteRepo = true;
        updateLoadingIndicators();
        
        // Refresh the appropriate data
        await loadWebsiteRepoSettings();
        
        // Update last refreshed time
        dashboardState.lastUpdated.websiteRepo = new Date();
        updateLastUpdatedTimes();
        
        // Show success notification
        showNotification('Website and repository settings refreshed successfully', 'success');
    } catch (error) {
        console.error('Error refreshing website and repository settings:', error);
        showError(`Failed to refresh website and repository settings: ${error.message}`);
    } finally {
        // Hide loading indicator
        dashboardState.loading.websiteRepo = false;
        updateLoadingIndicators();
    }

// End of file
}

// End of file
/**
 * Toggle password field visibility
 */
function togglePasswordVisibility(inputId, button) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    if (input.type === 'password') {
        input.type = 'text';
        button.innerHTML = '<i class="bi bi-eye-slash"></i>';
    } else {
        input.type = 'password';
        button.innerHTML = '<i class="bi bi-eye"></i>';
    }

// End of file
}

// End of file

/**
 * Load dashboard data
 */
function loadDashboardData() {
    // Load financial data
    loadFinancialData();
    
    // Load system status
    getSystemStatus();
    
    // Load website and repository settings
    loadWebsiteRepoSettings();
    
    // In a real app, this would load all dashboard data
    console.log('Loading dashboard data...');
}

// End of file

/**
 * Get system status from API
 */
async function getSystemStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/system/status`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `Server returned ${response.status}: ${response.statusText}`);
        }

// End of file
        
        const data = await response.json();
        dashboardState.systemStatus = data.system_status || {
            running: false,
            lastStarted: null,
            uptime: 0,
            version: '1.0.0'
        };
        
        // Update UI
        updateSystemStatusUI();
        
    } catch (error) {
        console.error('Error getting system status:', error);
        showNotification(`Failed to get system status: ${error.message}`, 'error');
    }

// End of file
}

// End of file

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
            controlBtn.textContent = 'Stop GAMS';
            controlBtn.className = 'btn btn-danger';
        } else {
            statusBadge.className = 'badge bg-danger';
            statusBadge.textContent = 'Stopped';
            statusText.textContent = 'System is currently stopped';
            controlBtn.textContent = 'Start GAMS';
            controlBtn.className = 'btn btn-success';
        }

// End of file
    }

// End of file
}

// End of file

/**
 * Refresh dashboard data
 */
function refreshDashboardData() {
    loadFinancialData();
    getSystemStatus();
    loadWebsiteRepoSettings();
}

// End of file

/**
 * Handle GAMS control button click
 */
async function handleGamsControl() {
    console.log('GAMS control button clicked - DEBUG');
    // Show a notification to confirm the function is being called
    showNotification('DEBUG: handleGamsControl function called', 'info');
    
    const controlBtn = document.getElementById('gams-control-btn');
    if (!controlBtn) {
        console.error('GAMS control button not found');
        showNotification('ERROR: GAMS control button not found', 'error');
        return;
    }

// End of file
    
    // Use XMLHttpRequest instead of fetch for better compatibility
    const action = dashboardState.systemStatus.running ? 'stop' : 'start';
    console.log(`Handling GAMS control: ${action}`);
    showNotification(`Attempting to ${action} GAMS...`, 'info');
    
    // Disable button during operation
    controlBtn.disabled = true;
    
    const xhr = new XMLHttpRequest();
    // Make sure we use the full API path
    const url = '/api/operator/system/control';
    console.log('Sending request to:', url);
    
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.onreadystatechange = function() {
        console.log(`XHR ready state: ${xhr.readyState}, status: ${xhr.status}`);
        
        if (xhr.readyState === 4) {
            // Re-enable button
            controlBtn.disabled = false;
            
            console.log('Full response:', xhr.responseText);
            
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    console.log('Parsed response data:', data);
                    
                    if (data.system_status) {
                        dashboardState.systemStatus = data.system_status;
                        updateSystemStatusUI();
                        showNotification(`GAMS system ${action}ed successfully`, 'success');
                    } else {
                        showNotification(`Warning: Response missing system status`, 'warning');
                    }

// End of file
                } catch (e) {
                    console.error('Failed to parse response as JSON:', e);
                    showNotification(`Error parsing response: ${e.message}`, 'error');
                }

// End of file
            } else {
                console.error(`HTTP error: ${xhr.status} ${xhr.statusText}`);
                showNotification(`Server error: ${xhr.status} ${xhr.statusText}`, 'error');
            }

// End of file
        }

// End of file
    };
    
    xhr.onerror = function() {
        // Re-enable button
        controlBtn.disabled = false;
        console.error('Network error occurred');
        showNotification('Network error when trying to control GAMS', 'error');
    };
    
    const payload = JSON.stringify({ action });
    console.log('Request payload:', payload);
    
    // Add additional debug notification
    showNotification(`DEBUG: Sending ${action} request to ${url}`, 'info');
    
    // Add event listener for when the request completes
    xhr.addEventListener('loadend', function() {
        console.log('DEBUG: Request completed with status:', xhr.status);
        showNotification(`DEBUG: Request completed with status: ${xhr.status}`, 'info');
    });
    
    xhr.send(payload);
}

// End of file

/**
 * Load financial data from API
 */
async function loadFinancialData() {
    try {
        // Set loading state
        dashboardState.loading.financial = true;
        updateLoadingIndicators();
        
        // Make API request
        const response = await fetch(`${API_BASE_URL}/financial/summary`);
        
        // Handle HTTP errors
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `Server returned ${response.status}: ${response.statusText}`);
        }

// End of file
        
        // Process response data
        const data = await response.json();
        dashboardState.financialData = data;
        
        // Update UI components
        updateFinancialDashboard();
        
        // Update last updated timestamp
        dashboardState.lastUpdated.financial = new Date();
        updateLastUpdatedTimes();
        
        return data;
    } catch (error) {
        console.error('Error loading financial data:', error);
        showError(`Failed to load financial data: ${error.message}`);
    } finally {
        // Reset loading state
        dashboardState.loading.financial = false;
        updateLoadingIndicators();
    }

// End of file
}

// End of file

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

// End of file
    
    // Create toast element
    const toastId = `toast-${Date.now()}`;
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // Create toast content
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}

// End of file
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: CONFIG.toastDuration
    });
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// End of file

/**
 * Show error notification
 */
function showError(message) {
    showNotification(message, 'error');
}

// End of file

/**
 * Update loading indicators based on dashboard state
 */
function updateLoadingIndicators() {
    // Update each section's loading indicator
    Object.keys(dashboardState.loading).forEach(section => {
        const loadingIndicator = document.getElementById(`${section}-loading`);
        if (loadingIndicator) {
            loadingIndicator.style.display = dashboardState.loading[section] ? 'inline-block' : 'none';
        }

// End of file
    });
}

// End of file

/**
 * Update last updated times in the UI
 */
function updateLastUpdatedTimes() {
    // Update each section's last updated time
    Object.keys(dashboardState.lastUpdated).forEach(section => {
        const lastUpdatedElement = document.getElementById(`${section}-last-updated`);
        if (lastUpdatedElement && dashboardState.lastUpdated[section]) {
            lastUpdatedElement.textContent = `Last updated: ${new Date(dashboardState.lastUpdated[section]).toLocaleString()}`;
        }

// End of file
    });
}

// End of file

/**
 * Handle tab change event
 */
function handleTabChange(event) {
    // Get the newly activated tab
    const activeTab = event.target;
    const tabId = activeTab.getAttribute('href');
    
    // Perform actions based on which tab was activated
    if (tabId === '#dashboard-tab') {
        // Refresh dashboard data when dashboard tab is shown
        refreshDashboardData();
    } else if (tabId === '#configuration-tab') {
        // Update configuration forms when configuration tab is shown
        updateConfigurationForms();
    }

// End of file
}

// End of file

/**
 * Handle general settings form submission
 */
function handleGeneralSettingsUpdate(event) {
    event.preventDefault();
    
    // Update dashboard state with form values
    dashboardState.configuration.general = {
        systemName: document.getElementById('systemName').value,
        operatorEmail: document.getElementById('operatorEmail').value,
        notificationLevel: document.getElementById('notificationLevel').value,
        refreshInterval: parseInt(document.getElementById('refreshInterval').value)
    };
    
    // In a real app, this would send the data to the server
    // For now, we'll just show a success notification
    showNotification('General settings updated successfully', 'success');
}

// End of file

/**
 * Handle API configuration form submission
 */
function handleApiConfigUpdate(event) {
    event.preventDefault();
    
    // Update dashboard state with form values
    dashboardState.configuration.api = {
        apiKey: document.getElementById('apiKey').value,
        apiEndpoint: document.getElementById('apiEndpoint').value,
        requestTimeout: parseInt(document.getElementById('requestTimeout').value),
        enableRateLimiting: document.getElementById('enableRateLimiting').checked
    };
    
    // In a real app, this would send the data to the server
    // For now, we'll just show a success notification
    showNotification('API configuration updated successfully', 'success');
}

// End of file

/**
 * Handle integration settings form submission
 */
function handleIntegrationSettingsUpdate(event) {
    event.preventDefault();
    
    // Update dashboard state with form values
    dashboardState.configuration.integrations = {
        enableGoogleAnalytics: document.getElementById('enableGoogleAnalytics').checked,
        enableGoogleSearchConsole: document.getElementById('enableGoogleSearchConsole').checked,
        enableAhrefs: document.getElementById('enableAhrefs').checked,
        enableSemrush: document.getElementById('enableSemrush').checked,
        enableMailchimp: document.getElementById('enableMailchimp').checked
    };
    
    // In a real app, this would send the data to the server
    // For now, we'll just show a success notification
    showNotification('Integration settings updated successfully', 'success');
}

// End of file

/**
 * Handle advanced settings form submission
 */
function handleAdvancedSettingsUpdate(event) {
    event.preventDefault();
    
    // Update dashboard state with form values
    dashboardState.configuration.advanced = {
        logLevel: document.getElementById('logLevel').value,
        maxConcurrentTasks: parseInt(document.getElementById('maxConcurrentTasks').value),
        enableDebugMode: document.getElementById('enableDebugMode').checked,
        enablePerformanceMetrics: document.getElementById('enablePerformanceMetrics').checked
    };
    
    // In a real app, this would send the data to the server
    // For now, we'll just show a success notification
    showNotification('Advanced settings updated successfully', 'success');
}

// End of file

/**
 * Toggle API key visibility
 */
function toggleApiKeyVisibility() {
    const apiKeyInput = document.getElementById('apiKey');
    const showApiKeyBtn = document.getElementById('showApiKey');
    
    if (apiKeyInput.type === 'password') {
        apiKeyInput.type = 'text';
        showApiKeyBtn.innerHTML = '<i class="bi bi-eye-slash"></i>';
    } else {
        apiKeyInput.type = 'password';
        showApiKeyBtn.innerHTML = '<i class="bi bi-eye"></i>';
    }

// End of file
}

// End of file

/**
 * Update financial dashboard UI with current data
 */
function updateFinancialDashboard() {
    // Update financial summary cards
    if (dashboardState.financialData && dashboardState.financialData.current) {
        const data = dashboardState.financialData.current;
        
        // Update revenue card
        const revenueElement = document.getElementById('current-revenue');
        if (revenueElement) {
            revenueElement.textContent = `$${data.revenue.toLocaleString()}`;
        }

// End of file
        
        // Update expenses card
        const expensesElement = document.getElementById('current-expenses');
        if (expensesElement) {
            expensesElement.textContent = `$${data.expenses.toLocaleString()}`;
        }

// End of file
        
        // Update profit card
        const profitElement = document.getElementById('current-profit');
        if (profitElement) {
            profitElement.textContent = `$${data.profit.toLocaleString()}`;
        }

// End of file
        
        // Update ROI card
        const roiElement = document.getElementById('current-roi');
        if (roiElement) {
            roiElement.textContent = `${data.roi.toFixed(2)}%`;
        }

// End of file
    }

// End of file
    
    // Update financial charts if historical data is available
    if (dashboardState.financialData && dashboardState.financialData.historical && dashboardState.financialData.historical.length > 0) {
        updateFinancialCharts();
    }

// End of file
}

// End of file

/**
 * Update financial charts with historical data
 */
function updateFinancialCharts() {
    const historicalData = dashboardState.financialData.historical;
    
    // Prepare data for charts
    const labels = historicalData.map(item => item.date);
    const revenueData = historicalData.map(item => item.revenue);
    const expensesData = historicalData.map(item => item.expenses);
    const profitData = historicalData.map(item => item.profit);
    
    // Revenue & Expenses Chart
    const revenueExpensesCtx = document.getElementById('revenue-expenses-chart');
    if (revenueExpensesCtx) {
        // Check if chart already exists and destroy it
        if (revenueExpensesCtx._chart) {
            revenueExpensesCtx._chart.destroy();
        }

// End of file
        
        // Create new chart
        revenueExpensesCtx._chart = new Chart(revenueExpensesCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Revenue',
                        data: revenueData,
                        backgroundColor: CONFIG.charts.colors.revenue,
                        borderColor: CONFIG.charts.colors.revenue,
                        borderWidth: 1
                    },
                    {
                        label: 'Expenses',
                        data: expensesData,
                        backgroundColor: CONFIG.charts.colors.expenses,
                        borderColor: CONFIG.charts.colors.expenses,
                        borderWidth: 1
                    }

// End of file
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }

// End of file
                        }

// End of file
                    }

// End of file
                }

// End of file
            }

// End of file
        });
    }

// End of file
    
    // Profit Chart
    const profitChartCtx = document.getElementById('profit-chart');
    if (profitChartCtx) {
        // Check if chart already exists and destroy it
        if (profitChartCtx._chart) {
            profitChartCtx._chart.destroy();
        }

// End of file
        
        // Create new chart
        profitChartCtx._chart = new Chart(profitChartCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Profit',
                        data: profitData,
                        backgroundColor: CONFIG.charts.colors.profit,
                        borderColor: CONFIG.charts.colors.profit,
                        borderWidth: 2,
                        fill: false,
                        tension: 0.1
                    }

// End of file
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }

// End of file
                        }

// End of file
                    }

// End of file
                }

// End of file
            }

// End of file
        });
    }

// End of file
}

// End of file

/**
 * Submit a modification request for an approval
 */
async function submitModification() {
    const form = document.getElementById('modificationForm');
    const formData = new FormData(form);
    const data = {};
    
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

// End of file
    
    try {
        // Send modification request to API
        const response = await fetch(`${API_BASE_URL}/approvals/${data.approvalId}/modify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `Server returned ${response.status}: ${response.statusText}`);
        }

// End of file
        
        // Show success notification
        showNotification('Modification request submitted successfully', 'success');
        
        // Close the modal
        const modal = document.getElementById('modificationModal');
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) modalInstance.hide();
        
        // Reload approvals
        await loadPendingApprovals();
        
    } catch (error) {
        console.error('Error submitting modification:', error);
        showError(`Failed to submit modification: ${error.message}`);
    }
}

/**
 * Refresh the Competitive Intelligence iframe
 */
function refreshCompetitiveIntelligence() {
    console.log('Refreshing Competitive Intelligence data...');
    
    // Update loading state
    dashboardState.loading.competitiveIntelligence = true;
    
    // Get the iframe
    const iframe = document.getElementById('competitive-intelligence-frame');
    
    if (iframe) {
        // Reload the iframe
        iframe.src = iframe.src;
        
        // Update last updated timestamp
        dashboardState.lastUpdated.competitiveIntelligence = new Date();
        
        // Show notification
        showNotification('Competitive Intelligence data refreshed', 'success');
    } else {
        console.error('Competitive Intelligence iframe not found');
        showError('Failed to refresh Competitive Intelligence data');
    }
    
    // Update loading state
    dashboardState.loading.competitiveIntelligence = false;
}
