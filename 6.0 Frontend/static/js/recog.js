/**
 * EhkoForge ReCog UI v2.1
 * Recursive Cognition Engine interface
 * Session 37 - Fixed conclusions [object Object] bug
 */

const RecogUI = {
    // State
    isOpen: false,
    isProcessing: false,
    pendingOps: [],
    currentTab: 'queue',
    
    // Insights state
    insights: [],
    insightsTotal: 0,
    insightsOffset: 0,
    insightsLimit: 20,
    selectedInsight: null,
    
    // Patterns state
    patterns: [],
    selectedPattern: null,
    
    // DOM Elements
    elements: {},
    
    // ==========================================================================
    // INITIALIZATION
    // ==========================================================================
    
    init() {
        this.cacheElements();
        this.bindEvents();
        this.loadInitialState();
        console.log('[ReCog] UI v2.0 initialised');
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
            
            // Insights pane
            insightsList: document.getElementById('insights-list'),
            insightsDetail: document.getElementById('insights-detail'),
            insightsSearch: document.getElementById('insights-search'),
            insightsFilter: document.getElementById('insights-filter'),
            insightsLoadMore: document.getElementById('insights-load-more'),
            
            // Reports pane
            reportsList: document.getElementById('reports-list'),
            reportDetail: document.getElementById('report-detail'),
            
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
        
        // Insights search
        this.elements.insightsSearch?.addEventListener('input', 
            this.debounce(() => this.loadInsights(true), 300)
        );
        
        // Insights filter
        this.elements.insightsFilter?.addEventListener('change', () => this.loadInsights(true));
        
        // Load more insights
        this.elements.insightsLoadMore?.addEventListener('click', () => this.loadMoreInsights());
        
        // Keyboard
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                if (this.selectedInsight) {
                    this.closeInsightDetail();
                } else if (this.selectedPattern) {
                    this.closePatternDetail();
                } else {
                    this.close();
                }
            }
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
        this.selectedInsight = null;
        this.selectedPattern = null;
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
        if (tabName === 'insights') this.loadInsights(true);
        if (tabName === 'reports') this.loadReports();
        if (tabName === 'progression') this.loadProgression();
    },
    
    // ==========================================================================
    // API CALLS - QUEUE
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
    
    // ==========================================================================
    // API CALLS - INSIGHTS
    // ==========================================================================
    
    async loadInsights(reset = false) {
        if (reset) {
            this.insightsOffset = 0;
            this.insights = [];
        }
        
        const search = this.elements.insightsSearch?.value || '';
        const filter = this.elements.insightsFilter?.value || 'all';
        
        let url = `/api/recog/insights?limit=${this.insightsLimit}&offset=${this.insightsOffset}`;
        
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (filter === 'flagged') url += '&flagged=true';
        if (filter === 'unreviewed') url += '&reviewed=false';
        if (filter === 'rejected') url += '&rejected=true';
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                if (reset) {
                    this.insights = data.insights;
                } else {
                    this.insights = [...this.insights, ...data.insights];
                }
                this.insightsTotal = data.total;
                this.renderInsightsList();
            }
        } catch (error) {
            console.error('[ReCog] Failed to load insights:', error);
            this.showError('Failed to load insights');
        }
    },
    
    async loadMoreInsights() {
        this.insightsOffset += this.insightsLimit;
        await this.loadInsights(false);
    },
    
    async loadInsightDetail(insightId) {
        try {
            const response = await fetch(`/api/recog/insights/${insightId}`);
            const data = await response.json();
            
            if (data.success) {
                this.selectedInsight = data.insight;
                this.renderInsightDetail();
            } else {
                this.showError(data.error || 'Failed to load insight');
            }
        } catch (error) {
            console.error('[ReCog] Failed to load insight detail:', error);
            this.showError('Failed to load insight details');
        }
    },
    
    async toggleInsightFlag(insightId) {
        try {
            const response = await fetch(`/api/recog/insights/${insightId}/flag`, { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                // Update local state
                const insight = this.insights.find(i => i.id === insightId);
                if (insight) insight.flagged = data.flagged;
                if (this.selectedInsight?.id === insightId) {
                    this.selectedInsight.flagged = data.flagged;
                }
                
                this.renderInsightsList();
                if (this.selectedInsight) this.renderInsightDetail();
                
                this.showToast('success', data.flagged ? 'Insight flagged' : 'Flag removed');
            }
        } catch (error) {
            console.error('[ReCog] Failed to toggle flag:', error);
            this.showError('Failed to update flag');
        }
    },
    
    async saveInsightContext(insightId, context) {
        try {
            const response = await fetch(`/api/recog/insights/${insightId}/context`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ context })
            });
            const data = await response.json();
            
            if (data.success) {
                if (this.selectedInsight?.id === insightId) {
                    this.selectedInsight.user_context = context;
                }
                this.showToast('success', 'Context saved');
            }
        } catch (error) {
            console.error('[ReCog] Failed to save context:', error);
            this.showError('Failed to save context');
        }
    },
    
    async rejectInsight(insightId, reject = true) {
        try {
            const response = await fetch(`/api/recog/insights/${insightId}/reject`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reject })
            });
            const data = await response.json();
            
            if (data.success) {
                // Remove from list or update
                if (reject) {
                    this.insights = this.insights.filter(i => i.id !== insightId);
                }
                this.renderInsightsList();
                this.closeInsightDetail();
                this.showToast('success', reject ? 'Insight rejected' : 'Insight restored');
            }
        } catch (error) {
            console.error('[ReCog] Failed to reject insight:', error);
            this.showError('Failed to reject insight');
        }
    },
    
    // ==========================================================================
    // API CALLS - PATTERNS
    // ==========================================================================
    
    async loadPatterns() {
        try {
            const response = await fetch('/api/recog/patterns?limit=50');
            const data = await response.json();
            
            if (data.success) {
                this.patterns = data.patterns;
            }
        } catch (error) {
            console.error('[ReCog] Failed to load patterns:', error);
        }
    },
    
    async loadPatternDetail(patternId) {
        try {
            const response = await fetch(`/api/recog/patterns/${patternId}`);
            const data = await response.json();
            
            if (data.success) {
                this.selectedPattern = data.pattern;
                this.renderPatternDetail();
            }
        } catch (error) {
            console.error('[ReCog] Failed to load pattern:', error);
        }
    },
    
    // ==========================================================================
    // API CALLS - REPORTS
    // ==========================================================================
    
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
    
    async loadReportDetail(reportId) {
        try {
            const response = await fetch(`/api/recog/reports/${reportId}/details`);
            const data = await response.json();
            
            if (data.success) {
                this.renderReportDetail(data.report);
            }
        } catch (error) {
            console.error('[ReCog] Failed to load report details:', error);
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
    // UI UPDATES - QUEUE
    // ==========================================================================
    
    updateStatusUI(data) {
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
        
        if (countEl) countEl.textContent = confirmed;
        if (btn) btn.disabled = confirmed === 0 || this.isProcessing;
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
        
        list.querySelectorAll('.op-btn-confirm').forEach(btn => {
            btn.addEventListener('click', () => this.confirmOperation(btn.dataset.opId));
        });
        
        list.querySelectorAll('.op-btn-cancel').forEach(btn => {
            btn.addEventListener('click', () => this.cancelOperation(btn.dataset.opId));
        });
    },
    
    renderOperationCard(op) {
        const icons = { 'extract': '📥', 'correlate': '🔗', 'synthesise': '✨', 'full_sweep': '🔄' };
        const tierLabels = { 'extract': 'Tier 1', 'correlate': 'Tier 2', 'synthesise': 'Tier 3', 'full_sweep': 'All Tiers' };
        
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
    
    // ==========================================================================
    // UI UPDATES - INSIGHTS
    // ==========================================================================
    
    renderInsightsList() {
        const list = this.elements.insightsList;
        if (!list) return;
        
        if (this.insights.length === 0) {
            list.innerHTML = `
                <div class="insights-empty">
                    <div class="insights-empty-icon">💡</div>
                    <div>No insights found</div>
                    <div style="font-size: 0.75rem; margin-top: 4px;">Process some content to extract insights</div>
                </div>
            `;
            this.updateLoadMoreButton();
            return;
        }
        
        list.innerHTML = this.insights.map(insight => this.renderInsightCard(insight)).join('');
        
        // Bind click handlers
        list.querySelectorAll('.insight-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.insight-flag-btn')) {
                    this.loadInsightDetail(card.dataset.insightId);
                }
            });
        });
        
        list.querySelectorAll('.insight-flag-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleInsightFlag(btn.dataset.insightId);
            });
        });
        
        this.updateLoadMoreButton();
    },
    
    renderInsightCard(insight) {
        const tierClass = insight.significance_tier || 'copper';
        const themes = (insight.themes || []).slice(0, 3);
        
        return `
            <div class="insight-card ${tierClass}" data-insight-id="${insight.id}">
                <div class="insight-header">
                    <div class="insight-tier-badge ${tierClass}">${tierClass}</div>
                    <button class="insight-flag-btn ${insight.flagged ? 'flagged' : ''}" 
                            data-insight-id="${insight.id}" 
                            title="${insight.flagged ? 'Remove flag' : 'Flag as important'}">
                        ${insight.flagged ? '★' : '☆'}
                    </button>
                </div>
                <div class="insight-summary">${this.escapeHtml(insight.summary)}</div>
                <div class="insight-meta">
                    ${themes.length > 0 ? `
                        <div class="insight-themes">
                            ${themes.map(t => `<span class="insight-theme">${t}</span>`).join('')}
                        </div>
                    ` : ''}
                    <div class="insight-stats">
                        <span title="Sources">${insight.source_count || 0} src</span>
                        ${insight.pattern_count > 0 ? `<span title="Patterns">→ ${insight.pattern_count} pat</span>` : ''}
                        ${!insight.reviewed ? '<span class="insight-new">NEW</span>' : ''}
                    </div>
                </div>
            </div>
        `;
    },
    
    renderInsightDetail() {
        const detail = this.elements.insightsDetail;
        if (!detail || !this.selectedInsight) return;
        
        const insight = this.selectedInsight;
        const tierClass = insight.significance_tier || 'copper';
        
        detail.innerHTML = `
            <div class="insight-detail-panel">
                <div class="detail-header">
                    <button class="detail-back-btn" title="Back to list">←</button>
                    <div class="insight-tier-badge ${tierClass}">${tierClass}</div>
                    <div class="detail-actions">
                        <button class="detail-flag-btn ${insight.flagged ? 'flagged' : ''}" title="Flag">
                            ${insight.flagged ? '★' : '☆'}
                        </button>
                        <button class="detail-reject-btn" title="Reject insight">✕</button>
                    </div>
                </div>
                
                <div class="detail-summary">${this.escapeHtml(insight.summary)}</div>
                
                <div class="detail-section">
                    <div class="detail-section-title">Significance</div>
                    <div class="detail-significance">
                        <div class="significance-bar">
                            <div class="significance-fill ${tierClass}" style="width: ${(insight.significance || 0) * 100}%"></div>
                        </div>
                        <span>${((insight.significance || 0) * 100).toFixed(0)}%</span>
                    </div>
                </div>
                
                ${insight.themes?.length > 0 ? `
                    <div class="detail-section">
                        <div class="detail-section-title">Themes</div>
                        <div class="detail-themes">
                            ${insight.themes.map(t => `<span class="detail-theme">${t}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div class="detail-section">
                    <div class="detail-section-title">Your Context</div>
                    <div class="detail-context-input">
                        <textarea id="insight-context-input" 
                                  placeholder="Add context the AI might have missed..."
                                  rows="3">${this.escapeHtml(insight.user_context || '')}</textarea>
                        <button class="context-save-btn">Save Context</button>
                    </div>
                </div>
                
                ${insight.sources?.length > 0 ? `
                    <div class="detail-section">
                        <div class="detail-section-title">Sources (${insight.sources.length})</div>
                        <div class="detail-sources">
                            ${insight.sources.map(src => `
                                <div class="detail-source">
                                    <div class="source-title">${this.escapeHtml(src.title)}</div>
                                    <div class="source-type">${src.type}</div>
                                    ${src.excerpt ? `<div class="source-excerpt">"${this.escapeHtml(src.excerpt)}"</div>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${insight.linked_patterns?.length > 0 ? `
                    <div class="detail-section">
                        <div class="detail-section-title">Contributes to Patterns</div>
                        <div class="detail-patterns">
                            ${insight.linked_patterns.map(pat => `
                                <div class="detail-pattern" data-pattern-id="${pat.id}">
                                    <span class="pattern-type">${pat.pattern_type}</span>
                                    <span class="pattern-summary">${this.escapeHtml(pat.summary)}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div class="detail-footer">
                    <span>Created ${this.formatDate(insight.created_at)}</span>
                    ${insight.reviewed_at ? `<span>Reviewed ${this.formatDate(insight.reviewed_at)}</span>` : ''}
                </div>
            </div>
        `;
        
        detail.classList.add('active');
        
        // Bind detail panel events
        detail.querySelector('.detail-back-btn')?.addEventListener('click', () => this.closeInsightDetail());
        detail.querySelector('.detail-flag-btn')?.addEventListener('click', () => this.toggleInsightFlag(insight.id));
        detail.querySelector('.detail-reject-btn')?.addEventListener('click', () => {
            if (confirm('Reject this insight? It will be hidden from the list.')) {
                this.rejectInsight(insight.id);
            }
        });
        detail.querySelector('.context-save-btn')?.addEventListener('click', () => {
            const ctx = detail.querySelector('#insight-context-input')?.value || '';
            this.saveInsightContext(insight.id, ctx);
        });
        detail.querySelectorAll('.detail-pattern')?.forEach(el => {
            el.addEventListener('click', () => this.loadPatternDetail(el.dataset.patternId));
        });
    },
    
    closeInsightDetail() {
        this.selectedInsight = null;
        this.elements.insightsDetail?.classList.remove('active');
    },
    
    updateLoadMoreButton() {
        const btn = this.elements.insightsLoadMore;
        if (!btn) return;
        
        const hasMore = this.insights.length < this.insightsTotal;
        btn.style.display = hasMore ? 'block' : 'none';
        btn.textContent = `Load More (${this.insightsTotal - this.insights.length} remaining)`;
    },
    
    // ==========================================================================
    // UI UPDATES - PATTERNS
    // ==========================================================================
    
    renderPatternDetail() {
        const detail = this.elements.insightsDetail;  // Reuse same panel
        if (!detail || !this.selectedPattern) return;
        
        const pattern = this.selectedPattern;
        
        detail.innerHTML = `
            <div class="pattern-detail-panel">
                <div class="detail-header">
                    <button class="detail-back-btn" title="Back">←</button>
                    <span class="pattern-type-badge">${pattern.pattern_type}</span>
                </div>
                
                <div class="detail-summary">${this.escapeHtml(pattern.summary)}</div>
                
                <div class="detail-section">
                    <div class="detail-section-title">Strength</div>
                    <div class="detail-significance">
                        <div class="significance-bar">
                            <div class="significance-fill" style="width: ${(pattern.strength || 0) * 100}%"></div>
                        </div>
                        <span>${((pattern.strength || 0) * 100).toFixed(0)}%</span>
                    </div>
                </div>
                
                ${pattern.insights?.length > 0 ? `
                    <div class="detail-section">
                        <div class="detail-section-title">Contributing Insights (${pattern.insights.length})</div>
                        <div class="detail-insights-list">
                            ${pattern.insights.map(ins => `
                                <div class="mini-insight-card" data-insight-id="${ins.id}">
                                    <span class="mini-insight-flag">${ins.flagged ? '★' : ''}</span>
                                    <span class="mini-insight-summary">${this.escapeHtml(ins.summary)}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        detail.classList.add('active');
        
        detail.querySelector('.detail-back-btn')?.addEventListener('click', () => this.closePatternDetail());
        detail.querySelectorAll('.mini-insight-card')?.forEach(el => {
            el.addEventListener('click', () => this.loadInsightDetail(el.dataset.insightId));
        });
    },
    
    closePatternDetail() {
        this.selectedPattern = null;
        if (this.selectedInsight) {
            this.renderInsightDetail();
        } else {
            this.elements.insightsDetail?.classList.remove('active');
        }
    },
    
    // ==========================================================================
    // UI UPDATES - REPORTS
    // ==========================================================================
    
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
            <div class="report-card clickable" data-report-id="${report.id}">
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
                <div class="report-drill-hint">Click to explore →</div>
            </div>
        `).join('');
        
        // Bind click handlers
        list.querySelectorAll('.report-card').forEach(card => {
            card.addEventListener('click', () => this.loadReportDetail(card.dataset.reportId));
        });
    },
    
    renderReportDetail(report) {
        const detail = this.elements.reportDetail;
        if (!detail) return;
        
        detail.innerHTML = `
            <div class="report-detail-panel">
                <div class="detail-header">
                    <button class="detail-back-btn" title="Back to reports">←</button>
                    <span class="report-type">${report.report_type}</span>
                    <span class="report-date">${this.formatDate(report.created_at)}</span>
                </div>
                
                <div class="detail-summary">${this.escapeHtml(report.summary || '')}</div>
                
                ${report.conclusions?.length > 0 ? `
                    <div class="detail-section">
                        <div class="detail-section-title">Conclusions</div>
                        <ul class="report-conclusions">
                            ${report.conclusions.map(c => `
                                <li class="conclusion-item ${c.emerging ? 'emerging' : ''}">
                                    <span class="conclusion-type">${this.escapeHtml(c.type || 'insight')}</span>
                                    <span class="conclusion-summary">${this.escapeHtml(c.summary || '')}</span>
                                    ${c.significance ? `<span class="conclusion-significance">Significance: ${c.significance.toFixed(2)}</span>` : ''}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${report.syntheses?.length > 0 ? `
                    <div class="detail-section">
                        <div class="detail-section-title">Syntheses (${report.syntheses.length})</div>
                        <div class="report-syntheses">
                            ${report.syntheses.map(syn => `
                                <div class="synthesis-item">
                                    <span class="synthesis-type">${syn.layer_type}</span>
                                    <span class="synthesis-content">${this.escapeHtml(syn.content)}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${report.patterns?.length > 0 ? `
                    <div class="detail-section">
                        <div class="detail-section-title">Patterns (${report.patterns.length})</div>
                        <div class="report-patterns">
                            ${report.patterns.map(pat => `
                                <div class="mini-pattern-card" data-pattern-id="${pat.id}">
                                    <span class="pattern-type">${pat.pattern_type}</span>
                                    <span class="pattern-summary">${this.escapeHtml(pat.summary)}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${report.insights?.length > 0 ? `
                    <div class="detail-section">
                        <div class="detail-section-title">Insights (${report.insights.length})</div>
                        <div class="report-insights">
                            ${report.insights.slice(0, 10).map(ins => `
                                <div class="mini-insight-card" data-insight-id="${ins.id}">
                                    <span class="mini-insight-flag">${ins.flagged ? '★' : ''}</span>
                                    <span class="mini-insight-summary">${this.escapeHtml(ins.summary)}</span>
                                </div>
                            `).join('')}
                            ${report.insights.length > 10 ? `<div class="more-items">+${report.insights.length - 10} more</div>` : ''}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        detail.classList.add('active');
        
        detail.querySelector('.detail-back-btn')?.addEventListener('click', () => {
            detail.classList.remove('active');
        });
        
        detail.querySelectorAll('.mini-insight-card')?.forEach(el => {
            el.addEventListener('click', () => {
                this.switchTab('insights');
                this.loadInsightDetail(el.dataset.insightId);
            });
        });
        
        detail.querySelectorAll('.mini-pattern-card')?.forEach(el => {
            el.addEventListener('click', () => {
                this.switchTab('insights');
                this.loadPatternDetail(el.dataset.patternId);
            });
        });
    },
    
    // ==========================================================================
    // UI UPDATES - PROGRESSION
    // ==========================================================================
    
    renderProgression(data) {
        if (this.elements.progressionStage) {
            this.elements.progressionStage.textContent = (data.stage || 'nascent').toUpperCase();
            this.elements.progressionStage.className = `progression-stage ${data.stage || 'nascent'}`;
        }
        
        if (this.elements.progressionEntered && data.stage_entered_at) {
            this.elements.progressionEntered.textContent = `Since ${this.formatDate(data.stage_entered_at)}`;
        }
        
        const pillars = data.pillars || {};
        const pillarNames = ['web', 'thread', 'mirror', 'compass', 'anchor', 'flame'];
        
        if (this.elements.pillarsList) {
            this.elements.pillarsList.innerHTML = pillarNames.map(name => {
                const items = pillars[name] || [];
                const count = items.length;
                
                let status, statusIcon;
                if (count >= 3) {
                    status = 'populated';
                    statusIcon = '●';
                } else if (count > 0) {
                    status = 'seeded';
                    statusIcon = '◐';
                } else {
                    status = 'empty';
                    statusIcon = '○';
                }
                
                let contentPreview = '';
                if (count > 0) {
                    const firstItem = items[0].content || '';
                    const preview = firstItem.length > 60 ? firstItem.substring(0, 60) + '...' : firstItem;
                    contentPreview = `<div class="pillar-preview">${this.escapeHtml(preview)}</div>`;
                    if (count > 1) {
                        contentPreview += `<div class="pillar-more">+${count - 1} more</div>`;
                    }
                }
                
                return `
                    <div class="pillar-item ${status}" data-pillar="${name}">
                        <div class="pillar-header">
                            <div class="pillar-status">${statusIcon}</div>
                            <span class="pillar-name">${this.capitalize(name)}</span>
                            ${count > 0 ? `<span class="pillar-count">${count}</span>` : ''}
                        </div>
                        ${contentPreview}
                    </div>
                `;
            }).join('');
            
            this.elements.pillarsList.querySelectorAll('.pillar-item').forEach(item => {
                item.addEventListener('click', () => item.classList.toggle('expanded'));
            });
        }
        
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
        
        if (this.elements.processingText) this.elements.processingText.textContent = text;
        if (this.elements.processingSubtext) this.elements.processingSubtext.textContent = subtext;
        
        overlay.classList.add('active');
    },
    
    hideProcessingOverlay() {
        this.elements.processingOverlay?.classList.remove('active');
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
        setTimeout(() => toast.classList.remove('visible'), 3000);
    },
    
    showError(message) {
        this.showToast('error', message);
    },
    
    // ==========================================================================
    // UTILITIES
    // ==========================================================================
    
    formatOpType(type) {
        const labels = { 'extract': 'Extract Insights', 'correlate': 'Find Patterns', 'synthesise': 'Synthesise', 'full_sweep': 'Full Sweep' };
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
        return date.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' });
    },
    
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    debounce(fn, delay) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn.apply(this, args), delay);
        };
    }
};

// Initialize when DOM ready
document.addEventListener('DOMContentLoaded', () => RecogUI.init());

// Export for console debugging
window.RecogUI = RecogUI;
