// API Configuration
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

// State Management
let currentAlphabetFilter = 'all';
let currentCategory = '';
let phrases = [];
let alphabet = [];
let dictionaryWords = [];
let videos = [];
let currentDictPage = 1;
let dictCategory = '';
let dictDifficulty = '';
let dictSearch = '';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadAlphabet();
    loadPhrases();
    loadTransliteratorRules();
    loadDictionary();
    loadVideos();
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

    // Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            const expanded = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', (!expanded).toString());
            navMenu.classList.toggle('open');
        });

        // Close mobile menu when a nav link is clicked
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    navMenu.classList.remove('open');
                    navToggle.setAttribute('aria-expanded', 'false');
                }
            });
        });
    }

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

    // Dictionary
    document.getElementById('dict-category-filter')?.addEventListener('change', function() {
        dictCategory = this.value;
        currentDictPage = 1;
        loadDictionary();
    });

    document.getElementById('dict-difficulty-filter')?.addEventListener('change', function() {
        dictDifficulty = this.value;
        currentDictPage = 1;
        loadDictionary();
    });

    document.getElementById('dict-search')?.addEventListener('input', debounce(function() {
        dictSearch = this.value;
        currentDictPage = 1;
        loadDictionary();
    }, 300));

    // Videos
    document.getElementById('video-category-filter')?.addEventListener('change', function() {
        renderVideos();
    });

    document.getElementById('video-search')?.addEventListener('input', debounce(function() {
        renderVideos();
    }, 300));
}

