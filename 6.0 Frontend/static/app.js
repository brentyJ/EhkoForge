/**
 * EhkoForge UI Application v1.2
 * Frontend logic for the Forge interface
 * Includes Ingot system for smelt/forge pipeline
 */

// =============================================================================
// STATE
// =============================================================================

const state = {
    currentSessionId: null,
    sessions: [],
    messages: [],
    stats: {},
    config: {},
    selectedMessageIds: new Set(),
    // Ingot system
    currentMode: 'chat',  // 'chat' or 'forge'
    ingots: [],
    currentIngotId: null,
    currentIngot: null,
    smeltStatus: {},
    ehkoStatus: {},
};

// =============================================================================
// API FUNCTIONS - SESSIONS & MESSAGES
// =============================================================================

async function fetchSessions() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();
        state.sessions = data.sessions;
        return data.sessions;
    } catch (error) {
        console.error('Failed to fetch sessions:', error);
        return [];
    }
}

async function createSession(title = 'New Session') {
    try {
        const response = await fetch('/api/sessions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title })
        });
        const session = await response.json();
        state.sessions.unshift(session);
        return session;
    } catch (error) {
        console.error('Failed to create session:', error);
        return null;
    }
}

async function fetchMessages(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}/messages`);
        const data = await response.json();
        state.messages = data.messages;
        return data.messages;
    } catch (error) {
        console.error('Failed to fetch messages:', error);
        return [];
    }
}

async function sendMessage(sessionId, content) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: 'user', content })
        });
        const data = await response.json();
        state.messages.push(...data.messages);
        return data.messages;
    } catch (error) {
        console.error('Failed to send message:', error);
        return null;
    }
}

async function forgeMessages(sessionId, messageIds, title, tags, emotionalTags) {
    try {
        const response = await fetch('/api/forge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                message_ids: messageIds,
                title: title,
                tags: tags,
                emotional_tags: emotionalTags
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to forge messages:', error);
        return { success: false, error: error.message };
    }
}

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        state.stats = await response.json();
        return state.stats;
    } catch (error) {
        console.error('Failed to fetch stats:', error);
        return {};
    }
}

async function fetchConfig() {
    try {
        const response = await fetch('/api/config');
        state.config = await response.json();
        return state.config;
    } catch (error) {
        console.error('Failed to fetch config:', error);
        return {};
    }
}

async function updateConfig(settings) {
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        state.config = await response.json();
        return state.config;
    } catch (error) {
        console.error('Failed to update config:', error);
        return state.config;
    }
}

// =============================================================================
// API FUNCTIONS - INGOTS
// =============================================================================

async function fetchIngots(status = 'surfaced', minSignificance = 0) {
    try {
        const response = await fetch(`/api/ingots?status=${status}&min_significance=${minSignificance}`);
        const data = await response.json();
        state.ingots = data.ingots;
        return data.ingots;
    } catch (error) {
        console.error('Failed to fetch ingots:', error);
        return [];
    }
}

async function fetchIngotDetail(ingotId) {
    try {
        const response = await fetch(`/api/ingots/${ingotId}`);
        const data = await response.json();
        state.currentIngot = data;
        return data;
    } catch (error) {
        console.error('Failed to fetch ingot detail:', error);
        return null;
    }
}

async function forgeIngot(ingotId) {
    try {
        const response = await fetch(`/api/ingots/${ingotId}/forge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to forge ingot:', error);
        return { success: false, error: error.message };
    }
}

