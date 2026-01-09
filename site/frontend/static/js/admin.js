// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State
let currentPhrase = null;
let currentLetter = null;
let phrases = [];
let alphabet = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupNavigation();
    loadPhrases();
    loadAlphabet();
    setupModals();
    setupEventListeners();
});

// Navigation
function setupNavigation() {
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.dataset.section;
            
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
    
    let filtered = phrases.filter(p => {
        const matchesSearch = p.nepali.includes(searchValue) || 
                            p.romanized.includes(searchValue) || 
                            p.english.includes(searchValue);
        const matchesCategory = !categoryFilter || p.category === categoryFilter;
        return matchesSearch && matchesCategory;
    });
    
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No phrases found</td></tr>';
        return;
    }
    
    tbody.innerHTML = filtered.map(phrase => `
        <tr>
            <td>${phrase.nepali}</td>
            <td>${phrase.romanized}</td>
            <td>${phrase.english}</td>
            <td><span style="background: var(--accent-color); padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem;">${phrase.category}</span></td>
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
    document.getElementById('phrase-modal').classList.add('show');
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
        renderAlphabetTable();
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
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No letters found</td></tr>';
        return;
    }
    
    tbody.innerHTML = filtered.map(letter => `
        <tr>
            <td style="font-size: 1.3rem; font-family: 'Noto Sans Devanagari';">${letter.devanagari}</td>
            <td>${letter.romanized}</td>
            <td>${letter.type}</td>
            <td>${letter.pronunciation || '-'}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editLetter(${letter.id})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteLetter(${letter.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function editLetter(id) {
    currentLetter = alphabet.find(l => l.id === id);
    document.getElementById('letter-devanagari').value = currentLetter.devanagari;
    document.getElementById('letter-romanized').value = currentLetter.romanized;
    document.getElementById('letter-type').value = currentLetter.type;
    document.getElementById('letter-pronunciation').value = currentLetter.pronunciation;
    document.getElementById('letter-modal').classList.add('show');
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

// Modal Setup
function setupModals() {
    // Phrase Modal
    document.getElementById('add-phrase-btn').addEventListener('click', function() {
        currentPhrase = null;
        document.getElementById('modal-title').textContent = 'Add New Phrase';
        document.getElementById('phrase-form').reset();
        document.getElementById('phrase-modal').classList.add('show');
    });
    
    document.getElementById('phrase-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        await savePhraseData();
    });
    
    // Letter Modal
    document.getElementById('add-letter-btn').addEventListener('click', function() {
        currentLetter = null;
        document.getElementById('letter-form').reset();
        document.getElementById('letter-modal').classList.add('show');
    });
    
    document.getElementById('letter-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        await saveLetterData();
    });
    
    // Close modals
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.modal').classList.remove('show');
        });
    });
    
    document.getElementById('modal-cancel').addEventListener('click', function() {
        document.getElementById('phrase-modal').classList.remove('show');
    });
    
    document.getElementById('letter-modal-cancel').addEventListener('click', function() {
        document.getElementById('letter-modal').classList.remove('show');
    });
}

// Save Functions
async function savePhraseData() {
    const data = {
        nepali: document.getElementById('phrase-nepali').value,
        romanized: document.getElementById('phrase-romanized').value,
        english: document.getElementById('phrase-english').value,
        category: document.getElementById('phrase-category').value
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
            document.getElementById('phrase-modal').classList.remove('show');
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
            alert('Letter saved successfully');
            document.getElementById('letter-modal').classList.remove('show');
            loadAlphabet();
        } else {
            alert('Error saving letter');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error saving letter');
    }
}

// Event Listeners
function setupEventListeners() {
    document.getElementById('phrase-search').addEventListener('input', renderPhrasesTable);
    document.getElementById('phrase-category-filter').addEventListener('change', renderPhrasesTable);
    document.getElementById('alphabet-search').addEventListener('input', renderAlphabetTable);
    document.getElementById('letter-type-filter').addEventListener('change', renderAlphabetTable);
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        const phraseModal = document.getElementById('phrase-modal');
        const letterModal = document.getElementById('letter-modal');
        
        if (e.target === phraseModal) {
            phraseModal.classList.remove('show');
        }
        if (e.target === letterModal) {
            letterModal.classList.remove('show');
        }
    });
}
