/**
 * EhkoForge Avatar Web Component v1.1
 * 
 * A self-contained, portable Ehko avatar display.
 * Uses Shadow DOM for style encapsulation - no CSS conflicts.
 * SVG-based procedural generation - no AI art.
 * 
 * Usage:
 *   <ehko-avatar 
 *     stage="nascent|signal|resonant|manifest|anchored"
 *     mood="ready|thinking|dormant"
 *     name="Ehko"
 *     size="120">
 *   </ehko-avatar>
 * 
 * Stages (aligned with Authority system):
 *   - nascent: Just beginning (complexity 1)
 *   - signal: First patterns emerging (complexity 2)
 *   - resonant: Clear identity forming (complexity 3)
 *   - manifest: Strong presence (complexity 4)
 *   - anchored: Fully realised (complexity 5)
 * 
 * Moods:
 *   - ready: Normal state
 *   - thinking: Processing, enhanced glow
 *   - dormant: Resting, reduced animation
 * 
 * @license AGPL-3.0
 * 
 * Changelog:
 *   v1.1 — 2025-12-16 — Added all 5 Authority stages (nascent, signal, resonant, manifest, anchored);
 *                        legacy stage names (emerging, established, transcendent) still supported;
 *                        added size attribute documentation
 *   v1.0 — Initial component with 4-stage system
 */

