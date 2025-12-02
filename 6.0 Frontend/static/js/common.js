/**
 * EhkoForge Common JavaScript v2.0
 * Shared utilities and functionality across all areas
 */

// =============================================================================
// GLOBAL STATE
// =============================================================================

const EhkoCommon = {
    config: {},
    stats: {},
    ehkoStatus: {},
};

// =============================================================================
// API HELPERS
// =============================================================================

async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        });
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`API call failed: ${endpoint}`, error);
        throw error;
    }
}

// =============================================================================
// CONFIG
// =============================================================================

async function loadConfig() {
    try {
        EhkoCommon.config = await fetchAPI('/api/config');
        applyConfig();
        return EhkoCommon.config;
    } catch (error) {
        console.error('Failed to load config:', error);
        return {};
    }
}

async function updateConfig(updates) {
    try {
        EhkoCommon.config = await fetchAPI('/api/config', {
            method: 'POST',
            body: JSON.stringify(updates),
        });
        applyConfig();
        return EhkoCommon.config;
    } catch (error) {
        console.error('Failed to update config:', error);
        return EhkoCommon.config;
    }
}

function applyConfig() {
    const body = document.body;
    const avatarZone = document.getElementById('avatar-zone');
    
    // Low motion mode
    body.classList.toggle('low-motion', EhkoCommon.config.low_motion_mode);
    
    // High contrast mode
    body.classList.toggle('high-contrast', EhkoCommon.config.high_contrast_mode);
    
    // Avatar visibility
    if (avatarZone) {
        avatarZone.classList.toggle('is-hidden', !EhkoCommon.config.avatar_visible);
    }
    
    // Update settings UI
    const settingAvatar = document.getElementById('setting-avatar');
    const settingMotion = document.getElementById('setting-motion');
    const settingContrast = document.getElementById('setting-contrast');
    const settingTheme = document.getElementById('setting-theme');
    
    if (settingAvatar) settingAvatar.checked = EhkoCommon.config.avatar_visible;
    if (settingMotion) settingMotion.checked = EhkoCommon.config.low_motion_mode;
    if (settingContrast) settingContrast.checked = EhkoCommon.config.high_contrast_mode;
    if (settingTheme) settingTheme.value = EhkoCommon.config.theme || 'forge-dark';
}

// =============================================================================
// STATS
// =============================================================================

async function loadStats() {
    try {
        EhkoCommon.stats = await fetchAPI('/api/stats');
        renderStats();
        return EhkoCommon.stats;
    } catch (error) {
        console.error('Failed to load stats:', error);
        return {};
    }
}

function renderStats() {
    const statItems = document.querySelectorAll('.stat-item');
    
    statItems.forEach(item => {
        const statName = item.dataset.stat;
        const value = EhkoCommon.stats[statName] || 0;
        
        let intensity = 'low';
        if (value > 0.3) intensity = 'medium';
        if (value > 0.6) intensity = 'high';
        
        item.dataset.intensity = intensity;
    });
}

// =============================================================================
// EHKO STATUS
// =============================================================================

async function loadEhkoStatus() {
    try {
        EhkoCommon.ehkoStatus = await fetchAPI('/api/ehko/status');
        renderEhkoStatus();
        return EhkoCommon.ehkoStatus;
    } catch (error) {
        console.error('Failed to load Ehko status:', error);
        return {};
    }
}

function renderEhkoStatus() {
    const status = EhkoCommon.ehkoStatus;
    const state = status.state || 'nascent';
    
    // Nav indicator
    const navIndicator = document.getElementById('ehko-state-nav');
    if (navIndicator) {
        const stateIcon = navIndicator.querySelector('.state-icon');
        const stateLabel = navIndicator.querySelector('.state-label');
        
        const icons = { nascent: '◇', forming: '◈', emerging: '✦', present: '★' };
        if (stateIcon) stateIcon.textContent = icons[state] || '◇';
        if (stateLabel) stateLabel.textContent = state.charAt(0).toUpperCase() + state.slice(1);
    }
    
    // Sidebar indicator
    const sidebarIndicator = document.getElementById('ehko-state-sidebar');
    if (sidebarIndicator) {
        const stateIcon = sidebarIndicator.querySelector('.state-icon');
        const stateText = sidebarIndicator.querySelector('.state-text');
        
        const icons = { nascent: '◇', forming: '◈', emerging: '✦', present: '★' };
        if (stateIcon) stateIcon.textContent = icons[state] || '◇';
        if (stateText) stateText.textContent = state.charAt(0).toUpperCase() + state.slice(1);
    }
    
    // Avatar state class
    const avatar = document.getElementById('avatar');
    if (avatar) {
        avatar.classList.remove('ehko-nascent', 'ehko-forming', 'ehko-emerging', 'ehko-present');
        avatar.classList.add(`ehko-${state}`);
    }
}

