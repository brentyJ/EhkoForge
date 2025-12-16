/**
 * EhkoForge Preflight UI v1.0
 * Context-aware content import with Tier 0 scanning
 * Session 34
 */

const PreflightUI = {
    // State
    sessionId: null,
    sessionData: null,
    isScanning: false,
    
    // DOM Elements
    elements: {},
    
    // ==========================================================================
    // INITIALIZATION
    // ==========================================================================
    
    init() {
        this.cacheElements();
        this.bindEvents();
        console.log('[Preflight] UI initialised');
    },
    
    cacheElements() {
        this.elements = {
            // Upload
            dropZone: document.getElementById('preflight-drop-zone'),
            fileInput: document.getElementById('preflight-file-input'),
            uploadSection: document.querySelector('.preflight-upload-section'),
            
            // Session
            sessionPanel: document.getElementById('preflight-session'),
            sessionType: document.getElementById('preflight-session-type'),
            sessionStatus: document.getElementById('preflight-session-status'),
            
            // Progress
            progressPanel: document.getElementById('preflight-progress'),
            progressFill: document.getElementById('preflight-progress-fill'),
            progressText: document.getElementById('preflight-progress-text'),
            
            // Summary
            summaryPanel: document.getElementById('preflight-summary'),
            itemCount: document.getElementById('pf-item-count'),
            wordCount: document.getElementById('pf-word-count'),
            entityCount: document.getElementById('pf-entity-count'),
            costEstimate: document.getElementById('pf-cost-estimate'),
            
            // Entities
            entitiesPanel: document.getElementById('preflight-entities'),
            unknownCount: document.getElementById('pf-unknown-count'),
            entitiesList: document.getElementById('preflight-entities-list'),
            
            // Filters
            filtersPanel: document.getElementById('preflight-filters'),
            filtersToggle: document.getElementById('pf-filters-toggle'),
            filtersContent: document.getElementById('pf-filters-content'),
            filterMinWords: document.getElementById('pf-filter-min-words'),
            filterDateAfter: document.getElementById('pf-filter-date-after'),
            filterKeywords: document.getElementById('pf-filter-keywords'),
            filterApplyBtn: document.getElementById('pf-filter-apply'),
            
            // Actions
            cancelBtn: document.getElementById('pf-cancel-btn'),
            confirmBtn: document.getElementById('pf-confirm-btn'),
            manaCost: document.getElementById('pf-mana-cost'),
            
            // Empty state
            emptyState: document.getElementById('preflight-empty'),
        };
    },
    
    bindEvents() {
        // File drop zone
        if (this.elements.dropZone) {
            this.elements.dropZone.addEventListener('click', () => {
                this.elements.fileInput?.click();
            });
            
            this.elements.dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                this.elements.dropZone.classList.add('dragover');
            });
            
            this.elements.dropZone.addEventListener('dragleave', () => {
                this.elements.dropZone.classList.remove('dragover');
            });
            
            this.elements.dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                this.elements.dropZone.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) this.handleFiles(files);
            });
        }
        
        // File input
        this.elements.fileInput?.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFiles(e.target.files);
            }
        });
        
        // Filters toggle
        this.elements.filtersToggle?.addEventListener('click', () => {
            const content = this.elements.filtersContent;
            const isOpen = content.style.display !== 'none';
            content.style.display = isOpen ? 'none' : 'block';
            this.elements.filtersToggle.textContent = isOpen ? '▼' : '▲';
        });
        
        // Filter apply
        this.elements.filterApplyBtn?.addEventListener('click', () => this.applyFilters());
        
        // Cancel
        this.elements.cancelBtn?.addEventListener('click', () => this.cancelSession());
        
        // Confirm
        this.elements.confirmBtn?.addEventListener('click', () => this.confirmSession());
    },
    
    // ==========================================================================
    // FILE HANDLING
    // ==========================================================================
    
    async handleFiles(files) {
        const file = files[0]; // Handle first file for now
        
        if (!file) return;
        
        console.log('[Preflight] Processing file:', file.name, file.type);
        
        // Determine file type
        let sessionType = 'document';
        if (file.name.endsWith('.json')) {
            sessionType = 'chatgpt_import';
        }
        
        // Show session panel
        this.showSessionPanel(sessionType);
        this.showProgress('Reading file...', 0);
        
        try {
            // Read file content
            const content = await this.readFile(file);
            
            // Create preflight session
            this.showProgress('Creating session...', 10);
            const session = await this.createSession(sessionType, [file.name]);
            this.sessionId = session.session_id;
            
            // Parse and add items
            if (sessionType === 'chatgpt_import') {
                await this.processChatGPTExport(content);
            } else {
                await this.processDocument(file.name, content);
            }
            
            // Scan session
            this.showProgress('Scanning content (FREE)...', 80);
            const scanResult = await this.scanSession();
            
            // Show results
            this.showResults(scanResult);
            
        } catch (error) {
            console.error('[Preflight] Error:', error);
            this.showError(error.message);
        }
    },
    
    readFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    },
    
    // ==========================================================================
    // CHATGPT EXPORT PARSING
    // ==========================================================================
    
    async processChatGPTExport(jsonContent) {
        let data;
        try {
            data = JSON.parse(jsonContent);
        } catch (e) {
            throw new Error('Invalid JSON file');
        }
        
        // ChatGPT export is an array of conversations
        if (!Array.isArray(data)) {
            throw new Error('Expected ChatGPT export format (array of conversations)');
        }
        
        const total = data.length;
        let processed = 0;
        
        for (const conversation of data) {
            // Extract conversation content
            const title = conversation.title || 'Untitled';
            const messages = this.extractMessages(conversation);
            
            if (messages.length === 0) continue;
            
            const content = messages.map(m => `${m.role}: ${m.content}`).join('\n\n');
            
            // Add to preflight session
            await this.addItem(
                'chatgpt_conversation',
                conversation.id || `conv-${processed}`,
                title,
                content
            );
            
            processed++;
            const progress = 10 + (processed / total * 70);
            this.showProgress(`Processing ${processed}/${total} conversations...`, progress);
        }
        
        this.elements.sessionStatus.textContent = `${processed} conversations`;
    },
    
    extractMessages(conversation) {
        const messages = [];
        
        // ChatGPT export structure: mapping -> {id: {message: {content: {parts: []}}}}
        if (conversation.mapping) {
            for (const nodeId in conversation.mapping) {
                const node = conversation.mapping[nodeId];
                if (node.message && node.message.content && node.message.content.parts) {
                    const role = node.message.author?.role || 'unknown';
                    const parts = node.message.content.parts;
                    const text = parts.filter(p => typeof p === 'string').join('\n');
                    
                    if (text.trim()) {
                        messages.push({ role, content: text });
                    }
                }
            }
        }
        
        return messages;
    },
    
    async processDocument(filename, content) {
        await this.addItem('document', filename, filename, content);
        this.elements.sessionStatus.textContent = '1 document';
    },
    
    // ==========================================================================
    // API CALLS
    // ==========================================================================
    
    async createSession(sessionType, sourceFiles) {
        const response = await fetch('/api/preflight/sessions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_type: sessionType, source_files: sourceFiles })
        });
        return response.json();
    },
    
    async addItem(sourceType, sourceId, title, content) {
        const response = await fetch(`/api/preflight/sessions/${this.sessionId}/items`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source_type: sourceType, source_id: sourceId, title, content })
        });
        return response.json();
    },
    
    async scanSession() {
        const response = await fetch(`/api/preflight/sessions/${this.sessionId}/scan`, {
            method: 'POST'
        });
        return response.json();
    },
    
    async applyFilters() {
        const filters = {
            min_words: parseInt(this.elements.filterMinWords?.value) || null,
            date_after: this.elements.filterDateAfter?.value || null,
            keywords: this.elements.filterKeywords?.value?.split(',').map(k => k.trim()).filter(Boolean) || null
        };
        
        this.showProgress('Applying filters...', 50);
        
        const response = await fetch(`/api/preflight/sessions/${this.sessionId}/filter`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(filters)
        });
        
        const result = await response.json();
        if (result.success) {
            this.showResults(result);
        }
    },
    
    async updateEntity(entityId, displayName, relationship) {
        const response = await fetch(`/api/entities/${entityId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                display_name: displayName,
                relationship: relationship,
                confirmed: true
            })
        });
        return response.json();
    },
    
    async confirmSession() {
        // TODO: Create ReCog operations from preflight items
        console.log('[Preflight] Confirming session', this.sessionId);
        
        // For now, just show toast
        if (window.RecogUI) {
            RecogUI.showToast('success', 'Session confirmed! ReCog operations created.');
        }
        
        this.cancelSession();
    },
    
    // ==========================================================================
    // UI UPDATES
    // ==========================================================================
    
    showSessionPanel(sessionType) {
        this.elements.uploadSection.style.display = 'none';
        this.elements.emptyState.style.display = 'none';
        this.elements.sessionPanel.style.display = 'block';
        
        const typeLabels = {
            'chatgpt_import': 'ChatGPT Import',
            'document': 'Document',
            'batch': 'Batch Import'
        };
        
        this.elements.sessionType.textContent = typeLabels[sessionType] || sessionType;
        this.elements.sessionStatus.textContent = 'Starting...';
    },
    
    showProgress(text, percent) {
        this.elements.progressPanel.style.display = 'block';
        this.elements.summaryPanel.style.display = 'none';
        this.elements.entitiesPanel.style.display = 'none';
        this.elements.filtersPanel.style.display = 'none';
        
        this.elements.progressText.textContent = text;
        this.elements.progressFill.style.width = `${percent}%`;
    },
    
    showResults(data) {
        this.elements.progressPanel.style.display = 'none';
        this.elements.summaryPanel.style.display = 'block';
        this.elements.filtersPanel.style.display = 'block';
        
        // Update summary stats
        this.elements.itemCount.textContent = data.item_count || 0;
        this.elements.wordCount.textContent = this.formatNumber(data.total_words || 0);
        this.elements.entityCount.textContent = data.total_entities || 0;
        this.elements.costEstimate.textContent = (data.estimated_cost_dollars || 0).toFixed(2);
        
        // Update mana cost (rough estimate: $1 ≈ 100 mana)
        const manaCost = Math.ceil((data.estimated_cost_dollars || 0) * 100);
        this.elements.manaCost.textContent = manaCost;
        
        // Show entities if any unknown
        const questions = data.questions || [];
        if (questions.length > 0) {
            this.elements.entitiesPanel.style.display = 'block';
            this.elements.unknownCount.textContent = `${questions.length} need identification`;
            this.renderEntityQuestions(questions);
        }
        
        // Enable confirm button
        this.elements.confirmBtn.disabled = false;
        this.elements.sessionStatus.textContent = 'Ready to process';
    },
    
    renderEntityQuestions(questions) {
        this.elements.entitiesList.innerHTML = questions.map(q => `
            <div class="entity-question" data-entity-id="${q.entity_id}">
                <div class="entity-info">
                    <span class="entity-type">${q.type}</span>
                    <span class="entity-value">${q.value}</span>
                </div>
                <div class="entity-inputs">
                    <input type="text" class="entity-name" placeholder="Name (e.g., Mum, David)">
                    <input type="text" class="entity-relationship" placeholder="Relationship">
                    <button class="entity-save-btn">✓</button>
                </div>
            </div>
        `).join('');
        
        // Bind save buttons
        this.elements.entitiesList.querySelectorAll('.entity-save-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const card = e.target.closest('.entity-question');
                const entityId = card.dataset.entityId;
                const name = card.querySelector('.entity-name').value;
                const relationship = card.querySelector('.entity-relationship').value;
                
                if (name) {
                    await this.updateEntity(entityId, name, relationship);
                    card.classList.add('saved');
                    btn.textContent = '✓';
                    btn.disabled = true;
                }
            });
        });
    },
    
    showError(message) {
        this.elements.progressPanel.style.display = 'none';
        this.elements.sessionStatus.textContent = 'Error';
        this.elements.sessionStatus.style.color = '#d97373';
        
        if (window.RecogUI) {
            RecogUI.showToast('error', message);
        }
    },
    
    cancelSession() {
        this.sessionId = null;
        this.sessionData = null;
        
        this.elements.sessionPanel.style.display = 'none';
        this.elements.uploadSection.style.display = 'block';
        this.elements.emptyState.style.display = 'block';
        
        // Reset all panels
        this.elements.progressPanel.style.display = 'none';
        this.elements.summaryPanel.style.display = 'none';
        this.elements.entitiesPanel.style.display = 'none';
        this.elements.filtersPanel.style.display = 'none';
        
        // Reset button
        this.elements.confirmBtn.disabled = true;
        this.elements.sessionStatus.style.color = '';
    },
    
    formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }
};

// Initialize when DOM ready
document.addEventListener('DOMContentLoaded', () => {
    PreflightUI.init();
});

// Export for debugging
window.PreflightUI = PreflightUI;