class EhkoAvatar extends HTMLElement {
    static get observedAttributes() {
        return ['stage', 'mood', 'name', 'size'];
    }

    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this._blinkInterval = null;
        this._glowPhase = 0;
        this._animationFrame = null;
    }

    connectedCallback() {
        this.render();
        this.startAnimations();
    }

    disconnectedCallback() {
        this.stopAnimations();
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (oldValue !== newValue) {
            this.render();
        }
    }

    // Getters for attributes with defaults
    get stage() { return this.getAttribute('stage') || 'nascent'; }
    get mood() { return this.getAttribute('mood') || 'ready'; }
    get name() { return this.getAttribute('name') || 'Ehko'; }
    get size() { return parseInt(this.getAttribute('size')) || 120; }

    // Stage-based visual parameters (aligned with Authority system)
    getStageParams() {
        const stages = {
            // Stage 1: Nascent - Just beginning
            nascent: {
                glowIntensity: 0.3,
                eyeGlow: 'rgba(107, 140, 206, 0.6)',
                frameColor: 'rgba(107, 140, 206, 0.4)',
                pulseSpeed: 3000,
                complexity: 1
            },
            // Stage 2: Signal - First patterns emerging
            signal: {
                glowIntensity: 0.45,
                eyeGlow: 'rgba(107, 140, 206, 0.75)',
                frameColor: 'rgba(107, 140, 206, 0.55)',
                pulseSpeed: 2750,
                complexity: 2
            },
            // Stage 3: Resonant - Clear identity forming
            resonant: {
                glowIntensity: 0.6,
                eyeGlow: 'rgba(120, 150, 215, 0.85)',
                frameColor: 'rgba(120, 150, 215, 0.65)',
                pulseSpeed: 2250,
                complexity: 3
            },
            // Stage 4: Manifest - Strong presence
            manifest: {
                glowIntensity: 0.8,
                eyeGlow: 'rgba(135, 165, 230, 0.95)',
                frameColor: 'rgba(135, 165, 230, 0.8)',
                pulseSpeed: 1750,
                complexity: 4
            },
            // Stage 5: Anchored - Fully realised
            anchored: {
                glowIntensity: 1.0,
                eyeGlow: 'rgba(150, 180, 255, 1.0)',
                frameColor: 'rgba(150, 180, 255, 0.9)',
                pulseSpeed: 1500,
                complexity: 5
            },
            // Legacy mappings for compatibility
            emerging: {
                glowIntensity: 0.45,
                eyeGlow: 'rgba(107, 140, 206, 0.75)',
                frameColor: 'rgba(107, 140, 206, 0.55)',
                pulseSpeed: 2750,
                complexity: 2
            },
            established: {
                glowIntensity: 0.6,
                eyeGlow: 'rgba(120, 150, 215, 0.85)',
                frameColor: 'rgba(120, 150, 215, 0.65)',
                pulseSpeed: 2250,
                complexity: 3
            },
            transcendent: {
                glowIntensity: 1.0,
                eyeGlow: 'rgba(150, 180, 255, 1.0)',
                frameColor: 'rgba(150, 180, 255, 0.9)',
                pulseSpeed: 1500,
                complexity: 5
            }
        };
        return stages[this.stage] || stages.nascent;
    }

    // Mood-based visual parameters
    getMoodParams() {
        const moods = {
            ready: {
                eyeScale: 1.0,
                statusText: 'Ready',
                statusColor: 'var(--ehko-accent, #6B8CCE)',
                animationSpeed: 1.0
            },
            thinking: {
                eyeScale: 1.1,
                statusText: 'Thinking...',
                statusColor: 'var(--ehko-accent-bright, #8BA4D9)',
                animationSpeed: 2.0
            },
            dormant: {
                eyeScale: 0.6,
                statusText: 'Resting',
                statusColor: 'var(--ehko-dim, #4a5568)',
                animationSpeed: 0.3
            }
        };
        return moods[this.mood] || moods.ready;
    }

    render() {
        const stageParams = this.getStageParams();
        const moodParams = this.getMoodParams();
        const size = this.size;
        
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    width: ${size}px;
                    height: ${size + 30}px;
                    --ehko-accent: #6B8CCE;
                    --ehko-accent-bright: #8BA4D9;
                    --ehko-dim: #4a5568;
                    --ehko-bg: #0a0c10;
                    --ehko-border: #2d3748;
                }

                .avatar-container {
                    position: relative;
                    width: 100%;
                    height: ${size}px;
                }

                .avatar-frame {
                    width: 100%;
                    height: 100%;
                    border: 2px solid ${stageParams.frameColor};
                    border-radius: 8px;
                    background: var(--ehko-bg);
                    position: relative;
                    overflow: hidden;
                    box-shadow: 
                        0 0 ${10 * stageParams.glowIntensity}px ${stageParams.frameColor},
                        inset 0 0 ${20 * stageParams.glowIntensity}px rgba(107, 140, 206, 0.1);
                    transition: box-shadow 0.3s ease;
                }

                .avatar-frame.thinking {
                    box-shadow: 
                        0 0 ${20 * stageParams.glowIntensity}px ${stageParams.eyeGlow},
                        inset 0 0 ${30 * stageParams.glowIntensity}px rgba(107, 140, 206, 0.2);
                }

                .eye-container {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    display: flex;
                    gap: ${size * 0.15}px;
                }

                .eye {
                    width: ${size * 0.12}px;
                    height: ${size * 0.25 * moodParams.eyeScale}px;
                    background: ${stageParams.eyeGlow};
                    border-radius: 2px;
                    box-shadow: 0 0 ${8 * stageParams.glowIntensity}px ${stageParams.eyeGlow};
                    transition: height 0.1s ease, opacity 0.1s ease;
                }

                .eye.blinking {
                    height: 2px !important;
                }

                .eye.dormant {
                    height: ${size * 0.08}px;
                    opacity: 0.5;
                }

                /* Scan line effect */
                .scanline {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 2px;
                    background: linear-gradient(90deg, 
                        transparent, 
                        ${stageParams.eyeGlow}, 
                        transparent
                    );
                    opacity: ${0.3 * stageParams.glowIntensity};
                    animation: scan ${4 / moodParams.animationSpeed}s linear infinite;
                }

                @keyframes scan {
                    0% { top: 0; }
                    100% { top: 100%; }
                }

                /* Corner accents based on complexity */
                .corner {
                    position: absolute;
                    width: ${8 + stageParams.complexity * 2}px;
                    height: ${8 + stageParams.complexity * 2}px;
                    border: 1px solid ${stageParams.frameColor};
                }
                .corner.tl { top: 4px; left: 4px; border-right: none; border-bottom: none; }
                .corner.tr { top: 4px; right: 4px; border-left: none; border-bottom: none; }
                .corner.bl { bottom: 4px; left: 4px; border-right: none; border-top: none; }
                .corner.br { bottom: 4px; right: 4px; border-left: none; border-top: none; }

                /* Status indicator */
                .status {
                    text-align: center;
                    margin-top: 8px;
                    font-family: 'JetBrains Mono', 'Fira Code', monospace;
                    font-size: 11px;
                    color: ${moodParams.statusColor};
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }

                /* Data streams (complexity-based) */
                .data-stream {
                    position: absolute;
                    width: 1px;
                    background: linear-gradient(180deg, 
                        transparent, 
                        ${stageParams.frameColor}, 
                        transparent
                    );
                    opacity: 0.4;
                    animation: stream ${2 / moodParams.animationSpeed}s linear infinite;
                }

                @keyframes stream {
                    0% { top: -20px; height: 20px; }
                    100% { top: 100%; height: 20px; }
                }

                /* Pulse ring for thinking state */
                .pulse-ring {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 60%;
                    height: 60%;
                    border: 1px solid ${stageParams.eyeGlow};
                    border-radius: 50%;
                    opacity: 0;
                    animation: pulse ${stageParams.pulseSpeed}ms ease-out infinite;
                }

                .thinking .pulse-ring {
                    animation-duration: ${stageParams.pulseSpeed / 2}ms;
                }

                @keyframes pulse {
                    0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.6; }
                    100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
                }
            </style>

            <div class="avatar-container">
                <div class="avatar-frame ${this.mood}">
                    <!-- Corner accents -->
                    <div class="corner tl"></div>
                    <div class="corner tr"></div>
                    <div class="corner bl"></div>
                    <div class="corner br"></div>

                    <!-- Eyes -->
                    <div class="eye-container">
                        <div class="eye ${this.mood === 'dormant' ? 'dormant' : ''}" id="eye-left"></div>
                        <div class="eye ${this.mood === 'dormant' ? 'dormant' : ''}" id="eye-right"></div>
                    </div>

                    <!-- Scan line -->
                    <div class="scanline"></div>

                    <!-- Pulse ring (visible when thinking) -->
                    ${this.mood === 'thinking' ? '<div class="pulse-ring"></div>' : ''}

                    <!-- Data streams based on complexity -->
                    ${this.renderDataStreams(stageParams.complexity)}
                </div>
            </div>
            <div class="status">${moodParams.statusText}</div>
        `;

        // Re-bind animations after render
        if (this.isConnected) {
            this.startAnimations();
        }
    }

    renderDataStreams(complexity) {
        let streams = '';
        for (let i = 0; i < complexity; i++) {
            const leftPos = 10 + (i * 15);
            const rightPos = 10 + (i * 15);
            const delay = i * 0.3;
            streams += `
                <div class="data-stream" style="left: ${leftPos}px; animation-delay: ${delay}s;"></div>
                <div class="data-stream" style="right: ${rightPos}px; animation-delay: ${delay + 0.5}s;"></div>
            `;
        }
        return streams;
    }

    startAnimations() {
        this.stopAnimations(); // Clear any existing

        // Eye blink animation
        if (this.mood !== 'dormant') {
            const blink = () => {
                const eyes = this.shadowRoot.querySelectorAll('.eye');
                eyes.forEach(eye => eye.classList.add('blinking'));
                setTimeout(() => {
                    eyes.forEach(eye => eye.classList.remove('blinking'));
                }, 100);
            };

            const scheduleBlink = () => {
                const delay = 3000 + Math.random() * 4000;
                this._blinkInterval = setTimeout(() => {
                    blink();
                    scheduleBlink();
                }, delay);
            };

            scheduleBlink();
        }
    }

    stopAnimations() {
        if (this._blinkInterval) {
            clearTimeout(this._blinkInterval);
            this._blinkInterval = null;
        }
        if (this._animationFrame) {
            cancelAnimationFrame(this._animationFrame);
            this._animationFrame = null;
        }
    }

    // Public API for external control
    setMood(mood) {
        this.setAttribute('mood', mood);
    }

    setStage(stage) {
        this.setAttribute('stage', stage);
    }
}

// Register the component
customElements.define('ehko-avatar', EhkoAvatar);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EhkoAvatar;
}
