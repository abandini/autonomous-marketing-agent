/**
 * GAMS Orchestrator Dashboard Integration
 * 
 * This file provides integration between the GAMS Operator Dashboard
 * and the refactored Orchestrator, allowing management of improvement cycles,
 * marketing goals, and campaigns.
 */

// API endpoint base URL
const ORCHESTRATOR_API_BASE_URL = '/api/operator/orchestrator';

// Orchestrator Dashboard Configuration
const ORCHESTRATOR_CONFIG = {
    refreshIntervals: {
        cycles: 60000,        // 1 minute
        goals: 120000,        // 2 minutes
        campaigns: 180000     // 3 minutes
    }
};

// Orchestrator Dashboard State
const orchestratorDashboardState = {
    cycles: [],
    goals: [],
    campaigns: [],
    loading: {
        cycles: false,
        goals: false,
        campaigns: false
    },
    lastUpdated: {
        cycles: null,
        goals: null,
        campaigns: null
    }
};

/**
 * Initialize the orchestrator dashboard integration
 */
function initializeOrchestratorDashboard() {
    console.log('Initializing orchestrator dashboard integration...');
    
    // Set up event listeners
    setupOrchestratorEventListeners();
    
    // Load initial data
    loadOrchestratorData();
    
    // Set up refresh intervals
    setInterval(() => refreshCycles(), ORCHESTRATOR_CONFIG.refreshIntervals.cycles);
    setInterval(() => refreshGoals(), ORCHESTRATOR_CONFIG.refreshIntervals.goals);
    setInterval(() => refreshCampaigns(), ORCHESTRATOR_CONFIG.refreshIntervals.campaigns);
}

/**
 * Set up event listeners for orchestrator dashboard
 */
function setupOrchestratorEventListeners() {
    console.log('Setting up orchestrator dashboard event listeners...');
    
    // Refresh buttons
    const refreshCyclesBtn = document.getElementById('refresh-cycles-btn');
    if (refreshCyclesBtn) {
        refreshCyclesBtn.addEventListener('click', function() {
            refreshCycles();
        });
    }
    
    const refreshGoalsBtn = document.getElementById('refresh-goals-btn');
    if (refreshGoalsBtn) {
        refreshGoalsBtn.addEventListener('click', function() {
            refreshGoals();
        });
    }
    
    const refreshCampaignsBtn = document.getElementById('refresh-campaigns-btn');
    if (refreshCampaignsBtn) {
        refreshCampaignsBtn.addEventListener('click', function() {
            refreshCampaigns();
        });
    }
    
    // Create buttons
    const createCycleBtn = document.getElementById('create-cycle-btn');
    if (createCycleBtn) {
        createCycleBtn.addEventListener('click', function() {
            showCreateCycleModal();
        });
    }
    
    const createGoalBtn = document.getElementById('create-goal-btn');
    if (createGoalBtn) {
        createGoalBtn.addEventListener('click', function() {
            showCreateGoalModal();
        });
    }
    
    const createCampaignBtn = document.getElementById('create-campaign-btn');
    if (createCampaignBtn) {
        createCampaignBtn.addEventListener('click', function() {
            showCreateCampaignModal();
        });
    }
}

/**
 * Load all orchestrator data
 */
function loadOrchestratorData() {
    console.log('Loading orchestrator data...');
    
    refreshCycles();
    refreshGoals();
    refreshCampaigns();
}

/**
 * Refresh improvement cycles
 */
function refreshCycles() {
    console.log('Refreshing improvement cycles...');
    orchestratorDashboardState.loading.cycles = true;
    updateLoadingState('cycles', true);
    
    fetch(`${ORCHESTRATOR_API_BASE_URL}/cycles`)
        .then(response => response.json())
        .then(data => {
            console.log('Received cycles data:', data);
            orchestratorDashboardState.cycles = data.cycles || [];
            orchestratorDashboardState.lastUpdated.cycles = new Date();
            updateCyclesUI(orchestratorDashboardState.cycles);
            updateLoadingState('cycles', false);
            showNotification('Improvement cycles refreshed', 'success');
        })
        .catch(error => {
            console.error('Error fetching cycles:', error);
            updateLoadingState('cycles', false);
            showNotification('Failed to refresh improvement cycles', 'error');
        });
}

