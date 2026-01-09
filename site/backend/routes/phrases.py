from flask import Blueprint, jsonify, request
from models import Phrase, UserProgress
from database import db

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
            'audio_url': p.audio_url
        } for p in phrases])
    
    elif request.method == 'POST':
        data = request.get_json()
        new_phrase = Phrase(
            nepali=data.get('nepali'),
            romanized=data.get('romanized'),
            english=data.get('english'),
            category=data.get('category'),
            difficulty=data.get('difficulty', 1)
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
            'audio_url': phrase.audio_url
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        phrase.nepali = data.get('nepali', phrase.nepali)
        phrase.romanized = data.get('romanized', phrase.romanized)
        phrase.english = data.get('english', phrase.english)
        phrase.category = data.get('category', phrase.category)
        phrase.difficulty = data.get('difficulty', phrase.difficulty)
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
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