async function rejectIngot(ingotId) {
    try {
        const response = await fetch(`/api/ingots/${ingotId}/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to reject ingot:', error);
        return { success: false, error: error.message };
    }
}

async function fetchSmeltStatus() {
    try {
        const response = await fetch('/api/smelt/status');
        const data = await response.json();
        state.smeltStatus = data;
        return data;
    } catch (error) {
        console.error('Failed to fetch smelt status:', error);
        return {};
    }
}

async function runSmelt(limit = 10) {
    try {
        const response = await fetch('/api/smelt/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ limit })
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to run smelt:', error);
        return { success: false, error: error.message };
    }
}

async function queueSessionForSmelt(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}/smelt`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to queue session for smelt:', error);
        return { success: false, error: error.message };
    }
}

async function fetchEhkoStatus() {
    try {
        const response = await fetch('/api/ehko/status');
        const data = await response.json();
        state.ehkoStatus = data;
        return data;
    } catch (error) {
        console.error('Failed to fetch Ehko status:', error);
        return {};
    }
}

// =============================================================================
// RENDER FUNCTIONS - SESSIONS & MESSAGES
// =============================================================================

function renderSidebar() {
    const container = document.getElementById('sessions-list');
    
    if (state.sessions.length === 0) {
        container.innerHTML = `
            <div class="empty-sessions">
                <p style="color: var(--text-muted); padding: 20px; text-align: center; font-size: 0.85rem;">
                    No sessions yet
                </p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = state.sessions.map(session => {
        const isActive = session.id === state.currentSessionId;
        const date = new Date(session.updated_at);
        const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const dateStr = date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        
        const tagsHtml = session.session_tags.length > 0 
            ? `<div class="session-tags">
                ${session.session_tags.map(tag => `<span class="session-tag">${tag}</span>`).join('')}
               </div>`
            : '';
        
        return `
            <div class="session-item ${isActive ? 'is-active' : ''}" 
                 data-session-id="${session.id}"
                 onclick="handleSessionClick('${session.id}')">
                <div class="session-title">${escapeHtml(session.title)}</div>
                <div class="session-meta">
                    <span>${session.message_count} messages</span>
                    <span>•</span>
                    <span>${dateStr} ${timeStr}</span>
                </div>
                ${tagsHtml}
            </div>
        `;
    }).join('');
}

function renderMessages() {
    const container = document.getElementById('chat-messages');
    
    if (state.messages.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>Begin a new session to start forging.</p>
                <p class="subtle">Your reflections become part of the Ehko.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = state.messages.map(msg => {
        const isUser = msg.role === 'user';
        const time = new Date(msg.timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        const isSelected = state.selectedMessageIds.has(msg.id);
        
        return `
            <div class="message message--${msg.role} ${msg.forged ? 'is-forged' : ''} ${isSelected ? 'is-selected' : ''}"
                 data-message-id="${msg.id}">
                <div class="message-content">${escapeHtml(msg.content)}</div>
                <div class="message-meta">
                    <span class="message-time">${time}</span>
                    <div class="message-actions">
                        ${!msg.forged ? `
                            <button class="message-action" onclick="toggleMessageSelection(${msg.id})" title="Select for forging">
                                ${isSelected ? '✓' : '○'}
                            </button>
                        ` : ''}
                        ${msg.forged ? '<span style="color: var(--accent-gold);">Forged</span>' : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    scrollToBottom();
}

function renderStats() {
    const ribbon = document.getElementById('stats-ribbon');
    const statElements = ribbon.querySelectorAll('.stat');
    
    statElements.forEach(el => {
        const statName = el.dataset.stat;
        const value = state.stats[statName] || 0;
        
        let intensity = 'low';
        if (value > 0.3) intensity = 'medium';
        if (value > 0.6) intensity = 'high';
        
        el.dataset.intensity = intensity;
    });
}

// =============================================================================
// RENDER FUNCTIONS - INGOTS
// =============================================================================

function renderIngotList() {
    const container = document.getElementById('ingot-list');
    const badge = document.getElementById('ingot-badge');
    
    // Update badge
    if (state.ingots.length > 0) {
        badge.textContent = state.ingots.length;
        badge.style.display = 'inline-flex';
    } else {
        badge.style.display = 'none';
    }
    
    if (state.ingots.length === 0) {
        container.innerHTML = `
            <div class="empty-ingots">
                <p style="color: var(--text-muted); padding: 20px; text-align: center; font-size: 0.85rem;">
                    No surfaced ingots yet
                </p>
                <p style="color: var(--text-muted); padding: 0 20px; text-align: center; font-size: 0.75rem;">
                    Chat sessions are smelted to extract insights
                </p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = state.ingots.map(ingot => {
        const isActive = ingot.id === state.currentIngotId;
        const tierClass = `tier-${ingot.significance_tier}`;
        const themes = ingot.themes.slice(0, 3).join(', ');
        
        return `
            <div class="ingot-item ${isActive ? 'is-active' : ''} ${tierClass}" 
                 data-ingot-id="${ingot.id}"
                 onclick="handleIngotClick('${ingot.id}')">
                <div class="ingot-tier-badge">${getTierIcon(ingot.significance_tier)}</div>
                <div class="ingot-summary">${escapeHtml(ingot.summary.slice(0, 80))}${ingot.summary.length > 80 ? '...' : ''}</div>
                <div class="ingot-meta">
                    <span class="ingot-themes">${themes || 'No themes'}</span>
                    <span class="ingot-sources">${ingot.source_count} source${ingot.source_count !== 1 ? 's' : ''}</span>
                </div>
            </div>
        `;
    }).join('');
}

function getTierIcon(tier) {
    const icons = {
        mythic: '💎',
        gold: '🥇',
        silver: '🥈',
        iron: '⚙️',
        copper: '🔶'
    };
    return icons[tier] || '◇';
}

function renderIngotDetail() {
    const container = document.getElementById('ingot-detail');
    const ingot = state.currentIngot;
    
    if (!ingot) {
        container.innerHTML = `
            <div class="ingot-empty">
                <p>Select an ingot from the queue to review.</p>
                <p class="subtle">Accept valuable insights to forge them into your Ehko.</p>
            </div>
        `;
        return;
    }
    
    const themes = ingot.themes.map(t => `<span class="theme-tag">${t}</span>`).join('');
    const emotions = ingot.emotional_tags.map(e => `<span class="emotion-tag">${e}</span>`).join('');
    const patterns = ingot.patterns.map(p => `<span class="pattern-tag">${p}</span>`).join('');
    
    const sources = ingot.sources ? ingot.sources.map(s => `
        <div class="source-item">
            <div class="source-type">${s.type}</div>
            <div class="source-title">${escapeHtml(s.title)}</div>
            ${s.excerpt ? `<div class="source-excerpt">"${escapeHtml(s.excerpt)}"</div>` : ''}
        </div>
    `).join('') : '<p class="subtle">No sources linked</p>';
    
    container.innerHTML = `
        <div class="ingot-detail-content">
            <div class="ingot-header">
                <span class="ingot-tier-large tier-${ingot.significance_tier}">${getTierIcon(ingot.significance_tier)} ${ingot.significance_tier.toUpperCase()}</span>
                <span class="ingot-significance">${Math.round(ingot.significance * 100)}% significance</span>
            </div>
            
            <div class="ingot-summary-full">
                <h3>Summary</h3>
                <p>${escapeHtml(ingot.summary)}</p>
            </div>
            
            <div class="ingot-tags-section">
                <div class="tag-group">
                    <h4>Themes</h4>
                    <div class="tag-list">${themes || '<span class="subtle">None</span>'}</div>
                </div>
                <div class="tag-group">
                    <h4>Emotions</h4>
                    <div class="tag-list">${emotions || '<span class="subtle">None</span>'}</div>
                </div>
                <div class="tag-group">
                    <h4>Patterns</h4>
                    <div class="tag-list">${patterns || '<span class="subtle">None</span>'}</div>
                </div>
            </div>
            
            <div class="ingot-sources-section">
                <h4>Sources (${ingot.source_count})</h4>
                <div class="sources-list">${sources}</div>
            </div>
            
            <div class="ingot-actions-inline">
                <button class="action-btn reject" onclick="handleRejectIngot('${ingot.id}')">
                    <span>✗</span> Reject
                </button>
                <button class="action-btn accept" onclick="handleForgeIngot('${ingot.id}')">
                    <span>◈</span> Forge into Ehko
                </button>
            </div>
        </div>
    `;
}

function renderSmeltStatus() {
    const container = document.getElementById('smelt-pending');
    const status = state.smeltStatus;
    
    const pending = status.queue?.pending?.count || 0;
    container.textContent = `${pending} pending`;
}

function renderEhkoStatus() {
    const container = document.getElementById('ehko-state');
    const avatar = document.getElementById('avatar');
    const status = state.ehkoStatus;
    
    const stateText = container.querySelector('.state-text');
    const stateIcon = container.querySelector('.state-icon');
    
    const state_name = status.state || 'nascent';
    stateText.textContent = state_name.charAt(0).toUpperCase() + state_name.slice(1);
    
    // Update avatar based on state
    avatar.className = 'avatar';
    avatar.classList.add(`ehko-${state_name}`);
    
    // State icons
    const icons = {
        nascent: '◇',
        forming: '◈',
        emerging: '✦',
        present: '★'
    };
    stateIcon.textContent = icons[state_name] || '◇';
    
    // Update title
    container.title = `Ehko: ${status.forged_count || 0} ingots forged, ${status.layer_count || 0} personality layers`;
}

// =============================================================================
// MODE SWITCHING
// =============================================================================

function switchMode(mode) {
    state.currentMode = mode;
    
    // Update buttons
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('is-active', btn.dataset.mode === mode);
    });
    
    // Update sidebars
    document.getElementById('chat-sidebar').style.display = mode === 'chat' ? 'flex' : 'none';
    document.getElementById('forge-sidebar').style.display = mode === 'forge' ? 'flex' : 'none';
    
    // Update main panels
    document.getElementById('chat-area').style.display = mode === 'chat' ? 'flex' : 'none';
    document.getElementById('input-bar').style.display = mode === 'chat' ? 'flex' : 'none';
    document.getElementById('ingot-area').style.display = mode === 'forge' ? 'flex' : 'none';
    
    // Refresh data for mode
    if (mode === 'forge') {
        refreshForgeMode();
    }
}

async function refreshForgeMode() {
    await fetchIngots();
    renderIngotList();
    
    await fetchSmeltStatus();
    renderSmeltStatus();
    
    await fetchEhkoStatus();
    renderEhkoStatus();
}

// =============================================================================
// CONFIG & STYLING
// =============================================================================

function applyConfig() {
    const body = document.body;
    const avatarZone = document.getElementById('avatar-zone');
    
    // Theme
    body.classList.remove('theme-arcane-blue', 'theme-ember-gold');
    if (state.config.theme === 'arcane-blue') {
        body.classList.add('theme-arcane-blue');
    } else if (state.config.theme === 'ember-gold') {
        body.classList.add('theme-ember-gold');
    }
    
    // Avatar visibility
    if (avatarZone) {
        avatarZone.classList.toggle('is-hidden', !state.config.avatar_visible);
    }
    
    // Low motion
    body.classList.toggle('low-motion', state.config.low_motion_mode);
    
    // High contrast
    body.classList.toggle('high-contrast', state.config.high_contrast_mode);
    
    // Update settings UI
    const settingAvatar = document.getElementById('setting-avatar');
    const settingMotion = document.getElementById('setting-motion');
    const settingContrast = document.getElementById('setting-contrast');
    const settingTheme = document.getElementById('setting-theme');
    
    if (settingAvatar) settingAvatar.checked = state.config.avatar_visible;
    if (settingMotion) settingMotion.checked = state.config.low_motion_mode;
    if (settingContrast) settingContrast.checked = state.config.high_contrast_mode;
    if (settingTheme) settingTheme.value = state.config.theme || 'forge-dark';
}

// =============================================================================
// UI HELPERS
// =============================================================================

function scrollToBottom() {
    const container = document.getElementById('chat-messages');
    container.scrollTop = container.scrollHeight;
}

function showThinkingIndicator() {
    const avatarZone = document.getElementById('avatar-zone');
    const status = document.getElementById('avatar-status');
    avatarZone.classList.add('is-thinking');
    status.textContent = 'Thinking...';
}

function hideThinkingIndicator() {
    const avatarZone = document.getElementById('avatar-zone');
    const status = document.getElementById('avatar-status');
    avatarZone.classList.remove('is-thinking');
    status.textContent = 'Ready';
}

function animateForge(messageId) {
    const messageEl = document.querySelector(`[data-message-id="${messageId}"]`);
    if (messageEl) {
        messageEl.classList.add('is-forging');
        setTimeout(() => {
            messageEl.classList.remove('is-forging');
            messageEl.classList.add('is-forged');
        }, 1000);
    }
}

function pulseStat(statName) {
    const statEl = document.querySelector(`[data-stat="${statName}"]`);
    if (statEl) {
        statEl.classList.add('is-pulsing');
        setTimeout(() => statEl.classList.remove('is-pulsing'), 1000);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}

// =============================================================================
// EVENT HANDLERS - SESSIONS & MESSAGES
// =============================================================================

async function handleSessionClick(sessionId) {
    state.currentSessionId = sessionId;
    state.selectedMessageIds.clear();
    
    renderSidebar();
    await fetchMessages(sessionId);
    renderMessages();
    await updateConfig({ last_session_id: sessionId });
}

async function handleNewSession() {
    const session = await createSession();
    if (session) {
        await handleSessionClick(session.id);
    }
}

async function handleSendMessage() {
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    
    if (!content) return;
    if (!state.currentSessionId) {
        await handleNewSession();
    }
    
    input.value = '';
    autoResizeTextarea(input);
    
    showThinkingIndicator();
    const messages = await sendMessage(state.currentSessionId, content);
    hideThinkingIndicator();
    
    if (messages) {
        renderMessages();
        renderSidebar();
    }
}

function toggleMessageSelection(messageId) {
    if (state.selectedMessageIds.has(messageId)) {
        state.selectedMessageIds.delete(messageId);
    } else {
        state.selectedMessageIds.add(messageId);
    }
    renderMessages();
    updateForgeCount();
}

function updateForgeCount() {
    const countEl = document.getElementById('forge-count');
    if (countEl) {
        countEl.textContent = state.selectedMessageIds.size;
    }
}

// =============================================================================
// EVENT HANDLERS - INGOTS
// =============================================================================

async function handleIngotClick(ingotId) {
    state.currentIngotId = ingotId;
    renderIngotList();
    
    await fetchIngotDetail(ingotId);
    renderIngotDetail();
}

async function handleForgeIngot(ingotId) {
    const result = await forgeIngot(ingotId);
    
    if (result.success) {
        // Refresh lists
        await fetchIngots();
        renderIngotList();
        
        // Clear detail
        state.currentIngotId = null;
        state.currentIngot = null;
        renderIngotDetail();
        
        // Update Ehko status
        await fetchEhkoStatus();
        renderEhkoStatus();
        
        // Pulse stats
        pulseStat('anchors');
        
        console.log('Ingot forged:', result);
    } else {
        alert('Failed to forge ingot: ' + (result.error || 'Unknown error'));
    }
}

async function handleRejectIngot(ingotId) {
    const result = await rejectIngot(ingotId);
    
    if (result.success) {
        // Refresh lists
        await fetchIngots();
        renderIngotList();
        
        // Clear detail
        state.currentIngotId = null;
        state.currentIngot = null;
        renderIngotDetail();
        
        console.log('Ingot rejected:', result);
    } else {
        alert('Failed to reject ingot: ' + (result.error || 'Unknown error'));
    }
}

async function handleRunSmelt() {
    const btn = document.getElementById('run-smelt');
    btn.disabled = true;
    btn.textContent = '⏳ Smelting...';
    
    try {
        const result = await runSmelt(10);
        
        if (result.success) {
            console.log('Smelt complete:', result);
            
            // Refresh everything
            await fetchSmeltStatus();
            renderSmeltStatus();
            
            await fetchIngots();
            renderIngotList();
        } else {
            alert('Smelt failed: ' + (result.error || 'Unknown error'));
        }
    } finally {
        btn.disabled = false;
        btn.textContent = '⚒️ Smelt';
    }
}

// =============================================================================
// MODAL HANDLERS
// =============================================================================

function openForgeModal() {
    if (state.selectedMessageIds.size === 0) {
        alert('Select messages to forge by clicking the ○ button on each message.');
        return;
    }
    
    const overlay = document.getElementById('forge-overlay');
    overlay.classList.add('is-visible');
    updateForgeCount();
    document.getElementById('forge-title').focus();
}

function closeForgeModal() {
    const overlay = document.getElementById('forge-overlay');
    overlay.classList.remove('is-visible');
}

async function handleForgeConfirm() {
    const title = document.getElementById('forge-title').value.trim() || 'Untitled Reflection';
    const tagsStr = document.getElementById('forge-tags').value;
    const emotionalStr = document.getElementById('forge-emotional').value;
    
    const tags = tagsStr.split(',').map(t => t.trim()).filter(t => t);
    const emotionalTags = emotionalStr.split(',').map(t => t.trim()).filter(t => t);
    
    const messageIds = Array.from(state.selectedMessageIds);
    
    const result = await forgeMessages(
        state.currentSessionId,
        messageIds,
        title,
        tags,
        emotionalTags
    );
    
    if (result.success) {
        messageIds.forEach(id => animateForge(id));
        
        state.messages = state.messages.map(msg => {
            if (messageIds.includes(msg.id)) {
                return { ...msg, forged: true };
            }
            return msg;
        });
        
        state.selectedMessageIds.clear();
        closeForgeModal();
        pulseStat('anchors');
        renderMessages();
        
        await fetchStats();
        renderStats();
        
        console.log('Forged to:', result.reflection_path);
    } else {
        alert('Failed to forge: ' + (result.error || 'Unknown error'));
    }
}

function openSettings() {
    const overlay = document.getElementById('settings-overlay');
    overlay.classList.add('is-visible');
}

function closeSettings() {
    const overlay = document.getElementById('settings-overlay');
    overlay.classList.remove('is-visible');
}

async function handleSettingChange(setting, value) {
    const updates = { [setting]: value };
    await updateConfig(updates);
    applyConfig();
}

function openIngotModal() {
    const overlay = document.getElementById('ingot-overlay');
    overlay.classList.add('is-visible');
}

function closeIngotModal() {
    const overlay = document.getElementById('ingot-overlay');
    overlay.classList.remove('is-visible');
}

// =============================================================================
// KEYBOARD SHORTCUTS
// =============================================================================

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const input = document.getElementById('message-input');
            if (document.activeElement === input) {
                e.preventDefault();
                handleSendMessage();
            }
        }
        
        if (e.key === 'Escape') {
            closeSettings();
            closeForgeModal();
            closeIngotModal();
        }
        
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            if (state.selectedMessageIds.size > 0) {
                e.preventDefault();
                openForgeModal();
            }
        }
        
        // Tab to switch modes
        if (e.key === 'Tab' && !e.target.closest('input, textarea, select')) {
            e.preventDefault();
            switchMode(state.currentMode === 'chat' ? 'forge' : 'chat');
        }
    });
}

// =============================================================================
// EVENT LISTENERS
// =============================================================================

function setupEventListeners() {
    // Mode toggle
    document.getElementById('mode-chat').addEventListener('click', () => switchMode('chat'));
    document.getElementById('mode-forge').addEventListener('click', () => switchMode('forge'));
    
    // New session button
    document.getElementById('new-session-btn').addEventListener('click', handleNewSession);
    
    // Send button
    document.getElementById('send-btn').addEventListener('click', handleSendMessage);
    
    // Message input
    const input = document.getElementById('message-input');
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    input.addEventListener('input', () => autoResizeTextarea(input));
    
    // Settings
    document.getElementById('settings-toggle').addEventListener('click', openSettings);
    document.getElementById('close-settings').addEventListener('click', closeSettings);
    document.getElementById('settings-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'settings-overlay') closeSettings();
    });
    
    // Settings changes
    document.getElementById('setting-avatar').addEventListener('change', (e) => {
        handleSettingChange('avatar_visible', e.target.checked);
    });
    document.getElementById('setting-motion').addEventListener('change', (e) => {
        handleSettingChange('low_motion_mode', e.target.checked);
    });
    document.getElementById('setting-contrast').addEventListener('change', (e) => {
        handleSettingChange('high_contrast_mode', e.target.checked);
    });
    document.getElementById('setting-theme').addEventListener('change', (e) => {
        handleSettingChange('theme', e.target.value);
    });
    
    // Forge modal
    document.getElementById('close-forge').addEventListener('click', closeForgeModal);
    document.getElementById('forge-cancel').addEventListener('click', closeForgeModal);
    document.getElementById('forge-confirm').addEventListener('click', handleForgeConfirm);
    document.getElementById('forge-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'forge-overlay') closeForgeModal();
    });
    
    // Ingot modal
    document.getElementById('close-ingot-modal').addEventListener('click', closeIngotModal);
    document.getElementById('ingot-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'ingot-overlay') closeIngotModal();
    });
    
    // Ingot actions in modal
    document.getElementById('ingot-accept').addEventListener('click', () => {
        if (state.currentIngotId) {
            handleForgeIngot(state.currentIngotId);
            closeIngotModal();
        }
    });
    document.getElementById('ingot-reject').addEventListener('click', () => {
        if (state.currentIngotId) {
            handleRejectIngot(state.currentIngotId);
            closeIngotModal();
        }
    });
    document.getElementById('ingot-defer').addEventListener('click', closeIngotModal);
    
    // Smelt controls
    document.getElementById('run-smelt').addEventListener('click', handleRunSmelt);
    document.getElementById('refresh-ingots').addEventListener('click', refreshForgeMode);
    
    // Add forge button to chat area
    addForgeButton();
    
    // Keyboard shortcuts
    setupKeyboardShortcuts();
}

function addForgeButton() {
    const chatArea = document.querySelector('.chat-area');
    const forgeBtn = document.createElement('button');
    forgeBtn.className = 'floating-forge-btn';
    forgeBtn.innerHTML = '◈ Forge Selected';
    forgeBtn.title = 'Forge selected messages to vault (Ctrl+F)';
    forgeBtn.style.cssText = `
        position: absolute;
        bottom: 80px;
        right: 20px;
        background: linear-gradient(135deg, var(--accent-gold), #b8944f);
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        color: var(--bg-primary);
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 10;
        box-shadow: 0 4px 15px var(--glow-gold);
    `;
    
    forgeBtn.addEventListener('click', openForgeModal);
    chatArea.style.position = 'relative';
    chatArea.appendChild(forgeBtn);
    
    setInterval(() => {
        const hasSelection = state.selectedMessageIds.size > 0;
        forgeBtn.style.opacity = hasSelection ? '1' : '0';
        forgeBtn.style.visibility = hasSelection ? 'visible' : 'hidden';
        if (hasSelection) {
            forgeBtn.innerHTML = `◈ Forge ${state.selectedMessageIds.size} Selected`;
        }
    }, 100);
}

// =============================================================================
// INITIALISATION
// =============================================================================

async function init() {
    console.log('EhkoForge UI v1.2 initialising...');
    
    // Load config and apply
    await fetchConfig();
    applyConfig();
    
    // Load sessions
    await fetchSessions();
    renderSidebar();
    
    // Load stats
    await fetchStats();
    renderStats();
    
    // Load Ehko status
    await fetchEhkoStatus();
    renderEhkoStatus();
    
    // Load ingots (for badge count)
    await fetchIngots();
    renderIngotList();
    
    // Load last session if exists
    if (state.config.last_session_id) {
        const sessionExists = state.sessions.some(s => s.id === state.config.last_session_id);
        if (sessionExists) {
            await handleSessionClick(state.config.last_session_id);
        }
    }
    
    // Setup event listeners
    setupEventListeners();
    
    console.log('EhkoForge UI ready');
}

// Start app when DOM is ready
document.addEventListener('DOMContentLoaded', init);