/**
 * Refresh marketing goals
 */
function refreshGoals() {
    console.log('Refreshing marketing goals...');
    orchestratorDashboardState.loading.goals = true;
    updateLoadingState('goals', true);
    
    fetch(`${ORCHESTRATOR_API_BASE_URL}/goals`)
        .then(response => response.json())
        .then(data => {
            console.log('Received goals data:', data);
            orchestratorDashboardState.goals = data.goals || [];
            orchestratorDashboardState.lastUpdated.goals = new Date();
            updateGoalsUI(orchestratorDashboardState.goals);
            updateLoadingState('goals', false);
            showNotification('Marketing goals refreshed', 'success');
        })
        .catch(error => {
            console.error('Error fetching goals:', error);
            updateLoadingState('goals', false);
            showNotification('Failed to refresh marketing goals', 'error');
        });
}

/**
 * Refresh marketing campaigns
 */
function refreshCampaigns() {
    console.log('Refreshing marketing campaigns...');
    orchestratorDashboardState.loading.campaigns = true;
    updateLoadingState('campaigns', true);
    
    fetch(`${ORCHESTRATOR_API_BASE_URL}/campaigns`)
        .then(response => response.json())
        .then(data => {
            console.log('Received campaigns data:', data);
            orchestratorDashboardState.campaigns = data.campaigns || [];
            orchestratorDashboardState.lastUpdated.campaigns = new Date();
            updateCampaignsUI(orchestratorDashboardState.campaigns);
            updateLoadingState('campaigns', false);
            showNotification('Marketing campaigns refreshed', 'success');
        })
        .catch(error => {
            console.error('Error fetching campaigns:', error);
            updateLoadingState('campaigns', false);
            showNotification('Failed to refresh marketing campaigns', 'error');
        });
}

/**
 * Update cycles UI with latest data
 */
function updateCyclesUI(cycles) {
    const cyclesContainer = document.getElementById('cycles-container');
    if (!cyclesContainer) return;
    
    // Update cycle badge count
    const cycleBadge = document.getElementById('cycle-badge');
    if (cycleBadge) {
        cycleBadge.textContent = cycles.length;
    }
    
    // Clear existing content
    cyclesContainer.innerHTML = '';
    
    if (cycles.length > 0) {
        cycles.forEach(cycle => {
            const cycleCard = document.createElement('div');
            cycleCard.className = 'card mb-3';
            
            // Determine card color based on cycle phase
            let headerClass = 'bg-primary';
            switch (cycle.current_phase) {
                case 'website_optimization':
                    headerClass = 'bg-info';
                    break;
                case 'multi_channel_marketing':
                    headerClass = 'bg-success';
                    break;
                case 'data_learning':
                    headerClass = 'bg-warning';
                    break;
                case 'content_refinement':
                    headerClass = 'bg-danger';
                    break;
                case 'revenue_optimization':
                    headerClass = 'bg-secondary';
                    break;
                case 'system_expansion':
                    headerClass = 'bg-dark';
                    break;
            }
            
            cycleCard.innerHTML = `
                <div class="card-header ${headerClass} text-white d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">Cycle ID: ${cycle.id}</h6>
                    <span class="badge bg-light text-dark">Phase: ${formatPhaseTitle(cycle.current_phase)}</span>
                </div>
                <div class="card-body">
                    <p><strong>Started:</strong> ${formatDateTime(cycle.start_time)}</p>
                    <p><strong>Last Phase Change:</strong> ${formatDateTime(cycle.last_phase_change)}</p>
                    <div class="progress mb-3">
                        <div class="progress-bar ${headerClass}" role="progressbar" 
                            style="width: ${calculatePhaseProgress(cycle)}%" 
                            aria-valuenow="${calculatePhaseProgress(cycle)}" 
                            aria-valuemin="0" 
                            aria-valuemax="100">
                            ${calculatePhaseProgress(cycle)}%
                        </div>
                    </div>
                    <div class="d-flex justify-content-end">
                        <button class="btn btn-sm btn-outline-primary me-2" 
                            onclick="viewCycleDetails('${cycle.id}')">
                            <i class="bi bi-eye"></i> View
                        </button>
                        <button class="btn btn-sm btn-outline-success" 
                            onclick="advanceCyclePhase('${cycle.id}')">
                            <i class="bi bi-arrow-right"></i> Advance Phase
                        </button>
                    </div>
                </div>
            `;
            
            cyclesContainer.appendChild(cycleCard);
        });
    } else {
        cyclesContainer.innerHTML = `
            <div class="alert alert-info">
                No active improvement cycles. Click "Create New Cycle" to start one.
            </div>
        `;
    }
}

