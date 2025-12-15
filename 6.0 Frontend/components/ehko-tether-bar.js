/**
 * EhkoForge Tether Bar Web Component v1.0
 * 
 * Displays tether connections to LLM Sources (BYOK conduits).
 * Unlike mana bars, tethers never deplete - they show connection status.
 * Always "full" when connected, representing an infinite conduit to the Source.
 * 
 * Usage:
 *   <ehko-tether-bar 
 *     provider="claude"
 *     status="valid"
 *     active="true">
 *   </ehko-tether-bar>
 * 
 * Attributes:
 *   provider - Provider key ('claude', 'openai', 'gemini')
 *   provider-name - Display name (auto-set if not provided)
 *   status - Verification status ('pending', 'valid', 'invalid', 'none')
 *   active - Whether tether is active (default: false)
 *   compact - Compact mode for smaller displays (default: false)
 * 
 * Events:
 *   tether-manage - Fired when manage button is clicked
 *   tether-toggle - Fired when toggle is requested
 *   tether-verify - Fired when verify is requested
 * 
 * @license AGPL-3.0
 */

class EhkoTetherBar extends HTMLElement {
    static get observedAttributes() {
        return ['provider', 'provider-name', 'status', 'active', 'compact'];
    }

    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (oldValue !== newValue && this.shadowRoot) {
            this.render();
        }
    }

    get provider() { return this.getAttribute('provider') || 'unknown'; }
    get providerName() { 
        return this.getAttribute('provider-name') || this.getDefaultProviderName(); 
    }
    get status() { return this.getAttribute('status') || 'none'; }
    get active() { return this.getAttribute('active') === 'true'; }
    get compact() { return this.hasAttribute('compact'); }

    get isConnected() { 
        return this.active && this.status === 'valid'; 
    }

    getDefaultProviderName() {
        const names = {
            'claude': 'Claude',
            'openai': 'OpenAI',
            'gemini': 'Gemini',
        };
        return names[this.provider] || this.provider;
    }

    getProviderIcon() {
        const icons = {
            'claude': '◈',  // Diamond with dot
            'openai': '◉',  // Circle with dot
            'gemini': '✧',  // Star
        };
        return icons[this.provider] || '◆';
    }

    getColors() {
        // Provider-specific colours
        const providerColors = {
            'claude': { main: '#d4a574', glow: 'rgba(212, 165, 116, 0.5)' },  // Warm amber
            'openai': { main: '#10a37f', glow: 'rgba(16, 163, 127, 0.5)' },   // OpenAI green
            'gemini': { main: '#4285f4', glow: 'rgba(66, 133, 244, 0.5)' },   // Google blue
        };
        
        const base = providerColors[this.provider] || { main: '#6B8CCE', glow: 'rgba(107, 140, 206, 0.5)' };
        
        // Modify based on status
        if (!this.active) {
            return { main: '#4a5568', glow: 'transparent' };  // Dim when inactive
        }
        if (this.status === 'invalid') {
            return { main: '#e74c3c', glow: 'rgba(231, 76, 60, 0.4)' };  // Red for invalid
        }
        if (this.status === 'pending') {
            return { main: '#f39c12', glow: 'rgba(243, 156, 18, 0.4)' };  // Yellow for pending
        }
        
        return base;
    }

    getStatusText() {
        if (!this.active) return 'Disconnected';
        switch (this.status) {
            case 'valid': return 'Connected';
            case 'invalid': return 'Invalid Key';
            case 'pending': return 'Verifying...';
            case 'none': return 'No Key';
            default: return this.status;
        }
    }

    render() {
        const colors = this.getColors();
        const icon = this.getProviderIcon();
        const fillWidth = this.isConnected ? 100 : 0;
        const statusText = this.getStatusText();

        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    width: 100%;
                    font-family: 'JetBrains Mono', 'Fira Code', monospace;
                }

                .tether-container {
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }

                .tether-header {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .tether-icon {
                    font-size: 14px;
                    color: ${colors.main};
                    text-shadow: ${this.isConnected ? `0 0 8px ${colors.glow}` : 'none'};
                    transition: all 0.3s ease;
                }

                .tether-info {
                    display: flex;
                    flex-direction: column;
                    flex: 1;
                }

                .tether-provider {
                    font-size: ${this.compact ? '11px' : '12px'};
                    font-weight: 600;
                    color: ${colors.main};
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                .tether-status {
                    font-size: 9px;
                    color: ${this.isConnected ? colors.main : '#718096'};
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .tether-actions {
                    display: flex;
                    gap: 4px;
                }

                .tether-btn {
                    padding: 2px 6px;
                    background: #161c28;
                    border: 1px solid rgba(107, 140, 206, 0.3);
                    color: #6B8CCE;
                    font-family: inherit;
                    font-size: 9px;
                    cursor: pointer;
                    transition: all 0.15s ease;
                    border-radius: 2px;
                }

                .tether-btn:hover {
                    background: ${colors.main};
                    color: #080a0e;
                    border-color: ${colors.main};
                    box-shadow: 0 0 8px ${colors.glow};
                }

                .tether-btn.toggle {
                    color: ${this.active ? '#10a37f' : '#718096'};
                    border-color: ${this.active ? 'rgba(16, 163, 127, 0.3)' : 'rgba(113, 128, 150, 0.3)'};
                }

                .tether-btn.toggle:hover {
                    background: ${this.active ? '#10a37f' : '#718096'};
                }

                .tether-track {
                    height: ${this.compact ? '4px' : '6px'};
                    background: #1a1d24;
                    border: 1px solid #2d3748;
                    border-radius: 3px;
                    overflow: hidden;
                    position: relative;
                }

                .tether-fill {
                    position: absolute;
                    top: 0;
                    left: 0;
                    height: 100%;
                    width: ${fillWidth}%;
                    background: linear-gradient(90deg, 
                        ${colors.main}cc,
                        ${colors.main}
                    );
                    border-radius: 2px;
                    transition: width 0.5s ease, background 0.3s ease;
                    ${this.isConnected ? `box-shadow: 0 0 12px ${colors.glow};` : ''}
                }

                /* Connected: Gentle pulse to show "always full" */
                ${this.isConnected ? `
                .tether-fill {
                    animation: connectedPulse 3s ease-in-out infinite;
                }
                
                .tether-icon {
                    animation: iconGlow 2s ease-in-out infinite;
                }
                
                @keyframes connectedPulse {
                    0%, 100% { 
                        opacity: 1; 
                        box-shadow: 0 0 12px ${colors.glow};
                    }
                    50% { 
                        opacity: 0.85; 
                        box-shadow: 0 0 20px ${colors.glow};
                    }
                }
                
                @keyframes iconGlow {
                    0%, 100% { text-shadow: 0 0 8px ${colors.glow}; }
                    50% { text-shadow: 0 0 16px ${colors.glow}, 0 0 24px ${colors.glow}; }
                }
                ` : ''}

                /* Pending: Animated verification */
                ${this.status === 'pending' ? `
                .tether-fill {
                    animation: pendingFlow 1.5s ease-in-out infinite;
                    width: 100%;
                    background: linear-gradient(90deg, 
                        transparent,
                        ${colors.main}88,
                        ${colors.main},
                        ${colors.main}88,
                        transparent
                    );
                    background-size: 200% 100%;
                }
                
                @keyframes pendingFlow {
                    0% { background-position: 100% 0; }
                    100% { background-position: -100% 0; }
                }
                ` : ''}

                /* Invalid: Warning pulse */
                ${this.status === 'invalid' ? `
                .tether-track {
                    border-color: ${colors.main}44;
                    animation: invalidPulse 1s ease-in-out infinite;
                }
                
                @keyframes invalidPulse {
                    0%, 100% { border-color: ${colors.main}44; }
                    50% { border-color: ${colors.main}; }
                }
                ` : ''}

                /* Shimmer effect for connected state */
                ${this.isConnected ? `
                .tether-fill::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(90deg,
                        transparent 0%,
                        rgba(255,255,255,0.15) 50%,
                        transparent 100%
                    );
                    animation: shimmer 3s ease-in-out infinite;
                }
                
                @keyframes shimmer {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }
                ` : ''}
            </style>

            <div class="tether-container">
                <div class="tether-header">
                    <span class="tether-icon">${icon}</span>
                    <div class="tether-info">
                        <span class="tether-provider">${this.providerName}</span>
                        <span class="tether-status">${statusText}</span>
                    </div>
                    <div class="tether-actions">
                        ${this.status !== 'none' ? `
                            <button class="tether-btn toggle" id="toggle-btn" title="${this.active ? 'Disconnect' : 'Connect'}">
                                ${this.active ? '◉' : '○'}
                            </button>
                        ` : ''}
                        <button class="tether-btn" id="manage-btn" title="Manage Tether">⚙</button>
                    </div>
                </div>
                <div class="tether-track">
                    <div class="tether-fill"></div>
                </div>
            </div>
        `;

        // Bind buttons
        const manageBtn = this.shadowRoot.getElementById('manage-btn');
        if (manageBtn) {
            manageBtn.addEventListener('click', () => {
                this.dispatchEvent(new CustomEvent('tether-manage', { 
                    bubbles: true,
                    detail: { provider: this.provider }
                }));
            });
        }

        const toggleBtn = this.shadowRoot.getElementById('toggle-btn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.dispatchEvent(new CustomEvent('tether-toggle', { 
                    bubbles: true,
                    detail: { provider: this.provider, active: !this.active }
                }));
            });
        }
    }

    // Public API
    setStatus(status, active = null) {
        this.setAttribute('status', status);
        if (active !== null) this.setAttribute('active', active);
    }

    connect() {
        this.setAttribute('active', 'true');
    }

    disconnect() {
        this.setAttribute('active', 'false');
    }
}

customElements.define('ehko-tether-bar', EhkoTetherBar);

if (typeof module !== 'undefined' && module.exports) {
    module.exports = EhkoTetherBar;
}
