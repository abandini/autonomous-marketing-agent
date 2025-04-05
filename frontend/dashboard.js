/**
 * GAMS Dashboard JavaScript
 * Handles API communication and dynamic updates for the GAMS dashboard
 */

// API endpoints
const API_ENDPOINTS = {
    TASKS: '/api/tasks',
    EVENTS: '/api/events',
    SYSTEM_STATUS: '/api/system-status',
    PERFORMANCE_DATA: '/api/performance-data',
    SCHEDULE_TASK: '/api/schedule-task',
    UPDATE_WEBSITE: '/api/update-website',
    ANALYTICS_SYNC: '/api/analytics/sync'
};

// Charts
let performanceChart = null;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initializeCharts();
    
    // Load initial data
    loadSystemStatus();
    loadRecentActivity();
    loadTasksData();
    
    // Set up refresh intervals
    setInterval(loadSystemStatus, 30000); // Refresh status every 30 seconds
    setInterval(loadRecentActivity, 60000); // Refresh activity every minute
    
    // Set up event handlers
    setupEventHandlers();
});

/**
 * Initialize charts on the dashboard
 */
function initializeCharts() {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    
    // Create initial chart with loading state
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Loading...'],
            datasets: [
                {
                    label: 'Loading...',
                    data: [0],
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.3
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
    
    // Load performance data for the chart
    loadPerformanceData();
}

/**
 * Load system status data from the API
 */
function loadSystemStatus() {
    fetch(API_ENDPOINTS.SYSTEM_STATUS)
        .then(response => response.json())
        .then(data => {
            updateSystemStatus(data);
        })
        .catch(error => {
            console.error('Error loading system status:', error);
        });
}

/**
 * Update the system status UI with the provided data
 */
function updateSystemStatus(data) {
    // Update Process Orchestrator status
    updateComponentStatus('Process Orchestrator', data.process_orchestrator);
    
    // Update Task Scheduler status
    updateComponentStatus('Task Scheduler', data.task_scheduler);
    
    // Update Event Manager status
    updateComponentStatus('Event Manager', data.event_manager);
    
    // Update Recovery Manager status
    updateComponentStatus('Recovery Manager', data.recovery_manager);
    
    // Update last updated timestamp
    const lastUpdated = new Date(data.last_updated);
    document.querySelector('.bottom-0 .small').textContent = 
        `Last updated: ${lastUpdated.toLocaleString()}`;
    
    // Update overall system status
    const allHealthy = Object.values(data).every(
        component => typeof component === 'object' && component.status === 'healthy'
    );
    
    const statusIndicator = document.querySelector('.bottom-0 .status-indicator');
    const statusText = document.querySelector('.bottom-0 .status-indicator + span');
    
    if (allHealthy) {
        statusIndicator.className = 'status-indicator status-healthy';
        statusText.textContent = 'System Status: Healthy';
    } else {
        statusIndicator.className = 'status-indicator status-warning';
        statusText.textContent = 'System Status: Degraded';
    }
}

/**
 * Update the status of a specific component
 */
function updateComponentStatus(componentName, data) {
    const componentCard = Array.from(document.querySelectorAll('.card-title'))
        .find(el => el.textContent === componentName)
        ?.closest('.card');
    
    if (!componentCard) return;
    
    const statusIndicator = componentCard.querySelector('.status-indicator');
    const statusText = componentCard.querySelector('.status-indicator + span');
    const statusDetails = componentCard.querySelector('.small');
    
    // Update status indicator and text
    if (data.status === 'healthy') {
        statusIndicator.className = 'status-indicator status-healthy';
        statusText.textContent = 'Healthy';
    } else if (data.status === 'degraded') {
        statusIndicator.className = 'status-indicator status-warning';
        statusText.textContent = 'Degraded';
    } else {
        statusIndicator.className = 'status-indicator status-error';
        statusText.textContent = 'Unhealthy';
    }
    
    // Update details text
    if (componentName === 'Process Orchestrator') {
        statusDetails.textContent = `${data.active_processes} active processes`;
    } else if (componentName === 'Task Scheduler') {
        statusDetails.textContent = `${data.scheduled_tasks} scheduled tasks`;
    } else if (componentName === 'Event Manager') {
        statusDetails.textContent = `${data.events_today} events today`;
    } else if (componentName === 'Recovery Manager') {
        statusDetails.textContent = `${data.recovery_actions} recovery actions`;
    }
}

/**
 * Load recent activity data from the API
 */
function loadRecentActivity() {
    fetch(API_ENDPOINTS.EVENTS)
        .then(response => response.json())
        .then(data => {
            updateRecentActivity(data);
        })
        .catch(error => {
            console.error('Error loading recent activity:', error);
        });
}

/**
 * Update the recent activity UI with the provided data
 */
function updateRecentActivity(events) {
    const activityList = document.querySelector('.card-header:contains("Recent Activity") + .card-body .list-group');
    if (!activityList) return;
    
    // Sort events by timestamp (newest first)
    events.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    // Take only the 5 most recent events
    const recentEvents = events.slice(0, 5);
    
    // Clear the list
    activityList.innerHTML = '';
    
    // Add each event to the list
    recentEvents.forEach(event => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        // Determine icon based on event name
        let icon = 'bi-bell';
        let iconClass = 'text-primary';
        
        if (event.name.includes('update') && event.name.includes('completed')) {
            icon = 'bi-globe';
            iconClass = 'text-success';
        } else if (event.name.includes('spike')) {
            icon = 'bi-bell';
            iconClass = 'text-primary';
        } else if (event.name.includes('content') && event.name.includes('generated')) {
            icon = 'bi-check-circle';
            iconClass = 'text-success';
        } else if (event.name.includes('performance') && event.name.includes('drop')) {
            icon = 'bi-exclamation-triangle';
            iconClass = 'text-warning';
        } else if (event.name.includes('backup')) {
            icon = 'bi-arrow-repeat';
            iconClass = 'text-info';
        } else if (event.name.includes('error')) {
            icon = 'bi-exclamation-circle';
            iconClass = 'text-danger';
        }
        
        // Format the event name for display
        const eventName = event.name
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
        
        // Format the timestamp
        const timestamp = new Date(event.timestamp);
        const timeAgo = getTimeAgo(timestamp);
        
        // Create the event details
        let details = '';
        if (event.data) {
            if (event.data.repository_name) {
                details = event.data.repository_name;
            } else if (event.data.page_url) {
                details = event.data.page_url;
            } else if (event.data.content_id) {
                details = event.data.content_id;
            } else if (event.data.content_count) {
                details = `${event.data.content_count} ${event.data.content_type || 'items'}`;
            } else if (event.data.backup_type) {
                details = `${event.data.backup_type} backup`;
            }
        }
        
        // Build the HTML
        li.innerHTML = `
            <div>
                <i class="bi ${icon} ${iconClass} me-2"></i>
                <span>${eventName}</span>
                <div class="small text-muted">${details}</div>
            </div>
            <span class="small text-muted">${timeAgo}</span>
        `;
        
        activityList.appendChild(li);
    });
}

/**
 * Load performance data for charts
 */
function loadPerformanceData() {
    fetch(API_ENDPOINTS.PERFORMANCE_DATA)
        .then(response => response.json())
        .then(data => {
            updatePerformanceChart(data);
        })
        .catch(error => {
            console.error('Error loading performance data:', error);
        });
}

/**
 * Update the performance chart with the provided data
 */
function updatePerformanceChart(data) {
    if (!performanceChart) return;
    
    performanceChart.data.labels = data.labels;
    performanceChart.data.datasets = [
        {
            label: 'Website Traffic',
            data: data.website_traffic,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.3
        },
        {
            label: 'Conversions',
            data: data.conversions,
            borderColor: 'rgba(153, 102, 255, 1)',
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            tension: 0.3
        }
    ];
    
    performanceChart.update();
}

/**
 * Load tasks data from the API
 */
function loadTasksData() {
    fetch(API_ENDPOINTS.TASKS)
        .then(response => response.json())
        .then(data => {
            updateTasksTable(data);
        })
        .catch(error => {
            console.error('Error loading tasks data:', error);
        });
}

/**
 * Update the tasks table with the provided data
 */
function updateTasksTable(tasks) {
    const tasksTable = document.querySelector('#tasks table tbody');
    if (!tasksTable) return;
    
    // Clear the table
    tasksTable.innerHTML = '';
    
    // Add each task to the table
    tasks.forEach(task => {
        const tr = document.createElement('tr');
        
        // Set priority class
        if (task.priority <= 3) {
            tr.className = 'task-priority-high';
        } else if (task.priority <= 6) {
            tr.className = 'task-priority-medium';
        } else {
            tr.className = 'task-priority-low';
        }
        
        // Format schedule
        let scheduleText = '';
        if (task.schedule_type === 'once') {
            const date = new Date(task.schedule_value);
            scheduleText = `Once (${date.toLocaleString()})`;
        } else if (task.schedule_type === 'interval') {
            const seconds = task.schedule_value;
            if (seconds < 60) {
                scheduleText = `Every ${seconds} seconds`;
            } else if (seconds < 3600) {
                scheduleText = `Every ${Math.floor(seconds / 60)} minutes`;
            } else if (seconds < 86400) {
                scheduleText = `Every ${Math.floor(seconds / 3600)} hours`;
            } else {
                scheduleText = `Every ${Math.floor(seconds / 86400)} days`;
            }
        } else if (task.schedule_type === 'cron') {
            scheduleText = `Cron: ${task.schedule_value}`;
        } else if (task.schedule_type === 'immediate') {
            scheduleText = 'Immediate';
        }
        
        // Format priority
        let priorityText = '';
        if (task.priority <= 3) {
            priorityText = 'High';
        } else if (task.priority <= 6) {
            priorityText = 'Medium';
        } else {
            priorityText = 'Low';
        }
        
        // Format status badge
        let statusBadgeClass = '';
        switch (task.status) {
            case 'scheduled':
                statusBadgeClass = 'bg-warning';
                break;
            case 'running':
                statusBadgeClass = 'bg-success';
                break;
            case 'completed':
                statusBadgeClass = 'bg-info';
                break;
            case 'failed':
                statusBadgeClass = 'bg-danger';
                break;
            default:
                statusBadgeClass = 'bg-secondary';
        }
        
        // Build the HTML
        tr.innerHTML = `
            <td>${task.id}</td>
            <td>${task.type}</td>
            <td>${scheduleText}</td>
            <td>${priorityText}</td>
            <td><span class="badge ${statusBadgeClass}">${task.status}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary me-1"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm btn-outline-danger"><i class="bi bi-trash"></i></button>
            </td>
        `;
        
        tasksTable.appendChild(tr);
    });
}

/**
 * Sync Google Analytics data
 */
function syncGoogleAnalytics() {
    // Show loading indicator
    const syncButton = document.getElementById('syncAnalyticsBtn');
    if (syncButton) {
        syncButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Syncing...';
        syncButton.disabled = true;
    }
    
    fetch(API_ENDPOINTS.ANALYTICS_SYNC, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        // Reset button
        if (syncButton) {
            syncButton.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i> Sync Analytics';
            syncButton.disabled = false;
        }
        
        if (data.status === 'success') {
            // Show success message
            alert(`Analytics data synced successfully!`);
            
            // Reload performance data
            loadPerformanceData();
        } else {
            alert(`Error syncing analytics data: ${data.message}`);
        }
    })
    .catch(error => {
        // Reset button
        if (syncButton) {
            syncButton.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i> Sync Analytics';
            syncButton.disabled = false;
        }
        
        console.error('Error syncing analytics data:', error);
        alert('Error syncing analytics data. See console for details.');
    });
}

