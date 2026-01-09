# नेपाली सिकौं - Learn Nepali Platform

A comprehensive, interactive platform for learning the Nepali language with beautiful animations, modern UI, and rich content management.

## 📋 Table of Contents
- [Current Features](#current-features)
- [Tech Stack](#tech-stack)
- [Installation & Setup](#installation--setup)
- [V2 Upgrade Plan](#v2-upgrade-plan-comprehensive-roadmap)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## ✨ Current Features (V1)

### Frontend
- 🎨 **Animated Learning Interface** - Smooth transitions, fade-in effects, floating elements
- 📱 **Responsive Design** - Mobile, tablet, and desktop optimized
- 🔤 **Devanagari Alphabet** - Interactive alphabet learning with pronunciation
- 💬 **Common Phrases** - Categorized phrases (greetings, emergency, food, directions)
- 🔄 **Text Converter** - Romanized to Devanagari transliteration

### Backend
- 🗄️ **SQLAlchemy ORM** - Robust database management
- 🔐 **CORS Enabled** - Secure cross-origin requests
- 📡 **RESTful API** - Clean, standard API endpoints
- 🎯 **Content Management** - Admin panel for managing phrases and alphabet

### Admin Panel
- ➕ **Add/Edit/Delete** - Full CRUD operations for phrases and alphabet
- 🔍 **Search & Filter** - Real-time content filtering
- 📊 **Data Tables** - Clean presentation of content
- 📋 **Form Validation** - Safe content entry

## 🛠️ Tech Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with animations and gradients
- **Vanilla JavaScript** - No dependencies, fast and lightweight
- **Fonts**: Poppins (UI), Noto Sans Devanagari (Script)

### Backend
- **Python 3.12** - Programming language
- **Flask 2.3.3** - Web framework
- **Flask-SQLAlchemy 3.1.1** - ORM
- **Flask-CORS 4.0.0** - Cross-origin support
- **SQLite** - Lightweight database

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- Windows PowerShell or bash terminal

### Step 1: Clone & Navigate
```bash
cd C:\Users\bhand\Desktop\Codefolder\site\backend
```

### Step 2: Activate Virtual Environment
```bash
..\..\nepalisite\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```bash
pip install -r ../requirements.txt
```

### Step 4: Start the Server
```bash
python app.py
```

### Step 5: Access the Platform
- **Main Site**: http://127.0.0.1:5000
- **Admin Panel**: http://127.0.0.1:5000/admin

---

# 🚀 V2 UPGRADE PLAN - Comprehensive Roadmap

## Vision
Transform the platform into a complete Nepali learning ecosystem with:
- Interactive dictionary with 1000+ words
- Curated YouTube video library
- Downloadable PDF learning materials
- Progress tracking and user accounts
- Gamification system
- Community features

---

## Phase 1: Content Management System Enhancement (Weeks 1-2)

### 1.1 Advanced Dictionary System
**Objective**: Create a searchable dictionary with word details

#### Features:
- **Word Database**: 1000+ common Nepali words
- **Word Details**:
  - Nepali script (नेपाली)
  - Romanized form (nepali)
  - English translation
  - Part of speech (noun, verb, adj, etc.)
  - Usage examples with context
  - Audio pronunciation (mp3 files)
  - Related words/synonyms
  - Difficulty level (beginner, intermediate, advanced)

#### Database Schema:
```python
class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nepali = db.Column(db.String(200), nullable=False, unique=True)
    romanized = db.Column(db.String(200), nullable=False)
    english = db.Column(db.String(200), nullable=False)
    part_of_speech = db.Column(db.String(50))  # noun, verb, adj, etc.
    usage_example = db.Column(db.Text)
    nepali_example = db.Column(db.String(500))
    audio_url = db.Column(db.String(500))
    difficulty = db.Column(db.Integer, default=1)  # 1=beginner, 2=intermediate, 3=advanced
    category = db.Column(db.String(100))  # animals, food, nature, etc.
    synonyms = db.Column(db.String(500))  # comma-separated related words
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
```

#### API Endpoints:
```
GET    /api/dictionary                  - Get all words (with pagination)
GET    /api/dictionary/<id>             - Get specific word
POST   /api/dictionary                  - Add new word (Admin)
PUT    /api/dictionary/<id>             - Update word (Admin)
DELETE /api/dictionary/<id>             - Delete word (Admin)
GET    /api/dictionary/search?q=hello   - Search words
GET    /api/dictionary/category/<cat>   - Get words by category
GET    /api/dictionary/difficulty/<lvl> - Get by difficulty level
```

#### Frontend Components:
- **Dictionary Search Bar**: Auto-complete suggestions
- **Word Cards**: Display word with examples, audio player
- **Category Tabs**: Browse by food, animals, nature, etc.
- **Difficulty Filter**: Filter by learning level
- **Audio Player**: Integrated pronunciation
- **Example Sentences**: Show usage context

---

### 1.2 Resource Library System
**Objective**: Organize all learning materials in one place

#### Features:
- **Categories**: 
  - Grammar Guides
  - Cultural Notes
  - Learning Tips
  - Worksheets
  - Study Materials
  
#### Database Schema:
```python
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    resource_type = db.Column(db.String(50))  # pdf, guide, tips, worksheet
    category = db.Column(db.String(100))
    file_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    difficulty = db.Column(db.Integer)
    order_index = db.Column(db.Integer)
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))
```

---

## Phase 2: Video Integration System (Weeks 2-3)

### 2.1 YouTube Video Library
**Objective**: Curate and organize Nepali learning videos

#### Features:
- **Video Database**: Store video metadata
- **Playlist Organization**: Group videos by topic
- **Video Details**:
  - Title and description
  - YouTube video ID (embed)
  - Duration
  - Difficulty level
  - Topic/category
  - Transcript/notes
  - Completion tracking

#### Database Schema:
```python
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    youtube_id = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer)  # in seconds
    thumbnail_url = db.Column(db.String(500))
    category = db.Column(db.String(100))
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    difficulty = db.Column(db.Integer)
    view_count = db.Column(db.Integer, default=0)
    transcript = db.Column(db.Text)
    notes = db.Column(db.Text)
    order_index = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    thumbnail_url = db.Column(db.String(500))
    video_count = db.Column(db.Integer, default=0)
    difficulty = db.Column(db.Integer)
    videos = db.relationship('Video', backref='playlist', lazy=True)
```

#### API Endpoints:
```
GET    /api/videos                      - Get all videos
GET    /api/videos/<id>                 - Get specific video
POST   /api/videos                      - Add video (Admin)
PUT    /api/videos/<id>                 - Update video (Admin)
DELETE /api/videos/<id>                 - Delete video (Admin)
GET    /api/videos/category/<cat>       - Get by category
GET    /api/playlists                   - Get all playlists
POST   /api/playlists                   - Create playlist (Admin)
GET    /api/playlists/<id>/videos       - Get playlist videos
```

#### Frontend Components:
- **Video Player**: Responsive YouTube embed
- **Video Cards**: Title, duration, difficulty, thumbnail
- **Playlist View**: Browse videos by collection
- **Transcript Panel**: Show video notes/transcript
- **Category Navigation**: Filter videos by topic

#### YouTube Integration:
```javascript
// Embed YouTube videos
const embedURL = `https://www.youtube.com/embed/${youtubeId}`;

// Create playlist layout
// Show transcript/notes alongside video
// Track completion status
```

---

## Phase 3: PDF Resources & Previews (Weeks 3-4)

### 3.1 PDF Management System
**Objective**: Store and preview printable learning materials

#### Features:
- **PDF Upload**: Admin can upload study guides, worksheets
- **Preview Generation**: Show first page preview
- **Metadata Storage**: Title, description, difficulty, category
- **Download Tracking**: Count downloads

#### Database Schema:
```python
class PDFResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # worksheet, guide, reference
    file_path = db.Column(db.String(500))  # stored in /frontend/static/pdfs/
    preview_url = db.Column(db.String(500))  # first page preview image
    file_size = db.Column(db.Integer)
    pages = db.Column(db.Integer)
    difficulty = db.Column(db.Integer)
    tags = db.Column(db.String(500))  # comma-separated
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))
```

#### API Endpoints:
```
GET    /api/resources                   - Get all resources
GET    /api/resources/<id>              - Get resource details
POST   /api/resources                   - Upload resource (Admin)
GET    /api/resources/<id>/download     - Download PDF
GET    /api/resources/category/<cat>    - Get by category
DELETE /api/resources/<id>              - Delete resource (Admin)
```

#### Frontend Components:
- **PDF Card**: Thumbnail preview + metadata
- **Download Button**: Track downloads
- **Preview Modal**: Show full preview before download
- **Category Grid**: Browse resources by type
- **Search**: Find by title/tags

#### Preview Generation:
```python
# Using pdf2image to generate previews
from pdf2image import convert_from_path