// =============================================================================
// INGOT COUNT (for nav badge)
// =============================================================================

async function updateIngotBadge() {
    try {
        const data = await fetchAPI('/api/ingots?status=surfaced&limit=100');
        const badge = document.getElementById('ingot-count-badge');
        
        if (badge) {
            const count = data.count || 0;
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-flex' : 'none';
        }
    } catch (error) {
        console.error('Failed to update ingot badge:', error);
    }
}

// =============================================================================
// SETTINGS MODAL
// =============================================================================

function setupSettingsModal() {
    const settingsBtn = document.getElementById('global-settings-btn');
    const settingsOverlay = document.getElementById('settings-overlay');
    const closeBtn = document.getElementById('close-settings');
    
    if (settingsBtn && settingsOverlay) {
        settingsBtn.addEventListener('click', () => {
            settingsOverlay.classList.add('is-visible');
        });
        
        closeBtn?.addEventListener('click', () => {
            settingsOverlay.classList.remove('is-visible');
        });
        
        settingsOverlay.addEventListener('click', (e) => {
            if (e.target === settingsOverlay) {
                settingsOverlay.classList.remove('is-visible');
            }
        });
    }
    
    // Settings change handlers
    const settingAvatar = document.getElementById('setting-avatar');
    const settingMotion = document.getElementById('setting-motion');
    const settingContrast = document.getElementById('setting-contrast');
    const settingTheme = document.getElementById('setting-theme');
    
    settingAvatar?.addEventListener('change', (e) => {
        updateConfig({ avatar_visible: e.target.checked });
    });
    
    settingMotion?.addEventListener('change', (e) => {
        updateConfig({ low_motion_mode: e.target.checked });
    });
    
    settingContrast?.addEventListener('change', (e) => {
        updateConfig({ high_contrast_mode: e.target.checked });
    });
    
    settingTheme?.addEventListener('change', (e) => {
        updateConfig({ theme: e.target.value });
    });
}

// =============================================================================
// KEYBOARD SHORTCUTS
// =============================================================================

function setupGlobalKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Escape closes modals
        if (e.key === 'Escape') {
            document.getElementById('settings-overlay')?.classList.remove('is-visible');
        }
    });
}

// =============================================================================
// AVATAR HELPERS
// =============================================================================

function setAvatarThinking(isThinking) {
    const avatarZone = document.getElementById('avatar-zone');
    const avatarStatus = document.getElementById('avatar-status');
    
    if (avatarZone) {
        avatarZone.classList.toggle('is-thinking', isThinking);
    }
    
    if (avatarStatus) {
        avatarStatus.textContent = isThinking ? 'Thinking...' : 'Ready';
    }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTimestamp(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}

// =============================================================================
// INITIALISATION
// =============================================================================

async function initCommon() {
    console.log('EhkoForge Common v2.0 initialising...');
    
    // Load global data
    await Promise.all([
        loadConfig(),
        loadStats(),
        loadEhkoStatus(),
        updateIngotBadge(),
    ]);
    
    // Setup global UI
    setupSettingsModal();
    setupGlobalKeyboardShortcuts();
    
    console.log('EhkoForge Common ready');
}

// Run on DOM ready
document.addEventListener('DOMContentLoaded', initCommon);

// Export for use by area-specific scripts
window.EhkoCommon = EhkoCommon;
window.fetchAPI = fetchAPI;
window.loadConfig = loadConfig;
window.updateConfig = updateConfig;
window.loadStats = loadStats;
window.loadEhkoStatus = loadEhkoStatus;
window.setAvatarThinking = setAvatarThinking;
window.escapeHtml = escapeHtml;
window.formatTimestamp = formatTimestamp;
window.formatDate = formatDate;
window.autoResizeTextarea = autoResizeTextarea;
