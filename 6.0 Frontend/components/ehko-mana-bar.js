/**
 * EhkoForge Mana Bar Web Component v1.1
 * 
 * Displays mana reserves with animated fill, glow effects, and dual-source support.
 * Self-contained - all styles encapsulated in Shadow DOM.
 * 
 * Usage:
 *   <ehko-mana-bar 
 *     current="75" 
 *     max="100" 
 *     regen="50" 
 *     purchased="25"
 *     show-breakdown="true">
 *   </ehko-mana-bar>
 * 
 * Attributes:
 *   current - Current total mana (regen + purchased available)
 *   max - Maximum mana capacity  
 *   regen - Regenerative mana amount (BYOK)
 *   purchased - Purchased mana amount
 *   label - Optional label text (default: "Mana")
 *   show-text - Show numeric value (default: true)
 *   show-breakdown - Show regen/purchased breakdown (default: false)
 *   compact - Compact mode for smaller displays (default: false)
 * 
 * Events:
 *   mana-topup - Fired when topup button is clicked
 * 
 * @license AGPL-3.0
 */

class EhkoManaBar extends HTMLElement {
    static get observedAttributes() {
        return ['current', 'max', 'regen', 'purchased', 'label', 'show-text', 'show-breakdown', 'compact'];
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

    get current() { return parseFloat(this.getAttribute('current')) || 0; }
    get max() { return parseFloat(this.getAttribute('max')) || 100; }
    get regen() { return parseFloat(this.getAttribute('regen')) || this.current; }
    get purchased() { return parseFloat(this.getAttribute('purchased')) || 0; }
    get label() { return this.getAttribute('label') || 'Mana'; }
    get showText() { return this.getAttribute('show-text') !== 'false'; }
    get showBreakdown() { return this.getAttribute('show-breakdown') === 'true'; }
    get compact() { return this.hasAttribute('compact'); }

    get percentage() {
        const total = this.regen + this.purchased;
        if (total === 0) return 0;
        return Math.min(100, Math.max(0, (this.current / total) * 100));
    }

    getBarColor() {
        const pct = this.percentage;
        if (pct > 60) return { main: '#6B8CCE', glow: 'rgba(107, 140, 206, 0.4)' };
        if (pct > 30) return { main: '#f39c12', glow: 'rgba(243, 156, 18, 0.4)' };
        return { main: '#e74c3c', glow: 'rgba(231, 76, 60, 0.4)' };
    }

    render() {
        const colors = this.getBarColor();
        const totalMax = this.regen + this.purchased;
        const regenPct = totalMax > 0 ? (this.regen / totalMax) * 100 : 0;
        const purchasedPct = totalMax > 0 ? (this.purchased / totalMax) * 100 : 0;
        
        // Calculate how much of current is from each source
        const currentFromRegen = Math.min(this.current, this.regen);
        const currentFromPurchased = Math.max(0, this.current - this.regen);
        const regenFillPct = this.regen > 0 ? (currentFromRegen / totalMax) * 100 : 0;
        const purchasedFillPct = this.purchased > 0 ? (currentFromPurchased / totalMax) * 100 : 0;

        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    width: 100%;
                    font-family: 'JetBrains Mono', 'Fira Code', monospace;
                }

                .mana-container {
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }

                .mana-header {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .mana-icon {
                    font-size: 14px;
                    color: ${colors.main};
                    text-shadow: 0 0 8px ${colors.glow};
                }

                .mana-values {
                    display: flex;
                    align-items: baseline;
                    gap: 2px;
                }

                .mana-current {
                    font-size: ${this.compact ? '14px' : '18px'};
                    font-weight: 600;
                    color: ${colors.main};
                }

                .mana-separator {
                    color: #4a5568;
                    font-size: ${this.compact ? '12px' : '14px'};
                }

                .mana-max {
                    font-size: ${this.compact ? '12px' : '14px'};
                    color: #4a5568;
                }

                .topup-btn {
                    margin-left: 8px;
                    padding: 2px 8px;
                    background: #161c28;
                    border: 1px solid rgba(107, 140, 206, 0.3);
                    color: #6B8CCE;
                    font-family: inherit;
                    font-size: 10px;
                    cursor: pointer;
                    transition: all 0.15s ease;
                    border-radius: 2px;
                }

                .topup-btn:hover {
                    background: #6B8CCE;
                    color: #080a0e;
                    box-shadow: 0 0 8px rgba(107, 140, 206, 0.4);
                }

                .mana-track {
                    height: ${this.compact ? '6px' : '8px'};
                    background: #1a1d24;
                    border: 1px solid #2d3748;
                    border-radius: 4px;
                    overflow: hidden;
                    position: relative;
                }

                .mana-fill-regen {
                    position: absolute;
                    top: 0;
                    left: 0;
                    height: 100%;
                    width: ${regenFillPct}%;
                    background: linear-gradient(90deg, 
                        ${colors.main}dd,
                        ${colors.main}
                    );
                    border-radius: 3px;
                    transition: width 0.5s ease;
                    box-shadow: 0 0 8px ${colors.glow};
                }

                .mana-fill-purchased {
                    position: absolute;
                    top: 0;
                    left: ${regenFillPct}%;
                    height: 100%;
                    width: ${purchasedFillPct}%;
                    background: linear-gradient(90deg, #9b7ed9, #c9a962);
                    border-radius: 3px;
                    transition: width 0.5s ease, left 0.5s ease;
                }

                .mana-fill-regen::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(90deg,
                        transparent 0%,
                        rgba(255,255,255,0.2) 50%,
                        transparent 100%
                    );
                    animation: shimmer 2s ease-in-out infinite;
                }

                @keyframes shimmer {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }

                /* Low mana pulse effect */
                ${this.percentage <= 30 ? `
                .mana-fill-regen {
                    animation: lowPulse 1.5s ease-in-out infinite;
                }
                @keyframes lowPulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.7; }
                }
                ` : ''}

                .mana-breakdown {
                    display: flex;
                    gap: 16px;
                    font-size: 10px;
                    color: #718096;
                    margin-top: 2px;
                }

                .breakdown-item {
                    display: flex;
                    align-items: center;
                    gap: 4px;
                }

                .breakdown-dot {
                    width: 6px;
                    height: 6px;
                    border-radius: 50%;
                }

                .breakdown-dot.regen {
                    background: ${colors.main};
                }

                .breakdown-dot.purchased {
                    background: linear-gradient(135deg, #9b7ed9, #c9a962);
                }
            </style>

            <div class="mana-container">
                <div class="mana-header">
                    <span class="mana-icon">◆</span>
                    ${this.showText ? `
                        <div class="mana-values">
                            <span class="mana-current">${Math.floor(this.current)}</span>
                            <span class="mana-separator">/</span>
                            <span class="mana-max">${Math.floor(totalMax)}</span>
                        </div>
                    ` : ''}
                    <button class="topup-btn" id="topup-btn" title="Purchase Mana-Cores">▲</button>
                </div>
                <div class="mana-track">
                    <div class="mana-fill-regen"></div>
                    <div class="mana-fill-purchased"></div>
                </div>
                ${this.showBreakdown ? `
                    <div class="mana-breakdown">
                        <div class="breakdown-item">
                            <span class="breakdown-dot regen"></span>
                            <span>Regen: ${Math.floor(this.regen)}</span>
                        </div>
                        <div class="breakdown-item">
                            <span class="breakdown-dot purchased"></span>
                            <span>Bought: ${Math.floor(this.purchased)}</span>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        // Bind topup button
        const topupBtn = this.shadowRoot.getElementById('topup-btn');
        if (topupBtn) {
            topupBtn.addEventListener('click', () => {
                this.dispatchEvent(new CustomEvent('mana-topup', { bubbles: true }));
            });
        }
    }

    // Public API
    setMana(current, regen = null, purchased = null) {
        this.setAttribute('current', current);
        if (regen !== null) this.setAttribute('regen', regen);
        if (purchased !== null) this.setAttribute('purchased', purchased);
    }

    // Animate mana change
    animateTo(newCurrent, duration = 500) {
        const startValue = this.current;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const currentValue = startValue + (newCurrent - startValue) * eased;
            
            this.setAttribute('current', currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
}

customElements.define('ehko-mana-bar', EhkoManaBar);

if (typeof module !== 'undefined' && module.exports) {
    module.exports = EhkoManaBar;
}