/**
 * Update goals UI with latest data
 */
function updateGoalsUI(goals) {
    const goalsContainer = document.getElementById('goals-container');
    if (!goalsContainer) return;
    
    // Clear existing content
    goalsContainer.innerHTML = '';
    
    if (goals.length > 0) {
        goals.forEach(goal => {
            const goalCard = document.createElement('div');
            goalCard.className = 'card mb-3';
            
            // Determine card color based on goal status
            let headerClass = 'bg-primary';
            if (goal.status === 'completed') {
                headerClass = 'bg-success';
            } else if (goal.status === 'at_risk') {
                headerClass = 'bg-warning';
            } else if (goal.status === 'failed') {
                headerClass = 'bg-danger';
            }
            
            // Format metrics
            let metricsHtml = '';
            if (goal.metrics && Object.keys(goal.metrics).length > 0) {
                metricsHtml = '<div class="mt-2"><strong>Metrics:</strong><ul>';
                for (const [key, value] of Object.entries(goal.metrics)) {
                    metricsHtml += `<li>${formatMetricName(key)}: ${formatMetricValue(key, value)}</li>`;
                }
                metricsHtml += '</ul></div>';
            }
            
            goalCard.innerHTML = `
                <div class="card-header ${headerClass} text-white">
                    <h6 class="mb-0">${goal.name}</h6>
                </div>
                <div class="card-body">
                    <p><strong>Type:</strong> ${goal.type}</p>
                    <p><strong>Target:</strong> ${goal.target}</p>
                    <p><strong>Status:</strong> <span class="badge ${getStatusBadgeClass(goal.status)}">${goal.status}</span></p>
                    ${metricsHtml}
                    <div class="d-flex justify-content-end mt-2">
                        <button class="btn btn-sm btn-outline-primary me-2" 
                            onclick="viewGoalDetails('${goal.id}')">
                            <i class="bi bi-eye"></i> View
                        </button>
                        <button class="btn btn-sm btn-outline-success" 
                            onclick="createCampaignForGoal('${goal.id}')">
                            <i class="bi bi-plus-circle"></i> Add Campaign
                        </button>
                    </div>
                </div>
            `;
            
            goalsContainer.appendChild(goalCard);
        });
    } else {
        goalsContainer.innerHTML = `
            <div class="alert alert-info">
                No marketing goals. Click "Create New Goal" to add one.
            </div>
        `;
    }
}

/**
 * Update campaigns UI with latest data
 */
