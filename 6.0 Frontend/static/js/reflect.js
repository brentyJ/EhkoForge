/**
 * EhkoForge Reflect JavaScript v2.0
 * Handles reflection chat, sessions, and forge-to-vault functionality
 */

// =============================================================================
// STATE
// =============================================================================

const ReflectState = {
    currentSessionId: null,
    sessions: [],
    messages: [],
    selectedMessageIds: new Set(),
};

// =============================================================================
// API FUNCTIONS
// =============================================================================

async function fetchSessions() {
    try {
        const data = await fetchAPI('/api/sessions');
        ReflectState.sessions = data.sessions;
        return data.sessions;
    } catch (error) {
        console.error('Failed to fetch sessions:', error);
        return [];
    }
}

async function createSession(title = 'New Session') {
    try {
        const data = await fetchAPI('/api/sessions', {
            method: 'POST',
            body: JSON.stringify({ title }),
        });
        ReflectState.sessions.unshift(data);
        return data;
    } catch (error) {
        console.error('Failed to create session:', error);
        return null;
    }
}

async function fetchMessages(sessionId) {
    try {
        const data = await fetchAPI(`/api/sessions/${sessionId}/messages`);
        ReflectState.messages = data.messages;
        return data.messages;
    } catch (error) {
        console.error('Failed to fetch messages:', error);
        return [];
    }
}

async function sendMessage(sessionId, content) {
    try {
        const data = await fetchAPI(`/api/sessions/${sessionId}/messages`, {
            method: 'POST',
            body: JSON.stringify({ role: 'user', content }),
        });
        ReflectState.messages.push(...data.messages);
        return data.messages;
    } catch (error) {
        console.error('Failed to send message:', error);
        return null;
    }
}

async function forgeMessages(sessionId, messageIds, title, tags, emotionalTags) {
    try {
        return await fetchAPI('/api/forge', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                message_ids: messageIds,
                title,
                tags,
                emotional_tags: emotionalTags,
            }),
        });
    } catch (error) {
        console.error('Failed to forge messages:', error);
        return { success: false, error: error.message };
    }
}

// =============================================================================
// RENDER FUNCTIONS
// =============================================================================

function renderSessions() {
    const container = document.getElementById('sessions-list');
    if (!container) return;
    
    if (ReflectState.sessions.length === 0) {
        container.innerHTML = `
            <div class="empty-sessions">
                <p style="color: var(--text-muted); padding: 20px; text-align: center; font-size: 0.85rem;">
                    No sessions yet
                </p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = ReflectState.sessions.map(session => {
        const isActive = session.id === ReflectState.currentSessionId;
        const date = new Date(session.updated_at);
        const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const dateStr = date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        
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
            </div>
        `;
    }).join('');
}

