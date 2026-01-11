// API Configuration
// Use relative URL to avoid localhost vs 127.0.0.1 cookie issues
const API_BASE_URL = '/api';

// XSS Protection: Escape HTML entities
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// State
let currentPhrase = null;
let currentLetter = null;
let currentWord = null;
let phrases = [];
let alphabet = [];
let dictionaryWords = [];
let manageDictWords = [];
let videos = [];
let currentDictionaryPage = 1;
let currentManageDictPage = 1;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupNavigation();
    loadPhrases();
    loadAlphabet();
    loadManageDictionary();
    loadVideos();
    setupModals();
    setupEventListeners();
});

// Navigation
function setupNavigation() {
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            const section = this.dataset.section;
            
            // Skip if this is the "Back to Site" link (no data-section attribute)
            if (!section) {
                return; // Allow default link behavior
            }
            
            e.preventDefault();
            
            // Update active menu
            document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
            this.classList.add('active');
            
            // Show section
            document.querySelectorAll('.admin-section').forEach(s => s.classList.remove('active'));
            document.getElementById(section + '-section').classList.add('active');
        });
    });
}

// Load Phrases
async function loadPhrases() {
    try {
        const response = await fetch(`${API_BASE_URL}/phrases`);
        phrases = await response.json();
        renderPhrasesTable();
        updatePhraseCategories();
    } catch (error) {
        console.error('Error loading phrases:', error);
        alert('Error loading phrases');
    }
}

