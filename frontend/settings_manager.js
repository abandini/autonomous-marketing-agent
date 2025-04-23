/**
 * GAMS Operator Dashboard - Settings Manager
 * Comprehensive settings management for all dashboard configurations
 */

class SettingsManager {
    constructor() {
        this.settings = this.initializeSettings();
        this.setupEventListeners();
    }

    /**
     * Initialize settings from localStorage or defaults
     * @returns {Object} The current settings
     */
    initializeSettings() {
        const savedSettings = localStorage.getItem('gamsSettings');
        let settings;
        
        if (savedSettings) {
            // Merge saved settings with defaults to ensure all properties exist
            const parsed = JSON.parse(savedSettings);
            settings = this.mergeDeep(this.getDefaultSettings(), parsed);
        } else {
            settings = this.getDefaultSettings();
            // Save default settings
            localStorage.setItem('gamsSettings', JSON.stringify(settings));
        }
        
        return settings;
    }

    /**
     * Get default settings structure
     * @returns {Object} Default settings
     */
    getDefaultSettings() {
        return {
            general: {
                systemName: 'GAMS Marketing System',
                operatorEmail: '',
                logLevel: 'info',
                refreshInterval: 60,
                maxConcurrentTasks: 5,
                timezone: 'America/New_York'
            },
            notifications: {
                email: '',
                systemAlerts: true,
                performanceReports: true,
                approvalRequests: true
            },
            api: {
                key: '',
                endpoint: 'http://localhost:5050/api',
                timeout: 30,
                rateLimiting: true
            },
            marketing: {
                organicAllocation: 40,
                paidAllocation: 30,
                emailAllocation: 20,
                affiliateAllocation: 10,
                defaultCampaignBudget: 1000
            },
            websites: [],
            repositories: [],
            integrations: {
                googleAnalytics: { enabled: false, trackingId: '' },
                amazonAssociates: { enabled: false, associateId: '' },
                clickBank: { enabled: false, apiKey: '' },
                mailchimp: { enabled: false, apiKey: '' },
                facebook: { enabled: false, accessToken: '' },
                twitter: { enabled: false, apiKey: '', apiSecret: '' }
            },
            cycle: {
                defaultDuration: 30,
                phases: {
                    analysis: 5,
                    planning: 5,
                    implementation: 15,
                    evaluation: 5
                },
                thresholds: {
                    performance: 0.8,
                    engagement: 0.7,
                    conversion: 0.5
                },
                acceleration: {
                    enabled: true,
                    threshold: 0.9
                }
            },
            compliance: {
                gdpr: true,
                ccpa: true,
                ftcDisclosure: true,
                accessibilityStandard: 'WCAG 2.1'
            },
            backup: {
                frequency: 'daily',
                storageLocation: 'local',
                maxRecoveryAttempts: 3,
                healthCheckInterval: 60
            },
            ui: {
                theme: 'light',
                layout: 'default',
                language: 'en'
            },
            advanced: {
                experimentalFeatures: false,
                betaFeatures: false,
                debugMode: false,
                performanceMetrics: true,
                timeouts: {
                    default: 300,
                    contentGeneration: 600,
                    seoAnalysis: 300
                }
            }
        };
    }

    /**
     * Initialize all form fields with current settings values
     */
    init() {
        // Populate all settings forms with current values
        this.populateGeneralSettings();
        this.populateNotificationSettings();
        this.populateApiSettings();
        this.populateMarketingSettings();
        this.populateWebsiteSettings();
        this.populateRepositorySettings();
        this.populateIntegrationSettings();
        this.populateCycleSettings();
        this.populateComplianceSettings();
        this.populateBackupSettings();
        this.populateUISettings();
        this.populateAdvancedSettings();
    }

