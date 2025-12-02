/**
 * EhkoForge Journal JavaScript v2.0
 * Handles journal entries with calendar navigation
 */

// =============================================================================
// STATE
// =============================================================================

const JournalState = {
    currentYear: new Date().getFullYear(),
    currentMonth: new Date().getMonth(),
    selectedDate: null,
    entries: [],
    currentEntry: null,
    isEditing: false,
};

// =============================================================================
// API FUNCTIONS
// =============================================================================

async function fetchJournalEntries(year, month) {
    try {
        // Build date range for the month
        const startDate = `${year}-${String(month + 1).padStart(2, '0')}-01`;
        const endDate = new Date(year, month + 1, 0);
        const endDateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(endDate.getDate()).padStart(2, '0')}`;
        
        const data = await fetchAPI(`/api/journal/entries?start=${startDate}&end=${endDateStr}`);
        JournalState.entries = data.entries || [];
        return JournalState.entries;
    } catch (error) {
        console.error('Failed to fetch journal entries:', error);
        // API might not exist yet, return empty
        JournalState.entries = [];
        return [];
    }
}

async function fetchJournalEntry(entryId) {
    try {
        const data = await fetchAPI(`/api/journal/entries/${entryId}`);
        return data;
    } catch (error) {
        console.error('Failed to fetch journal entry:', error);
        return null;
    }
}

async function createJournalEntry(entry) {
    try {
        return await fetchAPI('/api/journal/entries', {
            method: 'POST',
            body: JSON.stringify(entry),
        });
    } catch (error) {
        console.error('Failed to create journal entry:', error);
        return null;
    }
}

async function updateJournalEntry(entryId, entry) {
    try {
        return await fetchAPI(`/api/journal/entries/${entryId}`, {
            method: 'PUT',
            body: JSON.stringify(entry),
        });
    } catch (error) {
        console.error('Failed to update journal entry:', error);
        return null;
    }
}

// =============================================================================
// CALENDAR RENDERING
// =============================================================================

function getMonthName(month) {
    const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return months[month];
}

function getDaysInMonth(year, month) {
    return new Date(year, month + 1, 0).getDate();
}

function getFirstDayOfMonth(year, month) {
    return new Date(year, month, 1).getDay();
}

function hasEntryOnDate(year, month, day) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return JournalState.entries.some(e => e.entry_date === dateStr || e.original_date === dateStr);
}

function getEntryForDate(year, month, day) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return JournalState.entries.find(e => e.entry_date === dateStr || e.original_date === dateStr);
}

function renderCalendar() {
    const container = document.getElementById('calendar-grid');
    const monthLabel = document.getElementById('cal-month-label');
    
    if (!container) return;
    
    const year = JournalState.currentYear;
    const month = JournalState.currentMonth;
    
    // Update label
    if (monthLabel) {
        monthLabel.textContent = `${getMonthName(month)} ${year}`;
    }
    
    // Day headers
    const dayHeaders = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
    let html = dayHeaders.map(d => `<div class="cal-day-header">${d}</div>`).join('');
    
    const daysInMonth = getDaysInMonth(year, month);
    const firstDay = getFirstDayOfMonth(year, month);
    const today = new Date();
    const isCurrentMonth = today.getFullYear() === year && today.getMonth() === month;
    
    // Previous month padding
    const prevMonth = month === 0 ? 11 : month - 1;
    const prevYear = month === 0 ? year - 1 : year;
    const daysInPrevMonth = getDaysInMonth(prevYear, prevMonth);
    
    for (let i = firstDay - 1; i >= 0; i--) {
        const day = daysInPrevMonth - i;
        html += `<div class="cal-day other-month" data-date="${prevYear}-${String(prevMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}">${day}</div>`;
    }
    
    // Current month days
    for (let day = 1; day <= daysInMonth; day++) {
        const isToday = isCurrentMonth && today.getDate() === day;
        const hasEntry = hasEntryOnDate(year, month, day);
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const isSelected = JournalState.selectedDate === dateStr;
        
        let classes = 'cal-day';
        if (isToday) classes += ' is-today';
        if (hasEntry) classes += ' has-entry';
        if (isSelected) classes += ' is-selected';
        
        html += `<div class="${classes}" data-date="${dateStr}" onclick="handleDateClick('${dateStr}')">${day}</div>`;
    }
    
    // Next month padding
    const totalCells = firstDay + daysInMonth;
    const remainingCells = 7 - (totalCells % 7);
    if (remainingCells < 7) {
        const nextMonth = month === 11 ? 0 : month + 1;
        const nextYear = month === 11 ? year + 1 : year;
        
        for (let day = 1; day <= remainingCells; day++) {
            html += `<div class="cal-day other-month" data-date="${nextYear}-${String(nextMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}">${day}</div>`;
        }
    }
    
    container.innerHTML = html;
}

function renderEntriesList() {
    const container = document.getElementById('journal-entries-list');
    if (!container) return;
    
    if (JournalState.entries.length === 0) {
        container.innerHTML = `
            <div style="padding: 15px; text-align: center; color: var(--text-muted); font-size: 0.8rem;">
                No entries this month
            </div>
        `;
        return;
    }
    
    // Sort by date descending
    const sorted = [...JournalState.entries].sort((a, b) => 
        new Date(b.entry_date) - new Date(a.entry_date)
    );
    
    container.innerHTML = sorted.map(entry => {
        const date = new Date(entry.entry_date);
        const dayNum = date.getDate();
        const dayName = date.toLocaleDateString([], { weekday: 'short' });
        
        return `
            <div class="journal-entry-item" onclick="handleEntryClick(${entry.id})">
                <div class="entry-date">${dayName} ${dayNum}</div>
                <div class="entry-title">${escapeHtml(entry.title || 'Untitled')}</div>
            </div>
        `;
    }).join('');
}

// =============================================================================
// JOURNAL VIEW RENDERING
// =============================================================================

function renderJournalView() {
    const container = document.getElementById('journal-view');
    if (!container) return;
    
    if (JournalState.isEditing) {
        renderJournalEditor();
        return;
    }
    
    if (!JournalState.currentEntry) {
        container.innerHTML = `
            <div class="journal-empty">
                <p>Select a date to view or create an entry.</p>
                <p class="subtle">Your journal becomes part of your story.</p>
            </div>
        `;
        return;
    }
    
    const entry = JournalState.currentEntry;
    const date = new Date(entry.entry_date);
    const dateStr = date.toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    
    container.innerHTML = `
        <div class="journal-entry-view">
            <div class="journal-entry-header">
                <div>
                    <h1>${escapeHtml(entry.title || 'Untitled')}</h1>
                    <div class="journal-date">${dateStr}</div>
                </div>
                <button class="journal-edit-btn" onclick="startEditEntry()">Edit</button>
            </div>
            <div class="journal-body">
                ${formatJournalContent(entry.content)}
            </div>
        </div>
    `;
}

function renderJournalEditor() {
    const container = document.getElementById('journal-view');
    if (!container) return;
    
    const entry = JournalState.currentEntry || {
        title: '',
        content: '',
        entry_date: JournalState.selectedDate || new Date().toISOString().split('T')[0],
        tags: [],
        emotional_tags: [],
    };
    
    const tagsStr = (entry.tags || []).join(', ');
    const emotionalStr = (entry.emotional_tags || []).join(', ');
    
    container.innerHTML = `
        <div class="journal-editor">
            <div class="journal-editor-header">
                <input type="text" class="journal-title-input" id="journal-title" 
                       placeholder="Entry title..." value="${escapeHtml(entry.title || '')}">
            </div>
            <textarea class="journal-content-input" id="journal-content" 
                      placeholder="Write your thoughts...">${escapeHtml(entry.content || '')}</textarea>
            <div class="journal-meta-inputs">
                <input type="text" id="journal-tags" placeholder="Tags (comma-separated)" 
                       value="${escapeHtml(tagsStr)}">
                <input type="text" id="journal-emotional" placeholder="Emotional tags" 
                       value="${escapeHtml(emotionalStr)}">
            </div>
            <div class="journal-backdate">
                <label>
                    <input type="checkbox" id="journal-backdate-check" ${entry.original_date ? 'checked' : ''}>
                    Backdate entry
                </label>
                <input type="date" id="journal-original-date" 
                       value="${entry.original_date || ''}"
                       style="display: ${entry.original_date ? 'block' : 'none'}">
            </div>
            <div class="journal-actions">
                <button class="journal-cancel-btn" onclick="cancelEditEntry()">Cancel</button>
                <button class="journal-save-btn" onclick="saveEntry()">Save Entry</button>
            </div>
        </div>
    `;
    
    // Setup backdate toggle
    const backdateCheck = document.getElementById('journal-backdate-check');
    const backdateInput = document.getElementById('journal-original-date');
    
    backdateCheck?.addEventListener('change', (e) => {
        backdateInput.style.display = e.target.checked ? 'block' : 'none';
        if (e.target.checked && !backdateInput.value) {
            backdateInput.value = JournalState.selectedDate || new Date().toISOString().split('T')[0];
        }
    });
}

function formatJournalContent(content) {
    if (!content) return '<p class="subtle">No content</p>';
    
    // Basic markdown-like formatting
    let html = escapeHtml(content);
    
    // Convert line breaks to paragraphs
    html = html.split('\n\n').map(p => `<p>${p}</p>`).join('');
    html = html.replace(/\n/g, '<br>');
    
    return html;
}

// =============================================================================
// EVENT HANDLERS
// =============================================================================

async function handleDateClick(dateStr) {
    JournalState.selectedDate = dateStr;
    JournalState.isEditing = false;
    
    // Check if entry exists for this date
    const [year, month, day] = dateStr.split('-').map(Number);
    const entry = getEntryForDate(year, month - 1, day);
    
    if (entry) {
        JournalState.currentEntry = await fetchJournalEntry(entry.id) || entry;
    } else {
        JournalState.currentEntry = null;
    }
    
    renderCalendar();
    renderJournalView();
}

async function handleEntryClick(entryId) {
    JournalState.isEditing = false;
    JournalState.currentEntry = await fetchJournalEntry(entryId);
    
    if (JournalState.currentEntry) {
        JournalState.selectedDate = JournalState.currentEntry.entry_date;
        renderCalendar();
    }
    
    renderJournalView();
}

function startEditEntry() {
    JournalState.isEditing = true;
    renderJournalView();
}

function startNewEntry() {
    JournalState.currentEntry = null;
    JournalState.isEditing = true;
    renderJournalView();
}

function cancelEditEntry() {
    JournalState.isEditing = false;
    renderJournalView();
}

async function saveEntry() {
    const title = document.getElementById('journal-title')?.value.trim();
    const content = document.getElementById('journal-content')?.value.trim();
    const tagsStr = document.getElementById('journal-tags')?.value || '';
    const emotionalStr = document.getElementById('journal-emotional')?.value || '';
    const backdateCheck = document.getElementById('journal-backdate-check')?.checked;
    const originalDate = document.getElementById('journal-original-date')?.value;
    
    if (!content) {
        alert('Please write something before saving.');
        return;
    }
    
    const entryData = {
        title: title || 'Untitled',
        content,
        entry_date: JournalState.selectedDate || new Date().toISOString().split('T')[0],
        tags: tagsStr.split(',').map(t => t.trim()).filter(t => t),
        emotional_tags: emotionalStr.split(',').map(t => t.trim()).filter(t => t),
        original_date: backdateCheck ? originalDate : null,
    };
    
    let result;
    if (JournalState.currentEntry && JournalState.currentEntry.id) {
        result = await updateJournalEntry(JournalState.currentEntry.id, entryData);
    } else {
        result = await createJournalEntry(entryData);
    }
    
    if (result) {
        JournalState.currentEntry = result;
        JournalState.isEditing = false;
        
        // Refresh entries list
        await fetchJournalEntries(JournalState.currentYear, JournalState.currentMonth);
        renderCalendar();
        renderEntriesList();
        renderJournalView();
    } else {
        alert('Failed to save entry. The journal API may not be available yet.');
    }
}

// =============================================================================
// NAVIGATION
// =============================================================================

async function navigateMonth(delta) {
    JournalState.currentMonth += delta;
    
    if (JournalState.currentMonth < 0) {
        JournalState.currentMonth = 11;
        JournalState.currentYear--;
    } else if (JournalState.currentMonth > 11) {
        JournalState.currentMonth = 0;
        JournalState.currentYear++;
    }
    
    await fetchJournalEntries(JournalState.currentYear, JournalState.currentMonth);
    renderCalendar();
    renderEntriesList();
}

// =============================================================================
// SETUP
// =============================================================================

function setupJournalNavigation() {
    const prevBtn = document.getElementById('cal-prev');
    const nextBtn = document.getElementById('cal-next');
    
    prevBtn?.addEventListener('click', () => navigateMonth(-1));
    nextBtn?.addEventListener('click', () => navigateMonth(1));
}

// =============================================================================
// INITIALISATION
// =============================================================================

async function initJournal() {
    console.log('EhkoForge Journal v2.0 initialising...');
    
    // Load entries for current month
    await fetchJournalEntries(JournalState.currentYear, JournalState.currentMonth);
    
    // Render UI
    renderCalendar();
    renderEntriesList();
    renderJournalView();
    
    // Setup navigation
    setupJournalNavigation();
    
    console.log('EhkoForge Journal ready');
}

// Run when DOM ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initJournal, 150);
});

// Export for global access
window.handleDateClick = handleDateClick;
window.handleEntryClick = handleEntryClick;
window.startEditEntry = startEditEntry;
window.startNewEntry = startNewEntry;
window.cancelEditEntry = cancelEditEntry;
window.saveEntry = saveEntry;
