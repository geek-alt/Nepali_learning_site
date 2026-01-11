"""
Input validation utilities for security
Prevents XSS, SQL injection, and junk data
"""
import re
from flask import jsonify

# Dangerous patterns that should be rejected
DANGEROUS_PATTERNS = [
    r'<script',
    r'javascript:',
    r'onerror=',
    r'onclick=',
    r'onload=',
    r'<iframe',
    r'<embed',
    r'<object',
    r'eval\(',
    r'expression\(',
]

def contains_xss(text):
    """Check if text contains XSS attack patterns"""
    if not text:
        return False
    
    text_lower = text.lower()
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def is_suspiciously_long(text, max_length=1000):
    """Check if text is suspiciously long"""
    if not text:
        return False
    return len(text) > max_length

def is_repetitive_junk(text, min_unique_chars=3):
    """Check if text is just repetitive characters (like 'AAAAAAA...')"""
    if not text or len(text) < 20:
        return False
    
    # If string is long but has very few unique characters, it's junk
    unique_chars = len(set(text))
    if len(text) > 50 and unique_chars < min_unique_chars:
        return True
    
    return False

def validate_text_input(text, field_name, required=True, max_length=500):
    """
    Validate text input for security and quality
    
    Args:
        text: The text to validate
        field_name: Name of the field (for error messages)
        required: Whether the field is required
        max_length: Maximum allowed length
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if empty
    if not text or not text.strip():
        if required:
            return False, f"{field_name} is required"
        return True, None
    
    text = text.strip()
    
    # Check for XSS patterns
    if contains_xss(text):
        return False, f"{field_name} contains potentially dangerous content"
    
    # Check length
    if len(text) > max_length:
        return False, f"{field_name} is too long (maximum {max_length} characters)"
    
    # Check for repetitive junk
    if is_repetitive_junk(text):
        return False, f"{field_name} appears to be invalid (repetitive characters)"
    
    return True, None

def validate_dictionary_entry(data):
    """Validate dictionary entry data"""
    errors = []
    
    # Validate nepali
    valid, error = validate_text_input(data.get('nepali'), 'Nepali word', required=True, max_length=200)
    if not valid:
        errors.append(error)
    
    # Validate english
    valid, error = validate_text_input(data.get('english'), 'English translation', required=True, max_length=200)
    if not valid:
        errors.append(error)
    
    # Validate romanized (optional)
    if data.get('romanized'):
        valid, error = validate_text_input(data.get('romanized'), 'Romanized', required=False, max_length=200)
        if not valid:
            errors.append(error)
    
    # Validate examples (optional)
    if data.get('usage_example'):
        valid, error = validate_text_input(data.get('usage_example'), 'Usage example', required=False, max_length=500)
        if not valid:
            errors.append(error)
    
    if data.get('nepali_example'):
        valid, error = validate_text_input(data.get('nepali_example'), 'Nepali example', required=False, max_length=500)
        if not valid:
            errors.append(error)
    
    return errors

def validate_phrase(data):
    """Validate phrase data"""
    errors = []
    
    valid, error = validate_text_input(data.get('nepali'), 'Nepali phrase', required=True, max_length=300)
    if not valid:
        errors.append(error)
    
    valid, error = validate_text_input(data.get('english'), 'English translation', required=True, max_length=300)
    if not valid:
        errors.append(error)
    
    if data.get('romanized'):
        valid, error = validate_text_input(data.get('romanized'), 'Romanized', required=False, max_length=300)
        if not valid:
            errors.append(error)
    
    return errors

def validate_alphabet(data):
    """Validate alphabet/letter data"""
    errors = []
    
    valid, error = validate_text_input(data.get('devanagari'), 'Devanagari character', required=True, max_length=10)
    if not valid:
        errors.append(error)
    
    valid, error = validate_text_input(data.get('romanized'), 'Romanization', required=True, max_length=50)
    if not valid:
        errors.append(error)
    
    if data.get('sound'):
        valid, error = validate_text_input(data.get('sound'), 'Sound', required=False, max_length=50)
        if not valid:
            errors.append(error)
    
    return errors

def validation_error_response(errors):
    """Create a standardized error response for validation errors"""
    return jsonify({
        'error': 'Validation failed',
        'details': errors
    }), 400