function renderPhrasesTable() {
    const tbody = document.getElementById('phrases-table-body');
    const searchValue = document.getElementById('phrase-search').value.toLowerCase();
    const categoryFilter = document.getElementById('phrase-category-filter').value;
    const formalityFilter = document.getElementById('phrase-formality-filter').value;
    
    let filtered = phrases.filter(p => {
        const matchesSearch = p.nepali.includes(searchValue) || 
                            p.romanized.includes(searchValue) || 
                            p.english.includes(searchValue);
        const matchesCategory = !categoryFilter || p.category === categoryFilter;
        const matchesFormality = !formalityFilter || p.formality_level === formalityFilter;
        return matchesSearch && matchesCategory && matchesFormality;
    });
    
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No phrases found</td></tr>';
        return;
    }
    
    tbody.innerHTML = filtered.map(phrase => `
        <tr>
            <td>${escapeHtml(phrase.nepali)}</td>
            <td>${escapeHtml(phrase.romanized)}</td>
            <td>${escapeHtml(phrase.english)}</td>
            <td><span style="background: var(--accent-color); padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem;">${escapeHtml(phrase.category)}</span></td>
            <td>${escapeHtml(phrase.context || '-')}</td>
            <td><span style="background: #6c757d; color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem;">${escapeHtml(phrase.formality_level || 'casual')}</span></td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editPhrase(${phrase.id})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deletePhrase(${phrase.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function updatePhraseCategories() {
    const categories = [...new Set(phrases.map(p => p.category))];
    const select = document.getElementById('phrase-category-filter');
    const currentValue = select.value;
    
    categories.forEach(cat => {
        if (![...select.options].map(o => o.value).includes(cat)) {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
            select.appendChild(option);
        }
    });
    
    select.value = currentValue;
}

function editPhrase(id) {
    currentPhrase = phrases.find(p => p.id === id);
    document.getElementById('modal-title').textContent = 'Edit Phrase';
    document.getElementById('phrase-nepali').value = currentPhrase.nepali;
    document.getElementById('phrase-romanized').value = currentPhrase.romanized;
    document.getElementById('phrase-english').value = currentPhrase.english;
    document.getElementById('phrase-category').value = currentPhrase.category;
    document.getElementById('phrase-context').value = currentPhrase.context || '';
    document.getElementById('phrase-formality').value = currentPhrase.formality_level || 'casual';
    document.getElementById('phrase-modal').classList.add('active');
}

async function deletePhrase(id) {
    if (!confirm('Are you sure you want to delete this phrase?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/phrases/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Phrase deleted successfully');
            loadPhrases();
        } else {
            alert('Error deleting phrase');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting phrase');
    }
}

// Load Alphabet
async function loadAlphabet() {
    try {
        const response = await fetch(`${API_BASE_URL}/alphabet`);
        alphabet = await response.json();
        // Sort by order_index
        alphabet.sort((a, b) => (a.order_index || 0) - (b.order_index || 0));
        renderAlphabetTable();
        setupAlphabetDragDrop();
    } catch (error) {
        console.error('Error loading alphabet:', error);
        alert('Error loading alphabet');
    }
}

function renderAlphabetTable() {
    const tbody = document.getElementById('alphabet-table-body');
    const searchValue = document.getElementById('alphabet-search').value.toLowerCase();
    const typeFilter = document.getElementById('letter-type-filter').value;
    
    let filtered = alphabet.filter(l => {
        const matchesSearch = l.devanagari.includes(searchValue) || 
                            l.romanized.includes(searchValue);
        const matchesType = !typeFilter || l.type === typeFilter;
        return matchesSearch && matchesType;
    });
    
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No letters found</td></tr>';
        return;
    }
    
    tbody.innerHTML = filtered.map((letter, index) => `
        <tr class="draggable-row" draggable="true" data-id="${letter.id}">
            <td class="drag-handle">⋮⋮</td>
            <td style="font-size: 1.3rem; font-family: 'Noto Sans Devanagari';">${escapeHtml(letter.devanagari)}</td>
            <td>${escapeHtml(letter.romanized)}</td>
            <td>${escapeHtml(letter.type)}</td>
            <td>${escapeHtml(letter.pronunciation || '-')}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editLetter(${letter.id})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteLetter(${letter.id})">Delete</button>
            </td>
        </tr>
    `).join('');
    
    // Re-setup drag and drop after render
    setupAlphabetDragDrop();
}

function editLetter(id) {
    currentLetter = alphabet.find(l => l.id === id);
    document.getElementById('letter-modal-title').textContent = 'Edit Letter';
    document.getElementById('letter-devanagari').value = currentLetter.devanagari;
    document.getElementById('letter-romanized').value = currentLetter.romanized;
    document.getElementById('letter-type').value = currentLetter.type;
    document.getElementById('letter-pronunciation').value = currentLetter.pronunciation || '';
    document.getElementById('letter-modal').classList.add('active');
}

async function deleteLetter(id) {
    if (!confirm('Are you sure you want to delete this letter?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/alphabet/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Letter deleted successfully');
            loadAlphabet();
        } else {
            alert('Error deleting letter');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting letter');
    }
}

// Drag and Drop for Alphabet Reordering
let draggedRow = null;
let alphabetOrderChanged = false;
let dictionaryOrderChanged = false;

function setupAlphabetDragDrop() {
    const rows = document.querySelectorAll('#alphabet-table-body .draggable-row');
    
    rows.forEach(row => {
        row.addEventListener('dragstart', handleDragStart);
        row.addEventListener('dragover', handleDragOver);
        row.addEventListener('drop', handleDrop);
        row.addEventListener('dragend', handleDragEnd);
        row.addEventListener('dragenter', handleDragEnter);
        row.addEventListener('dragleave', handleDragLeave);
    });
}

function handleDragStart(e) {
    draggedRow = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    if (this !== draggedRow) {
        this.classList.add('drag-over');
    }
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    if (draggedRow !== this) {
        // Get all rows
        const tbody = document.getElementById('alphabet-table-body');
        const rows = Array.from(tbody.querySelectorAll('.draggable-row'));
        
        // Find positions
        const draggedIndex = rows.indexOf(draggedRow);
        const targetIndex = rows.indexOf(this);
        
        // Reorder in DOM
        if (draggedIndex < targetIndex) {
            this.parentNode.insertBefore(draggedRow, this.nextSibling);
        } else {
            this.parentNode.insertBefore(draggedRow, this);
        }
        
        // Update alphabet array order
        const draggedId = parseInt(draggedRow.dataset.id);
        const draggedItem = alphabet.find(l => l.id === draggedId);
        alphabet.splice(alphabet.indexOf(draggedItem), 1);
        
        const newRows = Array.from(tbody.querySelectorAll('.draggable-row'));
        const newIndex = newRows.indexOf(draggedRow);
        alphabet.splice(newIndex, 0, draggedItem);
        
        // Update order numbers visually
        updateOrderNumbers();
        
        // Show save button
        alphabetOrderChanged = true;
        document.getElementById('save-alphabet-order-btn').style.display = 'inline-flex';
    }
    
    return false;
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    
    // Remove all drag-over classes
    document.querySelectorAll('.drag-over').forEach(row => {
        row.classList.remove('drag-over');
    });
}

function updateOrderNumbers() {
    const rows = document.querySelectorAll('#alphabet-table-body .draggable-row');
    rows.forEach((row, index) => {
        const orderCell = row.querySelector('.order-number');
        if (orderCell) {
            orderCell.textContent = index + 1;
        }
    });
}

async function saveAlphabetOrder() {
    if (!alphabetOrderChanged) return;
    
    try {
        // Prepare order data
        const orderData = alphabet.map((letter, index) => ({
            id: letter.id,
            order_index: index + 1
        }));
        
        const response = await fetch(`${API_BASE_URL}/alphabet/reorder`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ order: orderData })
        });
        
        if (response.ok) {
            alert('✅ Alphabet order saved successfully!');
            alphabetOrderChanged = false;
            document.getElementById('save-alphabet-order-btn').style.display = 'none';
            await loadAlphabet();
        } else {
            const error = await response.json();
            alert('❌ Error saving order: ' + (error.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error saving alphabet order:', error);
        alert('❌ Network error: ' + error.message);
    }
}

// ===== DICTIONARY DRAG AND DROP =====

function setupDictionaryDragDrop() {
    const rows = document.querySelectorAll('#manage-dict-table-body .draggable-row');
    
    rows.forEach(row => {
        row.addEventListener('dragstart', handleDictDragStart);
        row.addEventListener('dragover', handleDragOver);
        row.addEventListener('drop', handleDictDrop);
        row.addEventListener('dragend', handleDragEnd);
        row.addEventListener('dragenter', handleDragEnter);
        row.addEventListener('dragleave', handleDragLeave);
    });
}

function handleDictDragStart(e) {
    draggedRow = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleDictDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    if (draggedRow !== this) {
        // Get all rows
        const tbody = document.getElementById('manage-dict-table-body');
        const rows = Array.from(tbody.querySelectorAll('.draggable-row'));
        
        // Find positions
        const draggedIndex = rows.indexOf(draggedRow);
        const targetIndex = rows.indexOf(this);
        
        // Reorder in DOM
        if (draggedIndex < targetIndex) {
            this.parentNode.insertBefore(draggedRow, this.nextSibling);
        } else {
            this.parentNode.insertBefore(draggedRow, this);
        }
        
        // Update manageDictWords array order
        const draggedId = parseInt(draggedRow.dataset.id);
        const draggedItem = manageDictWords.find(w => w.id === draggedId);
        manageDictWords.splice(manageDictWords.indexOf(draggedItem), 1);
        
        const newRows = Array.from(tbody.querySelectorAll('.draggable-row'));
        const newIndex = newRows.indexOf(draggedRow);
        manageDictWords.splice(newIndex, 0, draggedItem);
        
        // Show save button
        dictionaryOrderChanged = true;
        document.getElementById('save-dictionary-order-btn').style.display = 'inline-flex';
    }
    
    return false;
}

async function saveDictionaryOrder() {
    if (!dictionaryOrderChanged) return;
    
    try {
        // Prepare order data
        const orderData = manageDictWords.map((word, index) => ({
            id: word.id,
            order_index: index + 1
        }));
        
        const response = await fetch(`${API_BASE_URL}/dictionary/reorder`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ order: orderData })
        });
        
        if (response.ok) {
            alert('✅ Dictionary order saved successfully!');
            dictionaryOrderChanged = false;
            document.getElementById('save-dictionary-order-btn').style.display = 'none';
            await loadManageDictionary(currentManageDictPage);
        } else {
            const error = await response.json();
            console.error('Dictionary reorder error:', error);
            alert('❌ Error saving order: ' + (error.error || error.message || `Status ${response.status}`));
        }
    } catch (error) {
        console.error('Error saving dictionary order:', error);
        alert('❌ Network error: ' + error.message);
    }
}

// Modal Setup
function setupModals() {
    // Phrase Modal
    document.getElementById('add-phrase-btn').addEventListener('click', function() {
        currentPhrase = null;
        document.getElementById('modal-title').textContent = 'Add New Phrase';
        document.getElementById('phrase-form').reset();
        document.getElementById('phrase-modal').classList.add('active');
    });
    
    document.getElementById('phrase-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        await savePhraseData();
    });
    
    // Letter Modal
    document.getElementById('add-letter-btn').addEventListener('click', function() {
        currentLetter = null;
        document.getElementById('letter-modal-title').textContent = 'Add New Letter';
        document.getElementById('letter-form').reset();
        document.getElementById('letter-modal').classList.add('active');
    });
    
    document.getElementById('letter-save-btn')?.addEventListener('click', async function() {
        await saveLetterData();
    });
    
    document.getElementById('letter-modal-cancel')?.addEventListener('click', function() {
        document.getElementById('letter-modal').classList.remove('active');
    });
    
    document.getElementById('letter-modal-close')?.addEventListener('click', function() {
        document.getElementById('letter-modal').classList.remove('active');
    });
    
    // Close modals
    document.querySelector('#phrase-modal .close')?.addEventListener('click', function() {
        document.getElementById('phrase-modal').classList.remove('active');
    });
    
    document.getElementById('modal-cancel').addEventListener('click', function() {
        document.getElementById('phrase-modal').classList.remove('active');
    });
    
    // Word Modal
    document.getElementById('add-word-btn')?.addEventListener('click', function() {
        currentWord = null;
        document.getElementById('word-modal-title').textContent = 'Add New Word';
        document.getElementById('word-form').reset();
        document.getElementById('word-id').value = '';
        document.getElementById('word-modal').classList.add('active');
    });
    
    document.getElementById('word-form')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        await saveWordData();
    });
    
    document.getElementById('word-modal-close')?.addEventListener('click', function() {
        document.getElementById('word-modal').classList.remove('active');
    });
    
    document.getElementById('word-modal-cancel')?.addEventListener('click', function() {
        document.getElementById('word-modal').classList.remove('active');
    });
}

// Save Functions
async function savePhraseData() {
    const data = {
        nepali: document.getElementById('phrase-nepali').value,
        romanized: document.getElementById('phrase-romanized').value,
        english: document.getElementById('phrase-english').value,
        category: document.getElementById('phrase-category').value,
        context: document.getElementById('phrase-context').value,
        formality_level: document.getElementById('phrase-formality').value
    };
    
    try {
        const url = currentPhrase ? `${API_BASE_URL}/phrases/${currentPhrase.id}` : `${API_BASE_URL}/phrases`;
        const method = currentPhrase ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('Phrase saved successfully');
            document.getElementById('phrase-modal').classList.remove('active');
            loadPhrases();
        } else {
            alert('Error saving phrase');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error saving phrase');
    }
}

async function saveLetterData() {
    const data = {
        devanagari: document.getElementById('letter-devanagari').value,
        romanized: document.getElementById('letter-romanized').value,
        type: document.getElementById('letter-type').value,
        pronunciation: document.getElementById('letter-pronunciation').value,
        sound: document.getElementById('letter-romanized').value
    };
    
    try {
        const url = currentLetter ? `${API_BASE_URL}/alphabet/${currentLetter.id}` : `${API_BASE_URL}/alphabet`;
        const method = currentLetter ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('✅ Letter saved successfully!');
            document.getElementById('letter-modal').classList.remove('active');
            await loadAlphabet();
        } else {
            const error = await response.json();
            alert('❌ Error saving letter: ' + (error.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Network error: ' + error.message);
    }
}

// Event Listeners
function setupEventListeners() {
    document.getElementById('phrase-search').addEventListener('input', renderPhrasesTable);
    document.getElementById('phrase-category-filter').addEventListener('change', renderPhrasesTable);
    document.getElementById('alphabet-search').addEventListener('input', renderAlphabetTable);
    document.getElementById('letter-type-filter').addEventListener('change', renderAlphabetTable);
    
    // Alphabet order save button
    document.getElementById('save-alphabet-order-btn')?.addEventListener('click', saveAlphabetOrder);
    
    document.getElementById('save-dictionary-order-btn')?.addEventListener('click', saveDictionaryOrder);
    
    // Setup bulk upload form listeners
    document.getElementById('upload-dictionary-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await uploadCSV('dictionary');
    });
    document.getElementById('upload-phrases-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await uploadCSV('phrases');
    });
    document.getElementById('upload-alphabet-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await uploadCSV('alphabet');
    });
    document.getElementById('upload-videos-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await uploadCSV('videos');
    });
    
    // Manage Dictionary filters
    document.getElementById('manage-dict-search')?.addEventListener('input', renderManageDictTable);
    document.getElementById('manage-dict-category')?.addEventListener('change', () => loadManageDictionary(1));
    document.getElementById('manage-dict-difficulty')?.addEventListener('change', () => loadManageDictionary(1));
    
    // Video filters
    document.getElementById('videos-search')?.addEventListener('input', renderVideosTable);
    document.getElementById('videos-category-filter')?.addEventListener('change', renderVideosTable);
    document.getElementById('videos-difficulty-filter')?.addEventListener('change', renderVideosTable);
    
    // Video select all checkbox
    document.getElementById('select-all-videos')?.addEventListener('change', function() {
        const checkboxes = document.querySelectorAll('.video-checkbox');
        checkboxes.forEach(cb => cb.checked = this.checked);
        updateSelectedVideosCount();
    });
    
    // Mass delete videos button
    document.getElementById('mass-delete-videos-btn')?.addEventListener('click', massDeleteVideos);
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        const phraseModal = document.getElementById('phrase-modal');
        const letterModal = document.getElementById('letter-modal');
        const wordModal = document.getElementById('word-modal');
        
        if (e.target === phraseModal) {
            phraseModal.classList.remove('active');
        }
        if (e.target === letterModal) {
            letterModal.classList.remove('active');
        }
        if (e.target === wordModal) {
            wordModal.classList.remove('active');
        }
    });
}

// ===== BULK UPLOAD FUNCTIONS =====

// Download CSV Template
function downloadTemplate(type) {
    window.location.href = `/api/bulk/template/${type}`;
}

// Validate Before Upload
async function validateBeforeUpload(type) {
    const fileInput = document.getElementById(`${type}-file`);
    const validationDiv = document.getElementById(`${type}-validation`);
    const uploadBtn = document.getElementById(`upload-${type}-btn`);
    const file = fileInput.files[0];
    
    if (!file) {
        showValidationResult(validationDiv, 'Please select a file first', 'error');
        return;
    }
    
    // Show loading
    validationDiv.className = 'validation-result loading';
    validationDiv.innerHTML = '⏳ Validating file... checking for duplicates and errors';
    uploadBtn.disabled = true;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`/api/bulk/validate/${type}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayValidationResults(type, data, validationDiv);
            
            // Enable upload button if there are valid entries
            if (data.valid_count > 0) {
                uploadBtn.disabled = false;
            }
        } else {
            showValidationResult(validationDiv, `❌ Validation error: ${data.error}`, 'error');
        }
        
    } catch (error) {
        showValidationResult(validationDiv, `❌ Validation failed: ${error.message}`, 'error');
    }
}