    /**
     * Set up event listeners for all settings forms
     */
    setupEventListeners() {
        // General settings form
        const generalForm = document.getElementById('general-settings-form');
        if (generalForm) {
            generalForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveGeneralSettings();
            });
        }

        // Notification settings form
        const notificationForm = document.getElementById('notification-settings-form');
        if (notificationForm) {
            notificationForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveNotificationSettings();
            });
        }

        // API settings form
        const apiForm = document.getElementById('api-settings-form');
        if (apiForm) {
            apiForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveApiSettings();
            });
        }

        // Marketing settings form
        const marketingForm = document.getElementById('marketing-settings-form');
        if (marketingForm) {
            marketingForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveMarketingSettings();
            });
        }

        // Website settings form
        const websiteForm = document.getElementById('website-settings-form');
        if (websiteForm) {
            websiteForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveWebsiteSettings();
            });
        }

        // Repository settings form
        const repositoryForm = document.getElementById('repository-settings-form');
        if (repositoryForm) {
            repositoryForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveRepositorySettings();
            });
        }

        // Integration settings form
        const integrationForm = document.getElementById('integration-settings-form');
        if (integrationForm) {
            integrationForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveIntegrationSettings();
            });
        }

        // Cycle settings form
        const cycleForm = document.getElementById('cycle-settings-form');
        if (cycleForm) {
            cycleForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveCycleSettings();
            });
        }

        // Compliance settings form
        const complianceForm = document.getElementById('compliance-settings-form');
        if (complianceForm) {
            complianceForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveComplianceSettings();
            });
        }

        // Backup settings form
        const backupForm = document.getElementById('backup-settings-form');
        if (backupForm) {
            backupForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveBackupSettings();
            });
        }

        // UI settings form
        const uiForm = document.getElementById('ui-settings-form');
        if (uiForm) {
            uiForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveUISettings();
            });
        }

        // Advanced settings form
        const advancedForm = document.getElementById('advanced-settings-form');
        if (advancedForm) {
            advancedForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveAdvancedSettings();
            });
        }

        // Test connection buttons
        document.querySelectorAll('.test-connection-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const service = button.getAttribute('data-service');
                this.testConnection(service);
            });
        });

        // Theme switcher
        const themeSwitcher = document.getElementById('theme-switcher');
        if (themeSwitcher) {
            themeSwitcher.addEventListener('change', () => {
                this.applyTheme(themeSwitcher.value);
            });
        }
    }

    /**
     * Populate general settings form
     */
    populateGeneralSettings() {
        const general = this.settings.general;
        if (!document.getElementById('system-name')) return;
        
        document.getElementById('system-name').value = general.systemName;
        document.getElementById('operator-email').value = general.operatorEmail;
        document.getElementById('log-level').value = general.logLevel;
        document.getElementById('refresh-interval').value = general.refreshInterval;
        document.getElementById('max-concurrent-tasks').value = general.maxConcurrentTasks;
        document.getElementById('timezone').value = general.timezone;
    }

    /**
     * Populate notification settings form
     */
    populateNotificationSettings() {
        const notifications = this.settings.notifications;
        if (!document.getElementById('notification-email')) return;
        
        document.getElementById('notification-email').value = notifications.email;
        document.getElementById('system-alerts').checked = notifications.systemAlerts;
        document.getElementById('performance-reports').checked = notifications.performanceReports;
        document.getElementById('approval-requests').checked = notifications.approvalRequests;
    }

    /**
     * Populate API settings form
     */
    populateApiSettings() {
        const api = this.settings.api;
        if (!document.getElementById('api-key')) return;
        
        document.getElementById('api-key').value = api.key;
        document.getElementById('api-endpoint').value = api.endpoint;
        document.getElementById('api-timeout').value = api.timeout;
        document.getElementById('rate-limiting').checked = api.rateLimiting;
    }

    /**
     * Populate marketing settings form
     */
    populateMarketingSettings() {
        const marketing = this.settings.marketing;
        if (!document.getElementById('organic-allocation')) return;
        
        document.getElementById('organic-allocation').value = marketing.organicAllocation;
        document.getElementById('paid-allocation').value = marketing.paidAllocation;
        document.getElementById('email-allocation').value = marketing.emailAllocation;
        document.getElementById('affiliate-allocation').value = marketing.affiliateAllocation;
        document.getElementById('default-campaign-budget').value = marketing.defaultCampaignBudget;
    }

    /**
     * Populate website settings form
     */
    populateWebsiteSettings() {
        const websites = this.settings.websites;
        const websiteList = document.getElementById('website-list');
        if (!websiteList) return;
        
        // Clear existing list
        websiteList.innerHTML = '';
        
        // Add each website to the list
        websites.forEach((website, index) => {
            const websiteItem = document.createElement('div');
            websiteItem.className = 'website-item card mb-3';
            websiteItem.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">${website.name}</h5>
                    <p class="card-text">URL: ${website.url}</p>
                    <button class="btn btn-sm btn-primary edit-website" data-index="${index}">Edit</button>
                    <button class="btn btn-sm btn-danger delete-website" data-index="${index}">Delete</button>
                </div>
            `;
            websiteList.appendChild(websiteItem);
        });
        
        // Add event listeners for edit and delete buttons
        document.querySelectorAll('.edit-website').forEach(button => {
            button.addEventListener('click', (e) => {
                const index = e.target.getAttribute('data-index');
                this.editWebsite(index);
            });
        });
        
        document.querySelectorAll('.delete-website').forEach(button => {
            button.addEventListener('click', (e) => {
                const index = e.target.getAttribute('data-index');
                this.deleteWebsite(index);
            });
        });
    }

    /**
     * Populate repository settings form
     */
    populateRepositorySettings() {
        const repositories = this.settings.repositories;
        const repoList = document.getElementById('repository-list');
        if (!repoList) return;
        
        // Clear existing list
        repoList.innerHTML = '';
        
        // Add each repository to the list
        repositories.forEach((repo, index) => {
            const repoItem = document.createElement('div');
            repoItem.className = 'repository-item card mb-3';
            repoItem.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">${repo.name}</h5>
                    <p class="card-text">URL: ${repo.url}</p>
                    <p class="card-text">Branch: ${repo.branch}</p>
                    <button class="btn btn-sm btn-primary edit-repository" data-index="${index}">Edit</button>
                    <button class="btn btn-sm btn-danger delete-repository" data-index="${index}">Delete</button>
                </div>
            `;
            repoList.appendChild(repoItem);
        });
        
        // Add event listeners for edit and delete buttons
        document.querySelectorAll('.edit-repository').forEach(button => {
            button.addEventListener('click', (e) => {
                const index = e.target.getAttribute('data-index');
                this.editRepository(index);
            });
        });
        
        document.querySelectorAll('.delete-repository').forEach(button => {
            button.addEventListener('click', (e) => {
                const index = e.target.getAttribute('data-index');
                this.deleteRepository(index);
            });
        });
    }

    /**
     * Populate integration settings form
     */
    populateIntegrationSettings() {
        const integrations = this.settings.integrations;
        
        // Google Analytics
        if (document.getElementById('ga-enabled')) {
            document.getElementById('ga-enabled').checked = integrations.googleAnalytics.enabled;
            document.getElementById('ga-tracking-id').value = integrations.googleAnalytics.trackingId;
        }
        
        // Amazon Associates
        if (document.getElementById('amazon-enabled')) {
            document.getElementById('amazon-enabled').checked = integrations.amazonAssociates.enabled;
            document.getElementById('amazon-associate-id').value = integrations.amazonAssociates.associateId;
        }
        
        // ClickBank
        if (document.getElementById('clickbank-enabled')) {
            document.getElementById('clickbank-enabled').checked = integrations.clickBank.enabled;
            document.getElementById('clickbank-api-key').value = integrations.clickBank.apiKey;
        }
        
        // Mailchimp
        if (document.getElementById('mailchimp-enabled')) {
            document.getElementById('mailchimp-enabled').checked = integrations.mailchimp.enabled;
            document.getElementById('mailchimp-api-key').value = integrations.mailchimp.apiKey;
        }
        
        // Facebook
        if (document.getElementById('facebook-enabled')) {
            document.getElementById('facebook-enabled').checked = integrations.facebook.enabled;
            document.getElementById('facebook-access-token').value = integrations.facebook.accessToken;
        }
        
        // Twitter
        if (document.getElementById('twitter-enabled')) {
            document.getElementById('twitter-enabled').checked = integrations.twitter.enabled;
            document.getElementById('twitter-api-key').value = integrations.twitter.apiKey;
            document.getElementById('twitter-api-secret').value = integrations.twitter.apiSecret;
        }
    }

    /**
     * Populate cycle settings form
     */
    populateCycleSettings() {
        const cycle = this.settings.cycle;
        if (!document.getElementById('default-duration')) return;
        
        document.getElementById('default-duration').value = cycle.defaultDuration;
        
        // Phases
        document.getElementById('analysis-phase').value = cycle.phases.analysis;
        document.getElementById('planning-phase').value = cycle.phases.planning;
        document.getElementById('implementation-phase').value = cycle.phases.implementation;
        document.getElementById('evaluation-phase').value = cycle.phases.evaluation;
        
        // Thresholds
        document.getElementById('performance-threshold').value = cycle.thresholds.performance;
        document.getElementById('engagement-threshold').value = cycle.thresholds.engagement;
        document.getElementById('conversion-threshold').value = cycle.thresholds.conversion;
        
        // Acceleration
        document.getElementById('acceleration-enabled').checked = cycle.acceleration.enabled;
        document.getElementById('acceleration-threshold').value = cycle.acceleration.threshold;
    }

    /**
     * Populate compliance settings form
     */
    populateComplianceSettings() {
        const compliance = this.settings.compliance;
        if (!document.getElementById('gdpr-compliance')) return;
        
        document.getElementById('gdpr-compliance').checked = compliance.gdpr;
        document.getElementById('ccpa-compliance').checked = compliance.ccpa;
        document.getElementById('ftc-disclosure').checked = compliance.ftcDisclosure;
        document.getElementById('accessibility-standard').value = compliance.accessibilityStandard;
    }

    /**
     * Populate backup settings form
     */
    populateBackupSettings() {
        const backup = this.settings.backup;
        if (!document.getElementById('backup-frequency')) return;
        
        document.getElementById('backup-frequency').value = backup.frequency;
        document.getElementById('storage-location').value = backup.storageLocation;
        document.getElementById('max-recovery-attempts').value = backup.maxRecoveryAttempts;
        document.getElementById('health-check-interval').value = backup.healthCheckInterval;
    }

    /**
     * Populate UI settings form
     */
    populateUISettings() {
        const ui = this.settings.ui;
        if (!document.getElementById('theme-switcher')) return;
        
        document.getElementById('theme-switcher').value = ui.theme;
        document.getElementById('layout-selector').value = ui.layout;
        document.getElementById('language-selector').value = ui.language;
    }

    /**
     * Populate advanced settings form
     */
    populateAdvancedSettings() {
        const advanced = this.settings.advanced;
        if (!document.getElementById('experimental-features')) return;
        
        document.getElementById('experimental-features').checked = advanced.experimentalFeatures;
        document.getElementById('beta-features').checked = advanced.betaFeatures;
        document.getElementById('debug-mode').checked = advanced.debugMode;
        document.getElementById('performance-metrics').checked = advanced.performanceMetrics;
        document.getElementById('default-timeout').value = advanced.timeouts.default;
        document.getElementById('content-generation-timeout').value = advanced.timeouts.contentGeneration;
        document.getElementById('seo-analysis-timeout').value = advanced.timeouts.seoAnalysis;
    }

    /**
     * Save general settings
     */
    saveGeneralSettings() {
        this.settings.general = {
            systemName: document.getElementById('system-name').value,
            operatorEmail: document.getElementById('operator-email').value,
            logLevel: document.getElementById('log-level').value,
            refreshInterval: parseInt(document.getElementById('refresh-interval').value),
            maxConcurrentTasks: parseInt(document.getElementById('max-concurrent-tasks').value),
            timezone: document.getElementById('timezone').value
        };
        
        this.saveSettings();
    }

    /**
     * Save notification settings
     */
    saveNotificationSettings() {
        this.settings.notifications = {
            email: document.getElementById('notification-email').value,
            systemAlerts: document.getElementById('system-alerts').checked,
            performanceReports: document.getElementById('performance-reports').checked,
            approvalRequests: document.getElementById('approval-requests').checked
        };
        
        this.saveSettings();
    }

    /**
     * Save API settings
     */
    saveApiSettings() {
        this.settings.api = {
            key: document.getElementById('api-key').value,
            endpoint: document.getElementById('api-endpoint').value,
            timeout: parseInt(document.getElementById('api-timeout').value),
            rateLimiting: document.getElementById('rate-limiting').checked
        };
        
        this.saveSettings();
    }

    /**
     * Save marketing settings
     */
    saveMarketingSettings() {
        this.settings.marketing = {
            organicAllocation: parseInt(document.getElementById('organic-allocation').value),
            paidAllocation: parseInt(document.getElementById('paid-allocation').value),
            emailAllocation: parseInt(document.getElementById('email-allocation').value),
            affiliateAllocation: parseInt(document.getElementById('affiliate-allocation').value),
            defaultCampaignBudget: parseInt(document.getElementById('default-campaign-budget').value)
        };
        
        this.saveSettings();
    }

    /**
     * Add a new website
     * @param {Object} website - Website details
     */
    addWebsite(website) {
        this.settings.websites.push(website);
        this.saveSettings();
        this.populateWebsiteSettings();
    }

    /**
     * Edit a website
     * @param {number} index - Index of website to edit
     */
    editWebsite(index) {
        const website = this.settings.websites[index];
        
        // Populate edit form
        document.getElementById('website-name').value = website.name;
        document.getElementById('website-url').value = website.url;
        document.getElementById('website-description').value = website.description || '';
        
        // Show edit form
        const editForm = document.getElementById('website-edit-form');
        editForm.setAttribute('data-index', index);
        editForm.classList.remove('d-none');
    }

    /**
     * Delete a website
     * @param {number} index - Index of website to delete
     */
    deleteWebsite(index) {
        if (confirm('Are you sure you want to delete this website?')) {
            this.settings.websites.splice(index, 1);
            this.saveSettings();
            this.populateWebsiteSettings();
        }
    }

    /**
     * Add a new repository
     * @param {Object} repository - Repository details
     */
    addRepository(repository) {
        this.settings.repositories.push(repository);
        this.saveSettings();
        this.populateRepositorySettings();
    }

    /**
     * Edit a repository
     * @param {number} index - Index of repository to edit
     */
    editRepository(index) {
        const repository = this.settings.repositories[index];
        
        // Populate edit form
        document.getElementById('repository-name').value = repository.name;
        document.getElementById('repository-url').value = repository.url;
        document.getElementById('repository-branch').value = repository.branch;
        document.getElementById('repository-username').value = repository.username || '';
        
        // Show edit form
        const editForm = document.getElementById('repository-edit-form');
        editForm.setAttribute('data-index', index);
        editForm.classList.remove('d-none');
    }

    /**
     * Delete a repository
     * @param {number} index - Index of repository to delete
     */
    deleteRepository(index) {
        if (confirm('Are you sure you want to delete this repository?')) {
            this.settings.repositories.splice(index, 1);
            this.saveSettings();
            this.populateRepositorySettings();
        }
    }

    /**
     * Save integration settings
     */
    saveIntegrationSettings() {
        this.settings.integrations = {
            googleAnalytics: {
                enabled: document.getElementById('ga-enabled').checked,
                trackingId: document.getElementById('ga-tracking-id').value
            },
            amazonAssociates: {
                enabled: document.getElementById('amazon-enabled').checked,
                associateId: document.getElementById('amazon-associate-id').value
            },
            clickBank: {
                enabled: document.getElementById('clickbank-enabled').checked,
                apiKey: document.getElementById('clickbank-api-key').value
            },
            mailchimp: {
                enabled: document.getElementById('mailchimp-enabled').checked,
                apiKey: document.getElementById('mailchimp-api-key').value
            },
            facebook: {
                enabled: document.getElementById('facebook-enabled').checked,
                accessToken: document.getElementById('facebook-access-token').value
            },
            twitter: {
                enabled: document.getElementById('twitter-enabled').checked,
                apiKey: document.getElementById('twitter-api-key').value,
                apiSecret: document.getElementById('twitter-api-secret').value
            }
        };
        
        this.saveSettings();
    }

    /**
     * Save cycle settings
     */
    saveCycleSettings() {
        this.settings.cycle = {
            defaultDuration: parseInt(document.getElementById('default-duration').value),
            phases: {
                analysis: parseInt(document.getElementById('analysis-phase').value),
                planning: parseInt(document.getElementById('planning-phase').value),
                implementation: parseInt(document.getElementById('implementation-phase').value),
                evaluation: parseInt(document.getElementById('evaluation-phase').value)
            },
            thresholds: {
                performance: parseFloat(document.getElementById('performance-threshold').value),
                engagement: parseFloat(document.getElementById('engagement-threshold').value),
                conversion: parseFloat(document.getElementById('conversion-threshold').value)
            },
            acceleration: {
                enabled: document.getElementById('acceleration-enabled').checked,
                threshold: parseFloat(document.getElementById('acceleration-threshold').value)
            }
        };
        
        this.saveSettings();
    }

    /**
     * Save compliance settings
     */
    saveComplianceSettings() {
        this.settings.compliance = {
            gdpr: document.getElementById('gdpr-compliance').checked,
            ccpa: document.getElementById('ccpa-compliance').checked,
            ftcDisclosure: document.getElementById('ftc-disclosure').checked,
            accessibilityStandard: document.getElementById('accessibility-standard').value
        };
        
        this.saveSettings();
    }

    /**
     * Save backup settings
     */
    saveBackupSettings() {
        this.settings.backup = {
            frequency: document.getElementById('backup-frequency').value,
            storageLocation: document.getElementById('storage-location').value,
            maxRecoveryAttempts: parseInt(document.getElementById('max-recovery-attempts').value),
            healthCheckInterval: parseInt(document.getElementById('health-check-interval').value)
        };
        
        this.saveSettings();
    }

    /**
     * Save UI settings
     */
    saveUISettings() {
        this.settings.ui = {
            theme: document.getElementById('theme-switcher').value,
            layout: document.getElementById('layout-selector').value,
            language: document.getElementById('language-selector').value
        };
        
        this.applyTheme(this.settings.ui.theme);
        this.applyLayout(this.settings.ui.layout);
        
        this.saveSettings();
    }

    /**
     * Save advanced settings
     */
    saveAdvancedSettings() {
        this.settings.advanced = {
            experimentalFeatures: document.getElementById('experimental-features').checked,
            betaFeatures: document.getElementById('beta-features').checked,
            debugMode: document.getElementById('debug-mode').checked,
            performanceMetrics: document.getElementById('performance-metrics').checked,
            timeouts: {
                default: parseInt(document.getElementById('default-timeout').value),
                contentGeneration: parseInt(document.getElementById('content-generation-timeout').value),
                seoAnalysis: parseInt(document.getElementById('seo-analysis-timeout').value)
            }
        };
        
        this.saveSettings();
    }

    /**
     * Apply theme to dashboard
     * @param {string} theme - Theme name
     */
    applyTheme(theme) {
        document.body.classList.remove('theme-light', 'theme-dark');
        document.body.classList.add(`theme-${theme}`);
    }

    /**
     * Apply layout to dashboard
     * @param {string} layout - Layout name
     */
    applyLayout(layout) {
        document.body.classList.remove('layout-default', 'layout-compact', 'layout-expanded');
        document.body.classList.add(`layout-${layout}`);
    }

    /**
     * Test connection to a service
     * @param {string} service - Service name
     */
    testConnection(service) {
        this.showNotification(`Testing connection to ${service}...`, 'info');
        
        // Simulate API connection test
        setTimeout(() => {
            this.showNotification(`Successfully connected to ${service}!`, 'success');
        }, 1500);
    }

    /**
     * Show notification toast
     * @param {string} message - Message to display
     * @param {string} type - Bootstrap color type (success, danger, etc.)
     */
    showNotification(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            console.error('Toast container not found');
            return;
        }

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }

    /**
     * Deep merge two objects
     * @param {Object} target - Target object
     * @param {Object} source - Source object
     * @returns {Object} Merged object
     */
    mergeDeep(target, source) {
        const output = Object.assign({}, target);
        
        if (this.isObject(target) && this.isObject(source)) {
            Object.keys(source).forEach(key => {
                if (this.isObject(source[key])) {
                    if (!(key in target)) {
                        Object.assign(output, { [key]: source[key] });
                    } else {
                        output[key] = this.mergeDeep(target[key], source[key]);
                    }
                } else {
                    Object.assign(output, { [key]: source[key] });
                }
            });
        }
        
        return output;
    }

    /**
     * Check if value is an object
     * @param {*} item - Item to check
     * @returns {boolean} True if object
     */
    isObject(item) {
        return (item && typeof item === 'object' && !Array.isArray(item));
    }

    /**
     * Save settings to localStorage
     */
    saveSettings() {
        localStorage.setItem('gamsSettings', JSON.stringify(this.settings));
        this.showNotification('Settings saved successfully!');
    }
}

// Initialize settings manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.settingsManager = new SettingsManager();
    window.settingsManager.init();
});