function updateCampaignsUI(campaigns) {
    const campaignsTableBody = document.getElementById('campaigns-table-body');
    if (!campaignsTableBody) return;
    
    // Update active campaigns count
    const activeCampaignsCount = document.getElementById('active-campaigns-count');
    if (activeCampaignsCount) {
        const activeCount = campaigns.filter(c => c.status === 'active').length;
        activeCampaignsCount.textContent = activeCount;
    }
    
    // Clear existing rows
    campaignsTableBody.innerHTML = '';
    
    if (campaigns.length > 0) {
        campaigns.forEach(campaign => {
            const row = document.createElement('tr');
            
            // Format metrics
            let metricsHtml = '';
            if (campaign.metrics && Object.keys(campaign.metrics).length > 0) {
                const topMetrics = Object.entries(campaign.metrics).slice(0, 2);
                metricsHtml = topMetrics.map(([key, value]) => 
                    `${formatMetricName(key)}: ${formatMetricValue(key, value)}`
                ).join('<br>');
                
                if (Object.keys(campaign.metrics).length > 2) {
                    metricsHtml += '<br><small>+ more</small>';
                }
            } else {
                metricsHtml = '<small class="text-muted">No metrics</small>';
            }
            
            row.innerHTML = `
                <td>${campaign.id.substring(0, 8)}...</td>
                <td>${campaign.name}</td>
                <td>${campaign.type}</td>
                <td><span class="badge ${getStatusBadgeClass(campaign.status)}">${campaign.status}</span></td>
                <td>${campaign.goal_id ? campaign.goal_id.substring(0, 8) + '...' : 'N/A'}</td>
                <td>${metricsHtml}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" 
                        onclick="viewCampaignDetails('${campaign.id}')">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" 
                        onclick="updateCampaignStatus('${campaign.id}', '${campaign.status === 'active' ? 'paused' : 'active'}')">
                        <i class="bi bi-${campaign.status === 'active' ? 'pause' : 'play'}"></i>
                    </button>
                </td>
            `;
            
            campaignsTableBody.appendChild(row);
        });
    } else {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="7" class="text-center">No marketing campaigns. Click "Create New Campaign" to add one.</td>
        `;
        campaignsTableBody.appendChild(row);
    }
}

/**
 * View cycle details
 */
function viewCycleDetails(cycleId) {
    console.log(`Viewing details for cycle ${cycleId}`);
    
    fetch(`${ORCHESTRATOR_API_BASE_URL}/cycles/${cycleId}`)
        .then(response => response.json())
        .then(data => {
            console.log('Received cycle details:', data);
            showCycleDetailsModal(data);
        })
        .catch(error => {
            console.error('Error fetching cycle details:', error);
            showNotification('Failed to load cycle details', 'error');
        });
}

/**
 * Advance cycle phase
 */
function advanceCyclePhase(cycleId) {
    console.log(`Advancing phase for cycle ${cycleId}`);
    
    fetch(`${ORCHESTRATOR_API_BASE_URL}/cycles/${cycleId}/advance`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log('Received advance phase response:', data);
            if (data.status === 'success') {
                showNotification('Advanced to next phase successfully', 'success');
                refreshCycles();
            } else {
                showNotification(`Failed to advance phase: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error advancing phase:', error);
            showNotification('Failed to advance phase', 'error');
        });
}

/**
 * View goal details
 */
function viewGoalDetails(goalId) {
    console.log(`Viewing details for goal ${goalId}`);
    
    fetch(`${ORCHESTRATOR_API_BASE_URL}/goals/${goalId}`)
        .then(response => response.json())
        .then(data => {
            console.log('Received goal details:', data);
            showGoalDetailsModal(data);
        })
        .catch(error => {
            console.error('Error fetching goal details:', error);
            showNotification('Failed to load goal details', 'error');
        });
}

/**
 * Create campaign for goal
 */
function createCampaignForGoal(goalId) {
    console.log(`Creating campaign for goal ${goalId}`);
    showCreateCampaignModal(goalId);
}

/**
 * View campaign details
 */
function viewCampaignDetails(campaignId) {
    console.log(`Viewing details for campaign ${campaignId}`);
    
    fetch(`${ORCHESTRATOR_API_BASE_URL}/campaigns/${campaignId}`)
        .then(response => response.json())
        .then(data => {
            console.log('Received campaign details:', data);
            showCampaignDetailsModal(data);
        })
        .catch(error => {
            console.error('Error fetching campaign details:', error);
            showNotification('Failed to load campaign details', 'error');
        });
}

/**
 * Update campaign status
 */
function updateCampaignStatus(campaignId, newStatus) {
    console.log(`Updating status for campaign ${campaignId} to ${newStatus}`);
    
    fetch(`${ORCHESTRATOR_API_BASE_URL}/campaigns/${campaignId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Received update status response:', data);
            if (data.status === 'success') {
                showNotification(`Campaign status updated to ${newStatus}`, 'success');
                refreshCampaigns();
            } else {
                showNotification(`Failed to update status: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error updating campaign status:', error);
            showNotification('Failed to update campaign status', 'error');
        });
}

/**
 * Show create cycle modal
 */
function showCreateCycleModal() {
    // In a real implementation, this would create and show a modal dialog
    console.log('Showing create cycle modal');
    showNotification('Create cycle functionality not implemented yet', 'info');
}