def generate_pdf_preview(pdf_path):
    """Convert first page of PDF to image"""
    images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
    preview_path = pdf_path.replace('.pdf', '_preview.jpg')
    images[0].save(preview_path)
    return preview_path
```

---

## Phase 4: Enhanced Admin Panel (Week 4)

### 4.1 Admin Dashboard Extensions

#### Features:
- **Dashboard Stats**: Total words, videos, resources, users
- **Bulk Upload**: Add multiple dictionary words via CSV
- **Content Manager**: 
  - Dictionary management
  - Video library manager
  - Resource uploader
  - Phrase management (existing)
  - Alphabet management (existing)
- **Advanced Search**: Find content quickly
- **Analytics**: View stats, downloads, popular items
- **User Management**: (Phase 5)

#### New Admin Views:
```
/admin                          - Main dashboard
/admin/dictionary               - Manage dictionary
/admin/videos                   - Manage videos & playlists
/admin/resources                - Manage PDF resources
/admin/analytics                - View statistics
/admin/import                   - Bulk import CSV
```

---

## Phase 5: User System & Progress Tracking (Week 5)

### 5.1 User Accounts & Authentication

#### Features:
- **User Registration**: Email signup
- **Login System**: Secure authentication
- **User Profiles**: Track learning progress
- **Learning History**: Words viewed, videos watched, resources downloaded

#### Database Schema:
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    learning_streak = db.Column(db.Integer, default=0)
    total_xp = db.Column(db.Integer, default=0)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dictionary_id = db.Column(db.Integer, db.ForeignKey('dictionary.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'))
    resource_id = db.Column(db.Integer, db.ForeignKey('pdf_resource.id'))
    completed = db.Column(db.Boolean, default=False)
    progress_percent = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Auth Features:
- Flask-Login for session management
- Secure password hashing
- JWT tokens for API authentication
- User-specific content recommendations

---

## Phase 6: Gamification System (Week 6)

### 6.1 Learning Rewards

#### Features:
- **XP Points**: Earn points for learning activities
- **Achievements**: Badges for milestones
- **Streaks**: Daily learning streaks
- **Leaderboard**: Top learners (optional)

#### Achievement Types:
- First Word Learned (10 XP)
- Complete Alphabet (50 XP)
- Watch 5 Videos (100 XP)
- Download Resource (25 XP)
- 7-Day Streak (200 XP)

#### Database Schema:
```python
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon_url = db.Column(db.String(500))
    xp_reward = db.Column(db.Integer)
    requirement_type = db.Column(db.String(50))  # videos_watched, words_learned, etc.
    requirement_count = db.Column(db.Integer)