function displayValidationResults(type, data, div) {
    const hasIssues = data.duplicate_count > 0 || data.error_count > 0;
    
    div.className = `validation-result ${hasIssues ? 'has-issues' : 'clean'}`;
    
    let html = '<div class="validation-summary">';
    html += `📊 <strong>Validation Results:</strong><br>`;
    html += `Total rows: <strong>${data.total_rows}</strong><br>`;
    html += `✅ Valid entries: <strong>${data.valid_count}</strong><br>`;
    
    if (data.duplicate_count > 0) {
        html += `⚠️ Duplicates: <strong>${data.duplicate_count}</strong><br>`;
    }
    if (data.error_count > 0) {
        html += `❌ Errors: <strong>${data.error_count}</strong>`;
    }
    html += '</div>';
    
    if (data.valid_count > 0) {
        html += `<p style="color: #28a745; font-weight: bold; margin: 10px 0;">✅ ${data.valid_count} entries ready to upload!</p>`;
    }
    
    // Show duplicates
    if (data.duplicates.length > 0) {
        html += '<div class="validation-details">';
        html += `<h4>⚠️ Duplicates Found (${data.duplicates.length}):</h4>`;
        
        const showCount = Math.min(data.duplicates.length, 3);
        for (let i = 0; i < showCount; i++) {
            const dup = data.duplicates[i];
            html += `<div class="validation-item duplicate">`;
            html += `<strong>Row ${dup.row}:</strong> ${dup.reason}`;
            if (dup.existing) {
                const nepaliText = dup.existing.nepali || dup.existing.devanagari || dup.existing.title || dup.existing.youtube_id;
                html += `<br><small>Existing: ${nepaliText}</small>`;
            }
            html += `</div>`;
        }
        if (data.duplicates.length > showCount) {
            html += `<p style="font-size: 12px; color: #666;">... and ${data.duplicates.length - showCount} more duplicates</p>`;
        }
        html += '</div>';
    }
    
    // Show errors
    if (data.errors.length > 0) {
        html += '<div class="validation-details">';
        html += `<h4>❌ Errors Found (${data.errors.length}):</h4>`;
        
        const showCount = Math.min(data.errors.length, 3);
        for (let i = 0; i < showCount; i++) {
            const err = data.errors[i];
            html += `<div class="validation-item error">`;
            html += `<strong>Row ${err.row}:</strong> ${err.reason}`;
            html += `</div>`;
        }
        if (data.errors.length > showCount) {
            html += `<p style="font-size: 12px; color: #666;">... and ${data.errors.length - showCount} more errors</p>`;
        }
        html += '</div>';
    }
    
    div.innerHTML = html;
}

