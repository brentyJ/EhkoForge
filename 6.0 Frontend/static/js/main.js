/**
 * EhkoForge Main JavaScript v2.6
 * Phase 2: Web Components Migration Complete
 * Session 31: Full component migration
 * 
 * Web Components in use:
 * - <ehko-toast> for notifications
 * - <ehko-mana-bar> for mana display with topup event
 * - <ehko-tether-bar> and <ehko-tether-panel> for tether management
 * - <ehko-avatar> for avatar display with mood/stage states
 * - <ehko-message> for chat messages with role-based styling
 */

// =============================================================================
// EHKO TAGLINE ROTATOR
// =============================================================================

const EHKO_ACRONYMS = [
    ['Evolving', 'Human', 'Knowledge', 'Observer'],
    ['Eternal', 'Human', 'Knowledge', 'Origin'],
    ['Ethical', 'Heritage', 'Knowledge', 'Oracle'],
    ['Emergent', 'Human', 'Knowledge', 'Organizer'],
    ['Enduring', 'Human', 'Knowledge', 'Opus'],
    ['Experiential', 'Human', 'Knowledge', 'Object'],
    ['Essential', 'Human', 'Knowledge', 'Origin'],
    ['Existential', 'Human', 'Knowledge', 'Observer'],
    ['Encoded', 'Human', 'Knowledge', 'Output'],
    ['Everlasting', 'Human', 'Knowledge', 'Orchestrator']
];

function getRandomAcronym() {
    return EHKO_ACRONYMS[Math.floor(Math.random() * EHKO_ACRONYMS.length)];
}

// =============================================================================
// MODE DIAL TOGGLE
// =============================================================================

function initModeDial() {
    const knob = document.getElementById('dial-knob');
    const channel = document.querySelector('.dial-channel');
    const labelTerminal = document.querySelector('.dial-label-terminal');
    const labelReflect = document.querySelector('.dial-label-reflect');
    const ledTerminal = document.getElementById('led-terminal');
    const ledReflect = document.getElementById('led-reflect');
    
    if (!knob || !channel) return;
    
    function updateDialVisuals(mode) {
        if (mode === 'reflection') {
            knob.classList.add('right');
            labelTerminal.classList.remove('active');
            labelReflect.classList.add('active');
            ledTerminal.classList.remove('active');
            ledReflect.classList.add('active');
        } else {
            knob.classList.remove('right');
            labelTerminal.classList.add('active');
            labelReflect.classList.remove('active');
            ledTerminal.classList.add('active');
            ledReflect.classList.remove('active');
        }
    }
    
    function toggleMode() {
        const newMode = state.mode === 'terminal' ? 'reflection' : 'terminal';
        setMode(newMode);
        updateDialVisuals(newMode);
    }
    
    // Click handlers
    channel.addEventListener('click', toggleMode);
    knob.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleMode();
    });
    
    labelTerminal.addEventListener('click', () => {
        if (state.mode !== 'terminal') {
            setMode('terminal');
            updateDialVisuals('terminal');
        }
    });
    
    labelReflect.addEventListener('click', () => {
        if (state.mode !== 'reflection') {
            setMode('reflection');
            updateDialVisuals('reflection');
        }
    });
    
    // Initialize visuals
    updateDialVisuals(state.mode);
    labelTerminal.classList.add('active');
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', initModeDial);

// =============================================================================
// STATE
// =============================================================================

const state = {
    mode: 'terminal',  // 'terminal' or 'reflection'
    sessionId: null,
    messages: [],
    selectedModel: 'claude-sonnet-4',
    currentAcronym: null,  // Store selected acronym to prevent changes on re-render
    manaCosts: {
        terminal_message: 1,
        reflection_message: 3,
        recog_sweep: 20,
    },
    authority: null,
    mana: null,
    settings: {
        showAvatar: true,
        scanlines: true,
        reduceMotion: false,
    },
};

// =============================================================================
// API HELPERS
// =============================================================================

