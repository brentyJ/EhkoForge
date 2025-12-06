/**
 * EhkoForge ReCog UI v1.0
 * Recursive Cognition Engine interface
 * Session 26 - Phase 5
 */

const RecogUI = {
    // State
    isOpen: false,
    isProcessing: false,
    pendingOps: [],
    currentTab: 'queue',
    
    // DOM Elements
    elements: {},
    
    // ==========================================================================
    // INITIALIZATION
    // ==========================================================================
    
    init() {
        this.cacheElements();
        this.bindEvents();
        this.loadInitialState();
        console.log('[ReCog] UI initialised');
    },
    
    cacheElements() {
        this.elements = {
            // Header
            recogBtn: document.getElementById('recog-btn'),
            recogBadge: document.getElementById('recog-badge'),
            
            // Drawer
            overlay: document.getElementById('recog-overlay'),
            drawer: document.querySelector('.recog-drawer'),
            closeBtn: document.getElementById('recog-close'),
            
            // Tabs
            tabs: document.querySelectorAll('.recog-tab'),
            panes: document.querySelectorAll('.recog-pane'),
            
            // Queue pane
            statusDot: document.getElementById('recog-status-dot'),
            statusText: document.getElementById('recog-status-text'),
            statHot: document.getElementById('stat-hot'),
            statInsights: document.getElementById('stat-insights'),
            statPatterns: document.getElementById('stat-patterns'),
            checkBtn: document.getElementById('recog-check-btn'),
            pendingList: document.getElementById('pending-list'),
            processBtn: document.getElementById('recog-process-btn'),
            confirmedCount: document.getElementById('confirmed-count'),
            
            // Reports pane
            reportsList: document.getElementById('reports-list'),
            
            // Progression pane
            progressionStage: document.getElementById('progression-stage'),
            progressionEntered: document.getElementById('progression-entered'),
            pillarsList: document.getElementById('pillars-list'),
            coreMemoryCount: document.getElementById('core-memory-count'),
            
            // Processing overlay
            processingOverlay: document.getElementById('processing-overlay'),
            processingText: document.getElementById('processing-text'),
            processingSubtext: document.getElementById('processing-subtext'),
            
            // Toast
            toast: document.getElementById('recog-toast'),
        };
    },
    
    bindEvents() {
        // Header button
        this.elements.recogBtn?.addEventListener('click', () => this.toggle());
        
        // Close drawer
        this.elements.overlay?.addEventListener('click', (e) => {
            if (e.target === this.elements.overlay) this.close();
        });
        this.elements.closeBtn?.addEventListener('click', () => this.close());
        
        // Tabs
        this.elements.tabs.forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });
        
        // Check button
        this.elements.checkBtn?.addEventListener('click', () => this.checkAndQueue());
        
        // Process button
        this.elements.processBtn?.addEventListener('click', () => this.processConfirmed());
        
        // Keyboard
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) this.close();
        });
    },
    
    // ==========================================================================
    // DRAWER CONTROL
    // ==========================================================================
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    },
    
    open() {
        this.isOpen = true;
        this.elements.overlay?.classList.add('active');
        this.loadStatus();
        this.loadPending();
    },
    
    close() {
        this.isOpen = false;
        this.elements.overlay?.classList.remove('active');
    },
    
    switchTab(tabName) {
        this.currentTab = tabName;
        
        // Update tab states
        this.elements.tabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        // Update pane states
        this.elements.panes.forEach(pane => {
            pane.classList.toggle('active', pane.id === `recog-pane-${tabName}`);
        });
        
        // Load tab-specific data
        if (tabName === 'reports') this.loadReports();
        if (tabName === 'progression') this.loadProgression();
    },
    
    // ==========================================================================
    // API CALLS
    // ==========================================================================
    
    async loadInitialState() {
        try {
            const response = await fetch('/api/recog/status');
            const data = await response.json();
            
            if (data.success) {
                this.updateHeaderBadge(data.queue?.pending || 0);
            }
        } catch (error) {
            console.error('[ReCog] Failed to load initial state:', error);
        }
    },
    
    async loadStatus() {
        try {
            const response = await fetch('/api/recog/status');
            const data = await response.json();
            
            if (data.success) {
                this.updateStatusUI(data);
            }
        } catch (error) {
            console.error('[ReCog] Failed to load status:', error);
            this.showError('Failed to load ReCog status');
        }
    },
    
    async loadPending() {
        try {
            const response = await fetch('/api/recog/pending');
            const data = await response.json();
            
            if (data.success) {
                this.pendingOps = data.pending || [];
                this.renderPendingList();
                this.updateHeaderBadge(data.count || 0);
                this.updateProcessButton();
            }
        } catch (error) {
            console.error('[ReCog] Failed to load pending:', error);
        }
    },
    
    async checkAndQueue() {
        const btn = this.elements.checkBtn;
        if (!btn) return;
        
        btn.disabled = true;
        btn.textContent = 'Checking...';
        
        try {
            const response = await fetch('/api/recog/check', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                await this.loadPending();
                await this.loadStatus();
                
                if (data.count > 0) {
                    this.showToast('success', `Queued ${data.count} operation(s)`);
                } else {
                    this.showToast('success', 'No new operations to queue');
                }
            }
        } catch (error) {
            console.error('[ReCog] Check failed:', error);
            this.showError('Failed to check for operations');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Check Now';
        }
    },
    
    async confirmOperation(opId) {
        try {
            const response = await fetch(`/api/recog/confirm/${opId}`, { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                await this.loadPending();
                this.showToast('success', 'Operation confirmed');
            } else {
                this.showError(data.error || 'Failed to confirm');
            }
        } catch (error) {
            console.error('[ReCog] Confirm failed:', error);
            this.showError('Failed to confirm operation');
        }
    },
    
    async cancelOperation(opId) {
        try {
            const response = await fetch(`/api/recog/cancel/${opId}`, { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                await this.loadPending();
                this.showToast('success', 'Operation cancelled');
            } else {
                this.showError(data.error || 'Failed to cancel');
            }
        } catch (error) {
            console.error('[ReCog] Cancel failed:', error);
            this.showError('Failed to cancel operation');
        }
    },
    
    async processConfirmed() {
        const confirmedOps = this.pendingOps.filter(op => op.status === 'ready');
        if (confirmedOps.length === 0) {
            this.showToast('error', 'No confirmed operations to process');
            return;
        }
        
        this.isProcessing = true;
        this.showProcessingOverlay('Processing insights...', `${confirmedOps.length} operation(s)`);
        
        try {
            const response = await fetch('/api/recog/process', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                const results = data.results || [];
                const successful = results.filter(r => r.success).length;
                const failed = results.filter(r => !r.success).length;
                
                let message = `Processed ${successful} operation(s)`;
                if (failed > 0) message += `, ${failed} failed`;
                
                this.showToast(failed === 0 ? 'success' : 'error', message);
                
                await this.loadPending();
                await this.loadStatus();
            } else {
                this.showError(data.error || 'Processing failed');
            }
        } catch (error) {
            console.error('[ReCog] Process failed:', error);
            this.showError('Failed to process operations');
        } finally {
            this.isProcessing = false;
            this.hideProcessingOverlay();
        }
    },
    
    async loadReports() {
        try {
            const response = await fetch('/api/recog/reports');
            const data = await response.json();
            
            if (data.success) {
                this.renderReports(data.reports || []);
            }
        } catch (error) {
            console.error('[ReCog] Failed to load reports:', error);
        }
    },
    
    async loadProgression() {
        try {
            const response = await fetch('/api/recog/progression');
            const data = await response.json();
            
            if (data.success) {
                this.renderProgression(data);
            }
        } catch (error) {
            console.error('[ReCog] Failed to load progression:', error);
        }
    },
    
    // ==========================================================================
    // UI UPDATES
    // ==========================================================================
    
    updateStatusUI(data) {
        // Status indicator
        const dot = this.elements.statusDot;
        const text = this.elements.statusText;
        
        if (dot && text) {
            if (data.llm_available) {
                dot.classList.remove('processing');
                dot.classList.add('online');
                text.textContent = 'Online';
            } else {
                dot.classList.remove('online', 'processing');
                text.textContent = 'No LLM';
            }
        }
        
        // Stats
        if (this.elements.statHot) {
            this.elements.statHot.textContent = data.hot_sessions || 0;
        }
        if (this.elements.statInsights) {
            this.elements.statInsights.textContent = data.pending_insights || 0;
        }
        if (this.elements.statPatterns) {
            this.elements.statPatterns.textContent = data.patterns || 0;
        }
    },
    
    updateHeaderBadge(count) {
        const badge = this.elements.recogBadge;
        const btn = this.elements.recogBtn;
        
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        }
        
        if (btn) {
            btn.classList.toggle('has-pending', count > 0);
        }
    },
    
    updateProcessButton() {
        const btn = this.elements.processBtn;
        const countEl = this.elements.confirmedCount;
        
        const confirmed = this.pendingOps.filter(op => op.status === 'ready').length;
        
        if (countEl) {
            countEl.textContent = confirmed;
        }
        
        if (btn) {
            btn.disabled = confirmed === 0 || this.isProcessing;
        }
    },
    
    renderPendingList() {
        const list = this.elements.pendingList;
        if (!list) return;
        
        if (this.pendingOps.length === 0) {
            list.innerHTML = `
                <div class="pending-empty">
                    <div class="pending-empty-icon">○</div>
                    <div>No pending operations</div>
                    <div style="font-size: 0.75rem; margin-top: 4px;">Click "Check Now" to scan for new content</div>
                </div>
            `;
            return;
        }
        
        list.innerHTML = this.pendingOps.map(op => this.renderOperationCard(op)).join('');
        
        // Bind action buttons
        list.querySelectorAll('.op-btn-confirm').forEach(btn => {
            btn.addEventListener('click', () => this.confirmOperation(btn.dataset.opId));
        });
        
        list.querySelectorAll('.op-btn-cancel').forEach(btn => {
            btn.addEventListener('click', () => this.cancelOperation(btn.dataset.opId));
        });
    },
    
    renderOperationCard(op) {
        const icons = {
            'extract': '📥',
            'correlate': '🔗',
            'synthesise': '✨',
            'full_sweep': '🔄'
        };
        
        const tierLabels = {
            'extract': 'Tier 1',
            'correlate': 'Tier 2',
            'synthesise': 'Tier 3',
            'full_sweep': 'All Tiers'
        };
        
        const isConfirmed = op.status === 'ready';
        const isProcessing = op.status === 'processing';
        
        return `
            <div class="operation-card ${isProcessing ? 'processing' : ''}">
                <div class="operation-header">
                    <div class="operation-type">
                        <div class="operation-icon">${icons[op.operation_type] || '⚙'}</div>
                        <div>
                            <div class="operation-name">${this.formatOpType(op.operation_type)}</div>
                            <div class="operation-tier">${tierLabels[op.operation_type] || ''}</div>
                        </div>
                    </div>
                    <div class="operation-cost">
                        <span class="operation-cost-icon">◆</span>
                        <span>${op.estimated_mana}</span>
                    </div>
                </div>
                <div class="operation-description">${op.description}</div>
                <div class="operation-meta">
                    ~${op.estimated_tokens?.toLocaleString() || '?'} tokens • 
                    ${op.source_count} source(s) • 
                    Queued ${this.formatTime(op.queued_at)}
                </div>
                <div class="operation-actions">
                    ${isConfirmed ? `
                        <button class="op-btn op-btn-cancel" data-op-id="${op.id}">Unconfirm</button>
                        <button class="op-btn op-btn-confirm" disabled>✓ Confirmed</button>
                    ` : isProcessing ? `
                        <button class="op-btn op-btn-confirm" disabled>Processing...</button>
                    ` : `
                        <button class="op-btn op-btn-cancel" data-op-id="${op.id}">Cancel</button>
                        <button class="op-btn op-btn-confirm" data-op-id="${op.id}">Confirm</button>
                    `}
                </div>
            </div>
        `;
    },
    
    renderReports(reports) {
        const list = this.elements.reportsList;
        if (!list) return;
        
        if (reports.length === 0) {
            list.innerHTML = `
                <div class="reports-empty">
                    <p>No ReCog reports yet.</p>
                    <p style="font-size: 0.8rem; margin-top: 8px;">Reports are generated after Tier 3 synthesis completes.</p>
                </div>
            `;
            return;
        }
        
        list.innerHTML = reports.map(report => `
            <div class="report-card">
                <div class="report-header">
                    <span class="report-type">${report.report_type}</span>
                    <span class="report-date">${this.formatDate(report.created_at)}</span>
                </div>
                <div class="report-content">
                    <div class="report-summary">${report.summary || 'No summary available'}</div>
                    <div class="report-stats">
                        <div class="report-stat">
                            <span class="report-stat-value">${report.insights_count}</span> insights
                        </div>
                        <div class="report-stat">
                            <span class="report-stat-value">${report.patterns_count}</span> patterns
                        </div>
                        <div class="report-stat">
                            <span class="report-stat-value">${report.syntheses_count}</span> syntheses
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    },
    
    renderProgression(data) {
        // Stage
        if (this.elements.progressionStage) {
            this.elements.progressionStage.textContent = data.stage || 'nascent';
            this.elements.progressionStage.className = `progression-stage ${data.stage || 'nascent'}`;
        }
        
        // Entered date
        if (this.elements.progressionEntered && data.stage_entered_at) {
            this.elements.progressionEntered.textContent = `Since ${this.formatDate(data.stage_entered_at)}`;
        }
        
        // Pillars
        const pillars = data.pillars || {};
        const pillarNames = ['web', 'thread', 'mirror', 'compass', 'anchor', 'flame'];
        
        if (this.elements.pillarsList) {
            this.elements.pillarsList.innerHTML = pillarNames.map(name => {
                const status = pillars[name] || 'empty';
                const statusIcon = status === 'populated' ? '✓' : status === 'seeded' ? '◐' : '○';
                return `
                    <div class="pillar-item">
                        <div class="pillar-status ${status}">${statusIcon}</div>
                        <span class="pillar-name">${this.capitalize(name)}</span>
                    </div>
                `;
            }).join('');
        }
        
        // Core memory count
        if (this.elements.coreMemoryCount) {
            this.elements.coreMemoryCount.textContent = data.core_memory_count || 0;
        }
    },
    
    // ==========================================================================
    // PROCESSING OVERLAY
    // ==========================================================================
    
    showProcessingOverlay(text, subtext) {
        const overlay = this.elements.processingOverlay;
        if (!overlay) return;
        
        if (this.elements.processingText) {
            this.elements.processingText.textContent = text;
        }
        if (this.elements.processingSubtext) {
            this.elements.processingSubtext.textContent = subtext;
        }
        
        overlay.classList.add('active');
    },
    
    hideProcessingOverlay() {
        const overlay = this.elements.processingOverlay;
        if (overlay) {
            overlay.classList.remove('active');
        }
    },
    
    // ==========================================================================
    // TOAST NOTIFICATIONS
    // ==========================================================================
    
    showToast(type, message, details = '') {
        const toast = this.elements.toast;
        if (!toast) return;
        
        const icon = type === 'success' ? '✓' : '✗';
        
        toast.className = `recog-toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${icon}</span>
                <div>
                    <div class="toast-message">${message}</div>
                    ${details ? `<div class="toast-details">${details}</div>` : ''}
                </div>
            </div>
        `;
        
        toast.classList.add('visible');
        
        setTimeout(() => {
            toast.classList.remove('visible');
        }, 3000);
    },
    
    showError(message) {
        this.showToast('error', message);
    },
    
    // ==========================================================================
    // UTILITIES
    // ==========================================================================
    
    formatOpType(type) {
        const labels = {
            'extract': 'Extract Insights',
            'correlate': 'Find Patterns',
            'synthesise': 'Synthesise',
            'full_sweep': 'Full Sweep'
        };
        return labels[type] || type;
    },
    
    formatTime(isoString) {
        if (!isoString) return 'unknown';
        const date = new Date(isoString);
        const now = new Date();
        const diff = (now - date) / 1000;
        
        if (diff < 60) return 'just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return `${Math.floor(diff / 86400)}d ago`;
    },
    
    formatDate(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        return date.toLocaleDateString('en-AU', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    },
    
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
};

// Initialize when DOM ready
document.addEventListener('DOMContentLoaded', () => {
    RecogUI.init();
});

// Export for console debugging
window.RecogUI = RecogUI;