function showValidationResult(div, message, type) {
    div.className = `validation-result ${type}`;
    div.innerHTML = message;
}

// Upload CSV
async function uploadCSV(type) {
    const fileInput = document.getElementById(`${type}-file`);
    const resultDiv = document.getElementById(`${type}-result`);
    const uploadBtn = document.getElementById(`upload-${type}-btn`);
    const file = fileInput.files[0];
    
    if (!file) {
        showUploadResult(resultDiv, 'Please select a file', 'error');
        return;
    }
    
    // Disable button and show loading
    uploadBtn.disabled = true;
    resultDiv.className = 'upload-result loading';
    resultDiv.innerHTML = '⏳ Uploading... please wait';
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('skip_duplicates', 'true');
    
    try {
        const response = await fetch(`/api/bulk/${type}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            let message = `<strong>✅ Upload Successful!</strong><br>`;
            message += `Added: <strong>${data.added}</strong> new entries<br>`;
            if (data.skipped > 0) {
                message += `Skipped: <strong>${data.skipped}</strong> duplicates<br>`;
            }
            if (data.errors.length > 0) {
                message += `<br><strong>⚠️ ${data.errors.length} errors occurred:</strong><br>`;
                for (let i = 0; i < Math.min(data.errors.length, 3); i++) {
                    message += `• ${data.errors[i]}<br>`;
                }
                if (data.errors.length > 3) {
                    message += `... and ${data.errors.length - 3} more`;
                }
            }
            showUploadResult(resultDiv, message, 'success');
            fileInput.value = ''; // Clear file input
        } else {
            showUploadResult(resultDiv, `❌ Error: ${data.error}`, 'error');
        }
        
    } catch (error) {
        showUploadResult(resultDiv, `❌ Upload failed: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
    }
}

function showUploadResult(div, message, type) {
    div.className = `upload-result ${type}`;
    div.innerHTML = message;
}

// ===== DICTIONARY VIEW FUNCTIONS =====

async function loadDictionary(page = 1) {
    try {
        const category = document.getElementById('dictionary-category-filter')?.value || '';
        const difficulty = document.getElementById('dictionary-difficulty-filter')?.value || '';
        
        let url = `${API_BASE_URL}/dictionary/?page=${page}&per_page=50`;
        if (category) url += `&category=${category}`;
        if (difficulty) url += `&difficulty=${difficulty}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        dictionaryWords = data.words;
        currentDictionaryPage = data.current_page;
        
        renderDictionaryTable();
        renderDictionaryPagination(data.pages, data.current_page);
        updateDictionaryStats(data.total);
    } catch (error) {
        console.error('Error loading dictionary:', error);
        document.getElementById('dictionary-table-body').innerHTML = 
            '<tr><td colspan="5" class="text-center" style="color: red;">Error loading dictionary</td></tr>';
    }
}

function renderDictionaryTable() {
    const tbody = document.getElementById('dictionary-table-body');
    const searchTerm = document.getElementById('dictionary-search')?.value.toLowerCase() || '';
    
    let filtered = dictionaryWords;
    if (searchTerm) {
        filtered = dictionaryWords.filter(word => 
            word.nepali.toLowerCase().includes(searchTerm) ||
            word.romanized.toLowerCase().includes(searchTerm) ||
            word.english.toLowerCase().includes(searchTerm)
        );
    }
    
    // Update stats after filtering
    updateDictionaryStats(dictionaryWords.length);
    
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No words found</td></tr>';
        return;
    }
    
    tbody.innerHTML = filtered.map(word => `
        <tr>
            <td style="font-family: 'Noto Sans Devanagari', sans-serif; font-size: 20px; font-weight: 600; color: #1a1a1a;">${escapeHtml(word.nepali || word.romanized)}</td>
            <td style="color: #666; font-style: italic;">${escapeHtml(word.romanized)}</td>
            <td style="font-weight: 500;">${escapeHtml(word.english)}</td>
            <td><span class="badge">${escapeHtml(word.category || 'general')}</span></td>
            <td><span class="difficulty-${word.difficulty}">${getDifficultyLabel(word.difficulty)}</span></td>
        </tr>
    `).join('');
}

function renderDictionaryPagination(totalPages, currentPage) {
    const container = document.getElementById('dictionary-pagination');
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<div class="pagination">';
    
    if (currentPage > 1) {
        html += `<button class="btn btn-secondary" onclick="loadDictionary(${currentPage - 1})">← Previous</button>`;
    }
    
    html += `<span style="margin: 0 15px;">Page ${currentPage} of ${totalPages}</span>`;
    
    if (currentPage < totalPages) {
        html += `<button class="btn btn-secondary" onclick="loadDictionary(${currentPage + 1})">Next →</button>`;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function updateDictionaryStats(total) {
    // Update total count
    const totalEl = document.getElementById('dict-total-count');
    if (totalEl) totalEl.textContent = total;
    
    // Calculate unique categories
    const categories = new Set(dictionary.map(w => w.category));
    const categoriesEl = document.getElementById('dict-categories-count');
    if (categoriesEl) categoriesEl.textContent = categories.size;
    
    // Update showing count
    const showingEl = document.getElementById('dict-showing-count');
    if (showingEl) {
        const searchTerm = document.getElementById('dictionary-search')?.value || '';
        const categoryFilter = document.getElementById('dictionary-category-filter')?.value || '';
        const difficultyFilter = document.getElementById('dictionary-difficulty-filter')?.value || '';
        
        let filtered = dictionary;
        if (searchTerm) {
            filtered = filtered.filter(w => 
                w.nepali?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                w.romanized?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                w.english?.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        if (categoryFilter) filtered = filtered.filter(w => w.category === categoryFilter);
        if (difficultyFilter) filtered = filtered.filter(w => w.difficulty == difficultyFilter);
        
        showingEl.textContent = filtered.length;
    }
}

function getDifficultyLabel(level) {
    const labels = {
        1: 'Beginner',
        2: 'Intermediate',
        3: 'Advanced'
    };
    return labels[level] || 'N/A';
}

// ===== VIDEOS VIEW FUNCTIONS (Legacy - kept for potential future use) =====

async function loadVideos() {
    try {
        const tbody = document.getElementById('videos-table-body');
        if (!tbody) return; // Section doesn't exist, skip loading
        
        const category = document.getElementById('videos-category-filter')?.value || '';
        
        let url = `${API_BASE_URL}/resources/videos?per_page=100`;
        if (category) url += `&category=${category}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        videos = data.videos || [];
        renderVideosTable();
        updateVideosStats(videos.length);
    } catch (error) {
        console.error('Error loading videos:', error);
        const tbody = document.getElementById('videos-table-body');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="color: red;">Error loading videos. Please try again.</td></tr>';
        }
    }
}

