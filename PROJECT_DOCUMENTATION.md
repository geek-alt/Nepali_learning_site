# Nepali Learning Platform - Complete Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Backend Structure](#backend-structure)
5. [Frontend Structure](#frontend-structure)
6. [Database Models](#database-models)
7. [Security Implementation](#security-implementation)
8. [API Endpoints](#api-endpoints)
9. [Installation & Setup](#installation--setup)
10. [Deployment](#deployment)
11. [Technologies Used](#technologies-used)

---

## 🎯 Project Overview

**Nepali Learning Platform** is a comprehensive web application designed to help users learn the Nepali language through interactive lessons, alphabet learning, dictionary lookups, phrases, and video resources.

### Purpose
- Teach Nepali alphabet (consonants and vowels)
- Provide dictionary with English-Nepali translations
- Offer common phrases with pronunciations
- Include video tutorials for better learning
- Interactive transliterator for text conversion
- Admin panel for content management

### Target Users
- **Students**: Learning Nepali language
- **Teachers**: Managing educational content
- **Administrators**: Full content management access

---

## ✨ Features

### Public Features
1. **Alphabet Learning**
   - Complete Nepali alphabet with characters
   - English transliterations
   - Audio pronunciation (planned)
   - Visual character display

2. **Dictionary**
   - English to Nepali translations
   - Nepali words with definitions
   - Searchable database
   - Pagination support (12 words per page)
   - Category-based filtering

3. **Phrases**
   - Common Nepali phrases
   - English translations
   - Pronunciation guides
   - Usage examples
   - Category organization (greetings, questions, etc.)

4. **Transliterator**
   - Real-time text conversion
   - English to Nepali script
   - Rule-based transliteration engine
   - Copy-to-clipboard functionality

5. **Video Resources**
   - YouTube video integration
   - Categorized learning videos
   - Embedded video player
   - Description and metadata

### Admin Features
1. **Content Management**
   - Add/Edit/Delete alphabet entries
   - Manage dictionary words
   - Control phrase database
   - Upload video links
   - Bulk upload via CSV

2. **User Management**
   - Role-based access control (user, admin, superadmin)
   - User authentication with secure sessions
   - Account locking after failed login attempts
   - Password strength requirements

3. **Drag-and-Drop Reordering**
   - Reorder alphabet characters
   - Sort dictionary entries
   - Organize phrase sequences
   - Visual feedback with smooth animations

4. **Bulk Upload**
   - CSV file upload for dictionary
   - CSV upload for phrases
   - Data validation and sanitization
   - Error reporting

5. **Security Dashboard**
   - Login attempt monitoring
   - Session management
   - CSRF token validation
   - Rate limiting controls

---

## 🏗️ Architecture

### System Design
```
┌─────────────────┐
│   Web Browser   │
│  (Frontend)     │
└────────┬────────┘
         │ HTTP/HTTPS
         │ (Port 80/443)
         ↓
┌─────────────────┐
│   Nginx         │ ← Reverse Proxy
│  (Production)   │
└────────┬────────┘
         │ Port 5000
         ↓
┌─────────────────┐
│   Flask App     │ ← Python Backend
│   (Gunicorn)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   SQLite DB     │ ← Database
└─────────────────┘
```

### Request Flow
1. **User Request** → Browser sends HTTP request
2. **Nginx** → Receives request, forwards to Flask (production)
3. **Flask Router** → Routes request to appropriate endpoint
4. **Authentication** → Checks session/login status
5. **CSRF Protection** → Validates CSRF token (POST/PUT/DELETE)
6. **Rate Limiting** → Prevents abuse (100 requests/hour public, 200/hour admin)
7. **Business Logic** → Processes request, queries database
8. **Response** → Returns JSON/HTML to client

---

## 🔧 Backend Structure

### Directory Layout
```
backend/
├── app.py                  # Main Flask application
├── database.py             # Database initialization
├── models.py               # SQLAlchemy models
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── instance/
│   └── nepali_learning.db  # SQLite database file
└── routes/
    ├── auth.py             # Authentication endpoints
    ├── alphabet.py         # Alphabet CRUD operations
    ├── dictionary.py       # Dictionary management
    ├── phrases.py          # Phrases management
    ├── resources.py        # Video resources
    ├── transliterator.py   # Text transliteration
    └── bulk_upload.py      # CSV bulk upload
```

### Core Components

#### 1. **app.py** - Application Entry Point
- Flask app initialization
- CORS configuration
- Security middleware setup (CSRF, Talisman, Rate Limiting)
- Blueprint registration
- Database setup
- Session management
- Admin route serving

**Key Configurations:**
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///nepali_learning.db'
SECRET_KEY = '<secure-random-key>'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = None
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
```

#### 2. **models.py** - Database Models

**User Model:**
- Unique username and email
- Argon2 password hashing (more secure than bcrypt)
- Role-based access control (RBAC)
- Failed login tracking with account locking
- Session token management
- Last login IP tracking
- Password change tracking

**Alphabet Model:**
- Nepali character storage
- English transliteration
- Type classification (consonant/vowel)
- Display order management

**Dictionary Model:**
- English word
- Nepali translation
- Pronunciation guide
- Part of speech
- Usage example
- Order index for sorting

**Phrase Model:**
- English phrase
- Nepali translation
- Pronunciation
- Category (greeting, question, common, etc.)
- Usage context
- Order index

**Video Model:**
- YouTube URL
- Title and description
- Category
- Duration
- Difficulty level

#### 3. **routes/** - API Endpoints

**auth.py:**
- `/api/auth/login` - User authentication
- `/api/auth/logout` - Session termination
- `/api/auth/register` - New user registration
- `/api/auth/profile` - User profile management
- Implements rate limiting (5 login attempts per 15 minutes)

**alphabet.py:**
- `GET /api/alphabet/` - Fetch all alphabet
- `POST /api/alphabet/` - Add new character (admin)
- `PUT /api/alphabet/<id>` - Update character (admin)
- `DELETE /api/alphabet/<id>` - Delete character (admin)
- `POST /api/alphabet/reorder` - Drag-drop reordering (admin)

**dictionary.py:**
- `GET /api/dictionary/` - Paginated word list
- `GET /api/dictionary/search?q=word` - Search functionality
- `POST /api/dictionary/` - Add word (admin)
- `PUT /api/dictionary/<id>` - Update word (admin)
- `DELETE /api/dictionary/<id>` - Delete word (admin)
- `POST /api/dictionary/reorder` - Reorder entries (admin)

**phrases.py:**
- `GET /api/phrases/` - Get all phrases
- `GET /api/phrases/category/<cat>` - Filter by category
- `POST /api/phrases/` - Add phrase (admin)
- `PUT /api/phrases/<id>` - Update phrase (admin)
- `DELETE /api/phrases/<id>` - Delete phrase (admin)

**resources.py:**
- `GET /api/resources/videos` - Get all videos
- `POST /api/resources/videos` - Add video (admin)
- `DELETE /api/resources/videos/<id>` - Remove video (admin)

**transliterator.py:**
- `GET /api/transliterator/rules` - Get conversion rules
- `POST /api/transliterator/convert` - Convert text

**bulk_upload.py:**
- `POST /api/bulk/dictionary` - CSV upload for dictionary
- `POST /api/bulk/phrases` - CSV upload for phrases
- Data validation and sanitization
- Error reporting for invalid rows

---

## 🎨 Frontend Structure

### Directory Layout
```
frontend/
├── templates/
│   ├── index.html          # Public homepage
│   └── admin.html          # Admin dashboard
└── static/
    ├── css/
    │   ├── style.css       # Main styles
    │   └── admin.css       # Admin panel styles
    ├── js/
    │   ├── app.js          # Public page logic
    │   └── admin.js        # Admin panel logic
    └── assets/
        └── images/         # Static images
```

### Key Features

#### **index.html** - Public Interface
- Responsive design (mobile-friendly)
- Tabbed navigation (Alphabet, Dictionary, Phrases, Transliterator, Videos)
- Search functionality
- Pagination controls
- Loading states and error handling
- XSS protection with HTML escaping

#### **admin.html** - Admin Dashboard
- Secure login form with CSRF protection
- CRUD operations for all content types
- Drag-and-drop reordering with visual feedback
- Bulk CSV upload interface
- Form validation
- Success/error notifications
- Session management

#### **app.js** - Frontend Logic
- Fetch API for AJAX requests
- Dynamic content loading
- Search debouncing
- Pagination state management
- XSS prevention (HTML escaping)
- Error handling and user feedback

#### **admin.js** - Admin Logic
- CSRF token management
- Drag-and-drop implementation (SortableJS)
- Form submission with validation
- File upload handling
- Real-time order updates
- Credentials: 'include' for session cookies

---

## 🗄️ Database Models

### Entity Relationship Diagram
```
┌──────────────┐
│    User      │
├──────────────┤
│ id (PK)      │
│ username     │
│ email        │
│ password_hash│
│ role         │
│ is_active    │
│ failed_login │
│ locked_until │
│ created_at   │
└──────────────┘

┌──────────────┐       ┌──────────────┐
│  Alphabet    │       │  Dictionary  │
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ character    │       │ english_word │
│ transliterate│       │ nepali_word  │
│ type         │       │ pronunciation│
│ order_index  │       │ part_of_speech│
│ created_at   │       │ example      │
└──────────────┘       │ order_index  │
                       │ created_at   │
                       └──────────────┘

┌──────────────┐       ┌──────────────┐
│   Phrase     │       │    Video     │
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ english_text │       │ youtube_url  │
│ nepali_text  │       │ title        │
│ pronunciation│       │ description  │
│ category     │       │ category     │
│ usage_context│       │ duration     │
│ order_index  │       │ difficulty   │
│ created_at   │       │ created_at   │
└──────────────┘       └──────────────┘
```

### Table Details

#### **users**
| Column | Type | Description |
|--------|------|-------------|
| id | String(36) | UUID primary key |
| username | String(80) | Unique username, indexed |
| email | String(120) | Unique email, indexed |
| password_hash | String(256) | Argon2 hashed password |
| role | String(20) | user/admin/superadmin |
| is_active | Boolean | Account status |
| failed_login_attempts | Integer | Login failure counter |
| locked_until | DateTime | Account lock expiration |
| last_login | DateTime | Last successful login |
| last_ip | String(45) | Last login IP (IPv6 compatible) |
| session_token | String(64) | Unique session identifier |
| created_at | DateTime | Account creation timestamp |

#### **alphabet**
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Auto-increment PK |
| character | String(10) | Nepali character |
| transliteration | String(50) | English equivalent |
| type | String(20) | consonant/vowel |
| order_index | Integer | Display order |
| created_at | DateTime | Creation timestamp |

#### **dictionary**
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Auto-increment PK |
| english_word | String(100) | English word |
| nepali_word | String(100) | Nepali translation |
| pronunciation | String(100) | Pronunciation guide |
| part_of_speech | String(50) | noun/verb/adj/etc |
| example | Text | Usage example |
| order_index | Integer | Display order |
| created_at | DateTime | Creation timestamp |

#### **phrases**
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Auto-increment PK |
| english_text | String(200) | English phrase |
| nepali_text | String(200) | Nepali translation |
| pronunciation | String(200) | Pronunciation |
| category | String(50) | greeting/question/common |
| usage_context | Text | When to use |
| order_index | Integer | Display order |
| created_at | DateTime | Creation timestamp |

#### **videos**
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Auto-increment PK |
| youtube_url | String(255) | YouTube video URL |
| title | String(200) | Video title |
| description | Text | Video description |
| category | String(50) | beginner/intermediate/advanced |
| duration | Integer | Duration in seconds |
| difficulty | String(20) | Difficulty level |
| created_at | DateTime | Creation timestamp |

---

## 🔒 Security Implementation

### Authentication & Authorization

1. **Password Security**
   - Argon2 hashing (memory-hard, GPU-resistant)
   - Time cost: 3 iterations
   - Memory cost: 64 MB
   - Parallelism: 4 threads
   - Minimum 8 characters, must include uppercase, lowercase, digit, special char

2. **Session Management**
   - Flask-Login for session handling
   - HTTPOnly cookies (prevents XSS)
   - Secure flag in production (HTTPS only)
   - SameSite=None for CORS support
   - 1-hour session lifetime
   - Unique session tokens per user

3. **Account Protection**
   - Rate limiting: 5 login attempts per 15 minutes
   - Account locking: 30 minutes after 5 failed attempts
   - IP address logging
   - Last login timestamp tracking

### CSRF Protection

**Implementation:**
```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

- CSRF tokens for all state-changing operations (POST/PUT/DELETE)
- Token validation on admin routes
- Tokens included in forms and AJAX headers
- Time-unlimited tokens (no expiration)

### Rate Limiting

**Configuration:**
```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]  # Public routes
)

# Admin routes: 200 requests per hour
# Login attempts: 5 per 15 minutes
```

### CORS Configuration

```python
CORS(app, resources={
    r"/*": {
        "origins": ["https://lerishbhandari.com.np"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "X-CSRFToken"],
        "supports_credentials": True
    }
})
```

### Content Security

1. **Input Sanitization**
   - Bleach library for HTML sanitization
   - Email validation
   - SQL injection prevention (SQLAlchemy ORM)
   - XSS protection (HTML escaping in frontend)

2. **Output Encoding**
   - JSON responses with proper content-type
   - HTML entity encoding in templates
   - Safe JSON serialization

3. **Security Headers (Talisman)**
   ```python
   Talisman(app, 
       force_https=True,
       strict_transport_security=True,
       content_security_policy={
           'default-src': "'self'",
           'script-src': ["'self'", "'unsafe-inline'"],
           'style-src': ["'self'", "'unsafe-inline'"]
       }
   )
   ```

### File Upload Security

- CSV validation
- File size limits
- Content-type verification
- Sanitization of uploaded data
- Error handling for malformed files

---

## 🌐 API Endpoints

### Public Endpoints (No Auth Required)

#### Alphabet
```
GET /api/alphabet/
Response: [
  {
    "id": 1,
    "character": "क",
    "transliteration": "ka",
    "type": "consonant",
    "order_index": 1
  }
]
```

#### Dictionary
```
GET /api/dictionary/?page=1&per_page=12
Response: {
  "words": [...],
  "total": 150,
  "page": 1,
  "per_page": 12,
  "total_pages": 13
}

GET /api/dictionary/search?q=hello
Response: [...matching words...]
```

#### Phrases
```
GET /api/phrases/
GET /api/phrases/category/greeting
Response: [
  {
    "id": 1,
    "english_text": "Hello",
    "nepali_text": "नमस्ते",
    "pronunciation": "namaste",
    "category": "greeting"
  }
]
```

#### Videos
```
GET /api/resources/videos
Response: [
  {
    "id": 1,
    "youtube_url": "https://youtube.com/watch?v=...",
    "title": "Learn Nepali Alphabet",
    "category": "beginner"
  }
]
```

#### Transliterator
```
GET /api/transliterator/rules
POST /api/transliterator/convert
Body: { "text": "namaste" }
Response: { "result": "नमस्ते" }
```

### Admin Endpoints (Auth Required)

#### Authentication
```
POST /api/auth/login
Body: { "username": "admin", "password": "password" }
Response: { "success": true, "user": {...} }

POST /api/auth/logout
Response: { "success": true }
```

#### Content Management (POST/PUT/DELETE)
```
POST /api/alphabet/
Body: { "character": "क", "transliteration": "ka", "type": "consonant" }

PUT /api/alphabet/<id>
Body: { "transliteration": "kha" }

DELETE /api/alphabet/<id>

POST /api/alphabet/reorder
Body: { "order": [3, 1, 2, 4] }
```

#### Bulk Upload
```
POST /api/bulk/dictionary
Content-Type: multipart/form-data
Body: file=dictionary.csv

POST /api/bulk/phrases
Content-Type: multipart/form-data
Body: file=phrases.csv
```

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Virtual environment (recommended)
- Git (for cloning)

### Local Development Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd site
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Create .env File**
   ```bash
   # backend/.env
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-change-this
   DATABASE_URL=sqlite:///nepali_learning.db
   ALLOWED_ORIGINS=http://localhost:5000
   ```

5. **Initialize Database**
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

6. **Create Admin User**
   ```bash
   python
   >>> from app import app, db
   >>> from models import User
   >>> with app.app_context():
   ...     admin = User(username='admin', email='admin@example.com', role='admin')
   ...     admin.set_password('Admin123!')
   ...     db.session.add(admin)
   ...     db.session.commit()
   >>> exit()
   ```

7. **Run Development Server**
   ```bash
   python app.py
   ```

8. **Access Application**
   - Public Site: http://localhost:5000
   - Admin Panel: http://localhost:5000/admin
   - Login: admin / Admin123!

### Production Deployment (Oracle Cloud)

1. **Provision VM**
   - Oracle Cloud Free Tier
   - VM.Standard.E2.1.Micro (1 OCPU, 1GB RAM)
   - Oracle Linux 9
   - Public IP: Assign static IP

2. **SSH Access**
   ```bash
   ssh -i ssh-key.key opc@<public-ip>
   ```

3. **Install Dependencies**
   ```bash
   sudo dnf install -y python3 python3-pip nginx
   ```

4. **Upload Files**
   ```bash
   scp -i ssh-key.key -r site/ opc@<public-ip>:/home/opc/
   ```

5. **Setup Virtual Environment**
   ```bash
   cd /home/opc/site/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install --no-cache-dir -r requirements.txt
   ```

6. **Configure Environment**
   ```bash
   nano .env
   # Set production values
   FLASK_ENV=production
   SECRET_KEY=<strong-random-key>
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

7. **Initialize Database**
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

8. **Run with nohup**
   ```bash
   nohup python app.py > flask.log 2>&1 &
   ```

9. **Setup Nginx** (Recommended)
   ```bash
   sudo nano /etc/nginx/conf.d/nepali-site.conf
   ```
   
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
   
   ```bash
   sudo nginx -t
   sudo systemctl start nginx
   sudo systemctl enable nginx
   ```

10. **Configure Firewall**
    ```bash
    sudo firewall-cmd --add-service=http --permanent
    sudo firewall-cmd --add-service=https --permanent
    sudo firewall-cmd --reload
    ```

11. **Oracle Cloud Security List**
    - Add ingress rule: TCP port 80 (0.0.0.0/0)
    - Add ingress rule: TCP port 443 (0.0.0.0/0)

12. **Setup Cloudflare** (Optional)
    - Add A records: @ and www → Public IP
    - Enable proxy (orange cloud)
    - SSL/TLS: Full mode
    - Configure SSL certificate

---

## 🛠️ Technologies Used

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ | Programming language |
| Flask | 2.3.3 | Web framework |
| SQLAlchemy | 2.0.23 | ORM for database |
| Flask-SQLAlchemy | 3.1.1 | Flask-SQLAlchemy integration |
| Flask-Login | 0.6.3 | User session management |
| Flask-WTF | 1.2.2 | CSRF protection |
| Flask-CORS | 4.0.0 | Cross-origin requests |
| Flask-Limiter | 4.1.1 | Rate limiting |
| Flask-Talisman | 1.1.0 | Security headers |
| Argon2-cffi | 25.1.0 | Password hashing |
| Bleach | 6.3.0 | HTML sanitization |
| Marshmallow | 4.2.0 | Data validation |
| python-dotenv | 1.0.0 | Environment variables |

### Frontend
| Technology | Purpose |
|------------|---------|
| HTML5 | Markup structure |
| CSS3 | Styling and layout |
| JavaScript (ES6+) | Client-side logic |
| Fetch API | AJAX requests |
| SortableJS | Drag-and-drop functionality |

### Database
| Technology | Purpose |
|------------|---------|
| SQLite | Development database |
| PostgreSQL | Production (optional) |

### DevOps & Deployment
| Technology | Purpose |
|------------|---------|
| Nginx | Reverse proxy, static files |
| Gunicorn | WSGI server (production) |
| systemd | Process management |
| Oracle Cloud | Hosting platform |
| Cloudflare | CDN, SSL, DDoS protection |

### Security Tools
| Technology | Purpose |
|------------|---------|
| Argon2 | Password hashing |
| CSRF Tokens | Cross-site request forgery prevention |
| Rate Limiting | Brute force protection |
| Talisman | Security headers (HSTS, CSP) |
| Bleach | XSS prevention |

---

## 📊 System Requirements

### Development
- **RAM**: 2GB minimum
- **Storage**: 500MB
- **OS**: Windows/Linux/macOS
- **Browser**: Chrome/Firefox/Safari (latest)

### Production (Oracle Cloud Free Tier)
- **VM**: VM.Standard.E2.1.Micro
- **CPU**: 1 OCPU
- **RAM**: 1GB (sufficient with optimization)
- **Storage**: 46.6GB
- **OS**: Oracle Linux 9
- **Network**: 10 Mbps bandwidth

---

## 🚀 Performance Optimization

1. **Database Indexing**
   - Indexed columns: username, email, order_index
   - Query optimization with proper joins

2. **Caching Strategy**
   - Browser caching for static assets
   - CDN caching via Cloudflare

3. **Frontend Optimization**
   - Minified CSS/JS (production)
   - Image compression
   - Lazy loading for videos

4. **Backend Optimization**
   - Database connection pooling
   - Pagination for large datasets
   - Efficient query design

---

## 🧪 Testing

### Manual Testing Checklist
- [ ] User registration and login
- [ ] Admin authentication
- [ ] Alphabet CRUD operations
- [ ] Dictionary search and pagination
- [ ] Phrase filtering by category
- [ ] Video resource loading
- [ ] Transliterator functionality
- [ ] Drag-and-drop reordering
- [ ] Bulk CSV upload
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Session management

### Security Testing
- [ ] SQL injection attempts
- [ ] XSS attack prevention
- [ ] CSRF token validation
- [ ] Brute force login protection
- [ ] Session hijacking prevention
- [ ] File upload validation

---

## 📝 Maintenance & Monitoring

### Log Files
- **Flask logs**: `/home/opc/site/backend/flask.log`
- **Nginx access**: `/var/log/nginx/access.log`
- **Nginx error**: `/var/log/nginx/error.log`
- **System logs**: `journalctl -u nepali-site`

### Monitoring Commands
```bash
# Check Flask process
ps aux | grep "app.py"

# View Flask logs
tail -f flask.log

# Check Nginx status
sudo systemctl status nginx

# Monitor resource usage
top
htop
```

### Backup Strategy
```bash
# Backup database
cp /home/opc/site/backend/nepali_learning.db ~/backup/db_$(date +%Y%m%d).db

# Backup entire site
tar -czf ~/backup/site_$(date +%Y%m%d).tar.gz /home/opc/site/
```

---

## 🐛 Troubleshooting

### Common Issues

1. **Flask not accessible from internet**
   - Check Oracle Cloud Security List (add port ingress rules)
   - Verify firewall rules: `sudo firewall-cmd --list-all`
   - Check Flask binding: should be `0.0.0.0:5000`

2. **Database locked error**
   - Stop all Flask instances
   - Check for multiple processes: `ps aux | grep python`
   - Kill duplicate processes: `pkill -f "python app.py"`

3. **CSRF validation failed**
   - Ensure `credentials: 'include'` in fetch requests
   - Verify CSRF token in request headers
   - Check CORS configuration

4. **Memory issues (1GB RAM)**
   - Use `pip install --no-cache-dir`
   - Restart services periodically
   - Monitor with `free -m`

5. **ERR_BLOCKED_BY_CLIENT in browser**
   - Disable ad blocker for the site
   - Whitelist API endpoints
   - Check browser extensions

---

## 📞 Support & Contact

- **Documentation**: This file
- **Issues**: Report bugs via GitHub Issues
- **Admin Credentials**: admin / Admin123! (change after first login)

---

## 📜 License

[Add your license information here]

---

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Nepali Language Reference](https://en.wikipedia.org/wiki/Nepali_language)
- [Web Security Best Practices](https://owasp.org/www-project-top-ten/)

---

**Last Updated**: January 11, 2026  
**Version**: 1.0.0  
**Deployed**: Oracle Cloud (lerishbhandari.com.np)
