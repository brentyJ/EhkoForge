/**
 * EhkoForge Chat Message Web Component v1.0
 * 
 * Renders a single chat message with role-based styling.
 * Supports markdown-style formatting and timestamps.
 * 
 * Usage:
 *   <ehko-message role="user" timestamp="2025-12-08T10:30:00">
 *     Hello Ehko!
 *   </ehko-message>
 * 
 *   <ehko-message role="ehko" timestamp="2025-12-08T10:30:05">
 *     Greetings, Keeper.
 *   </ehko-message>
 * 
 * @license AGPL-3.0
 */

class EhkoMessage extends HTMLElement {
    static get observedAttributes() {
        return ['role', 'timestamp', 'typing'];
    }

    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (oldValue !== newValue) {
            this.render();
        }
    }

    get role() { return this.getAttribute('role') || 'user'; }
    get timestamp() { return this.getAttribute('timestamp') || null; }
    get isTyping() { return this.hasAttribute('typing'); }

    formatTimestamp(isoString) {
        if (!isoString) return '';
        try {
            const date = new Date(isoString);
            return date.toLocaleTimeString('en-AU', { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: false 
            });
        } catch {
            return '';
        }
    }

    getRoleConfig() {
        const configs = {
            user: {
                label: 'You',
                color: '#9F7AEA',
                bgColor: 'rgba(159, 122, 234, 0.1)',
                borderColor: 'rgba(159, 122, 234, 0.3)',
                align: 'flex-end'
            },
            ehko: {
                label: 'Ehko',
                color: '#6B8CCE',
                bgColor: 'rgba(107, 140, 206, 0.1)',
                borderColor: 'rgba(107, 140, 206, 0.3)',
                align: 'flex-start'
            },
            system: {
                label: 'System',
                color: '#718096',
                bgColor: 'rgba(113, 128, 150, 0.1)',
                borderColor: 'rgba(113, 128, 150, 0.3)',
                align: 'center'
            }
        };
        return configs[this.role] || configs.user;
    }

    render() {
        const config = this.getRoleConfig();
        const time = this.formatTimestamp(this.timestamp);
        const content = this.isTyping ? '' : this.innerHTML;

        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    margin-bottom: 16px;
                    animation: fadeIn 0.3s ease-out;
                }

                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }

                .message-wrapper {
                    display: flex;
                    flex-direction: column;
                    align-items: ${config.align};
                }

                .message-header {
                    display: flex;
                    gap: 8px;
                    align-items: center;
                    margin-bottom: 4px;
                    font-family: 'JetBrains Mono', 'Fira Code', monospace;
                    font-size: 11px;
                }

                .role-label {
                    color: ${config.color};
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    font-weight: 500;
                }

                .timestamp {
                    color: #4a5568;
                }

                .message-bubble {
                    max-width: 85%;
                    padding: 12px 16px;
                    background: ${config.bgColor};
                    border: 1px solid ${config.borderColor};
                    border-radius: 8px;
                    font-family: 'JetBrains Mono', 'Fira Code', monospace;
                    font-size: 14px;
                    line-height: 1.6;
                    color: #e2e8f0;
                }

                .message-bubble.system {
                    max-width: 100%;
                    text-align: center;
                    font-size: 12px;
                    color: #718096;
                }

                /* Basic markdown-ish styling */
                .message-content code {
                    background: rgba(0, 0, 0, 0.3);
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 13px;
                }

                .message-content strong {
                    color: ${config.color};
                }

                /* Typing indicator */
                .typing-indicator {
                    display: flex;
                    gap: 4px;
                    padding: 8px 0;
                }

                .typing-dot {
                    width: 8px;
                    height: 8px;
                    background: ${config.color};
                    border-radius: 50%;
                    animation: typingBounce 1.4s ease-in-out infinite;
                }

                .typing-dot:nth-child(2) { animation-delay: 0.2s; }
                .typing-dot:nth-child(3) { animation-delay: 0.4s; }

                @keyframes typingBounce {
                    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
                    30% { transform: translateY(-8px); opacity: 1; }
                }
            </style>

            <div class="message-wrapper">
                <div class="message-header">
                    <span class="role-label">${config.label}</span>
                    ${time ? `<span class="timestamp">${time}</span>` : ''}
                </div>
                <div class="message-bubble ${this.role === 'system' ? 'system' : ''}">
                    ${this.isTyping ? `
                        <div class="typing-indicator">
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                        </div>
                    ` : `
                        <div class="message-content">${content}</div>
                    `}
                </div>
            </div>
        `;
    }

    // Public API
    setContent(html) {
        this.innerHTML = html;
        this.removeAttribute('typing');
        this.render();
    }

    showTyping() {
        this.setAttribute('typing', '');
    }

    hideTyping() {
        this.removeAttribute('typing');
    }
}

customElements.define('ehko-message', EhkoMessage);

if (typeof module !== 'undefined' && module.exports) {
    module.exports = EhkoMessage;
}