function renderVideosTable() {
    const tbody = document.getElementById('videos-table-body');
    if (!tbody) return; // Section doesn't exist, skip rendering
    
    const searchTerm = document.getElementById('videos-search')?.value.toLowerCase() || '';
    const categoryFilter = document.getElementById('videos-category-filter')?.value || '';
    const difficultyFilter = document.getElementById('videos-difficulty-filter')?.value || '';
    
    let filtered = videos;
    
    // Apply filters
    if (searchTerm) {
        filtered = filtered.filter(video => 
            video.title.toLowerCase().includes(searchTerm) ||
            video.youtube_id.toLowerCase().includes(searchTerm) ||
            (video.description && video.description.toLowerCase().includes(searchTerm))
        );
    }
    
    if (categoryFilter) {
        filtered = filtered.filter(video => video.category === categoryFilter);
    }
    
    if (difficultyFilter) {
        filtered = filtered.filter(video => video.difficulty == difficultyFilter);
    }
    
    // Update stats after filtering
    updateVideosStats(videos.length);
    
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No videos found</td></tr>';
        return;
    }
    
    tbody.innerHTML = filtered.map(video => `
        <tr>
            <td style="text-align: center;">
                <input type="checkbox" class="video-checkbox" value="${video.id}">
            </td>
            <td>
                <strong style="display: block; margin-bottom: 4px;">${video.title}</strong>
                <small style="color: #666; display: block; line-height: 1.4;">${(video.description || '').substring(0, 100)}${(video.description || '').length > 100 ? '...' : ''}</small>
            </td>
            <td>
                <a href="https://youtube.com/watch?v=${video.youtube_id}" target="_blank" 
                   style="color: #1976d2; text-decoration: none; word-break: break-all; font-size: 0.85rem;"
                   title="Watch on YouTube">
                    ${video.youtube_id}
                </a>
            </td>
            <td>
                <span class="badge" style="display: inline-block; white-space: nowrap;">${video.category || 'general'}</span>
            </td>
            <td style="text-align: center;">
                <span class="badge" style="background: ${getDifficultyColor(video.difficulty)}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem;">
                    Lvl ${video.difficulty || 1}
                </span>
            </td>
            <td style="text-align: center; font-family: monospace; font-size: 0.9rem;">
                ${formatDuration(video.duration)}
            </td>
            <td style="text-align: center;">
                <button onclick="deleteVideo(${video.id})" class="btn btn-danger btn-sm" title="Delete video" style="padding: 6px 10px;">
                    🗑️
                </button>
            </td>
        </tr>
    `).join('');
    
    // Add event listeners for checkboxes
    document.querySelectorAll('.video-checkbox').forEach(cb => {
        cb.addEventListener('change', updateSelectedVideosCount);
    });
}

function getDifficultyColor(difficulty) {
    switch(difficulty) {
        case 1: return '#4CAF50'; // Green
        case 2: return '#FF9800'; // Orange
        case 3: return '#F44336'; // Red
        default: return '#9E9E9E'; // Gray
    }
}