/**
 * Show create goal modal
 */
function showCreateGoalModal() {
    // In a real implementation, this would create and show a modal dialog
    console.log('Showing create goal modal');
    showNotification('Create goal functionality not implemented yet', 'info');
}

/**
 * Show create campaign modal
 */
function showCreateCampaignModal(goalId = null) {
    // In a real implementation, this would create and show a modal dialog
    console.log('Showing create campaign modal', goalId ? `for goal ${goalId}` : '');
    showNotification('Create campaign functionality not implemented yet', 'info');
}

/**
 * Show cycle details modal
 */
function showCycleDetailsModal(cycleData) {
    // In a real implementation, this would create and show a modal dialog
    console.log('Showing cycle details modal for:', cycleData);
    showNotification('Cycle details view not implemented yet', 'info');
}

/**
 * Show goal details modal
 */
function showGoalDetailsModal(goalData) {
    // In a real implementation, this would create and show a modal dialog
    console.log('Showing goal details modal for:', goalData);
    showNotification('Goal details view not implemented yet', 'info');
}

/**
 * Show campaign details modal
 */
function showCampaignDetailsModal(campaignData) {
    // In a real implementation, this would create and show a modal dialog
    console.log('Showing campaign details modal for:', campaignData);
    showNotification('Campaign details view not implemented yet', 'info');
}

/**
 * Update loading state for a specific section
 */
function updateLoadingState(section, isLoading) {
    orchestratorDashboardState.loading[section] = isLoading;
    
    // Update UI loading indicators
    const loadingIndicator = document.getElementById(`${section}-loading`);
    if (loadingIndicator) {
        loadingIndicator.style.display = isLoading ? 'inline-block' : 'none';
    }
}

/**
 * Format phase title
 */
function formatPhaseTitle(phase) {
    if (!phase) return 'Unknown';
    
    // Convert snake_case to Title Case
    return phase.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Calculate phase progress percentage
 */
function calculatePhaseProgress(cycle) {
    // This is a simplified implementation
    // In a real implementation, you would calculate this based on tasks completed, time elapsed, etc.
    const phases = [
        'website_optimization',
        'multi_channel_marketing',
        'data_learning',
        'content_refinement',
        'revenue_optimization',
        'system_expansion'
    ];
    
    const currentPhaseIndex = phases.indexOf(cycle.current_phase);
    if (currentPhaseIndex === -1) return 0;
    
    // Calculate progress as percentage of phases completed
    return Math.round(((currentPhaseIndex + 0.5) / phases.length) * 100);
}

/**
 * Get status badge class
 */
function getStatusBadgeClass(status) {
    switch (status) {
        case 'active':
            return 'bg-success';
        case 'paused':
            return 'bg-warning';
        case 'completed':
            return 'bg-info';
        case 'failed':
            return 'bg-danger';
        case 'at_risk':
            return 'bg-warning';
        default:
            return 'bg-secondary';
    }
}

/**
 * Format metric name
 */
function formatMetricName(key) {
    // Convert snake_case to Title Case
    return key.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Format metric value
 */
function formatMetricValue(key, value) {
    // Format based on metric type
    if (typeof value === 'number') {
        if (key.includes('rate') || key.includes('percentage')) {
            return (value * 100).toFixed(1) + '%';
        } else if (key.includes('revenue') || key.includes('cost') || key.includes('spend')) {
            return '$' + value.toFixed(2);
        } else {
            return value.toLocaleString();
        }
    }
    return value;
}

/**
 * Format date and time
 */
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Initialize the orchestrator dashboard when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the orchestrator tab
    if (document.getElementById('orchestrator')) {
        initializeOrchestratorDashboard();
    }
});

// Make functions globally accessible
window.viewCycleDetails = viewCycleDetails;
window.advanceCyclePhase = advanceCyclePhase;
window.viewGoalDetails = viewGoalDetails;
window.createCampaignForGoal = createCampaignForGoal;
window.viewCampaignDetails = viewCampaignDetails;
window.updateCampaignStatus = updateCampaignStatus;
window.refreshCycles = refreshCycles;
window.refreshGoals = refreshGoals;
window.refreshCampaigns = refreshCampaigns;
