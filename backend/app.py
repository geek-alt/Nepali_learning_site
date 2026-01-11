from flask import Flask, jsonify, request, render_template, send_from_directory, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from database import db
from datetime import datetime
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static',
            static_url_path='/static')

# If running behind Gunicorn / Nginx / Cloudflare ensure the original
# client IP, host and protocol are preserved so redirects and secure
# cookie detection work correctly.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///nepali_learning.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production-CRITICAL')
app.config['WTF_CSRF_TIME_LIMIT'] = None  # CSRF tokens don't expire
app.config['WTF_CSRF_SSL_STRICT'] = True  # Enforce HTTPS in production
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Disable default CSRF check, we'll enable selectively
# Determine SESSION_COOKIE_SECURE from env for flexibility behind proxies/CDNs.
# If SESSION_COOKIE_SECURE is not set, fall back to FLASK_ENV == 'production'.
sess_secure_env = os.getenv('SESSION_COOKIE_SECURE')
if sess_secure_env is None or sess_secure_env == '':
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
else:
    app.config['SESSION_COOKIE_SECURE'] = str(sess_secure_env).lower() in ('1', 'true', 'yes')
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = None  # Allow cookies in AJAX requests
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Initialize extensions
db.init_app(app)
CORS(app, resources={
    r"/*": {  # Allow CORS for all routes
        "origins": os.getenv('ALLOWED_ORIGINS', '*').split(','),
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "X-CSRFToken"],
        "supports_credentials": True
    }
})

# CSRF Protection - Disabled for auth endpoints (session cookies provide protection)
# csrf = CSRFProtect(app)  # Commented out - causing 415 errors on JSON endpoints

# Rate Limiting (in-memory storage, use Redis in production)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://"  # Use "redis://localhost:6379" in production
)

# Security Headers (Talisman)
csp = {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'", "https://www.youtube.com", "https://cdn.jsdelivr.net"],
    'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
    'img-src': ["'self'", "data:", "https://i.ytimg.com", "https://img.youtube.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net"],
    'frame-src': ["'self'", "https://www.youtube.com"],
    'connect-src': ["'self'", "http://localhost:5000", "http://127.0.0.1:5000"]
}

'''Talisman(app, 
    force_https=os.getenv('FLASK_ENV') == 'production',
    strict_transport_security=True,
    content_security_policy=csp
    # content_security_policy_nonce_in removed - nonces disable 'unsafe-inline'
)'''

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'  # Points to /login route
login_manager.login_message = 'Please log in to access this page'
login_manager.session_protection = 'strong'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(user_id)

# Import models and routes
from models import Phrase, Alphabet, UserProgress, Dictionary, Resource, PDFResource, Video, Playlist, User
from routes import phrases, alphabet, transliterator, dictionary, resources, auth

# Register blueprints
app.register_blueprint(phrases.bp)
app.register_blueprint(alphabet.bp)
app.register_blueprint(transliterator.bp)
app.register_blueprint(dictionary.bp)  # V2: Dictionary system
app.register_blueprint(resources.bp)   # V2: Resources, Videos, PDFs
app.register_blueprint(auth.auth_bp)   # Authentication routes

# CSRF token injection for all responses
@app.after_request
def inject_csrf_token(response):
    """Add CSRF token to response headers"""
    if request.endpoint and not request.endpoint.startswith('static'):
        csrf_token = generate_csrf()
        response.headers['X-CSRFToken'] = csrf_token
    return response

# Error handlers
@app.errorhandler(429)
def ratelimit_handler(e):
    """Rate limit exceeded handler"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429

@app.errorhandler(403)
def forbidden_handler(e):
    """Forbidden access handler"""
    return jsonify({
        'error': 'Forbidden',
        'message': 'You do not have permission to access this resource.'
    }), 403

@app.errorhandler(401)
def unauthorized_handler(e):
    """Unauthorized access handler"""
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required.'
    }), 401

@app.errorhandler(404)
def not_found_handler(e):
    """Not found handler"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found.'
    }), 404

@app.errorhandler(500)
def internal_error_handler(e):
    """Internal server error handler"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again later.'
    }), 500

# Serve frontend
@app.route('/')
@limiter.limit("100 per minute")
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET'])
@login_required
def admin():
    """Admin panel - requires authentication"""
    if not current_user.is_admin():
        return redirect(url_for('login_page'))
    return render_template('admin.html')

@app.route('/login')
def login_page():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    return render_template('login.html')


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
        {"devanagari": "अ", "romanized": "a", "sound": "a", "type": "vowel", "pronunciation": "like 'a' in 'about'", "order_index": 1},
        {"devanagari": "आ", "romanized": "aa", "sound": "aa", "type": "vowel", "pronunciation": "like 'a' in 'father'", "order_index": 2},
        {"devanagari": "क", "romanized": "ka", "sound": "ka", "type": "consonant", "pronunciation": "like 'k' in 'king'", "order_index": 3},
        {"devanagari": "ख", "romanized": "kha", "sound": "kha", "type": "consonant", "pronunciation": "aspirated 'k'", "order_index": 4},
    ]
    
    for letter in alphabet_data:
        db.session.add(Alphabet(**letter))
    db.session.commit()

# Database initialization
def initialize_data():
    """Initialize database with seed data if empty"""
    if not Phrase.query.first():
        seed_phrases()
        seed_alphabet()
    
    # Create default superadmin if no users exist
    if not User.query.first():
        create_default_admin()

def create_default_admin():
    """Create default superadmin account"""
    admin = User(
        username='admin',
        email='admin@nepalilearning.com',
        role='superadmin',
        is_active=True
    )
    admin.set_password('Admin@123456789')  # Must change on first login
    admin.must_change_password = True
    
    db.session.add(admin)
    db.session.commit()
    print("✓ Default admin created - Username: admin, Password: Admin@123456789")
    print("⚠ IMPORTANT: Change this password immediately!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_data()
    app.run(debug=True)
