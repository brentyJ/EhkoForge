/**
 * EhkoForge Tether Panel Web Component v1.0
 * 
 * Management panel for tether connections. Allows adding, removing,
 * and verifying API keys for LLM providers.
 * 
 * Usage:
 *   <ehko-tether-panel></ehko-tether-panel>
 * 
 * Methods:
 *   open(provider?) - Open panel, optionally focused on a provider
 *   close() - Close panel
 *   refresh() - Reload tether data from API
 * 
 * Events:
 *   tether-updated - Fired when any tether is modified
 *   panel-closed - Fired when panel is closed
 * 
 * @license AGPL-3.0
 */

class EhkoTetherPanel extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.tethers = [];
        this.providers = [];
        this.isOpen = false;
        this.focusedProvider = null;
    }

    connectedCallback() {
        this.render();
        this.loadData();
    }

    async loadData() {
        try {
            // Load providers
            const providersRes = await fetch('/api/tethers/providers');
            const providersData = await providersRes.json();
            if (providersData.success) {
                this.providers = providersData.providers;
            }

            // Load tethers
            const tethersRes = await fetch('/api/tethers');
            const tethersData = await tethersRes.json();
            if (tethersData.success) {
                this.tethers = tethersData.tethers;
            }

            this.render();
        } catch (err) {
            console.error('[TetherPanel] Load failed:', err);
        }
    }

    getTetherForProvider(providerKey) {
        return this.tethers.find(t => t.provider === providerKey);
    }

    getProviderIcon(providerKey) {
        const icons = {
            'claude': '◈',
            'openai': '◉',
            'gemini': '✧',
        };
        return icons[providerKey] || '◆';
    }

    getProviderColor(providerKey) {
        const colors = {
            'claude': '#d4a574',
            'openai': '#10a37f',
            'gemini': '#4285f4',
        };
        return colors[providerKey] || '#6B8CCE';
    }

    render() {
        const color = '#6B8CCE';

        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    font-family: 'JetBrains Mono', 'Fira Code', monospace;
                }

                .overlay {
                    display: ${this.isOpen ? 'flex' : 'none'};
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(8, 10, 14, 0.85);
                    z-index: 1000;
                    justify-content: center;
                    align-items: center;
                    backdrop-filter: blur(4px);
                }

                .panel {
                    background: #0d1117;
                    border: 1px solid #2d3748;
                    border-radius: 8px;
                    width: 90%;
                    max-width: 500px;
                    max-height: 80vh;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                    box-shadow: 0 0 40px rgba(0, 0, 0, 0.5);
                }

                .panel-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 16px 20px;
                    border-bottom: 1px solid #2d3748;
                    background: #161c28;
                }

                .panel-title {
                    font-size: 14px;
                    font-weight: 600;
                    color: #e2e8f0;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .panel-title-icon {
                    color: ${color};
                }

                .close-btn {
                    background: none;
                    border: none;
                    color: #718096;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 4px 8px;
                    transition: color 0.15s ease;
                }

                .close-btn:hover {
                    color: #e2e8f0;
                }

                .panel-body {
                    padding: 20px;
                    overflow-y: auto;
                    flex: 1;
                }

                .panel-intro {
                    font-size: 11px;
                    color: #718096;
                    margin-bottom: 20px;
                    line-height: 1.6;
                }

                .tether-list {
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }

                .tether-item {
                    background: #161c28;
                    border: 1px solid #2d3748;
                    border-radius: 6px;
                    padding: 16px;
                    transition: border-color 0.15s ease;
                }

                .tether-item:hover {
                    border-color: #4a5568;
                }

                .tether-item.connected {
                    border-color: var(--provider-color, #10a37f);
                    box-shadow: 0 0 8px var(--provider-glow, rgba(16, 163, 127, 0.2));
                }

                .tether-item-header {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    margin-bottom: 12px;
                }

                .provider-icon {
                    font-size: 20px;
                    width: 32px;
                    text-align: center;
                }

                .provider-info {
                    flex: 1;
                }

                .provider-name {
                    font-size: 13px;
                    font-weight: 600;
                    color: #e2e8f0;
                }

                .provider-status {
                    font-size: 10px;
                    color: #718096;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .provider-status.valid {
                    color: #10a37f;
                }

                .provider-status.invalid {
                    color: #e74c3c;
                }

                .provider-status.pending {
                    color: #f39c12;
                }

                .tether-form {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }

                .input-group {
                    display: flex;
                    gap: 8px;
                }

                .key-input {
                    flex: 1;
                    padding: 8px 12px;
                    background: #0d1117;
                    border: 1px solid #2d3748;
                    border-radius: 4px;
                    color: #e2e8f0;
                    font-family: inherit;
                    font-size: 11px;
                }

                .key-input:focus {
                    outline: none;
                    border-color: ${color};
                }

                .key-input::placeholder {
                    color: #4a5568;
                }

                .btn {
                    padding: 8px 16px;
                    border: 1px solid #2d3748;
                    border-radius: 4px;
                    font-family: inherit;
                    font-size: 11px;
                    cursor: pointer;
                    transition: all 0.15s ease;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                .btn-primary {
                    background: ${color};
                    border-color: ${color};
                    color: #080a0e;
                }

                .btn-primary:hover {
                    box-shadow: 0 0 12px rgba(107, 140, 206, 0.4);
                }

                .btn-secondary {
                    background: #161c28;
                    color: #e2e8f0;
                }

                .btn-secondary:hover {
                    background: #1a2332;
                    border-color: #4a5568;
                }

                .btn-danger {
                    background: #161c28;
                    border-color: #e74c3c44;
                    color: #e74c3c;
                }

                .btn-danger:hover {
                    background: #e74c3c;
                    border-color: #e74c3c;
                    color: #080a0e;
                }

                .btn-success {
                    background: #161c28;
                    border-color: #10a37f44;
                    color: #10a37f;
                }

                .btn-success:hover {
                    background: #10a37f;
                    border-color: #10a37f;
                    color: #080a0e;
                }

                .btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                .action-row {
                    display: flex;
                    gap: 8px;
                    margin-top: 8px;
                }

                .key-display {
                    font-size: 11px;
                    color: #718096;
                    padding: 8px 12px;
                    background: #0d1117;
                    border-radius: 4px;
                    font-family: monospace;
                }

                .message {
                    font-size: 10px;
                    padding: 8px;
                    border-radius: 4px;
                    margin-top: 8px;
                }

                .message.success {
                    background: #10a37f22;
                    color: #10a37f;
                    border: 1px solid #10a37f44;
                }

                .message.error {
                    background: #e74c3c22;
                    color: #e74c3c;
                    border: 1px solid #e74c3c44;
                }
            </style>

            <div class="overlay" id="overlay">
                <div class="panel">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span class="panel-title-icon">⟡</span>
                            Tether Management
                        </div>
                        <button class="close-btn" id="close-btn">✕</button>
                    </div>
                    <div class="panel-body">
                        <div class="panel-intro">
                            Tethers are direct conduits to LLM Sources. Unlike mana, tethers never 
                            deplete—they channel directly from the Source while connected.
                        </div>
                        <div class="tether-list">
                            ${this.providers.map(provider => this.renderProviderItem(provider)).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.bindEvents();
    }

    renderProviderItem(provider) {
        const tether = this.getTetherForProvider(provider.provider_key);
        const hasKey = tether && tether.has_key;
        const status = tether?.verification_status || 'none';
        const active = tether?.active === 1;
        const isConnected = hasKey && active && status === 'valid';
        const color = this.getProviderColor(provider.provider_key);
        const icon = this.getProviderIcon(provider.provider_key);

        let statusLabel = 'No key configured';
        let statusClass = '';
        if (hasKey) {
            statusLabel = status === 'valid' ? (active ? 'Connected' : 'Disconnected') 
                        : status === 'invalid' ? 'Invalid key'
                        : status === 'pending' ? 'Verification pending'
                        : 'Key saved';
            statusClass = status;
        }

        return `
            <div class="tether-item ${isConnected ? 'connected' : ''}" 
                 style="--provider-color: ${color}; --provider-glow: ${color}33;"
                 data-provider="${provider.provider_key}">
                <div class="tether-item-header">
                    <span class="provider-icon" style="color: ${color}">${icon}</span>
                    <div class="provider-info">
                        <div class="provider-name">${provider.display_name}</div>
                        <div class="provider-status ${statusClass}">${statusLabel}</div>
                    </div>
                </div>
                <div class="tether-form">
                    ${hasKey ? `
                        <div class="key-display">API Key: ****${tether.has_key ? '****' : ''}</div>
                        <div class="action-row">
                            <button class="btn btn-secondary verify-btn" data-provider="${provider.provider_key}">
                                Verify
                            </button>
                            <button class="btn ${active ? 'btn-secondary' : 'btn-success'} toggle-btn" 
                                    data-provider="${provider.provider_key}" data-active="${active}">
                                ${active ? 'Disconnect' : 'Connect'}
                            </button>
                            <button class="btn btn-danger remove-btn" data-provider="${provider.provider_key}">
                                Remove
                            </button>
                        </div>
                    ` : `
                        <div class="input-group">
                            <input type="password" 
                                   class="key-input" 
                                   id="key-${provider.provider_key}"
                                   placeholder="Enter ${provider.display_name} API key..."
                                   autocomplete="off">
                            <button class="btn btn-primary save-btn" data-provider="${provider.provider_key}">
                                Save
                            </button>
                        </div>
                    `}
                    <div class="message-container" data-provider="${provider.provider_key}"></div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // Close button
        const closeBtn = this.shadowRoot.getElementById('close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // Overlay click to close
        const overlay = this.shadowRoot.getElementById('overlay');
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) this.close();
            });
        }

        // Save buttons
        this.shadowRoot.querySelectorAll('.save-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleSave(e.target.dataset.provider));
        });

        // Verify buttons
        this.shadowRoot.querySelectorAll('.verify-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleVerify(e.target.dataset.provider));
        });

        // Toggle buttons
        this.shadowRoot.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const active = e.target.dataset.active === 'true';
                this.handleToggle(e.target.dataset.provider, !active);
            });
        });

        // Remove buttons
        this.shadowRoot.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleRemove(e.target.dataset.provider));
        });
    }

    showMessage(provider, message, type = 'success') {
        const container = this.shadowRoot.querySelector(`.message-container[data-provider="${provider}"]`);
        if (container) {
            container.innerHTML = `<div class="message ${type}">${message}</div>`;
            setTimeout(() => { container.innerHTML = ''; }, 3000);
        }
    }

    async handleSave(provider) {
        const input = this.shadowRoot.getElementById(`key-${provider}`);
        const apiKey = input?.value?.trim();
        
        if (!apiKey) {
            this.showMessage(provider, 'Please enter an API key', 'error');
            return;
        }

        try {
            const res = await fetch('/api/tethers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider, api_key: apiKey })
            });
            const data = await res.json();

            if (data.success) {
                this.showMessage(provider, 'Tether created! Verifying...', 'success');
                this.dispatchEvent(new CustomEvent('tether-updated', { bubbles: true }));
                
                // Auto-verify after save
                setTimeout(() => this.handleVerify(provider), 500);
                await this.loadData();
            } else {
                this.showMessage(provider, data.error || 'Save failed', 'error');
            }
        } catch (err) {
            this.showMessage(provider, 'Network error', 'error');
        }
    }

    async handleVerify(provider) {
        try {
            const res = await fetch(`/api/tethers/${provider}/verify`, { method: 'POST' });
            const data = await res.json();

            if (data.valid) {
                this.showMessage(provider, 'Tether verified! Connection established.', 'success');
            } else {
                this.showMessage(provider, data.message || 'Verification failed', 'error');
            }

            this.dispatchEvent(new CustomEvent('tether-updated', { bubbles: true }));
            await this.loadData();
        } catch (err) {
            this.showMessage(provider, 'Verification failed', 'error');
        }
    }

    async handleToggle(provider, active) {
        try {
            const res = await fetch(`/api/tethers/${provider}/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ active })
            });
            const data = await res.json();

            if (data.success) {
                this.showMessage(provider, active ? 'Tether connected' : 'Tether disconnected', 'success');
                this.dispatchEvent(new CustomEvent('tether-updated', { bubbles: true }));
                await this.loadData();
            } else {
                this.showMessage(provider, data.error || 'Toggle failed', 'error');
            }
        } catch (err) {
            this.showMessage(provider, 'Network error', 'error');
        }
    }

    async handleRemove(provider) {
        if (!confirm(`Remove ${provider} tether? This will delete the stored API key.`)) {
            return;
        }

        try {
            const res = await fetch(`/api/tethers/${provider}`, { method: 'DELETE' });
            const data = await res.json();

            if (data.success) {
                this.showMessage(provider, 'Tether removed', 'success');
                this.dispatchEvent(new CustomEvent('tether-updated', { bubbles: true }));
                await this.loadData();
            } else {
                this.showMessage(provider, data.error || 'Remove failed', 'error');
            }
        } catch (err) {
            this.showMessage(provider, 'Network error', 'error');
        }
    }

    // Public API
    open(provider = null) {
        console.log('[TetherPanel] Opening panel');
        this.focusedProvider = provider;
        this.isOpen = true;
        this.render();  // Re-render to show overlay
        this.loadData();
    }

    close() {
        this.isOpen = false;
        this.render();
        this.dispatchEvent(new CustomEvent('panel-closed', { bubbles: true }));
    }

    async refresh() {
        await this.loadData();
    }
}

customElements.define('ehko-tether-panel', EhkoTetherPanel);

if (typeof module !== 'undefined' && module.exports) {
    module.exports = EhkoTetherPanel;
}
