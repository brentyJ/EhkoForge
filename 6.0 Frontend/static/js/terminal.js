/**
 * EhkoForge Terminal JavaScript v2.0
 * Handles general AI chat with model selection
 */

// =============================================================================
// STATE
// =============================================================================

const TerminalState = {
    currentSessionId: null,
    sessions: [],
    messages: [],
    currentModel: 'claude-sonnet-4',
    pendingModelSwitch: null,
};

// =============================================================================
// API FUNCTIONS
// =============================================================================

async function fetchTerminalSessions() {
    try {
        // Terminal sessions are stored separately with source='terminal'
        const data = await fetchAPI('/api/sessions?source=terminal');
        TerminalState.sessions = data.sessions || [];
        return TerminalState.sessions;
    } catch (error) {
        // Fallback to all sessions for now
        const data = await fetchAPI('/api/sessions');
        TerminalState.sessions = data.sessions || [];
        return TerminalState.sessions;
    }
}

async function createTerminalSession(model) {
    try {
        const data = await fetchAPI('/api/sessions', {
            method: 'POST',
            body: JSON.stringify({ 
                title: `Terminal - ${model}`,
                source: 'terminal',
                model: model,
            }),
        });
        TerminalState.sessions.unshift(data);
        return data;
    } catch (error) {
        console.error('Failed to create terminal session:', error);
        return null;
    }
}

async function fetchTerminalMessages(sessionId) {
    try {
        const data = await fetchAPI(`/api/sessions/${sessionId}/messages`);
        TerminalState.messages = data.messages;
        return data.messages;
    } catch (error) {
        console.error('Failed to fetch terminal messages:', error);
        return [];
    }
}

async function sendTerminalMessage(sessionId, content, model) {
    try {
        const data = await fetchAPI(`/api/sessions/${sessionId}/messages`, {
            method: 'POST',
            body: JSON.stringify({ 
                role: 'user', 
                content,
                model: model, // Pass model for routing
            }),
        });
        TerminalState.messages.push(...data.messages);
        return data.messages;
    } catch (error) {
        console.error('Failed to send terminal message:', error);
        return null;
    }
}

// =============================================================================
// RENDER FUNCTIONS
// =============================================================================

function renderTerminalSessions() {
    const container = document.getElementById('terminal-sessions-list');
    if (!container) return;
    
    // Show last 20 sessions
    const sessionsToShow = TerminalState.sessions.slice(0, 20);
    
    if (sessionsToShow.length === 0) {
        container.innerHTML = `
            <div style="padding: 20px; text-align: center; color: var(--text-muted); font-size: 0.8rem;">
                No terminal history yet
            </div>
        `;
        return;
    }
    
    container.innerHTML = sessionsToShow.map(session => {
        const isActive = session.id === TerminalState.currentSessionId;
        const date = new Date(session.updated_at);
        const dateStr = date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        
        return `
            <div class="terminal-session-item ${isActive ? 'is-active' : ''}" 
                 data-session-id="${session.id}"
                 onclick="handleTerminalSessionClick('${session.id}')">
                <div class="terminal-session-title">${escapeHtml(session.title)}</div>
                <div class="terminal-session-meta">${session.message_count} msgs • ${dateStr}</div>
            </div>
        `;
    }).join('');
}

