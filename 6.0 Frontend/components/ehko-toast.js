/**
 * EhkoForge Toast Web Component v1.0
 * 
 * Self-contained toast notifications with encapsulated styles.
 * The tether animation lives inside Shadow DOM - no CSS conflicts.
 * 
 * Usage:
 *   // Programmatic
 *   EhkoToast.show('Message saved!', 'success');
 *   EhkoToast.show('Something went wrong', 'error');
 * 
 *   // Or create element directly
 *   <ehko-toast type="success" message="Done!"></ehko-toast>
 * 
 * @license AGPL-3.0
 */

class EhkoToast extends HTMLElement {
    static get observedAttributes() {
        return ['type', 'message', 'duration'];
    }

    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this._startTime = null;
        this._animationFrame = null;
    }

    connectedCallback() {
        this.render();
        this.startTetherAnimation();
        this.scheduleRemoval();
    }

    disconnectedCallback() {
        if (this._animationFrame) {
            cancelAnimationFrame(this._animationFrame);
        }
    }

    get type() { return this.getAttribute('type') || 'info'; }
    get message() { return this.getAttribute('message') || ''; }
    get duration() { return parseInt(this.getAttribute('duration')) || 3000; }

    getTypeConfig() {
        const configs = {
            success: {
                icon: '✓',
                color: '#6B8CCE',
                bgColor: 'rgba(107, 140, 206, 0.1)'
            },
            error: {
                icon: '✗',
                color: '#e74c3c',
                bgColor: 'rgba(231, 76, 60, 0.1)'
            },
            warning: {
                icon: '⚠',
                color: '#f39c12',
                bgColor: 'rgba(243, 156, 18, 0.1)'
            },
            info: {
                icon: 'ⓘ',
                color: '#9F7AEA',
                bgColor: 'rgba(159, 122, 234, 0.1)'
            }
        };
        return configs[this.type] || configs.info;
    }

    render() {
        const config = this.getTypeConfig();

        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    pointer-events: auto;
                    animation: slideIn 0.3s ease-out;
                }

                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }

                @keyframes slideOut {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }

                :host(.removing) {
                    animation: slideOut 0.3s ease-out forwards;
                }

                .toast {
                    display: flex;
                    align-items: stretch;
                    background: #12141a;
                    border: 1px solid #2d3748;
                    border-left: none;
                    border-radius: 4px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
                    min-width: 280px;
                    max-width: 400px;
                    overflow: hidden;
                    position: relative;
                }

                .tether {
                    width: 4px;
                    background: ${config.color};
                    transform-origin: top center;
                    /* No animation property - controlled by JS */
                }

                .content {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 12px 16px;
                    flex: 1;
                }

                .icon {
                    font-size: 16px;
                    color: ${config.color};
                    flex-shrink: 0;
                }

                .message {
                    font-family: 'JetBrains Mono', 'Fira Code', monospace;
                    font-size: 13px;
                    color: #e2e8f0;
                    line-height: 1.4;
                }
            </style>

            <div class="toast">
                <div class="tether" id="tether"></div>
                <div class="content">
                    <span class="icon">${config.icon}</span>
                    <span class="message">${this.message}</span>
                </div>
            </div>
        `;
    }

    startTetherAnimation() {
        const tether = this.shadowRoot.getElementById('tether');
        if (!tether) return;

        this._startTime = performance.now();
        const duration = this.duration;

        const animate = (currentTime) => {
            const elapsed = currentTime - this._startTime;
            const progress = Math.min(elapsed / duration, 1);
            const scale = 1 - progress;
            
            tether.style.transform = `scaleY(${scale})`;

            if (progress < 1) {
                this._animationFrame = requestAnimationFrame(animate);
            }
        };

        this._animationFrame = requestAnimationFrame(animate);
    }

    scheduleRemoval() {
        setTimeout(() => {
            this.classList.add('removing');
            setTimeout(() => {
                this.remove();
            }, 300);
        }, this.duration);
    }

    // Static factory method for easy creation
    static show(message, type = 'info', duration = 3000) {
        // Ensure container exists
        let container = document.querySelector('ehko-toast-container');
        if (!container) {
            container = document.createElement('ehko-toast-container');
            document.body.appendChild(container);
        }

        // Create and add toast
        const toast = document.createElement('ehko-toast');
        toast.setAttribute('message', message);
        toast.setAttribute('type', type);
        toast.setAttribute('duration', duration);
        container.appendChild(toast);

        return toast;
    }
}

/**
 * Toast Container - manages positioning of multiple toasts
 */
class EhkoToastContainer extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                    pointer-events: none;
                }
            </style>
            <slot></slot>
        `;
    }
}

// Register components
customElements.define('ehko-toast', EhkoToast);
customElements.define('ehko-toast-container', EhkoToastContainer);

// Global helper
window.EhkoToast = EhkoToast;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EhkoToast, EhkoToastContainer };
}
