// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State Management
let currentAlphabetFilter = 'all';
let currentCategory = '';
let phrases = [];
let alphabet = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadAlphabet();
    loadPhrases();
    loadTransliteratorRules();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // Alphabet filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentAlphabetFilter = this.dataset.type;
            renderAlphabet();
        });
    });

    // Transliterator
    const convertBtn = document.getElementById('convert-btn');
    const romanInput = document.getElementById('roman-input');
    
    convertBtn.addEventListener('click', convertText);
    romanInput.addEventListener('input', debounce(convertText, 500));

    // Phrases
    document.getElementById('category-filter').addEventListener('change', function() {
        currentCategory = this.value;
        renderPhrases();
    });

    document.getElementById('phrase-search').addEventListener('input', debounce(function() {
        renderPhrases();
    }, 300));
}

// API Functions
async function loadAlphabet() {
    try {
        const response = await fetch(`${API_BASE_URL}/alphabet/`);
        alphabet = await response.json();
        renderAlphabet();
    } catch (error) {
        console.error('Error loading alphabet:', error);
    }
}

async function loadPhrases() {
    try {
        const response = await fetch(`${API_BASE_URL}/phrases/`);
        phrases = await response.json();
        
        // Load categories
        const categoryResponse = await fetch(`${API_BASE_URL}/phrases/categories`);
        const categories = await categoryResponse.json();
        renderCategories(categories);
        
        renderPhrases();
    } catch (error) {
        console.error('Error loading phrases:', error);
    }
}

async function loadTransliteratorRules() {
    try {
        const response = await fetch(`${API_BASE_URL}/transliterator/rules`);
        const rules = await response.json();
        renderTransliteratorRules(rules);
    } catch (error) {
        console.error('Error loading transliterator rules:', error);
    }
}

async function convertText() {
    const text = document.getElementById('roman-input').value;
    if (!text) {
        document.getElementById('devanagari-output').textContent = '';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/transliterator/convert`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text }),
        });
        
        const result = await response.json();
        document.getElementById('devanagari-output').textContent = result.devanagari;
    } catch (error) {
        console.error('Error converting text:', error);
    }
}

// Rendering Functions
function renderAlphabet() {
    const grid = document.getElementById('alphabet-grid');
    const filteredAlphabet = currentAlphabetFilter === 'all' 
        ? alphabet 
        : alphabet.filter(letter => letter.type === currentAlphabetFilter);

    grid.innerHTML = filteredAlphabet.map(letter => `
        <div class="letter-card">
            <div class="letter-devanagari">${letter.devanagari}</div>
            <div class="letter-romanized">${letter.romanized}</div>
            <div class="letter-pronunciation">${letter.pronunciation || ''}</div>
        </div>
    `).join('');
}

function renderCategories(categories) {
    const select = document.getElementById('category-filter');
    select.innerHTML = '<option value="">All Categories</option>' +
        categories.map(cat => `<option value="${cat}">${cat.charAt(0).toUpperCase() + cat.slice(1)}</option>`).join('');
}

function renderPhrases() {
    const container = document.getElementById('phrases-container');
    const searchTerm = document.getElementById('phrase-search').value.toLowerCase();
    
    let filteredPhrases = phrases;
    
    if (currentCategory) {
        filteredPhrases = filteredPhrases.filter(p => p.category === currentCategory);
    }
    
    if (searchTerm) {
        filteredPhrases = filteredPhrases.filter(p => 
            p.nepali.toLowerCase().includes(searchTerm) ||
            p.romanized.toLowerCase().includes(searchTerm) ||
            p.english.toLowerCase().includes(searchTerm)
        );
    }

    container.innerHTML = filteredPhrases.map(phrase => `
        <div class="phrase-card">
            <div class="phrase-nepali">${phrase.nepali}</div>
            <div class="phrase-romanized">${phrase.romanized}</div>
            <div class="phrase-english">${phrase.english}</div>
            <span class="phrase-category">${phrase.category}</span>
        </div>
    `).join('');
}

function renderTransliteratorRules(rules) {
    const container = document.getElementById('rules-container');
    
    container.innerHTML = `
        <div class="rules-section">
            <h4>Vowels</h4>
            <div class="rules-grid">
                ${Object.entries(rules.vowels).map(([roman, deva]) => `
                    <div class="rule-item">
                        <span class="rule-roman">${roman}</span>
                        <span class="rule-arrow">→</span>
                        <span class="rule-deva">${deva}</span>
                    </div>
                `).join('')}
            </div>
        </div>
        <div class="rules-section">
            <h4>Consonants</h4>
            <div class="rules-grid">
                ${Object.entries(rules.consonants).map(([roman, deva]) => `
                    <div class="rule-item">
                        <span class="rule-roman">${roman}</span>
                        <span class="rule-arrow">→</span>
                        <span class="rule-deva">${deva}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Utility Functions
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