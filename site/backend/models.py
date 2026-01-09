from database import db
from datetime import datetime

# ===== EXISTING MODELS =====

class Phrase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nepali = db.Column(db.String(200), nullable=False)
    romanized = db.Column(db.String(200), nullable=False)
    english = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    audio_url = db.Column(db.String(500))
    difficulty = db.Column(db.Integer, default=1)
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