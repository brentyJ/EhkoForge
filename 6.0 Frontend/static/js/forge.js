/**
 * EhkoForge Forge JavaScript v2.0
 * Handles ingot queue, review, and forging into Ehko
 */

// =============================================================================
// STATE
// =============================================================================

const ForgeState = {
    ingots: [],
    currentIngotId: null,
    currentIngot: null,
    smeltStatus: {},
    filterTier: '',
};

// =============================================================================
// API FUNCTIONS
// =============================================================================

async function fetchIngots(status = 'surfaced', minSignificance = 0) {
    try {
        let url = `/api/ingots?status=${status}&min_significance=${minSignificance}`;
        if (ForgeState.filterTier) {
            url += `&tier=${ForgeState.filterTier}`;
        }
        const data = await fetchAPI(url);
        ForgeState.ingots = data.ingots;
        return data.ingots;
    } catch (error) {
        console.error('Failed to fetch ingots:', error);
        return [];
    }
}

async function fetchIngotDetail(ingotId) {
    try {
        const data = await fetchAPI(`/api/ingots/${ingotId}`);
        ForgeState.currentIngot = data;
        return data;
    } catch (error) {
        console.error('Failed to fetch ingot detail:', error);
        return null;
    }
}

async function forgeIngot(ingotId) {
    try {
        return await fetchAPI(`/api/ingots/${ingotId}/forge`, {
            method: 'POST',
        });
    } catch (error) {
        console.error('Failed to forge ingot:', error);
        return { success: false, error: error.message };
    }
}

async function rejectIngot(ingotId) {
    try {
        return await fetchAPI(`/api/ingots/${ingotId}/reject`, {
            method: 'POST',
        });
    } catch (error) {
        console.error('Failed to reject ingot:', error);
        return { success: false, error: error.message };
    }
}

async function fetchSmeltStatus() {
    try {
        const data = await fetchAPI('/api/smelt/status');
        ForgeState.smeltStatus = data;
        return data;
    } catch (error) {
        console.error('Failed to fetch smelt status:', error);
        return {};
    }
}

async function runSmelt(limit = 10) {
    try {
        return await fetchAPI('/api/smelt/run', {
            method: 'POST',
            body: JSON.stringify({ limit }),
        });
    } catch (error) {
        console.error('Failed to run smelt:', error);
        return { success: false, error: error.message };
    }
}

// =============================================================================
// RENDER FUNCTIONS
// =============================================================================

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