// API Functions
async function loadAlphabet() {
    try {
        const response = await fetch(`${API_BASE_URL}/alphabet/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        alphabet = await response.json();
        console.log(`✅ Loaded ${alphabet.length} alphabet letters`);
        renderAlphabet();
    } catch (error) {
        console.error('❌ Error loading alphabet:', error);
        const grid = document.getElementById('alphabet-grid');
        if (grid) {
            grid.innerHTML = '<p style="text-align: center; color: red;">Error loading alphabet. Please refresh the page.</p>';
        }
    }
}

async function loadPhrases() {
    try {
        const response = await fetch(`${API_BASE_URL}/phrases/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        phrases = await response.json();
        console.log(`✅ Loaded ${phrases.length} phrases`);
        
        // Extract unique categories from phrases
        const uniqueCategories = [...new Set(phrases.map(p => p.category).filter(c => c))];
        console.log(`✅ Found ${uniqueCategories.length} categories:`, uniqueCategories);
        renderCategories(uniqueCategories);
        
        renderPhrases();
    } catch (error) {
        console.error('❌ Error loading phrases:', error);
        const container = document.getElementById('phrases-container');
        if (container) {
            container.innerHTML = '<p style="text-align: center; color: red;">Error loading phrases. Please refresh the page.</p>';
        }
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

async function loadDictionary(page = 1) {
    try {
        let url = `${API_BASE_URL}/dictionary/?page=${page}&per_page=12`;
        if (dictCategory) url += `&category=${dictCategory}`;
        if (dictDifficulty) url += `&difficulty=${dictDifficulty}`;

        console.log(`🔍 Fetching dictionary from: ${url}`);
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`✅ Loaded ${data.words.length} dictionary words (page ${data.current_page}/${data.pages})`);
        
        dictionaryWords = data.words;
        currentDictPage = data.current_page;
        
        // Load categories on first load (page 1 without filters)
        if (page === 1 && !dictCategory && !dictDifficulty) {
            loadDictionaryCategories();
        }
        
        renderDictionary(data.pages, data.current_page);
    } catch (error) {
        console.error('❌ Error loading dictionary:', error);
        document.getElementById('dictionary-grid').innerHTML = 
            '<p style="text-align: center; color: red;">Error loading dictionary. Please try again.</p>';
    }
}

async function loadDictionaryCategories() {
    try {
        // Use dedicated categories endpoint
        const response = await fetch(`${API_BASE_URL}/dictionary/categories`);
        if (!response.ok) {
            console.warn('Categories endpoint not available, using fallback');
            return;
        }
        
        const categories = await response.json();
        console.log(`✅ Found ${categories.length} dictionary categories:`, categories);
        
        const select = document.getElementById('dict-category-filter');
        if (select) {
            select.innerHTML = '<option value="">All Categories</option>' +
                categories.sort().map(cat => `<option value="${escapeHtml(cat)}">${escapeHtml(cat.charAt(0).toUpperCase() + cat.slice(1))}</option>`).join('');
            console.log('✅ Dictionary categories dropdown populated');
        }
    } catch (error) {
        console.warn('⚠️ Could not load dictionary categories:', error);
    }
}

async function loadVideos() {
    try {
        const response = await fetch(`${API_BASE_URL}/resources/videos`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // Handle both array response and object with videos property
        videos = Array.isArray(data) ? data : (data.videos || []);
        console.log(`✅ Loaded ${videos.length} videos`);
        renderVideos();
    } catch (error) {
        console.error('❌ Error loading videos:', error);
        const grid = document.getElementById('videos-grid');
        if (grid) {
            grid.innerHTML = '<p style="text-align: center; color: red;">Error loading videos. Please try again.</p>';
        }
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
            <div class="letter-devanagari">${escapeHtml(letter.devanagari)}</div>
            <div class="letter-romanized">${escapeHtml(letter.romanized)}</div>
            <div class="letter-pronunciation">${escapeHtml(letter.pronunciation || '')}</div>
        </div>
    `).join('');
}

function renderCategories(categories) {
    const select = document.getElementById('category-filter');
    if (!select) {
        console.warn('Category filter dropdown not found');
        return;
    }
    select.innerHTML = '<option value="">All Categories</option>' +
        categories.map(cat => `<option value="${escapeHtml(cat)}">${escapeHtml(cat.charAt(0).toUpperCase() + cat.slice(1))}</option>`).join('');
    console.log('✅ Categories dropdown populated');
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
            <div class="phrase-nepali">${escapeHtml(phrase.nepali)}</div>
            <div class="phrase-romanized">${escapeHtml(phrase.romanized)}</div>
            <div class="phrase-english">${escapeHtml(phrase.english)}</div>
            <span class="phrase-category">${escapeHtml(phrase.category)}</span>
        </div>
    `).join('');
}

function renderDictionary(totalPages, currentPage) {
    const grid = document.getElementById('dictionary-grid');
    const searchTerm = dictSearch.toLowerCase();
    
    let filtered = dictionaryWords;
    if (searchTerm) {
        filtered = dictionaryWords.filter(word =>
            word.nepali.toLowerCase().includes(searchTerm) ||
            word.romanized.toLowerCase().includes(searchTerm) ||
            word.english.toLowerCase().includes(searchTerm)
        );
    }

    if (filtered.length === 0) {
        grid.innerHTML = '<p style="text-align: center; color: #666; grid-column: 1/-1;">No words found</p>';
        return;
    }

    grid.innerHTML = filtered.map(word => {
        const difficultyClass = word.difficulty === 1 ? 'beginner' : word.difficulty === 2 ? 'intermediate' : 'advanced';
        const difficultyLabel = word.difficulty === 1 ? 'Beginner' : word.difficulty === 2 ? 'Intermediate' : 'Advanced';
        
        return `
            <div class="word-card">
                <div class="word-nepali">${escapeHtml(word.nepali)}</div>
                <div class="word-romanized">${escapeHtml(word.romanized)}</div>
                <div class="word-english">${escapeHtml(word.english)}</div>
                <div class="word-meta">
                    <span class="word-badge badge-category">${escapeHtml(word.category || 'general')}</span>
                    <span class="word-badge badge-difficulty ${difficultyClass}">${difficultyLabel}</span>
                </div>
            </div>
        `;
    }).join('');

    // Pagination
    const paginationDiv = document.getElementById('dict-pagination');
    if (totalPages > 1) {
        let html = '';
        if (currentPage > 1) {
            html += `<button onclick="loadDictionary(${currentPage - 1})">← Previous</button>`;
        }
        html += `<span style="padding: 0 20px; font-weight: 600;">Page ${currentPage} of ${totalPages}</span>`;
        if (currentPage < totalPages) {
            html += `<button onclick="loadDictionary(${currentPage + 1})">Next →</button>`;
        }
        paginationDiv.innerHTML = html;
    } else {
        paginationDiv.innerHTML = '';
    }
}

function renderVideos() {
    const grid = document.getElementById('videos-grid');
    if (!grid) return; // Element doesn't exist, skip rendering
    
    const categoryFilter = document.getElementById('video-category-filter')?.value || '';
    const searchTerm = document.getElementById('video-search')?.value.toLowerCase() || '';
    
    let filtered = Array.isArray(videos) ? videos : [];
    
    if (categoryFilter) {
        filtered = filtered.filter(v => v.category === categoryFilter);
    }
    
    if (searchTerm) {
        filtered = filtered.filter(v =>
            v.title.toLowerCase().includes(searchTerm) ||
            v.channel_name.toLowerCase().includes(searchTerm)
        );
    }

    if (filtered.length === 0) {
        grid.innerHTML = '<p style="text-align: center; color: #666; grid-column: 1/-1;">No videos found</p>';
        return;
    }

    grid.innerHTML = filtered.map(video => {
        // Use youtube_id directly from the database
        const videoId = video.youtube_id || '';
        const youtubeUrl = `https://www.youtube.com/watch?v=${videoId}`;
        // Use YouTube's thumbnail API (much lighter than iframe)
        const thumbnailUrl = video.thumbnail_url || `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
        const duration = video.duration ? formatVideoDuration(video.duration) : '';

        return `
            <div class="video-card" onclick="window.open('${escapeHtml(youtubeUrl)}', '_blank')">
                <div class="video-thumbnail">
                    <img src="${escapeHtml(thumbnailUrl)}" 
                         alt="${escapeHtml(video.title || 'Video thumbnail')}"
                         loading="lazy"
                         onerror="this.src='https://img.youtube.com/vi/${escapeHtml(videoId)}/hqdefault.jpg'">
                    <div class="play-button-overlay">
                        <svg width="68" height="48" viewBox="0 0 68 48" fill="none">
                            <path d="M66.52,7.74c-0.78-2.93-2.49-5.41-5.42-6.19C55.79,.13,34,0,34,0S12.21,.13,6.9,1.55 C3.97,2.33,2.27,4.81,1.48,7.74C0.06,13.05,0,24,0,24s0.06,10.95,1.48,16.26c0.78,2.93,2.49,5.41,5.42,6.19 C12.21,47.87,34,48,34,48s21.79-0.13,27.1-1.55c2.93-0.78,4.64-3.26,5.42-6.19C67.94,34.95,68,24,68,24S67.94,13.05,66.52,7.74z" fill="#f00"></path>
                            <path d="M 45,24 27,14 27,34" fill="#fff"></path>
                        </svg>
                    </div>
                    ${duration ? `<div class="video-duration">${escapeHtml(duration)}</div>` : ''}
                </div>
                <div class="video-info">
                    <h3 class="video-title">${escapeHtml(video.title || 'Untitled Video')}</h3>
                    <p class="video-description">${escapeHtml((video.description || '').substring(0, 100))}${(video.description || '').length > 100 ? '...' : ''}</p>
                    <div class="video-meta">
                        <span class="word-badge badge-category">${video.category || 'general'}</span>
                        ${video.difficulty ? `<span class="word-badge badge-difficulty-${video.difficulty}">Level ${video.difficulty}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function formatVideoDuration(seconds) {
    if (!seconds) return '';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function renderTransliteratorRules(rules) {
    const container = document.getElementById('rules-container');
    if (!container) return; // Element doesn't exist, skip rendering
    
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