class UserAchievement(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), primary_key=True)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## Phase 7: Community & Social Features (Week 7)

### 7.1 Community Interaction

#### Features:
- **Discussion Forum**: Ask questions, share tips
- **Word Comments**: Add usage examples
- **Resource Reviews**: Rate materials
- **User Profiles**: Show learning stats

#### Database Schema:
```python
class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text)
    category = db.Column(db.String(100))
    reply_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'))
    content = db.Column(db.Text)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## File Structure - V2

```
site/
├── backend/
│   ├── app.py                          # Main Flask app
│   ├── database.py                     # Database initialization
│   ├── models.py                       # Old models + new V2 models
│   ├── routes/
│   │   ├── phrases.py                  # Phrase CRUD
│   │   ├── alphabet.py                 # Alphabet CRUD
│   │   ├── transliterator.py           # Text conversion
│   │   ├── dictionary.py               # NEW: Dictionary CRUD & search
│   │   ├── videos.py                   # NEW: Video library & playlists
│   │   ├── resources.py                # NEW: PDF resources
│   │   ├── users.py                    # NEW: User auth & profiles
│   │   ├── progress.py                 # NEW: Learning progress tracking
│   │   └── achievements.py             # NEW: Gamification
│   ├── utils/
│   │   ├── helpers.py                  # Utility functions
│   │   ├── validators.py               # Input validation
│   │   └── pdf_processor.py            # NEW: PDF preview generation
│   └── migrations/                     # NEW: Database migrations
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css               # Main styles
│   │   │   ├── admin.css               # Admin panel styles
│   │   │   └── components.css          # NEW: Reusable components
│   │   ├── js/
│   │   │   ├── app.js                  # Main app logic
│   │   │   ├── admin.js                # Admin panel logic
│   │   │   ├── dictionary.js           # NEW: Dictionary functionality
│   │   │   ├── videos.js               # NEW: Video player logic
│   │   │   ├── resources.js            # NEW: Resource handling
│   │   │   ├── auth.js                 # NEW: User auth
│   │   │   ├── progress.js             # NEW: Progress tracking
│   │   │   └── api-client.js           # NEW: API utilities
│   │   ├── pdfs/                       # NEW: Stored PDF files
│   │   ├── images/
│   │   │   └── previews/               # NEW: PDF previews
│   │   └── audio/                      # NEW: Word pronunciations
│   │
│   └── templates/
│       ├── index.html                  # Main page
│       ├── admin.html                  # Admin dashboard
│       ├── dictionary.html             # NEW: Dictionary page
│       ├── videos.html                 # NEW: Video library
│       ├── resources.html              # NEW: PDF library
│       ├── auth.html                   # NEW: Login/signup
│       ├── profile.html                # NEW: User profile
│       └── components/
│           ├── navbar.html             # Shared navbar
│           ├── footer.html             # Shared footer
│           └── sidebar.html            # Shared sidebar
│
├── requirements.txt                    # Python dependencies
├── README.md                           # Documentation (this file)
├── .env.example                        # Environment variables template
└── .gitignore
```

---

## 📊 Recommended Dependencies - V2

```
Flask==2.3.3
Flask-CORS==4.0.0
SQLAlchemy==2.0.23
Flask-SQLAlchemy==3.1.1
python-dotenv==1.0.0
Flask-Login==0.6.2
Werkzeug==3.1.5
pdf2image==1.16.3
PyPDF2==4.0.1
Pillow==10.0.0
requests==2.31.0
```

---

## 🎨 UI Component Library - V2

### New Components to Build:

1. **Dictionary Card**
   ```html
   <div class="dict-card">
     <h3>{nepali}</h3>
     <p class="romanized">{romanized}</p>
     <p class="translation">{english}</p>
     <button class="audio-btn">🔊 Pronounce</button>
     <p class="example">{example}</p>
   </div>
   ```

2. **Video Card**
   ```html
   <div class="video-card">
     <div class="thumbnail">
       <img src="{thumbnail}" />
       <span class="duration">{duration}</span>
     </div>
     <h3>{title}</h3>
     <p class="category">{category}</p>
     <a class="btn-play">Play Video</a>
   </div>
   ```

3. **PDF Card**
   ```html
   <div class="pdf-card">
     <div class="preview-img">
       <img src="{preview}" />
     </div>
     <h3>{title}</h3>
     <p class="meta">{pages} pages • {size}</p>
     <button class="btn-download">Download PDF</button>
   </div>
   ```

4. **Achievement Badge**
   ```html
   <div class="achievement-badge">
     <img src="{icon}" class="badge-icon" />
     <p>{name}</p>
     <span class="xp">+{xp} XP</span>
   </div>
   ```

---

## 🚀 Deployment Roadmap

### Development (Current)
- Local development on Windows
- SQLite database
- Flask development server

### Production (V2)
- PostgreSQL database
- Gunicorn/uWSGI WSGI server
- Nginx reverse proxy
- Docker containerization
- AWS/DigitalOcean hosting

---

## 📈 Growth Metrics to Track

- **User Metrics**: Registrations, active users, retention
- **Content Metrics**: Words learned, videos watched, resources downloaded
- **Engagement**: Daily active users, average session time, streaks
- **Learning Metrics**: Words mastered, completion rates, accuracy

---

## 💡 How to Add Content Easily - Quick Guide

### Adding Dictionary Words
1. Go to `/admin`
2. Click "Manage Dictionary" (Phase 1)
3. Use form to add word with:
   - Nepali script
   - Romanized form
   - English translation
   - Part of speech
   - Usage example
   - Audio file
   - Difficulty level
4. Click Save - instantly available on platform!

### Adding YouTube Videos
1. Go to `/admin`
2. Click "Manage Videos" (Phase 2)
3. Paste YouTube video ID
4. Fill in title, description, difficulty
5. Optionally add transcript/notes
6. Save - embedded on platform!

### Adding PDF Resources
1. Go to `/admin`
2. Click "Manage Resources" (Phase 3)
3. Upload PDF file
4. System auto-generates preview
5. Add title, category, description
6. Save - downloadable with preview!

### Bulk Import Words
```csv
nepali,romanized,english,part_of_speech,category,difficulty
पानी,pani,water,noun,nature,1
खान,kana,eat,verb,food,1
घर,ghar,house,noun,building,1
```
Upload CSV to admin panel and all words are imported at once!

---

## 🔒 Security Considerations

- Password hashing with Werkzeug
- CSRF protection on forms
- XSS prevention in templates
- SQL injection prevention via SQLAlchemy
- File upload validation
- Rate limiting on APIs
- Admin role-based access control

---

## 📞 Support & Contribution

For questions, feature requests, or bug reports, please reach out to the development team.

---

**Last Updated**: January 9, 2026
**Version**: 1.0 Planning
**Status**: Ready for Phase 1 Implementation