async function api(endpoint, options = {}) {
    const response = await fetch(`/api${endpoint}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    return response.json();
}

// =============================================================================
// AUTHORITY & MANA
// =============================================================================

async function fetchAuthority() {
    try {
        const data = await api('/authority');
        state.authority = data;
        updateAuthorityDisplay(data);
    } catch (err) {
        console.error('Failed to fetch authority:', err);
    }
}

function updateAuthorityDisplay(auth) {
    // Total percentage
    const totalPct = Math.round((auth.authority_total || 0) * 100);
    document.getElementById('authority-total').textContent = `${totalPct}%`;
    
    // Stage with proper capitalisation
    const stage = auth.advancement_stage || 'nascent';
    const stageCapitalised = stage.charAt(0).toUpperCase() + stage.slice(1);
    document.getElementById('authority-stage').textContent = stageCapitalised;
    
    // Sync avatar stage with Authority stage
    setAvatarStage(stage);
    
    // Component bars - components are at top level, not nested
    const componentKeys = ['memory_depth', 'identity_clarity', 'emotional_range', 'temporal_coverage', 'core_density'];
    componentKeys.forEach(key => {
        const value = auth[key] || 0;
        const bar = document.querySelector(`.authority-bar[data-component="${key}"] .bar-fill`);
        if (bar) {
            bar.style.width = `${Math.round(value * 100)}%`;
        }
    });
}

async function fetchMana() {
    // Deprecated - use fetchManaBalance() instead
    // Kept for backward compatibility, redirects to new function
    await fetchManaBalance();
}

function updateCostDisplay() {
    const cost = state.mode === 'reflection' 
        ? state.manaCosts.reflection_message 
        : state.manaCosts.terminal_message;
    document.querySelector('.cost-value').textContent = cost;
}

async function refreshAuthority() {
    try {
        const data = await api('/authority/refresh', { method: 'POST' });
        state.authority = data;
        updateAuthorityDisplay(data);
        showNotice('Authority recalculated');
    } catch (err) {
        console.error('Failed to refresh authority:', err);
    }
}

async function refillMana() {
    try {
        const data = await api('/mana/refill', { method: 'POST' });
        // Refresh mana display from server
        await fetchManaBalance();
        showNotice('Mana refilled');
    } catch (err) {
        console.error('Failed to refill mana:', err);
    }
}

// =============================================================================
// TETHERS (BYOK Conduits)
// =============================================================================

async function fetchTethers() {
    try {
        const data = await api('/tethers');
        if (data.success) {
            renderTethers(data.tethers);
        }
    } catch (err) {
        console.error('Failed to fetch tethers:', err);
    }
}

function renderTethers(tethers) {
    const container = document.getElementById('tethers-list');
    if (!container) return;
    
    // Clear existing
    container.innerHTML = '';
    
    // Create tether bars for each configured tether
    tethers.forEach(tether => {
        const bar = document.createElement('ehko-tether-bar');
        bar.setAttribute('provider', tether.provider);
        bar.setAttribute('provider-name', tether.provider_display_name || tether.provider);
        bar.setAttribute('status', tether.verification_status || 'none');
        bar.setAttribute('active', tether.active === 1 ? 'true' : 'false');
        bar.setAttribute('compact', '');
        
        // Event handlers
        bar.addEventListener('tether-manage', (e) => {
            openTetherPanel(e.detail.provider);
        });
        
        bar.addEventListener('tether-toggle', async (e) => {
            const { provider, active } = e.detail;
            await toggleTetherConnection(provider, active);
        });
        
        container.appendChild(bar);
    });
    
    // If no tethers, show placeholder
    if (tethers.length === 0) {
        container.innerHTML = `
            <div class="tethers-empty" style="font-size: 10px; color: var(--text-dim); text-align: center; padding: 8px;">
                No tethers configured. Click ⚙ to add.
            </div>
        `;
    }
}

async function toggleTetherConnection(provider, active) {
    try {
        const data = await api(`/tethers/${provider}/toggle`, {
            method: 'POST',
            body: JSON.stringify({ active }),
        });
        
        if (data.success) {
            showNotification(data.message, 'success');
            await fetchTethers();
        } else {
            showNotification(data.error || 'Toggle failed', 'error');
        }
    } catch (err) {
        console.error('Failed to toggle tether:', err);
        showNotification('Failed to toggle tether', 'error');
    }
}

function openTetherPanel(provider = null) {
    console.log('[EhkoForge] openTetherPanel called');
    const panel = document.getElementById('tether-panel');
    console.log('[EhkoForge] Panel element:', panel);
    if (panel) {
        panel.open(provider);
    } else {
        console.error('[EhkoForge] Tether panel element not found!');
    }
}

function initTetherEvents() {
    // Manage button
    const manageBtn = document.getElementById('tethers-manage-btn');
    console.log('[EhkoForge] initTetherEvents - manageBtn:', manageBtn);
    if (manageBtn) {
        manageBtn.addEventListener('click', () => {
            console.log('[EhkoForge] Tethers manage button clicked');
            openTetherPanel();
        });
    } else {
        console.error('[EhkoForge] Tethers manage button not found!');
    }
    
    // Panel events
    const panel = document.getElementById('tether-panel');
    if (panel) {
        panel.addEventListener('tether-updated', () => {
            fetchTethers();
        });
    }
}

// =============================================================================
// INSITE COUNT
// =============================================================================

async function fetchInsiteCount() {
    try {
        const data = await api('/ingots?status=surfaced&limit=100');
        const count = data.count || 0;
        const badge = document.getElementById('insite-badge');
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    } catch (err) {
        console.error('Failed to fetch insite count:', err);
    }
}

// =============================================================================
// MODE SWITCHING
// =============================================================================

function setMode(mode) {
    state.mode = mode;
    
    // Update body class for styling
    document.body.classList.toggle('mode-reflection', mode === 'reflection');
    document.body.classList.toggle('mode-terminal', mode === 'terminal');
    
    // Update welcome text
    const welcomeText = document.getElementById('welcome-text');
    if (welcomeText) {
        welcomeText.textContent = mode === 'reflection'
            ? '> REFLECTION MODE — Explore your inner landscape.'
            : '> TERMINAL MODE — Your Ehko awaits.';
    }
    
    // Update placeholder
    const input = document.getElementById('message-input');
    input.placeholder = mode === 'reflection'
        ? 'Share what\'s on your mind...'
        : 'Type a message...';
    
    // Update cost displays
    updateCostDisplay();
    updateModelCost();
}

function updateModelCost() {
    const dropdown = document.getElementById('model-dropdown');
    const activeOption = dropdown.querySelector('.model-option.active');
    
    if (!activeOption) return;
    
    const costAttr = state.mode === 'reflection' ? 'data-cost-reflection' : 'data-cost-terminal';
    const cost = parseFloat(activeOption.getAttribute(costAttr));
    
    // Update trigger display
    document.getElementById('selected-model-cost').textContent = `◆${cost}`;
    
    // Update input cost display
    document.querySelector('.cost-value').textContent = cost;
    
    // Update all option costs in menu based on current mode
    document.querySelectorAll('.model-option').forEach(option => {
        const optionCost = parseFloat(option.getAttribute(costAttr));
        option.querySelector('.option-cost').textContent = `◆${optionCost}`;
    });
    
    // Store in state
    state.manaCosts[state.mode + '_message'] = cost;
    state.selectedModel = activeOption.dataset.model;
}

function toggleModelDropdown() {
    const dropdown = document.getElementById('model-dropdown');
    const isOpen = dropdown.classList.contains('open');
    
    if (isOpen) {
        dropdown.classList.remove('open');
    } else {
        dropdown.classList.add('open');
        updateModelCost(); // Refresh costs when opening
    }
}

function selectModel(modelElement) {
    // Remove active from all
    document.querySelectorAll('.model-option').forEach(opt => opt.classList.remove('active'));
    
    // Set active
    modelElement.classList.add('active');
    
    // Update trigger text
    const modelName = modelElement.querySelector('.option-name').textContent;
    document.getElementById('selected-model-name').textContent = modelName;
    
    // Update costs
    updateModelCost();
    
    // Close dropdown
    document.getElementById('model-dropdown').classList.remove('open');
}

// =============================================================================
// SESSION MANAGEMENT
// =============================================================================

async function createSession() {
    try {
        const data = await api('/sessions', {
            method: 'POST',
            body: JSON.stringify({ title: 'New Chat' }),
        });
        state.sessionId = data.id;
        state.messages = [];
        state.currentAcronym = getRandomAcronym();  // Fresh acronym for new session
        document.getElementById('session-title').textContent = data.title;
        clearMessages();
        updateAsciiDisplay();  // Update ASCII with new acronym
        showWelcome();
        return data;
    } catch (err) {
        console.error('Failed to create session:', err);
    }
}

async function loadSession(sessionId) {
    try {
        const data = await api(`/sessions/${sessionId}/messages`);
        state.sessionId = sessionId;
        state.messages = data.messages;
        
        // Update session title
        const sessionData = await api(`/sessions/${sessionId}`);
        document.getElementById('session-title').textContent = sessionData.title;
        
        // Render messages
        clearMessages();
        data.messages.forEach(msg => renderMessage(msg));
        scrollToBottom();
    } catch (err) {
        console.error('Failed to load session:', err);
    }
}

async function fetchSessions() {
    try {
        const data = await api('/sessions');
        return data.sessions || [];
    } catch (err) {
        console.error('Failed to fetch sessions:', err);
        return [];
    }
}

function clearMessages() {
    const output = document.getElementById('terminal-output');
    output.innerHTML = '';
}

function updateAsciiDisplay() {
    const asciiDisplay = document.getElementById('ascii-display');
    if (!asciiDisplay) return;
    
    // Use stored acronym if exists, otherwise generate and store new one
    if (!state.currentAcronym) {
        state.currentAcronym = getRandomAcronym();
    }
    const acronym = state.currentAcronym;
    
    // Full ASCII logo with acronym
    const formatWord = (word) => `<span class="blink-dot">•</span> <span class="glow-letter">${word[0]}</span>${word.slice(1)}`;
    
    asciiDisplay.innerHTML = `███████╗██╗  ██╗██╗  ██╗ ██████╗
██╔════╝██║  ██║██║ ██╔╝██╔═══██╗  ${formatWord(acronym[0])}
█████╗  ███████║█████╔╝ ██║   ██║  ${formatWord(acronym[1])}
██╔══╝  ██╔══██║██╔═██╗ ██║   ██║  ${formatWord(acronym[2])}
███████╗██║  ██║██║  ██╗╚██████╔╝  ${formatWord(acronym[3])}
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝`;
}

function showWelcome() {
    const output = document.getElementById('terminal-output');
    
    // Update ASCII display in avatar zone
    updateAsciiDisplay();
    
    // Simple welcome message in terminal output
    output.innerHTML = `
        <div class="welcome-message">
            <p class="welcome-text" id="welcome-text">
                > ${state.mode === 'reflection' ? 'REFLECTION MODE — Explore your inner landscape.' : 'TERMINAL MODE — Your Ehko awaits.'}
            </p>
        </div>
    `;
}

// =============================================================================
// MESSAGING
// =============================================================================

async function sendMessage() {
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    
    if (!content) return;
    
    // Ensure we have a session
    if (!state.sessionId) {
        await createSession();
    }
    
    // Check mana
    const cost = state.mode === 'reflection' 
        ? state.manaCosts.reflection_message 
        : state.manaCosts.terminal_message;
    
    if (state.mana && state.mana.current_mana < cost) {
        showDormantModal(state.mana.current_mana, cost);
        return;
    }
    
    // Clear input and reset height
    input.value = '';
    input.style.height = 'auto';
    
    // Show user message immediately
    const userMsg = {
        role: 'user',
        content: content,
        timestamp: new Date().toISOString(),
    };
    renderMessage(userMsg);
    
    // Show typing indicator
    showTyping();
    
    // Update avatar
    setAvatarState('thinking');
    
    try {
        const data = await api(`/sessions/${state.sessionId}/messages`, {
            method: 'POST',
            body: JSON.stringify({
                content: content,
                role: 'user',
                mode: state.mode,
            }),
        });
        
        // Handle dormant response
        if (data.dormant) {
            hideTyping();
            setAvatarState('dormant');
            showDormantModal(data.current_mana, data.required);
            return;
        }
        
        // Remove typing indicator
        hideTyping();
        setAvatarState('ready');
        
        // Render Ehko response
        const ehkoMsg = data.messages.find(m => m.role === 'ehko');
        if (ehkoMsg) {
            renderMessage(ehkoMsg);
            state.messages.push(userMsg);
            state.messages.push(ehkoMsg);
        }
        
        // Update mana display
        await fetchMana();
        
        scrollToBottom();
        
    } catch (err) {
        console.error('Failed to send message:', err);
        hideTyping();
        setAvatarState('ready');
        showNotice('Failed to send message', 'error');
    }
}

function renderMessage(msg) {
    const output = document.getElementById('terminal-output');
    
    // Remove welcome if present
    const welcome = output.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    // Create message component
    const message = document.createElement('ehko-message');
    message.setAttribute('role', msg.role === 'ehko' ? 'ehko' : 'user');
    if (msg.timestamp) {
        message.setAttribute('timestamp', msg.timestamp);
    }
    message.innerHTML = escapeHtml(msg.content);
    
    output.appendChild(message);
    scrollToBottom();
}

function showTyping() {
    const output = document.getElementById('terminal-output');
    const existing = output.querySelector('ehko-message[typing]');
    if (existing) return;
    
    // Create typing indicator using component
    const typingMsg = document.createElement('ehko-message');
    typingMsg.setAttribute('role', 'ehko');
    typingMsg.setAttribute('typing', '');
    typingMsg.id = 'typing-indicator';
    
    output.appendChild(typingMsg);
    scrollToBottom();
}

function hideTyping() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
}

function scrollToBottom() {
    const output = document.getElementById('terminal-output');
    output.scrollTop = output.scrollHeight;
}

// =============================================================================
// AVATAR
// =============================================================================

let matrixInterval = null;

function initMatrixCode() {
    const canvas = document.getElementById('matrix-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Make canvas responsive
    function resizeCanvas() {
        const container = document.querySelector('.avatar-zone');
        if (!container) return;
        const width = Math.min(container.offsetWidth, 1200);
        canvas.width = width;
        canvas.height = 120;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    const fontSize = 10;
    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
    
    let columns = Math.floor(canvas.width / (fontSize * 4)); // Quarter as many columns
    let drops = [];
    
    function initDrops() {
        columns = Math.floor(canvas.width / (fontSize * 4)); // Quarter as many columns
        drops = [];
        for (let i = 0; i < columns; i++) {
            drops[i] = Math.random() * -20;
        }
    }
    initDrops();
    
    // Ehko center position (relative to canvas)
    const ehkoCenter = 0.5; // Center of canvas (50%)
    const ehkoRadius = 0.15; // 15% of canvas width on each side
    
    let speed = 1;
    
    function draw() {
        ctx.fillStyle = 'rgba(8, 10, 14, 0.15)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = 'rgba(107, 140, 206, 0.6)';
        ctx.font = `${fontSize}px monospace`;
        
        for (let i = 0; i < drops.length; i++) {
            const char = chars[Math.floor(Math.random() * chars.length)];
            const x = i * fontSize * 4; // Match column spacing
            
            // Calculate normalized position (0 to 1)
            const normalizedX = i / columns;
            
            // Check if this column is near the Ehko
            const distanceFromCenter = Math.abs(normalizedX - ehkoCenter);
            const isNearEhko = distanceFromCenter < ehkoRadius;
            
            if (isNearEhko) {
                // Flow UPWARD near Ehko
                const y = canvas.height - (drops[i] * fontSize);
                ctx.fillText(char, x, y);
                
                // Move up (slower)
                drops[i] += speed * 0.3;
                
                // Reset if off top
                if (drops[i] * fontSize > canvas.height) {
                    drops[i] = 0;
                }
            } else {
                // Flow DOWNWARD everywhere else
                const y = drops[i] * fontSize;
                ctx.fillText(char, x, y);
                
                // Move down (slower)
                drops[i] += speed * 0.3;
                
                // Reset if off bottom
                if (y > canvas.height && Math.random() > 0.95) {
                    drops[i] = 0;
                }
            }
        }
    }
    
    matrixInterval = setInterval(draw, 50);
    
    window.setMatrixSpeed = (newSpeed) => {
        speed = newSpeed;
    };
    
    // Re-init on resize
    window.addEventListener('resize', () => {
        resizeCanvas();
        initDrops();
    });
}

function setAvatarState(status) {
    const avatar = document.getElementById('ehko-avatar');
    if (!avatar) return;
    
    // Map status to mood
    avatar.setMood(status);
    
    // Adjust matrix speed based on mood
    switch (status) {
        case 'thinking':
            if (window.setMatrixSpeed) window.setMatrixSpeed(2); // Faster
            break;
        case 'dormant':
            if (window.setMatrixSpeed) window.setMatrixSpeed(0.3); // Slower
            break;
        default:
            if (window.setMatrixSpeed) window.setMatrixSpeed(1); // Normal
    }
}

function setAvatarStage(stage) {
    const avatar = document.getElementById('ehko-avatar');
    if (!avatar) return;
    
    // Component supports all Authority stages directly:
    // nascent, signal, resonant, manifest, anchored
    avatar.setStage(stage.toLowerCase());
}

// =============================================================================
// FORGE TO VAULT
// =============================================================================

function openForgeModal() {
    if (!state.sessionId || state.messages.length === 0) {
        showNotice('No messages to forge', 'warning');
        return;
    }
    
    document.getElementById('forge-count').textContent = 
        `${state.messages.length} messages in session`;
    document.getElementById('forge-title').value = '';
    document.getElementById('forge-tags').value = '';
    document.getElementById('forge-emotional').value = '';
    
    document.getElementById('forge-overlay').classList.add('active');
}

function closeForgeModal() {
    document.getElementById('forge-overlay').classList.remove('active');
}

async function executeForge() {
    const title = document.getElementById('forge-title').value.trim() || 'Forged Reflection';
    const tags = document.getElementById('forge-tags').value
        .split(',')
        .map(t => t.trim())
        .filter(Boolean);
    const emotional = document.getElementById('forge-emotional').value
        .split(',')
        .map(t => t.trim())
        .filter(Boolean);
    
    // Get all message IDs
    const messageIds = state.messages.map(m => m.id).filter(Boolean);
    
    if (messageIds.length === 0) {
        showNotice('No messages to forge', 'error');
        return;
    }
    
    try {
        const data = await api('/forge', {
            method: 'POST',
            body: JSON.stringify({
                session_id: state.sessionId,
                message_ids: messageIds,
                title: title,
                tags: tags,
                emotional_tags: emotional,
            }),
        });
        
        if (data.success) {
            closeForgeModal();
            showNotice(`Forged: ${title}`);
            
            // Start new session
            await createSession();
        } else {
            showNotice(data.error || 'Forge failed', 'error');
        }
    } catch (err) {
        console.error('Failed to forge:', err);
        showNotice('Forge failed', 'error');
    }
}

// =============================================================================
// DORMANT MODAL
// =============================================================================

function showDormantModal(current, required) {
    document.getElementById('dormant-current').textContent = Math.floor(current);
    document.getElementById('dormant-required').textContent = required;
    document.getElementById('dormant-overlay').classList.add('active');
}

function closeDormantModal() {
    document.getElementById('dormant-overlay').classList.remove('active');
}

// =============================================================================
// SESSION HISTORY DRAWER
// =============================================================================

async function openHistoryDrawer() {
    const sessions = await fetchSessions();
    const list = document.getElementById('session-list');
    
    list.innerHTML = sessions.map(s => `
        <div class="session-item ${s.id === state.sessionId ? 'active' : ''}" 
             data-session-id="${s.id}">
            <div class="session-item-title">${escapeHtml(s.title)}</div>
            <div class="session-item-meta">
                ${s.message_count} messages · ${formatDate(s.updated_at)}
            </div>
        </div>
    `).join('') || '<p style="color: var(--text-dim);">No sessions yet</p>';
    
    // Add click handlers
    list.querySelectorAll('.session-item').forEach(item => {
        item.addEventListener('click', () => {
            loadSession(item.dataset.sessionId);
            closeHistoryDrawer();
        });
    });
    
    document.getElementById('history-overlay').classList.add('active');
}

function closeHistoryDrawer() {
    document.getElementById('history-overlay').classList.remove('active');
}

// =============================================================================
// SETTINGS DRAWER
// =============================================================================

async function openSettingsDrawer() {
    document.getElementById('settings-overlay').classList.add('active');
    await loadManaConfig();
    await loadApiKeys();
}

function closeSettingsDrawer() {
    document.getElementById('settings-overlay').classList.remove('active');
}

function applySettings() {
    // Avatar visibility
    document.body.classList.toggle('avatar-hidden', !state.settings.showAvatar);
    
    // Scanlines
    document.body.classList.toggle('scanlines-enabled', state.settings.scanlines);
    
    // Reduced motion
    document.body.classList.toggle('reduce-motion', state.settings.reduceMotion);
}

// =============================================================================
// UTILITIES
// =============================================================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-AU', { hour: '2-digit', minute: '2-digit' });
}

function formatDate(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-AU', { day: 'numeric', month: 'short' });
}

function showNotice(message, type = 'info') {
    // Use toast notification system
    showNotification(message, type);
}

// =============================================================================
// MANA PURCHASE SYSTEM
// =============================================================================

async function fetchManaBalance() {
    try {
        const response = await fetch('/api/mana/balance');
        const data = await response.json();
        
        if (data.success) {
            updateManaDisplay(data.balance, data.limits);
            updateTetherDisplay(data.config);
        }
    } catch (error) {
        console.error('[MANA] Failed to fetch balance:', error);
    }
}

function updateManaDisplay(balance, limits) {
    const regenMana = balance.regenerative_mana || 0;
    const purchasedMana = balance.purchased_mana || 0;
    const totalMana = balance.total_available || 0;
    
    // Update state for mana checks elsewhere
    state.mana = {
        current_mana: totalMana,
        regenerative_mana: regenMana,
        purchased_mana: purchasedMana
    };
    
    // Update web component attributes
    const manaBar = document.getElementById('mana-bar');
    if (manaBar) {
        manaBar.setAttribute('current', Math.floor(totalMana));
        manaBar.setAttribute('regen', Math.floor(regenMana));
        manaBar.setAttribute('purchased', Math.floor(purchasedMana));
    }
    
    // Update cost display
    updateCostDisplay();
    
    // Check for low mana warning
    if (limits && limits.daily_alert) {
        console.warn('[MANA] Daily spending limit alert');
    }
}

function updateTetherDisplay(config) {
    // Legacy function - tether display now handled by web components
    // This is called from fetchManaBalance but can be a no-op
    if (!config) return;
    console.log('[TETHERS] Config received:', config);
}

async function openPurchaseModal() {
    document.getElementById('purchase-overlay').classList.add('active');
    await loadPricingTiers();
}

function closePurchaseModal() {
    document.getElementById('purchase-overlay').classList.remove('active');
}

async function loadPricingTiers() {
    try {
        const response = await fetch('/api/mana/pricing');
        const data = await response.json();
        
        if (data.success && data.tiers) {
            const tiersContainer = document.getElementById('pricing-tiers');
            tiersContainer.innerHTML = '';
            
            data.tiers.forEach((tier, index) => {
                const tierEl = document.createElement('div');
                tierEl.className = 'pricing-tier';
                if (index === 1) tierEl.classList.add('best-value'); // Ember tier
                
                const manaFormatted = (tier.mana_amount / 1000).toFixed(0) + 'k';
                const ratePerDollar = (tier.mana_amount / tier.price_usd).toFixed(0);
                
                tierEl.innerHTML = `
                    <div class="tier-name">${tier.tier_name}</div>
                    <div class="tier-mana">${manaFormatted} mana</div>
                    <div class="tier-price">${tier.price_usd.toFixed(0)}</div>
                    <div class="tier-rate">${ratePerDollar} mana/$</div>
                `;
                
                tierEl.addEventListener('click', () => purchaseMana(tier.id));
                tiersContainer.appendChild(tierEl);
            });
        }
    } catch (error) {
        console.error('[MANA] Failed to load pricing:', error);
    }
}

async function purchaseMana(tierId) {
    try {
        const response = await fetch('/api/mana/purchase', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tier_id: tierId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('[MANA] Purchase successful:', data.purchase_id);
            
            // Get tier info for message
            const pricingResponse = await fetch('/api/mana/pricing');
            const pricingData = await pricingResponse.json();
            const tier = pricingData.tiers?.find(t => t.id === tierId);
            const manaAmount = tier ? (tier.mana_amount / 1000).toFixed(0) + 'k' : '';
            
            closePurchaseModal();
            await fetchManaBalance();
            
            // Show success message with amount
            showNotification(`+${manaAmount} mana purchased!`, 'success');
        } else {
            showNotification('Purchase failed: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('[MANA] Purchase failed:', error);
        showNotification('Purchase failed', 'error');
    }
}

async function openUsageHistoryModal() {
    document.getElementById('usage-overlay').classList.add('active');
    await loadUsageHistory();
}

function closeUsageHistoryModal() {
    document.getElementById('usage-overlay').classList.remove('active');
}

async function loadUsageHistory() {
    try {
        const response = await fetch('/api/mana/history?limit=10&days=30');
        const data = await response.json();
        
        if (data.success) {
            renderPurchaseHistory(data.purchases);
            renderUsageStats(data.usage);
        }
    } catch (error) {
        console.error('[MANA] Failed to load history:', error);
    }
}

function renderPurchaseHistory(purchases) {
    const container = document.getElementById('purchase-history');
    
    if (!purchases || purchases.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No purchases yet</p>';
        return;
    }
    
    container.innerHTML = purchases.map(purchase => {
        const date = new Date(purchase.purchase_date);
        const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        return `
            <div class="purchase-item">
                <div class="purchase-details">
                    <div class="purchase-amount">${(purchase.amount_mana / 1000).toFixed(1)}k mana</div>
                    <div class="purchase-date">${dateStr}</div>
                </div>
                <div class="purchase-price">${purchase.cost_usd.toFixed(2)}</div>
            </div>
        `;
    }).join('');
}

function renderUsageStats(usage) {
    const container = document.getElementById('usage-stats');
    
    if (!usage || !usage.totals) {
        container.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No usage data yet</p>';
        return;
    }
    
    const totals = usage.totals;
    const byOperation = usage.by_operation || [];
    
    container.innerHTML = `
        <div class="stat-group">
            <div class="stat-label">Total Mana Spent (Last 30 Days)</div>
            <div class="stat-value">${Math.floor(totals.total_spent || 0)}</div>
            <div class="stat-breakdown">
                <span>Operations: ${totals.operation_count || 0}</span>
                <span>Average per operation: ${Math.floor(totals.avg_per_operation || 0)}</span>
            </div>
        </div>
        <div class="stat-group">
            <div class="stat-label">Usage Breakdown</div>
            <div class="stat-breakdown">
                ${byOperation.slice(0, 5).map(op => `
                    <span>${op.operation}: ${Math.floor(op.spent)} mana (${op.count} ops)</span>
                `).join('')}
            </div>
        </div>
    `;
}

async function loadManaConfig() {
    try {
        const response = await fetch('/api/mana/config');
        const data = await response.json();
        
        if (data.success && data.config) {
            document.getElementById('mana-mode').value = data.config.mana_mode;
            document.getElementById('byok-max-mana').value = data.config.byok_max_mana;
            document.getElementById('byok-regen-rate').value = data.config.byok_regen_rate;
            
            toggleBYOKConfig(data.config.mana_mode);
        }
    } catch (error) {
        console.error('[MANA] Failed to load config:', error);
    }
}

function toggleBYOKConfig(mode) {
    const byokElements = document.querySelectorAll('.byok-config');
    byokElements.forEach(el => {
        el.style.display = (mode === 'byok' || mode === 'hybrid') ? 'block' : 'none';
    });
}

async function saveManaConfig() {
    const mode = document.getElementById('mana-mode').value;
    const maxMana = parseFloat(document.getElementById('byok-max-mana').value);
    const regenRate = parseFloat(document.getElementById('byok-regen-rate').value);
    
    try {
        const response = await fetch('/api/mana/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mana_mode: mode,
                byok_max_mana: maxMana,
                byok_regen_rate: regenRate
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const modeLabels = { byok: 'BYOK', mana: 'Mana', hybrid: 'Hybrid' };
            const modeLabel = modeLabels[mode] || mode;
            showNotification(`Config saved: ${modeLabel} mode`, 'success');
            await fetchManaBalance();
        } else {
            showNotification('Failed to save config', 'error');
        }
    } catch (error) {
        console.error('[MANA] Failed to save config:', error);
        showNotification('Failed to save config', 'error');
    }
}

// =============================================================================
// API KEY MANAGEMENT
// =============================================================================

async function loadApiKeys() {
    try {
        const response = await fetch('/api/mana/api-keys');
        const data = await response.json();
        
        if (data.success && data.keys) {
            // Update status indicators
            const claudeStatus = document.getElementById('claude-key-status');
            const openaiStatus = document.getElementById('openai-key-status');
            
            if (data.keys.claude) {
                claudeStatus.textContent = `Configured: ${data.keys.claude}`;
                claudeStatus.classList.add('configured');
            } else {
                claudeStatus.textContent = 'No key configured';
                claudeStatus.classList.remove('configured');
            }
            
            if (data.keys.openai) {
                openaiStatus.textContent = `Configured: ${data.keys.openai}`;
                openaiStatus.classList.add('configured');
            } else {
                openaiStatus.textContent = 'No key configured';
                openaiStatus.classList.remove('configured');
            }
        }
    } catch (error) {
        console.error('[API KEYS] Failed to load:', error);
    }
}

function toggleApiKeyVisibility(inputId) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
    } else {
        input.type = 'password';
    }
}

async function saveApiKeys() {
    const claudeKey = document.getElementById('api-key-claude').value.trim();
    const openaiKey = document.getElementById('api-key-openai').value.trim();
    
    // Validate key format (basic check)
    if (claudeKey && !claudeKey.startsWith('sk-ant-')) {
        showNotification('Claude API key should start with sk-ant-', 'warning');
        return;
    }
    
    if (openaiKey && !openaiKey.startsWith('sk-')) {
        showNotification('OpenAI API key should start with sk-', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/mana/api-keys', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                claude_key: claudeKey || null,
                openai_key: openaiKey || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('API keys saved! Reloading LLM config...', 'success');
            
            // Clear input fields
            document.getElementById('api-key-claude').value = '';
            document.getElementById('api-key-openai').value = '';
            
            // Reload LLM configuration to use new keys immediately
            try {
                const reloadResponse = await fetch('/api/llm/reload', {
                    method: 'POST'
                });
                const reloadData = await reloadResponse.json();
                
                if (reloadData.success) {
                    showNotification('Tethers activated! Config reloaded', 'success');
                    console.log('[API KEYS] LLM config reloaded:', reloadData);
                } else {
                    showNotification('Keys saved but reload failed. Restart server.', 'warning');
                }
            } catch (reloadError) {
                console.error('[API KEYS] Reload failed:', reloadError);
                showNotification('Keys saved but reload failed. Restart server.', 'warning');
            }
            
            // Reload key status and tether display
            await loadApiKeys();
            await fetchManaBalance();
        } else {
            showNotification('Failed to save API keys', 'error');
        }
    } catch (error) {
        console.error('[API KEYS] Failed to save:', error);
        showNotification('Failed to save API keys', 'error');
    }
}

async function clearApiKeys() {
    if (!confirm('Are you sure you want to clear all API keys? This will disable your LLM tethers.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/mana/api-keys', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                claude_key: null,
                openai_key: null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('All API keys cleared', 'success');
            
            // Clear input fields
            document.getElementById('api-key-claude').value = '';
            document.getElementById('api-key-openai').value = '';
            
            // Reload LLM configuration
            try {
                const reloadResponse = await fetch('/api/llm/reload', {
                    method: 'POST'
                });
                const reloadData = await reloadResponse.json();
                
                if (reloadData.success) {
                    console.log('[API KEYS] LLM config reloaded after clear');
                }
            } catch (reloadError) {
                console.error('[API KEYS] Reload failed:', reloadError);
            }
            
            // Reload status
            await loadApiKeys();
            await fetchManaBalance();
        } else {
            showNotification('Failed to clear API keys', 'error');
        }
    } catch (error) {
        console.error('[API KEYS] Failed to clear:', error);
        showNotification('Failed to clear API keys', 'error');
    }
}

function showNotification(message, type = 'info') {
    // Web Component toast - Shadow DOM handles all styling
    EhkoToast.show(message, type);
}

// =============================================================================
// EVENT LISTENERS
// =============================================================================

function initEventListeners() {
    // Model dropdown
    const modelTrigger = document.getElementById('model-trigger');
    modelTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleModelDropdown();
    });
    
    // Model options
    document.querySelectorAll('.model-option').forEach(option => {
        option.addEventListener('click', () => selectModel(option));
    });
    
    // Set first option as active on init
    const firstOption = document.querySelector('.model-option');
    if (firstOption) {
        firstOption.classList.add('active');
        updateModelCost();
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const dropdown = document.getElementById('model-dropdown');
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('open');
        }
    });
    
    // Message input
    const input = document.getElementById('message-input');
    
    // Auto-expand textarea
    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 200) + 'px';
    });
    
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Send button
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    
    // Session controls
    document.getElementById('new-session-btn').addEventListener('click', createSession);
    document.getElementById('forge-session-btn').addEventListener('click', openForgeModal);
    document.getElementById('history-btn').addEventListener('click', openHistoryDrawer);
    
    // Settings
    document.getElementById('settings-btn').addEventListener('click', openSettingsDrawer);
    document.getElementById('settings-close').addEventListener('click', closeSettingsDrawer);
    document.getElementById('settings-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'settings-overlay') closeSettingsDrawer();
    });
    
    // Settings checkboxes
    document.getElementById('setting-avatar').addEventListener('change', (e) => {
        state.settings.showAvatar = e.target.checked;
        applySettings();
    });
    document.getElementById('setting-scanlines').addEventListener('change', (e) => {
        state.settings.scanlines = e.target.checked;
        applySettings();
    });
    document.getElementById('setting-motion').addEventListener('change', (e) => {
        state.settings.reduceMotion = e.target.checked;
        applySettings();
    });
    
    // ASCII Logo toggle
    const asciiLogoCheckbox = document.getElementById('setting-ascii-logo');
    if (asciiLogoCheckbox) {
        asciiLogoCheckbox.addEventListener('change', (e) => {
            state.settings.showAsciiLogo = e.target.checked;
            const asciiSection = document.getElementById('ascii-section');
            if (asciiSection) {
                asciiSection.style.display = e.target.checked ? 'flex' : 'none';
            }
        });
    }
    
    // Settings actions
    document.getElementById('refresh-authority').addEventListener('click', refreshAuthority);
    
    // Open Tether Panel from settings
    const openTetherPanelBtn = document.getElementById('open-tether-panel');
    if (openTetherPanelBtn) {
        openTetherPanelBtn.addEventListener('click', () => {
            closeSettingsDrawer();
            openTetherPanel();
        });
    }
    
    // Refresh tethers
    const refreshTethersBtn = document.getElementById('refresh-tethers');
    if (refreshTethersBtn) {
        refreshTethersBtn.addEventListener('click', async () => {
            showNotification('Refreshing tethers...', 'info');
            await fetchTethers();
            showNotification('Tethers refreshed', 'success');
        });
    }
    
    // View usage history
    const viewUsageHistoryBtn = document.getElementById('view-usage-history');
    if (viewUsageHistoryBtn) {
        viewUsageHistoryBtn.addEventListener('click', openUsageHistoryModal);
    }
    
    // Export data
    const exportDataBtn = document.getElementById('export-data');
    if (exportDataBtn) {
        exportDataBtn.addEventListener('click', async () => {
            showNotification('Export functionality coming soon', 'info');
        });
    }
    
    // Clear all data
    const clearAllDataBtn = document.getElementById('clear-all-data');
    if (clearAllDataBtn) {
        clearAllDataBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to clear ALL local data? This cannot be undone.')) {
                return;
            }
            if (!confirm('This will remove all sessions, settings, and cached data. Continue?')) {
                return;
            }
            // Clear localStorage
            localStorage.clear();
            showNotification('Local data cleared. Reloading...', 'success');
            setTimeout(() => window.location.reload(), 1500);
        });
    }
    
    // Mana bar topup event (from web component)
    const manaBar = document.getElementById('mana-bar');
    if (manaBar) {
        manaBar.addEventListener('mana-topup', openPurchaseModal);
    }
    
    // Mana purchase system (elements may not exist)
    const manaTopupBtn = document.getElementById('mana-topup-btn');
    if (manaTopupBtn) {
        manaTopupBtn.addEventListener('click', openPurchaseModal);
    }
    const purchaseClose = document.getElementById('purchase-close');
    if (purchaseClose) {
        purchaseClose.addEventListener('click', closePurchaseModal);
    }
    const purchaseOverlay = document.getElementById('purchase-overlay');
    if (purchaseOverlay) {
        purchaseOverlay.addEventListener('click', (e) => {
            if (e.target.id === 'purchase-overlay') closePurchaseModal();
        });
    }
    
    // Usage history modal (elements may not exist)
    const usageClose = document.getElementById('usage-close');
    if (usageClose) {
        usageClose.addEventListener('click', closeUsageHistoryModal);
    }
    const usageOverlay = document.getElementById('usage-overlay');
    if (usageOverlay) {
        usageOverlay.addEventListener('click', (e) => {
            if (e.target.id === 'usage-overlay') closeUsageHistoryModal();
        });
    }
    
    // Usage tabs
    document.querySelectorAll('.usage-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const targetTab = e.target.dataset.tab;
            
            // Update tab buttons
            document.querySelectorAll('.usage-tab').forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
            
            // Update panes
            document.querySelectorAll('.usage-pane').forEach(pane => pane.classList.remove('active'));
            document.getElementById(targetTab + '-pane').classList.add('active');
        });
    });
    
    // History drawer
    document.getElementById('history-close').addEventListener('click', closeHistoryDrawer);
    document.getElementById('history-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'history-overlay') closeHistoryDrawer();
    });
    
    // Forge modal
    document.getElementById('forge-close').addEventListener('click', closeForgeModal);
    document.getElementById('forge-cancel').addEventListener('click', closeForgeModal);
    document.getElementById('forge-confirm').addEventListener('click', executeForge);
    document.getElementById('forge-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'forge-overlay') closeForgeModal();
    });
    
    // Dormant modal
    document.getElementById('dormant-ok').addEventListener('click', closeDormantModal);
    document.getElementById('dormant-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'dormant-overlay') closeDormantModal();
    });
}

// =============================================================================
// INITIALISATION
// =============================================================================

async function init() {
    console.log('[EhkoForge] Initialising...');
    
    // Apply initial settings
    document.body.classList.add('scanlines-enabled');
    applySettings();
    
    // Initialize matrix background (avatar component handles its own animations)
    initMatrixCode();
    
    // Initialize ASCII display with random acronym
    state.currentAcronym = getRandomAcronym();
    updateAsciiDisplay();
    
    // Set initial mode
    setMode('terminal');
    
    // Fetch initial data
    await Promise.all([
        fetchAuthority(),
        fetchManaBalance(),
        fetchInsiteCount(),
        loadManaConfig(),
        fetchTethers(),
    ]);
    
    // Create initial session
    await createSession();
    
    // Bind events
    initEventListeners();
    initTetherEvents();
    
    // Focus input
    document.getElementById('message-input').focus();
    
    // Periodic updates
    setInterval(fetchManaBalance, 60000);  // Update mana every minute
    setInterval(fetchInsiteCount, 120000);  // Update insite count every 2 minutes
    
    console.log('[EhkoForge] Ready');
}

// Start when DOM is ready
document.addEventListener('DOMContentLoaded', init);