function renderIngotList() {
    const container = document.getElementById('ingot-list');
    if (!container) return;
    
    if (ForgeState.ingots.length === 0) {
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
    
    container.innerHTML = ForgeState.ingots.map(ingot => {
        const isActive = ingot.id === ForgeState.currentIngotId;
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

function renderIngotDetail() {
    const container = document.getElementById('ingot-detail');
    if (!container) return;
    
    const ingot = ForgeState.currentIngot;
    
    if (!ingot) {
        container.innerHTML = `
            <div class="ingot-empty">
                <p>Select an ingot from the queue to review.</p>
                <p class="subtle">Accept valuable insights to forge them into your Ehko.</p>
            </div>
        `;
        return;
    }
    
    const themes = ingot.themes.map(t => `<span class="theme-tag">${escapeHtml(t)}</span>`).join('');
    const emotions = ingot.emotional_tags.map(e => `<span class="emotion-tag">${escapeHtml(e)}</span>`).join('');
    const patterns = ingot.patterns.map(p => `<span class="pattern-tag">${escapeHtml(p)}</span>`).join('');
    
    const sources = ingot.sources ? ingot.sources.map(s => `
        <div class="source-item">
            <div class="source-type">${escapeHtml(s.type)}</div>
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
    if (!container) return;
    
    const status = ForgeState.smeltStatus;
    const pending = status.queue?.pending?.count || 0;
    container.textContent = `${pending} pending`;
}

// =============================================================================
// EVENT HANDLERS
// =============================================================================

async function handleIngotClick(ingotId) {
    ForgeState.currentIngotId = ingotId;
    renderIngotList();
    
    await fetchIngotDetail(ingotId);
    renderIngotDetail();
}

async function handleForgeIngot(ingotId) {
    const result = await forgeIngot(ingotId);
    
    if (result.success) {
        // Refresh everything
        await fetchIngots();
        renderIngotList();
        
        // Clear detail
        ForgeState.currentIngotId = null;
        ForgeState.currentIngot = null;
        renderIngotDetail();
        
        // Update Ehko status
        await loadEhkoStatus();
        
        console.log('Ingot forged:', result);
    } else {
        alert('Failed to forge ingot: ' + (result.error || 'Unknown error'));
    }
}

async function handleRejectIngot(ingotId) {
    const result = await rejectIngot(ingotId);
    
    if (result.success) {
        // Refresh list
        await fetchIngots();
        renderIngotList();
        
        // Clear detail
        ForgeState.currentIngotId = null;
        ForgeState.currentIngot = null;
        renderIngotDetail();
        
        console.log('Ingot rejected:', result);
    } else {
        alert('Failed to reject ingot: ' + (result.error || 'Unknown error'));
    }
}

async function handleRunSmelt() {
    const btn = document.getElementById('run-smelt');
    if (!btn) return;
    
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

function handleTierFilter(tier) {
    ForgeState.filterTier = tier;
    fetchIngots().then(renderIngotList);
}

// =============================================================================
// MODAL HANDLERS
// =============================================================================

function openIngotModal() {
    const overlay = document.getElementById('ingot-overlay');
    overlay?.classList.add('is-visible');
}

function closeIngotModal() {
    const overlay = document.getElementById('ingot-overlay');
    overlay?.classList.remove('is-visible');
}

// =============================================================================
// SETUP
// =============================================================================

function setupForgeUI() {
    // Tier filter
    const tierFilter = document.getElementById('ingot-filter-tier');
    tierFilter?.addEventListener('change', (e) => handleTierFilter(e.target.value));
    
    // Refresh button
    const refreshBtn = document.getElementById('refresh-ingots');
    refreshBtn?.addEventListener('click', async () => {
        await fetchIngots();
        renderIngotList();
        await fetchSmeltStatus();
        renderSmeltStatus();
    });
    
    // Smelt button
    const smeltBtn = document.getElementById('run-smelt');
    smeltBtn?.addEventListener('click', handleRunSmelt);
    
    // Modal handlers
    const closeModalBtn = document.getElementById('close-ingot-modal');
    closeModalBtn?.addEventListener('click', closeIngotModal);
    
    const overlay = document.getElementById('ingot-overlay');
    overlay?.addEventListener('click', (e) => {
        if (e.target === overlay) closeIngotModal();
    });
    
    // Modal action buttons
    document.getElementById('ingot-accept')?.addEventListener('click', () => {
        if (ForgeState.currentIngotId) {
            handleForgeIngot(ForgeState.currentIngotId);
            closeIngotModal();
        }
    });
    
    document.getElementById('ingot-reject')?.addEventListener('click', () => {
        if (ForgeState.currentIngotId) {
            handleRejectIngot(ForgeState.currentIngotId);
            closeIngotModal();
        }
    });
    
    document.getElementById('ingot-defer')?.addEventListener('click', closeIngotModal);
}

// =============================================================================
// INITIALISATION
// =============================================================================

async function initForge() {
    console.log('EhkoForge Forge v2.0 initialising...');
    
    // Load initial data
    await Promise.all([
        fetchIngots(),
        fetchSmeltStatus(),
    ]);
    
    // Render UI
    renderIngotList();
    renderSmeltStatus();
    
    // Setup event handlers
    setupForgeUI();
    
    console.log('EhkoForge Forge ready');
}

// Run when DOM ready (after common.js)
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initForge, 100);
});

// Export for global access
window.handleIngotClick = handleIngotClick;
window.handleForgeIngot = handleForgeIngot;
window.handleRejectIngot = handleRejectIngot;
