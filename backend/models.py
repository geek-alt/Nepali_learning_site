from database import db
from datetime import datetime, timedelta
from flask_login import UserMixin
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import uuid
import secrets

# Initialize Argon2 password hasher (more secure than bcrypt)
ph = PasswordHasher(
    time_cost=3,        # Number of iterations
    memory_cost=65536,  # Memory usage in KB (64 MB)
    parallelism=4,      # Number of parallel threads
    hash_len=32,        # Hash length in bytes
    salt_len=16         # Salt length in bytes
)

# ===== SECURITY MODELS =====

class User(UserMixin, db.Model):
    """User model with comprehensive security features"""
    __tablename__ = 'users'
    
    # Primary identification
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Role-based access control
    role = db.Column(db.String(20), nullable=False, default='user')  # user, admin, superadmin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Security tracking
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    last_ip = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    session_token = db.Column(db.String(64), nullable=True, unique=True)
    
    # Password management
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    must_change_password = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash password using Argon2"""
        self.password_hash = ph.hash(password)
        self.password_changed_at = datetime.utcnow()
    
    def check_password(self, password):
        """Verify password and rehash if needed"""
        try:
            ph.verify(self.password_hash, password)
            # Check if rehash is needed (Argon2 parameters changed)
            if ph.check_needs_rehash(self.password_hash):
                self.password_hash = ph.hash(password)
                db.session.commit()
            return True
        except VerifyMismatchError:
            return False
    
    def is_locked(self):
        """Check if account is locked due to failed login attempts"""
        if self.locked_until:
            if datetime.utcnow() < self.locked_until:
                return True
            else:
                # Unlock account if lock period expired
                self.locked_until = None
                self.failed_login_attempts = 0
                db.session.commit()
        return False
    
    def record_failed_login(self):
        """Record failed login attempt and lock account if threshold reached"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes after 5 failed attempts
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
    
    def record_successful_login(self, ip_address=None):
        """Record successful login and reset failed attempts"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()
        if ip_address:
            self.last_ip = ip_address
        # Generate new session token
        self.session_token = secrets.token_urlsafe(48)
        db.session.commit()
    
    def has_role(self, *roles):
        """Check if user has any of the specified roles"""
        return self.role in roles
    
    def is_admin(self):
        """Check if user is admin or superadmin"""
        return self.role in ['admin', 'superadmin']
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'



class Phrase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nepali = db.Column(db.String(200), nullable=False)
    romanized = db.Column(db.String(200), nullable=False)
    english = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    audio_url = db.Column(db.String(500))
    difficulty = db.Column(db.Integer, default=1)
    context = db.Column(db.String(200))  # Conversation context: restaurant, travel, shopping, etc.
    formality_level = db.Column(db.String(20), default='casual')  # formal, casual, neutral
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Alphabet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    devanagari = db.Column(db.String(10), nullable=False, unique=True)
    romanized = db.Column(db.String(20), nullable=False)
    sound = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # vowel, consonant
    pronunciation = db.Column(db.String(200))
    audio_url = db.Column(db.String(500))
    order_index = db.Column(db.Integer)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    phrase_id = db.Column(db.Integer, db.ForeignKey('phrase.id'))
    alphabet_id = db.Column(db.Integer, db.ForeignKey('alphabet.id'))
    learned = db.Column(db.Boolean, default=False)
    practice_count = db.Column(db.Integer, default=0)
    last_practiced = db.Column(db.DateTime, default=datetime.utcnow)

# ===== V2 NEW MODELS =====

# Phase 1: Dictionary System
class Dictionary(db.Model):
    """Complete Nepali dictionary with 1000+ words"""
    id = db.Column(db.Integer, primary_key=True)
    nepali = db.Column(db.String(200), nullable=False, unique=True, index=True)
    romanized = db.Column(db.String(200), nullable=False, index=True)
    english = db.Column(db.String(200), nullable=False)
    part_of_speech = db.Column(db.String(50))  # noun, verb, adjective, adverb, etc.
    usage_example = db.Column(db.Text)  # English example
    nepali_example = db.Column(db.String(500))  # Nepali example
    audio_url = db.Column(db.String(500))  # Pronunciation audio
    difficulty = db.Column(db.Integer, default=1)  # 1=beginner, 2=intermediate, 3=advanced
    category = db.Column(db.String(100), index=True)  # animals, food, nature, etc.
    synonyms = db.Column(db.String(500))  # comma-separated related words
    antonyms = db.Column(db.String(500))  # opposite words
    views = db.Column(db.Integer, default=0)  # popular words
    order_index = db.Column(db.Integer)  # For manual reordering
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Dictionary {self.nepali}>'

class Resource(db.Model):
    """Learning resources: guides, tips, worksheets"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    resource_type = db.Column(db.String(50), index=True)  # pdf, guide, tips, worksheet
    category = db.Column(db.String(100), index=True)
    file_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    difficulty = db.Column(db.Integer)  # 1-3 difficulty level
    order_index = db.Column(db.Integer)
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))

# Phase 2: Video System
class Playlist(db.Model):
    """Collections of related videos"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), index=True)
    thumbnail_url = db.Column(db.String(500))
    difficulty = db.Column(db.Integer)  # 1-3 difficulty level
    video_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    videos = db.relationship('Video', backref='playlist', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Playlist {self.name}>'

class Video(db.Model):
    """YouTube videos with metadata"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    youtube_id = db.Column(db.String(50), nullable=False, unique=True, index=True)
    duration = db.Column(db.Integer)  # in seconds
    thumbnail_url = db.Column(db.String(500))
    category = db.Column(db.String(100), index=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    difficulty = db.Column(db.Integer)  # 1-3 difficulty level
    view_count = db.Column(db.Integer, default=0)
    transcript = db.Column(db.Text)  # Video transcript
    notes = db.Column(db.Text)  # Learning notes
    order_index = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Video {self.title}>'

# Phase 3: PDF Resources
class PDFResource(db.Model):
    """Downloadable PDF learning materials"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), index=True)  # worksheet, guide, reference
    file_path = db.Column(db.String(500), nullable=False)  # /static/pdfs/...
    preview_url = db.Column(db.String(500))  # First page preview image
    file_size = db.Column(db.Integer)  # in bytes
    pages = db.Column(db.Integer)
    difficulty = db.Column(db.Integer)  # 1-3 difficulty level
    tags = db.Column(db.String(500))  # comma-separated keywords
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<PDFResource {self.title}>'