function renderMessages() {
    const container = document.getElementById('chat-messages');
    if (!container) return;
    
    if (ReflectState.messages.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>Begin a new session to start reflecting.</p>
                <p class="subtle">Your reflections become part of the Ehko.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = ReflectState.messages.map(msg => {
        const time = formatTimestamp(msg.timestamp);
        const isSelected = ReflectState.selectedMessageIds.has(msg.id);
        
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
                        ${msg.forged ? '<span style="color: var(--warning);">Forged</span>' : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    scrollToBottom();
}

function scrollToBottom() {
    const container = document.getElementById('chat-messages');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

// =============================================================================
// EVENT HANDLERS
// =============================================================================

async function handleSessionClick(sessionId) {
    ReflectState.currentSessionId = sessionId;
    ReflectState.selectedMessageIds.clear();
    
    renderSessions();
    await fetchMessages(sessionId);
    renderMessages();
    
    // Update config with last session
    updateConfig({ last_session_id: sessionId });
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
    
    // Create session if none exists
    if (!ReflectState.currentSessionId) {
        await handleNewSession();
    }
    
    input.value = '';
    autoResizeTextarea(input);
    
    setAvatarThinking(true);
    const messages = await sendMessage(ReflectState.currentSessionId, content);
    setAvatarThinking(false);
    
    if (messages) {
        renderMessages();
        renderSessions(); // Update message count
    }
}

function toggleMessageSelection(messageId) {
    if (ReflectState.selectedMessageIds.has(messageId)) {
        ReflectState.selectedMessageIds.delete(messageId);
    } else {
        ReflectState.selectedMessageIds.add(messageId);
    }
    renderMessages();
    updateForgeButton();
}

function updateForgeButton() {
    const count = ReflectState.selectedMessageIds.size;
    const forgeBtn = document.getElementById('floating-forge-btn');
    
    if (forgeBtn) {
        if (count > 0) {
            forgeBtn.classList.add('is-visible');
            forgeBtn.textContent = `◈ Forge ${count} Selected`;
        } else {
            forgeBtn.classList.remove('is-visible');
        }
    }
}

// =============================================================================
// FORGE MODAL
// =============================================================================

function openForgeModal() {
    if (ReflectState.selectedMessageIds.size === 0) {
        alert('Select messages to forge by clicking the ○ button on each message.');
        return;
    }
    
    const overlay = document.getElementById('forge-overlay');
    overlay?.classList.add('is-visible');
    
    const countEl = document.getElementById('forge-count');
    if (countEl) countEl.textContent = ReflectState.selectedMessageIds.size;
    
    document.getElementById('forge-title')?.focus();
}

function closeForgeModal() {
    const overlay = document.getElementById('forge-overlay');
    overlay?.classList.remove('is-visible');
}

async function handleForgeConfirm() {
    const title = document.getElementById('forge-title')?.value.trim() || 'Untitled Reflection';
    const tagsStr = document.getElementById('forge-tags')?.value || '';
    const emotionalStr = document.getElementById('forge-emotional')?.value || '';
    
    const tags = tagsStr.split(',').map(t => t.trim()).filter(t => t);
    const emotionalTags = emotionalStr.split(',').map(t => t.trim()).filter(t => t);
    const messageIds = Array.from(ReflectState.selectedMessageIds);
    
    const result = await forgeMessages(
        ReflectState.currentSessionId,
        messageIds,
        title,
        tags,
        emotionalTags
    );
    
    if (result.success) {
        // Update messages as forged
        ReflectState.messages = ReflectState.messages.map(msg => {
            if (messageIds.includes(msg.id)) {
                return { ...msg, forged: true };
            }
            return msg;
        });
        
        ReflectState.selectedMessageIds.clear();
        closeForgeModal();
        renderMessages();
        updateForgeButton();
        
        // Reload stats
        loadStats();
        
        console.log('Forged to:', result.reflection_path);
    } else {
        alert('Failed to forge: ' + (result.error || 'Unknown error'));
    }
}

// =============================================================================
// FLOATING FORGE BUTTON
// =============================================================================

function createFloatingForgeButton() {
    const chatContent = document.querySelector('.chat-content');
    if (!chatContent) return;
    
    const btn = document.createElement('button');
    btn.id = 'floating-forge-btn';
    btn.className = 'floating-forge-btn';
    btn.innerHTML = '◈ Forge Selected';
    btn.style.cssText = `
        position: fixed;
        bottom: 100px;
        right: 30px;
        background: var(--accent-primary);
        border: none;
        border-radius: 20px;
        padding: 12px 20px;
        color: var(--bg-primary);
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 100;
        box-shadow: 0 4px 15px var(--accent-glow);
    `;
    
    btn.addEventListener('click', openForgeModal);
    document.body.appendChild(btn);
    
    // Add CSS for visibility
    const style = document.createElement('style');
    style.textContent = `
        .floating-forge-btn.is-visible {
            opacity: 1 !important;
            visibility: visible !important;
        }
        .floating-forge-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px var(--accent-glow);
        }
    `;
    document.head.appendChild(style);
}

// =============================================================================
// INPUT HANDLING
// =============================================================================

function setupChatInput() {
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });
        
        input.addEventListener('input', () => autoResizeTextarea(input));
    }
    
    if (sendBtn) {
        sendBtn.addEventListener('click', handleSendMessage);
    }
}

function setupForgeModal() {
    const closeBtn = document.getElementById('close-forge');
    const cancelBtn = document.getElementById('forge-cancel');
    const confirmBtn = document.getElementById('forge-confirm');
    const overlay = document.getElementById('forge-overlay');
    
    closeBtn?.addEventListener('click', closeForgeModal);
    cancelBtn?.addEventListener('click', closeForgeModal);
    confirmBtn?.addEventListener('click', handleForgeConfirm);
    
    overlay?.addEventListener('click', (e) => {
        if (e.target === overlay) closeForgeModal();
    });
}

// =============================================================================
// INITIALISATION
// =============================================================================

async function initReflect() {
    console.log('EhkoForge Reflect v2.0 initialising...');
    
    // Check if we're on chat submode
    const chatContent = document.querySelector('.chat-content');
    if (!chatContent?.classList.contains('is-visible')) {
        console.log('Not in chat mode, skipping reflect.js init');
        return;
    }
    
    // Load sessions
    await fetchSessions();
    renderSessions();
    
    // Load last session if exists
    if (EhkoCommon.config.last_session_id) {
        const sessionExists = ReflectState.sessions.some(s => s.id === EhkoCommon.config.last_session_id);
        if (sessionExists) {
            await handleSessionClick(EhkoCommon.config.last_session_id);
        }
    }
    
    // Setup UI
    setupChatInput();
    setupForgeModal();
    createFloatingForgeButton();
    
    // New session button
    const newSessionBtn = document.getElementById('new-session-btn');
    newSessionBtn?.addEventListener('click', handleNewSession);
    
    console.log('EhkoForge Reflect ready');
}

// Run when DOM ready (after common.js)
document.addEventListener('DOMContentLoaded', () => {
    // Wait a tick for common.js to load config
    setTimeout(initReflect, 100);
});

// Export for global access
window.handleSessionClick = handleSessionClick;
window.toggleMessageSelection = toggleMessageSelection;
