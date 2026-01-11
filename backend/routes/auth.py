"""
Authentication routes with comprehensive security features
"""
from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from functools import wraps
from datetime import datetime, timedelta
import re
import jwt
import os

from database import db
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Get CSRF instance to use for exemptions
from flask import current_app

def get_csrf():
    return current_app.extensions['csrf']

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Password requirements
MIN_PASSWORD_LENGTH = 12
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'

def validate_password(password):
    """Validate password meets security requirements"""
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letters"
    
    if not re.search(r'\d', password):
        return False, "Password must contain digits"
    
    if not re.search(r'[@$!%*?&]', password):
        return False, "Password must contain special characters (@$!%*?&)"
    
    return True, "Password is valid"

def validate_username(username):
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 80:
        return False, "Username must be less than 80 characters"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, "Username is valid"

def validate_email(email):
    """Basic email validation"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False, "Invalid email format"
    return True, "Email is valid"

def generate_jwt_token(user_id, role):
    """Generate JWT token for API authentication"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token):
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['user_id'], payload['role']
    except jwt.ExpiredSignatureError:
        return None, None
    except jwt.InvalidTokenError:
        return None, None

def require_admin(f):
    """Decorator to require admin or superadmin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_superadmin(f):
    """Decorator to require superadmin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'superadmin':
            return jsonify({'error': 'Superadmin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def jwt_required(f):
    """Decorator for JWT authentication (API endpoints)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_id, role = verify_jwt_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user_id and role to request context
        request.jwt_user_id = user_id
        request.jwt_role = role
        
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user with validation"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Username, email, and password required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validate username
        valid, message = validate_username(username)
        if not valid:
            return jsonify({'error': message}), 400
        
        # Validate email
        valid, message = validate_email(email)
        if not valid:
            return jsonify({'error': message}), 400
        
        # Validate password
        valid, message = validate_password(password)
        if not valid:
            return jsonify({'error': message}), 400
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        user = User(
            username=username,
            email=email,
            role='user'  # Default role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with account lockout protection"""
    try:
        # Check Content-Type
        if not request.is_json:
            return jsonify({
                'error': f'Content-Type must be application/json. Received: {request.content_type}'
            }), 415
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({'error': 'Username and password required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username.lower())
        ).first()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if account is locked
        if user.is_locked():
            lock_time_remaining = (user.locked_until - datetime.utcnow()).total_seconds() / 60
            return jsonify({
                'error': f'Account locked due to multiple failed login attempts. Try again in {int(lock_time_remaining)} minutes.'
            }), 423
        
        # Check if account is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Verify password
        if not user.check_password(password):
            user.record_failed_login()
            attempts_left = 5 - user.failed_login_attempts
            if attempts_left > 0:
                return jsonify({
                    'error': f'Invalid credentials. {attempts_left} attempts remaining.'
                }), 401
            else:
                return jsonify({
                    'error': 'Account locked due to multiple failed login attempts. Try again in 30 minutes.'
                }), 423
        
        # Successful login
        ip_address = request.remote_addr
        user.record_successful_login(ip_address)
        
        # Log user in (session-based)
        login_user(user, remember=data.get('remember', False))
        
        # Generate JWT token for API authentication
        jwt_token = generate_jwt_token(user.id, user.role)
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            },
            'token': jwt_token,
            'session_token': user.session_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout current user"""
    try:
        # Clear session token
        current_user.session_token = None
        db.session.commit()
        
        logout_user()
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role,
            'is_active': current_user.is_active,
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
            'created_at': current_user.created_at.isoformat()
        }
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['current_password', 'new_password']):
            return jsonify({'error': 'Current password and new password required'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        valid, message = validate_password(new_password)
        if not valid:
            return jsonify({'error': message}), 400
        
        # Ensure new password is different
        if current_password == new_password:
            return jsonify({'error': 'New password must be different from current password'}), 400
        
        # Update password
        current_user.set_password(new_password)
        current_user.must_change_password = False
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500

@auth_bp.route('/users', methods=['GET'])
@require_admin
def list_users():
    """List all users (admin only)"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': user.created_at.isoformat()
            } for user in users]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch users: {str(e)}'}), 500

@auth_bp.route('/users/<user_id>/role', methods=['PUT'])
@require_superadmin
def update_user_role(user_id):
    """Update user role (superadmin only)"""
    try:
        data = request.get_json()
        
        if not data or 'role' not in data:
            return jsonify({'error': 'Role required'}), 400
        
        new_role = data['role']
        if new_role not in ['user', 'admin', 'superadmin']:
            return jsonify({'error': 'Invalid role. Must be: user, admin, or superadmin'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent superadmin from demoting themselves
        if user.id == current_user.id and new_role != 'superadmin':
            return jsonify({'error': 'Cannot change your own role'}), 403
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update role: {str(e)}'}), 500

@auth_bp.route('/users/<user_id>/deactivate', methods=['PUT'])
@require_admin
def deactivate_user(user_id):
    """Deactivate user account (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent admin from deactivating themselves
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot deactivate your own account'}), 403
        
        # Only superadmin can deactivate other admins
        if user.is_admin() and current_user.role != 'superadmin':
            return jsonify({'error': 'Only superadmin can deactivate admin accounts'}), 403
        
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'User deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to deactivate user: {str(e)}'}), 500

@auth_bp.route('/users/<user_id>/unlock', methods=['PUT'])
@require_admin
def unlock_user(user_id):
    """Unlock locked user account (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()
        
        return jsonify({'message': 'User account unlocked successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to unlock user: {str(e)}'}), 500