function renderTerminalOutput() {
    const container = document.getElementById('terminal-output');
    if (!container) return;
    
    if (TerminalState.messages.length === 0) {
        container.innerHTML = `
            <div class="terminal-welcome">
                <pre class="terminal-ascii">
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗██╗  ██╗██╗  ██╗ ██████╗                          ║
║   ██╔════╝██║  ██║██║ ██╔╝██╔═══██╗                         ║
║   █████╗  ███████║█████╔╝ ██║   ██║                         ║
║   ██╔══╝  ██╔══██║██╔═██╗ ██║   ██║                         ║
║   ███████╗██║  ██║██║  ██╗╚██████╔╝                         ║
║   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝                          ║
║                                                              ║
║   TERMINAL MODE — General AI Assistant                       ║
║   Model: ${TerminalState.currentModel.padEnd(30)}            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
                </pre>
                <p class="terminal-hint">&gt; Type a message to begin. Your Ehko remembers everything.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = TerminalState.messages.map(msg => {
        const isUser = msg.role === 'user';
        const timestamp = formatTimestamp(msg.timestamp);
        
        return `
            <div class="terminal-message ${isUser ? 'user' : 'ehko'}">
                <span class="terminal-message-content">${escapeHtml(msg.content)}</span>
                <div class="terminal-timestamp">${timestamp}</div>
            </div>
        `;
    }).join('');
    
    scrollTerminalToBottom();
}

function scrollTerminalToBottom() {
    const container = document.getElementById('terminal-output');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

function showTypingIndicator() {
    const container = document.getElementById('terminal-output');
    if (!container) return;
    
    const indicator = document.createElement('div');
    indicator.className = 'terminal-typing';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
        <span class="terminal-typing-dots">
            <span class="terminal-typing-dot"></span>
            <span class="terminal-typing-dot"></span>
            <span class="terminal-typing-dot"></span>
        </span>
    `;
    container.appendChild(indicator);
    scrollTerminalToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    indicator?.remove();
}

function updateCurrentModelDisplay() {
    const modelValue = document.querySelector('.current-model .model-value');
    if (modelValue) {
        modelValue.textContent = TerminalState.currentModel;
    }
    
    // Update welcome screen if visible
    const welcome = document.querySelector('.terminal-welcome');
    if (welcome) {
        renderTerminalOutput();
    }
}

// =============================================================================
// EVENT HANDLERS
// =============================================================================

async function handleTerminalSessionClick(sessionId) {
    TerminalState.currentSessionId = sessionId;
    
    renderTerminalSessions();
    await fetchTerminalMessages(sessionId);
    renderTerminalOutput();
}

async function handleNewTerminalSession() {
    const session = await createTerminalSession(TerminalState.currentModel);
    if (session) {
        TerminalState.messages = [];
        await handleTerminalSessionClick(session.id);
    }
}

async function handleTerminalSend() {
    const input = document.getElementById('terminal-input');
    const content = input.value.trim();
    
    if (!content) return;
    
    // Create session if none exists
    if (!TerminalState.currentSessionId) {
        await handleNewTerminalSession();
    }
    
    input.value = '';
    
    setAvatarThinking(true);
    showTypingIndicator();
    
    const messages = await sendTerminalMessage(
        TerminalState.currentSessionId, 
        content,
        TerminalState.currentModel
    );
    
    hideTypingIndicator();
    setAvatarThinking(false);
    
    if (messages) {
        renderTerminalOutput();
        renderTerminalSessions();
    }
}

// =============================================================================
// MODEL SWITCHING
// =============================================================================

function handleModelSelect(model) {
    if (model === TerminalState.currentModel) return;
    
    // If there's an active session with messages, show warning
    if (TerminalState.currentSessionId && TerminalState.messages.length > 0) {
        TerminalState.pendingModelSwitch = model;
        showModelSwitchModal();
    } else {
        // No active session or empty session, just switch
        TerminalState.currentModel = model;
        updateCurrentModelDisplay();
        updateModelSelector();
    }
}

function showModelSwitchModal() {
    const overlay = document.getElementById('model-switch-overlay');
    overlay?.classList.add('is-visible');
}

function hideModelSwitchModal() {
    const overlay = document.getElementById('model-switch-overlay');
    overlay?.classList.remove('is-visible');
    TerminalState.pendingModelSwitch = null;
}

async function confirmModelSwitch() {
    if (TerminalState.pendingModelSwitch) {
        TerminalState.currentModel = TerminalState.pendingModelSwitch;
        TerminalState.pendingModelSwitch = null;
        
        // Start new session with new model
        await handleNewTerminalSession();
        
        updateCurrentModelDisplay();
        updateModelSelector();
    }
    hideModelSwitchModal();
}

function updateModelSelector() {
    const radios = document.querySelectorAll('.model-selector input[name="model"]');
    radios.forEach(radio => {
        radio.checked = radio.value === TerminalState.currentModel;
    });
}

// =============================================================================
// SETUP
// =============================================================================

function setupTerminalInput() {
    const input = document.getElementById('terminal-input');
    const sendBtn = document.getElementById('terminal-send-btn');
    
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleTerminalSend();
            }
        });
    }
    
    if (sendBtn) {
        sendBtn.addEventListener('click', handleTerminalSend);
    }
}

function setupModelSelector() {
    const radios = document.querySelectorAll('.model-selector input[name="model"]');
    radios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            handleModelSelect(e.target.value);
        });
    });
}

function setupModelSwitchModal() {
    const cancelBtn = document.getElementById('model-switch-cancel');
    const confirmBtn = document.getElementById('model-switch-confirm');
    const overlay = document.getElementById('model-switch-overlay');
    
    cancelBtn?.addEventListener('click', hideModelSwitchModal);
    confirmBtn?.addEventListener('click', confirmModelSwitch);
    
    overlay?.addEventListener('click', (e) => {
        if (e.target === overlay) hideModelSwitchModal();
    });
}

function setupNewTerminalButton() {
    const btn = document.getElementById('new-terminal-btn');
    btn?.addEventListener('click', handleNewTerminalSession);
}

// =============================================================================
// INITIALISATION
// =============================================================================

async function initTerminal() {
    console.log('EhkoForge Terminal v2.0 initialising...');
    
    // Load sessions
    await fetchTerminalSessions();
    renderTerminalSessions();
    
    // Render initial output
    renderTerminalOutput();
    
    // Setup UI
    setupTerminalInput();
    setupModelSelector();
    setupModelSwitchModal();
    setupNewTerminalButton();
    
    // Update displays
    updateCurrentModelDisplay();
    updateModelSelector();
    
    console.log('EhkoForge Terminal ready');
}

// Run when DOM ready (after common.js)
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initTerminal, 100);
});

// Export for global access
window.handleTerminalSessionClick = handleTerminalSessionClick;