/**
 * Set up event handlers for forms and buttons
 */
function setupEventHandlers() {
    // Google Analytics sync buttons
    const syncAnalyticsBtn = document.getElementById('syncAnalyticsBtn');
    if (syncAnalyticsBtn) {
        syncAnalyticsBtn.addEventListener('click', syncGoogleAnalytics);
    }
    
    const syncAnalyticsBtn2 = document.getElementById('syncAnalyticsBtn2');
    if (syncAnalyticsBtn2) {
        syncAnalyticsBtn2.addEventListener('click', syncGoogleAnalytics);
    }
    
    // Schedule Task form
    const scheduleTaskForm = document.querySelector('#scheduleTaskModal form');
    if (scheduleTaskForm) {
        const scheduleTaskButton = document.querySelector('#scheduleTaskModal .btn-primary');
        scheduleTaskButton.addEventListener('click', function() {
            const taskType = document.getElementById('taskType').value;
            const scheduleType = document.getElementById('scheduleType').value;
            const scheduleValue = document.getElementById('scheduleValue').value;
            const priority = document.getElementById('priority').value;
            const taskParams = document.getElementById('taskParams').value;
            
            let params = {};
            try {
                if (taskParams) {
                    params = JSON.parse(taskParams);
                }
            } catch (e) {
                alert('Invalid JSON in parameters field');
                return;
            }
            
            const taskData = {
                type: taskType,
                schedule_type: scheduleType,
                schedule_value: scheduleValue,
                priority: priority,
                params: params
            };
            
            scheduleTask(taskData);
        });
        
        // Update schedule value field based on schedule type
        const scheduleTypeSelect = document.getElementById('scheduleType');
        const scheduleValueInput = document.getElementById('scheduleValue');
        
        scheduleTypeSelect.addEventListener('change', function() {
            if (this.value === 'once') {
                scheduleValueInput.type = 'datetime-local';
                scheduleValueInput.value = new Date().toISOString().slice(0, 16);
            } else if (this.value === 'interval') {
                scheduleValueInput.type = 'number';
                scheduleValueInput.value = '3600'; // Default to 1 hour
            } else if (this.value === 'cron') {
                scheduleValueInput.type = 'text';
                scheduleValueInput.value = '0 0 * * *'; // Default to midnight
            } else if (this.value === 'immediate') {
                scheduleValueInput.type = 'hidden';
                scheduleValueInput.value = '';
            }
        });
    }
    
    // Update Website form
    const updateWebsiteForm = document.querySelector('#updateWebsiteModal form');
    if (updateWebsiteForm) {
        const updateWebsiteButton = document.querySelector('#updateWebsiteModal .btn-success');
        updateWebsiteButton.addEventListener('click', function() {
            const repositoryName = document.getElementById('repositoryName').value;
            const scheduleType = document.getElementById('updateScheduleType').value;
            const scheduleValue = document.getElementById('updateScheduleValue').value;
            
            const updateData = {
                repository_name: repositoryName,
                schedule_type: scheduleType,
                schedule_value: scheduleValue
            };
            
            updateWebsite(updateData);
        });
        
        // Update schedule value field based on schedule type
        const scheduleTypeSelect = document.getElementById('updateScheduleType');
        const scheduleValueInput = document.getElementById('updateScheduleValue');
        
        scheduleTypeSelect.addEventListener('change', function() {
            if (this.value === 'once') {
                scheduleValueInput.type = 'datetime-local';
                scheduleValueInput.value = new Date().toISOString().slice(0, 16);
                scheduleValueInput.parentElement.style.display = 'block';
            } else if (this.value === 'interval') {
                scheduleValueInput.type = 'number';
                scheduleValueInput.value = '86400'; // Default to 1 day
                scheduleValueInput.parentElement.style.display = 'block';
            } else if (this.value === 'immediate') {
                scheduleValueInput.parentElement.style.display = 'none';
            }
        });
    }
}

