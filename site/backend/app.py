from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from database import db
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static',
            static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///nepali_learning.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

db.init_app(app)
CORS(app)

# Import models and routes
from models import Phrase, Alphabet, UserProgress, Dictionary, Resource, PDFResource, Video, Playlist
from routes import phrases, alphabet, transliterator, dictionary, resources

# Register blueprints
app.register_blueprint(phrases.bp)
app.register_blueprint(alphabet.bp)
app.register_blueprint(transliterator.bp)
app.register_blueprint(dictionary.bp)  # V2: Dictionary system
app.register_blueprint(resources.bp)   # V2: Resources, Videos, PDFs

# Serve frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

def initialize_data():
    """Initialize database with seed data if empty"""
    if not Phrase.query.first():
        seed_phrases()
        seed_alphabet()

def seed_phrases():
    """Seed survival phrases data"""
    phrases_data = [
        # Greetings
        {"nepali": "नमस्ते", "romanized": "namaste", "english": "Hello", "category": "greetings"},
        {"nepali": "धन्यवाद", "romanized": "dhanyabad", "english": "Thank you", "category": "greetings"},
        {"nepali": "स्वागतम्", "romanized": "swagatam", "english": "Welcome", "category": "greetings"},
        
        # Emergency
        {"nepali": "मलाई मद्दत चाहिन्छ", "romanized": "malai maddat chahinchha", "english": "I need help", "category": "emergency"},
        {"nepali": "पुलिस बोलाउनुहोस्", "romanized": "police bolaaunuhos", "english": "Call the police", "category": "emergency"},
        
        # Food
        {"nepali": "म तिर्खाएको छु", "romanized": "ma tirkhaeko chu", "english": "I am thirsty", "category": "food"},
        {"nepali": "म भोकाएको छु", "romanized": "ma bhokaeko chu", "english": "I am hungry", "category": "food"},
        
        # Directions
        {"nepali": "यो कहाँ छ?", "romanized": "yo kaha chha?", "english": "Where is this?", "category": "directions"},
        {"nepali": "बाटो कता जान्छ?", "romanized": "bato kata janchha?", "english": "Where does the road go?", "category": "directions"},
    ]
    
    for phrase in phrases_data:
        db.session.add(Phrase(**phrase))
    db.session.commit()

def seed_alphabet():
    """Seed alphabet data"""
    alphabet_data = [
        {"devanagari": "अ", "romanized": "a", "sound": "a", "type": "vowel", "pronunciation": "like 'a' in 'about'"},
        {"devanagari": "आ", "romanized": "aa", "sound": "aa", "type": "vowel", "pronunciation": "like 'a' in 'father'"},
        {"devanagari": "क", "romanized": "ka", "sound": "ka", "type": "consonant", "pronunciation": "like 'k' in 'king'"},
        {"devanagari": "ख", "romanized": "kha", "sound": "kha", "type": "consonant", "pronunciation": "aspirated 'k'"},
    ]
    
    for letter in alphabet_data:
        db.session.add(Alphabet(**letter))
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_data()
    app.run(debug=True)

def initialize_data():
    """Initialize database with seed data if empty"""
    if not Phrase.query.first():
        seed_phrases()
        seed_alphabet()

def seed_phrases():
    """Seed survival phrases data"""
    phrases_data = [
        # Greetings
        {"nepali": "नमस्ते", "romanized": "namaste", "english": "Hello", "category": "greetings"},
        {"nepali": "धन्यवाद", "romanized": "dhanyabad", "english": "Thank you", "category": "greetings"},
        {"nepali": "स्वागतम्", "romanized": "swagatam", "english": "Welcome", "category": "greetings"},
        
        # Emergency
        {"nepali": "मलाई मद्दत चाहिन्छ", "romanized": "malai maddat chahinchha", "english": "I need help", "category": "emergency"},
        {"nepali": "पुलिस बोलाउनुहोस्", "romanized": "police bolaaunuhos", "english": "Call the police", "category": "emergency"},
        
        # Food
        {"nepali": "म तिर्खाएको छु", "romanized": "ma tirkhaeko chu", "english": "I am thirsty", "category": "food"},
        {"nepali": "म भोकाएको छु", "romanized": "ma bhokaeko chu", "english": "I am hungry", "category": "food"},
        
        # Directions
        {"nepali": "यो कहाँ छ?", "romanized": "yo kaha chha?", "english": "Where is this?", "category": "directions"},
        {"nepali": "बाटो कता जान्छ?", "romanized": "bato kata janchha?", "english": "Where does the road go?", "category": "directions"},
    ]
    
    for phrase in phrases_data:
        db.session.add(Phrase(**phrase))
    db.session.commit()

def seed_alphabet():
    """Seed alphabet data"""
    alphabet_data = [
        {"devanagari": "अ", "romanized": "a", "sound": "a", "type": "vowel", "pronunciation": "like 'a' in 'about'"},
        {"devanagari": "आ", "romanized": "aa", "sound": "aa", "type": "vowel", "pronunciation": "like 'a' in 'father'"},
        {"devanagari": "क", "romanized": "ka", "sound": "ka", "type": "consonant", "pronunciation": "like 'k' in 'king'"},
        {"devanagari": "ख", "romanized": "kha", "sound": "kha", "type": "consonant", "pronunciation": "aspirated 'k'"},
    ]
    
    for letter in alphabet_data:
        db.session.add(Alphabet(**letter))
    db.session.commit()