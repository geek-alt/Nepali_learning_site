from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Phrase, UserProgress
from database import db
from validation import validate_phrase, validation_error_response

bp = Blueprint('phrases', __name__, url_prefix='/api/phrases')

@bp.route('/', methods=['GET', 'POST'])
def get_or_create_phrases():
    if request.method == 'GET':
        category = request.args.get('category')
        difficulty = request.args.get('difficulty', type=int)
        
        query = Phrase.query
        
        if category:
            query = query.filter_by(category=category)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        
        phrases = query.all()
        return jsonify([{
            'id': p.id,
            'nepali': p.nepali,
            'romanized': p.romanized,
            'english': p.english,
            'category': p.category,
            'audio_url': p.audio_url,
            'context': p.context,
            'formality_level': p.formality_level,
            'difficulty': p.difficulty
        } for p in phrases])
    
    elif request.method == 'POST':
        # Only admins can create phrases
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate input data
        validation_errors = validate_phrase(data)
        if validation_errors:
            return validation_error_response(validation_errors)
        
        new_phrase = Phrase(
            nepali=data.get('nepali', '').strip(),
            romanized=data.get('romanized', '').strip() if data.get('romanized') else None,
            english=data.get('english', '').strip(),
            category=data.get('category'),
            difficulty=data.get('difficulty', 1),
            context=data.get('context'),
            formality_level=data.get('formality_level', 'casual')
        )
        db.session.add(new_phrase)
        db.session.commit()
        return jsonify({'id': new_phrase.id}), 201

@bp.route('/<int:phrase_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_phrase(phrase_id):
    phrase = Phrase.query.get_or_404(phrase_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': phrase.id,
            'nepali': phrase.nepali,
            'romanized': phrase.romanized,
            'english': phrase.english,
            'category': phrase.category,
            'audio_url': phrase.audio_url,
            'context': phrase.context,
            'formality_level': phrase.formality_level,
            'difficulty': phrase.difficulty
        })
    
    elif request.method == 'PUT':
        # Only admins can update phrases
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        phrase.nepali = data.get('nepali', phrase.nepali)
        phrase.romanized = data.get('romanized', phrase.romanized)
        phrase.english = data.get('english', phrase.english)
        phrase.category = data.get('category', phrase.category)
        phrase.difficulty = data.get('difficulty', phrase.difficulty)
        phrase.context = data.get('context', phrase.context)
        phrase.formality_level = data.get('formality_level', phrase.formality_level)
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        # Only admins can delete phrases
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        db.session.delete(phrase)
        db.session.commit()
        return jsonify({'success': True}), 204

@bp.route('/categories', methods=['GET'])
def get_categories():
    categories = db.session.query(Phrase.category).distinct().all()
    return jsonify([cat[0] for cat in categories])

@bp.route('/search', methods=['GET'])
def search_phrases():
    query = request.args.get('q', '')
    phrases = Phrase.query.filter(
        db.or_(
            Phrase.nepali.contains(query),
            Phrase.romanized.contains(query),
            Phrase.english.contains(query)
        )
    ).all()
    
    return jsonify([{
        'id': p.id,
        'nepali': p.nepali,
        'romanized': p.romanized,
        'english': p.english,
        'category': p.category
    } for p in phrases])