/**
 * Schedule a new task via the API
 */
function scheduleTask(taskData) {
    fetch(API_ENDPOINTS.SCHEDULE_TASK, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(taskData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('scheduleTaskModal'));
            modal.hide();
            
            // Show success message
            alert(`Task scheduled successfully with ID: ${data.task_id}`);
            
            // Reload tasks data
            loadTasksData();
        } else {
            alert(`Error scheduling task: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error scheduling task:', error);
        alert('Error scheduling task. See console for details.');
    });
}

/**
 * Schedule a website update via the API
 */
function updateWebsite(updateData) {
    fetch(API_ENDPOINTS.UPDATE_WEBSITE, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('updateWebsiteModal'));
            modal.hide();
            
            // Show success message
            alert(`Website update scheduled successfully with process ID: ${data.process_id}`);
            
            // Reload recent activity
            loadRecentActivity();
        } else {
            alert(`Error scheduling website update: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error scheduling website update:', error);
        alert('Error scheduling website update. See console for details.');
    });
}

/**
 * Get a human-readable time ago string from a timestamp
 */
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    let interval = Math.floor(seconds / 31536000);
    if (interval >= 1) {
        return interval === 1 ? '1 year ago' : `${interval} years ago`;
    }
    
    interval = Math.floor(seconds / 2592000);
    if (interval >= 1) {
        return interval === 1 ? '1 month ago' : `${interval} months ago`;
    }
    
    interval = Math.floor(seconds / 86400);
    if (interval >= 1) {
        return interval === 1 ? '1 day ago' : `${interval} days ago`;
    }
    
    interval = Math.floor(seconds / 3600);
    if (interval >= 1) {
        return interval === 1 ? '1 hour ago' : `${interval} hours ago`;
    }
    
    interval = Math.floor(seconds / 60);
    if (interval >= 1) {
        return interval === 1 ? '1 minute ago' : `${interval} minutes ago`;
    }
    
    return seconds < 10 ? 'just now' : `${seconds} seconds ago`;
}

// Add a contains selector to jQuery-like functionality
Element.prototype.matches = Element.prototype.matches || Element.prototype.msMatchesSelector;
NodeList.prototype.forEach = NodeList.prototype.forEach || Array.prototype.forEach;

// Add :contains selector functionality
document.querySelectorAll = (function(querySelectorAll) {
    return function(selector) {
        if (selector.includes(':contains(')) {
            const parts = selector.match(/(.*):contains\(["']?([^"']*)["']?\)(.*)/);
            if (parts) {
                const [, before, text, after] = parts;
                const elements = document.querySelectorAll(before);
                const filtered = Array.from(elements).filter(el => 
                    el.textContent.includes(text)
                );
                
                if (after) {
                    let results = [];
                    filtered.forEach(el => {
                        results = results.concat(Array.from(el.querySelectorAll(after)));
                    });
                    return results;
                }
                
                return filtered;
            }
        }
        return querySelectorAll.call(document, selector);
    };
})(document.querySelectorAll);