async function deleteVideo(id) {
    if (!confirm('Are you sure you want to delete this video? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/resources/videos/${id}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('✅ Video deleted successfully');
            await loadVideos(); // Reload the list
        } else {
            alert('❌ Error: ' + (result.error || 'Failed to delete video'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Network error: ' + error.message);
    }
}

function updateSelectedVideosCount() {
    const checkboxes = document.querySelectorAll('.video-checkbox:checked');
    const count = checkboxes.length;
    const countSpan = document.getElementById('selected-videos-count');
    const deleteBtn = document.getElementById('mass-delete-videos-btn');
    
    if (countSpan) countSpan.textContent = count;
    if (deleteBtn) deleteBtn.style.display = count > 0 ? 'inline-block' : 'none';
}

async function massDeleteVideos() {
    const checkboxes = document.querySelectorAll('.video-checkbox:checked');
    const ids = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    if (ids.length === 0) {
        alert('⚠️ Please select videos to delete');
        return;
    }
    
    if (!confirm(`Are you sure you want to delete ${ids.length} video(s)? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/resources/videos/bulk-delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert(`✅ ${result.deleted} video(s) deleted successfully`);
            await loadVideos(); // Reload the list
        } else {
            alert('❌ Error: ' + (result.error || 'Failed to delete videos'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Network error: ' + error.message);
    }
}

// ===== MANAGE DICTIONARY FUNCTIONS =====

async function loadManageDictionary(page = 1) {
    try {
        const category = document.getElementById('manage-dict-category')?.value || '';
        const difficulty = document.getElementById('manage-dict-difficulty')?.value || '';
        
        let url = `${API_BASE_URL}/dictionary/?page=${page}&per_page=50`;
        if (category) url += `&category=${category}`;
        if (difficulty) url += `&difficulty=${difficulty}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        manageDictWords = data.words;
        currentManageDictPage = data.current_page;
        
        renderManageDictTable();
        renderManageDictPagination(data.pages, data.current_page);
    } catch (error) {
        console.error('Error loading manage dictionary:', error);
        document.getElementById('manage-dict-table-body').innerHTML = 
            '<tr><td colspan="6" class="text-center" style="color: red;">Error loading dictionary</td></tr>';
    }
}

function renderManageDictTable() {
    const tbody = document.getElementById('manage-dict-table-body');
    const searchTerm = document.getElementById('manage-dict-search')?.value.toLowerCase() || '';
    
    let filtered = manageDictWords;
    if (searchTerm) {
        filtered = manageDictWords.filter(word => 
            word.nepali.toLowerCase().includes(searchTerm) ||
            word.romanized.toLowerCase().includes(searchTerm) ||
            word.english.toLowerCase().includes(searchTerm)
        );
    }
    
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No words found</td></tr>';
        return;
    }
    
    tbody.innerHTML = filtered.map(word => `
        <tr class="draggable-row" draggable="true" data-id="${word.id}">
            <td class="drag-handle">⋮⋮</td>
            <td style="font-family: 'Noto Sans Devanagari', sans-serif; font-size: 20px; font-weight: 600; color: #1a1a1a;">${word.nepali}</td>
            <td style="color: #666; font-style: italic;">${word.romanized}</td>
            <td style="font-weight: 500;">${word.english}</td>
            <td><span class="badge">${word.category || 'general'}</span></td>
            <td><span class="difficulty-${word.difficulty}">${getDifficultyLabel(word.difficulty)}</span></td>
            <td>
                <button class="btn-icon btn-edit" onclick="editWord(${word.id})" title="Edit">✏️</button>
                <button class="btn-icon btn-delete" onclick="deleteWord(${word.id})" title="Delete">🗑️</button>
            </td>
        </tr>
    `).join('');
    
    // Setup drag and drop after rendering
    setupDictionaryDragDrop();
}

function renderManageDictPagination(totalPages, currentPage) {
    const container = document.getElementById('manage-dict-pagination');
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<div class="pagination">';
    
    if (currentPage > 1) {
        html += `<button class="btn btn-secondary" onclick="loadManageDictionary(${currentPage - 1})">← Previous</button>`;
    }
    
    html += `<span style="margin: 0 15px;">Page ${currentPage} of ${totalPages}</span>`;
    
    if (currentPage < totalPages) {
        html += `<button class="btn btn-secondary" onclick="loadManageDictionary(${currentPage + 1})">Next →</button>`;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

async function editWord(wordId) {
    try {
        const response = await fetch(`${API_BASE_URL}/dictionary/${wordId}`);
        currentWord = await response.json();
        
        document.getElementById('word-modal-title').textContent = 'Edit Word';
        document.getElementById('word-id').value = currentWord.id;
        document.getElementById('word-nepali').value = currentWord.nepali;
        document.getElementById('word-romanized').value = currentWord.romanized;
        document.getElementById('word-english').value = currentWord.english;
        document.getElementById('word-category').value = currentWord.category || 'general';
        document.getElementById('word-difficulty').value = currentWord.difficulty || 1;
        document.getElementById('word-part-of-speech').value = currentWord.part_of_speech || '';
        
        document.getElementById('word-modal').classList.add('active');
    } catch (error) {
        console.error('Error loading word:', error);
        alert('Error loading word details');
    }
}

async function deleteWord(wordId) {
    if (!confirm('Are you sure you want to delete this word?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/dictionary/${wordId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadManageDictionary(currentManageDictPage);
            alert('Word deleted successfully');
        } else {
            alert('Error deleting word');
        }
    } catch (error) {
        console.error('Error deleting word:', error);
        alert('Error deleting word');
    }
}

async function saveWordData() {
    const wordId = document.getElementById('word-id').value;
    const data = {
        nepali: document.getElementById('word-nepali').value,
        romanized: document.getElementById('word-romanized').value,
        english: document.getElementById('word-english').value,
        category: document.getElementById('word-category').value,
        difficulty: parseInt(document.getElementById('word-difficulty').value),
        part_of_speech: document.getElementById('word-part-of-speech').value
    };
    
    try {
        const url = wordId ? `${API_BASE_URL}/dictionary/${wordId}` : `${API_BASE_URL}/dictionary/`;
        const method = wordId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success !== false) {
            alert('Word saved successfully! ✅');
            document.getElementById('word-modal').classList.remove('active');
            await loadManageDictionary(currentManageDictPage);
            // Also refresh the view dictionary if it's the current section
            await loadDictionary(currentDictionaryPage);
        } else {
            const errorMsg = result.error || result.message || 'Unknown error';
            alert('❌ Error saving word:\n\n' + errorMsg + '\n\nPlease check if this word already exists or try different text.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Network error: ' + error.message + '\n\nPlease check your connection and try again.');
    }
}

function updateVideosStats(total) {
    // Update total count
    const totalEl = document.getElementById('videos-total-count');
    if (totalEl) totalEl.textContent = total;
    
    // Calculate unique categories
    const categories = new Set(videos.map(v => v.category));
    const categoriesEl = document.getElementById('videos-categories-count');
    if (categoriesEl) categoriesEl.textContent = categories.size;
    
    // Update showing count
    const showingEl = document.getElementById('videos-showing-count');
    if (showingEl) {
        const searchTerm = document.getElementById('videos-search')?.value || '';
        const categoryFilter = document.getElementById('videos-category-filter')?.value || '';
        
        let filtered = videos;
        if (searchTerm) {
            filtered = filtered.filter(v => 
                v.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                v.youtube_id?.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        if (categoryFilter) filtered = filtered.filter(v => v.category === categoryFilter);
        
        showingEl.textContent = filtered.length;
    }
}

function formatDuration(seconds) {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Video Preview Function
function previewVideo() {
    const urlInput = document.getElementById('video-preview-url');
    const url = urlInput.value.trim();
    
    if (!url) {
        alert('⚠️ Please enter a YouTube URL');
        return;
    }
    
    // Extract video ID from various YouTube URL formats
    let videoId = null;
    
    // Pattern 1: https://www.youtube.com/watch?v=VIDEO_ID
    // Pattern 2: https://youtu.be/VIDEO_ID
    // Pattern 3: https://www.youtube.com/embed/VIDEO_ID
    
    try {
        const urlObj = new URL(url);
        
        if (urlObj.hostname.includes('youtube.com')) {
            videoId = urlObj.searchParams.get('v');
        } else if (urlObj.hostname.includes('youtu.be')) {
            videoId = urlObj.pathname.slice(1).split('?')[0];
        }
        
        // If not found, try regex as fallback
        if (!videoId) {
            const match = url.match(/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/);
            if (match && match[1]) {
                videoId = match[1];
            }
        }
        
        if (!videoId) {
            alert('⚠️ Could not extract video ID from URL. Please use a valid YouTube URL format:\n\n' +
                  '✓ https://www.youtube.com/watch?v=VIDEO_ID\n' +
                  '✓ https://youtu.be/VIDEO_ID');
            return;
        }
        
        // Display the video
        const iframe = document.getElementById('video-preview-iframe');
        const container = document.getElementById('video-preview-container');
        const idDisplay = document.getElementById('video-id-display');
        
        iframe.src = `https://www.youtube.com/embed/${videoId}`;
        idDisplay.textContent = videoId;
        container.style.display = 'block';
        
        // Scroll to preview
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        alert('⚠️ Invalid URL format. Please enter a valid YouTube URL.');
        console.error('Error parsing URL:', error);
    }
}

// ========== ADVANCED DICTIONARY FEATURES ==========

// Global Search
document.getElementById('global-search-btn')?.addEventListener('click', function() {
    document.getElementById('global-search-modal').classList.add('active');
    document.getElementById('global-search-input').focus();
});

document.getElementById('global-search-close')?.addEventListener('click', function() {
    document.getElementById('global-search-modal').classList.remove('active');
});

document.getElementById('global-search-input')?.addEventListener('input', debounce(async function(e) {
    const query = e.target.value.trim();
    if (query.length < 2) {
        document.getElementById('global-search-results').innerHTML = '<p class="text-center" style="color: #888;">Enter at least 2 characters</p>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/dictionary/global-search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        const resultsDiv = document.getElementById('global-search-results');
        const totalResults = data.total_results || 0;
        
        if (totalResults === 0) {
            resultsDiv.innerHTML = '<p class="text-center" style="color: #888;">No results found</p>';
            return;
        }
        
        let html = `<h3>Found ${totalResults} results</h3>`;
        
        // Dictionary results
        if (data.dictionary && data.dictionary.length > 0) {
            html += `<div style="margin-top: 1rem;">
                <h4>📚 Dictionary (${data.dictionary.length})</h4>
                <div style="max-height: 200px; overflow-y: auto;">`;
            data.dictionary.forEach(item => {
                html += `<div style="padding: 0.5rem; border-bottom: 1px solid #eee;">
                    <strong>${escapeHtml(item.nepali)}</strong> (${escapeHtml(item.romanized)}) - ${escapeHtml(item.english)}
                    <span style="color: #888; font-size: 0.9rem;">${escapeHtml(item.category || '')}</span>
                </div>`;
            });
            html += '</div></div>';
        }
        
        // Alphabet results
        if (data.alphabet && data.alphabet.length > 0) {
            html += `<div style="margin-top: 1rem;">
                <h4>🔤 Alphabet (${data.alphabet.length})</h4>
                <div style="max-height: 150px; overflow-y: auto;">`;
            data.alphabet.forEach(item => {
                html += `<div style="padding: 0.5rem; border-bottom: 1px solid #eee;">
                    <strong style="font-size: 1.2rem;">${escapeHtml(item.devanagari)}</strong> (${escapeHtml(item.romanized)}) - ${escapeHtml(item.sound)}
                </div>`;
            });
            html += '</div></div>';
        }
        
        // Phrase results
        if (data.phrases && data.phrases.length > 0) {
            html += `<div style="margin-top: 1rem;">
                <h4>💬 Phrases (${data.phrases.length})</h4>
                <div style="max-height: 200px; overflow-y: auto;">`;
            data.phrases.forEach(item => {
                html += `<div style="padding: 0.5rem; border-bottom: 1px solid #eee;">
                    <strong>${escapeHtml(item.nepali)}</strong> (${escapeHtml(item.romanized)}) - ${escapeHtml(item.english)}
                    <span style="color: #888; font-size: 0.9rem;">${escapeHtml(item.category || '')}</span>
                </div>`;
            });
            html += '</div></div>';
        }
        
        resultsDiv.innerHTML = html;
    } catch (error) {
        console.error('Error searching:', error);
        document.getElementById('global-search-results').innerHTML = '<p class="text-center" style="color: red;">Error performing search</p>';
    }
}, 300));

// Statistics Dashboard
document.getElementById('show-statistics-btn')?.addEventListener('click', async function() {
    document.getElementById('statistics-modal').classList.add('active');
    await loadStatistics();
});

document.getElementById('statistics-close')?.addEventListener('click', function() {
    document.getElementById('statistics-modal').classList.remove('active');
});

async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/dictionary/statistics`);
        const stats = await response.json();
        
        const content = document.getElementById('statistics-content');
        content.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
                <!-- Total Content -->
                <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 10px;">
                    <h3 style="margin: 0 0 0.5rem 0;">📊 Total Content</h3>
                    <p style="font-size: 2.5rem; font-weight: bold; margin: 0;">${stats.totals.all_content}</p>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">All learning materials</p>
                </div>
                
                <!-- Dictionary -->
                <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1.5rem; border-radius: 10px;">
                    <h3 style="margin: 0 0 0.5rem 0;">📚 Dictionary</h3>
                    <p style="font-size: 2.5rem; font-weight: bold; margin: 0;">${stats.dictionary.total}</p>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">${Object.keys(stats.dictionary.by_category || {}).length} categories</p>
                </div>
                
                <!-- Alphabet -->
                <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 1.5rem; border-radius: 10px;">
                    <h3 style="margin: 0 0 0.5rem 0;">🔤 Alphabet</h3>
                    <p style="font-size: 2.5rem; font-weight: bold; margin: 0;">${stats.alphabet.total}</p>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">${stats.alphabet.vowels} vowels, ${stats.alphabet.consonants} consonants</p>
                </div>
                
                <!-- Phrases -->
                <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 1.5rem; border-radius: 10px;">
                    <h3 style="margin: 0 0 0.5rem 0;">💬 Phrases</h3>
                    <p style="font-size: 2.5rem; font-weight: bold; margin: 0;">${stats.phrases.total}</p>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">${Object.keys(stats.phrases.by_category || {}).length} categories</p>
                </div>
            </div>
            
            <!-- Detailed Breakdown -->
            <div style="margin-top: 2rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
                    <h3>📚 Dictionary by Difficulty</h3>
                    ${Object.entries(stats.dictionary.by_difficulty || {}).map(([level, count]) => `
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #dee2e6;">
                            <span>Level ${level}</span>
                            <strong>${count}</strong>
                        </div>
                    `).join('')}
                </div>
                
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
                    <h3>💬 Phrases by Formality</h3>
                    ${Object.entries(stats.phrases.by_formality || {}).map(([level, count]) => `
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #dee2e6;">
                            <span>${level || 'casual'}</span>
                            <strong>${count}</strong>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <!-- Popular Words -->
            <div style="margin-top: 2rem; background: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
                <h3>🔥 Most Popular Words</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    ${stats.dictionary.popular.map(word => `
                        <div style="padding: 0.8rem; background: white; border-radius: 5px; border-left: 4px solid var(--accent-color);">
                            <strong>${escapeHtml(word.nepali)}</strong><br>
                            <small style="color: #888;">${word.views} views</small>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading statistics:', error);
        document.getElementById('statistics-content').innerHTML = '<p style="color: red;">Error loading statistics</p>';
    }
}

// Bulk Operations
document.getElementById('bulk-operations-btn')?.addEventListener('click', function() {
    document.getElementById('bulk-operations-modal').classList.add('active');
});

document.getElementById('bulk-operations-close')?.addEventListener('click', function() {
    document.getElementById('bulk-operations-modal').classList.remove('active');
});

document.getElementById('bulk-operations-cancel')?.addEventListener('click', function() {
    document.getElementById('bulk-operations-modal').classList.remove('active');
});

document.getElementById('bulk-operation-type')?.addEventListener('change', function() {
    const operation = this.value;
    document.getElementById('bulk-category-group').style.display = operation === 'update-category' ? 'block' : 'none';
    document.getElementById('bulk-difficulty-group').style.display = operation === 'update-difficulty' ? 'block' : 'none';
});

document.getElementById('bulk-operations-form')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    await executeBulkOperation();
});

async function executeBulkOperation() {
    const operation = document.getElementById('bulk-operation-type').value;
    const idsText = document.getElementById('bulk-ids').value;
    
    if (!operation || !idsText) {
        alert('Please select an operation and enter IDs');
        return;
    }
    
    const ids = idsText.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));
    
    if (ids.length === 0) {
        alert('No valid IDs provided');
        return;
    }
    
    if (!confirm(`Are you sure you want to perform this operation on ${ids.length} items?`)) {
        return;
    }
    
    try {
        let url = '';
        let data = { ids };
        
        switch (operation) {
            case 'delete':
                url = `${API_BASE_URL}/dictionary/bulk-delete`;
                break;
            case 'update-category':
                url = `${API_BASE_URL}/dictionary/bulk-update-category`;
                data.category = document.getElementById('bulk-new-category').value;
                break;
            case 'update-difficulty':
                url = `${API_BASE_URL}/dictionary/bulk-update-difficulty`;
                data.difficulty = parseInt(document.getElementById('bulk-new-difficulty').value);
                break;
            default:
                alert('Invalid operation');
                return;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            alert(`✅ ${result.message}`);
            document.getElementById('bulk-operations-modal').classList.remove('active');
            document.getElementById('bulk-operations-form').reset();
            loadManageDictionary();
        } else {
            alert(`❌ Error: ${result.error || 'Operation failed'}`);
        }
    } catch (error) {
        console.error('Error executing bulk operation:', error);
        alert('Error executing bulk operation');
    }
}

// Utility: Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===== LOGIN HANDLER (missing) =====
document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        const remember = document.getElementById('remember').checked;

        if (!username || !password) {
            alert('Please enter both username and password');
            return;
        }

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ username, password, remember })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Redirect to the original page (next parameter)
                const urlParams = new URLSearchParams(window.location.search);
                const next = urlParams.get('next') || '/admin';
                window.location.href = next;
            } else {
                alert(data.message || 'Login failed');
            }
        } catch (err) {
            console.error(err);
            alert('Network error');
        }
    });
});

// Add event listeners for search fields
document.getElementById('phrase-search')?.addEventListener('input', renderPhrasesTable);
document.getElementById('phrase-category-filter')?.addEventListener('change', renderPhrasesTable);
document.getElementById('phrase-formality-filter')?.addEventListener('change', renderPhrasesTable);
document.getElementById('alphabet-search')?.addEventListener('input', renderAlphabetTable);
document.getElementById('letter-type-filter')?.addEventListener('change', renderAlphabetTable);


