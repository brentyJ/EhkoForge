/**
 * EhkoForge Main JavaScript v2.0
 * Phase 2: UI Consolidation
 * 
 * Single terminal interface with mode toggle
 */

// =============================================================================
// STATE
// =============================================================================

const state = {
    mode: 'terminal',  // 'terminal' or 'reflection'
    sessionId: null,
    messages: [],
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
    try {
        const data = await api('/mana');
        state.mana = data;
        updateManaDisplay(data);
    } catch (err) {
        console.error('Failed to fetch mana:', err);
    }
}

function updateManaDisplay(mana) {
    const current = Math.floor(mana.current_mana || 0);
    const max = mana.max_mana || 100;
    const pct = (current / max) * 100;
    
    document.getElementById('mana-current').textContent = current;
    document.getElementById('mana-max').textContent = max;
    document.getElementById('mana-regen').textContent = `+${mana.regen_rate || 1}/hr`;
    
    const fill = document.getElementById('mana-fill');
    fill.style.width = `${pct}%`;
    fill.classList.toggle('low', pct < 20);
    
    // Update cost display for current mode
    updateCostDisplay();
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
        state.mana = data.mana;
        updateManaDisplay(data.mana);
        showNotice('Mana refilled');
    } catch (err) {
        console.error('Failed to refill mana:', err);
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
    
    // Update buttons
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
    
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
    
    // Update cost display
    updateCostDisplay();
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
        document.getElementById('session-title').textContent = data.title;
        clearMessages();
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

function showWelcome() {
    const output = document.getElementById('terminal-output');
    output.innerHTML = `
        <div class="welcome-message">
            <pre class="ascii-art">
╔═══════════════════════════════════════════════════════════════╗
║  ███████╗██╗  ██╗██╗  ██╗ ██████╗                             ║
║  ██╔════╝██║  ██║██║ ██╔╝██╔═══██╗                            ║
║  █████╗  ███████║█████╔╝ ██║   ██║                            ║
║  ██╔══╝  ██╔══██║██╔═██╗ ██║   ██║                            ║
║  ███████╗██║  ██║██║  ██╗╚██████╔╝                            ║
║  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝                             ║
╚═══════════════════════════════════════════════════════════════╝
            </pre>
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
    
    // Clear input
    input.value = '';
    
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
    
    const div = document.createElement('div');
    div.className = `message ${msg.role}`;
    div.innerHTML = `
        <span class="message-content">${escapeHtml(msg.content)}</span>
        <div class="message-timestamp">${formatTime(msg.timestamp)}</div>
    `;
    
    output.appendChild(div);
    scrollToBottom();
}

function showTyping() {
    const output = document.getElementById('terminal-output');
    const existing = output.querySelector('.typing-indicator');
    if (existing) return;
    
    const div = document.createElement('div');
    div.className = 'typing-indicator';
    div.innerHTML = `
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    output.appendChild(div);
    scrollToBottom();
}

function hideTyping() {
    const typing = document.querySelector('.typing-indicator');
    if (typing) typing.remove();
}

function scrollToBottom() {
    const output = document.getElementById('terminal-output');
    output.scrollTop = output.scrollHeight;
}

// =============================================================================
// AVATAR
// =============================================================================

function setAvatarState(status) {
    const avatar = document.getElementById('avatar');
    const statusEl = document.getElementById('avatar-status');
    
    avatar.classList.remove('thinking', 'dormant');
    
    switch (status) {
        case 'thinking':
            avatar.classList.add('thinking');
            statusEl.textContent = 'Thinking...';
            break;
        case 'dormant':
            avatar.classList.add('dormant');
            statusEl.textContent = 'Resting';
            break;
        default:
            statusEl.textContent = 'Ready';
    }
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

function openSettingsDrawer() {
    document.getElementById('settings-overlay').classList.add('active');
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
    // Simple notice - could be enhanced with a toast system
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // For now, update avatar status briefly
    const statusEl = document.getElementById('avatar-status');
    const original = statusEl.textContent;
    statusEl.textContent = message;
    setTimeout(() => {
        statusEl.textContent = original;
    }, 2000);
}

// =============================================================================
// EVENT LISTENERS
// =============================================================================

function initEventListeners() {
    // Mode toggle
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => setMode(btn.dataset.mode));
    });
    
    // Message input
    const input = document.getElementById('message-input');
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
    
    // Settings actions
    document.getElementById('refresh-authority').addEventListener('click', refreshAuthority);
    document.getElementById('refill-mana').addEventListener('click', refillMana);
    
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
    
    // Set initial mode
    setMode('terminal');
    
    // Fetch initial data
    await Promise.all([
        fetchAuthority(),
        fetchMana(),
        fetchInsiteCount(),
    ]);
    
    // Create initial session
    await createSession();
    
    // Bind events
    initEventListeners();
    
    // Focus input
    document.getElementById('message-input').focus();
    
    // Periodic updates
    setInterval(fetchMana, 60000);  // Update mana every minute
    setInterval(fetchInsiteCount, 120000);  // Update insite count every 2 minutes
    
    console.log('[EhkoForge] Ready');
}

// Start when DOM is ready
document.addEventListener('DOMContentLoaded', init);
