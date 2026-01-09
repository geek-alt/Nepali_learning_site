from flask import Blueprint, jsonify, request
from models import Dictionary
from database import db

bp = Blueprint('dictionary', __name__, url_prefix='/api/dictionary')

# Get all words with pagination
@bp.route('/', methods=['GET', 'POST'])
def get_or_create_words():
    if request.method == 'GET':
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        difficulty = request.args.get('difficulty', type=int)
        category = request.args.get('category', type=str)
        
        query = Dictionary.query
        
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        if category:
            query = query.filter_by(category=category)
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'words': [{
                'id': w.id,
                'nepali': w.nepali,
                'romanized': w.romanized,
                'english': w.english,
                'part_of_speech': w.part_of_speech,
                'difficulty': w.difficulty,
                'category': w.category,
                'audio_url': w.audio_url,
                'views': w.views
            } for w in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        new_word = Dictionary(
            nepali=data.get('nepali'),
            romanized=data.get('romanized'),
            english=data.get('english'),
            part_of_speech=data.get('part_of_speech'),
            usage_example=data.get('usage_example'),
            nepali_example=data.get('nepali_example'),
            audio_url=data.get('audio_url'),
            difficulty=data.get('difficulty', 1),
            category=data.get('category'),
            synonyms=data.get('synonyms'),
            antonyms=data.get('antonyms')
        )
        db.session.add(new_word)
        db.session.commit()
        return jsonify({'id': new_word.id, 'message': 'Word added successfully'}), 201

# Get single word
@bp.route('/<int:word_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_word(word_id):
    word = Dictionary.query.get_or_404(word_id)
    
    if request.method == 'GET':
        # Increment view count
        word.views += 1
        db.session.commit()
        
        return jsonify({
            'id': word.id,
            'nepali': word.nepali,
            'romanized': word.romanized,
            'english': word.english,
            'part_of_speech': word.part_of_speech,
            'usage_example': word.usage_example,
            'nepali_example': word.nepali_example,
            'audio_url': word.audio_url,
            'difficulty': word.difficulty,
            'category': word.category,
            'synonyms': word.synonyms,
            'antonyms': word.antonyms,
            'views': word.views
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        word.nepali = data.get('nepali', word.nepali)
        word.romanized = data.get('romanized', word.romanized)
        word.english = data.get('english', word.english)
        word.part_of_speech = data.get('part_of_speech', word.part_of_speech)
        word.usage_example = data.get('usage_example', word.usage_example)
        word.nepali_example = data.get('nepali_example', word.nepali_example)
        word.audio_url = data.get('audio_url', word.audio_url)
        word.difficulty = data.get('difficulty', word.difficulty)
        word.category = data.get('category', word.category)
        word.synonyms = data.get('synonyms', word.synonyms)
        word.antonyms = data.get('antonyms', word.antonyms)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Word updated'})
    
    elif request.method == 'DELETE':
        db.session.delete(word)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Word deleted'}), 204

# Search words
@bp.route('/search', methods=['GET'])
def search_words():
    q = request.args.get('q', '').lower()
    difficulty = request.args.get('difficulty', type=int)
    category = request.args.get('category', type=str)
    
    if not q or len(q) < 2:
        return jsonify({'error': 'Query too short'}), 400
    
    query = Dictionary.query.filter(
        db.or_(
            Dictionary.nepali.contains(q),
            Dictionary.romanized.ilike(f'%{q}%'),
            Dictionary.english.ilike(f'%{q}%')
        )
    )
    
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if category:
        query = query.filter_by(category=category)
    
    results = query.limit(50).all()
    
    return jsonify([{
        'id': w.id,
        'nepali': w.nepali,
        'romanized': w.romanized,
        'english': w.english,
        'category': w.category,
        'difficulty': w.difficulty
    } for w in results])

# Get categories
@bp.route('/categories', methods=['GET'])
def get_categories():
    categories = db.session.query(Dictionary.category).distinct().filter(
        Dictionary.category != None
    ).all()
    return jsonify([cat[0] for cat in categories if cat[0]])

# Get by category
@bp.route('/category/<category>', methods=['GET'])
def get_by_category(category):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    paginated = Dictionary.query.filter_by(category=category).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'words': [{
            'id': w.id,
            'nepali': w.nepali,
            'romanized': w.romanized,
            'english': w.english,
            'difficulty': w.difficulty,
            'category': w.category
        } for w in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages
    })

# Get by difficulty
@bp.route('/difficulty/<int:level>', methods=['GET'])
def get_by_difficulty(level):
    if level not in [1, 2, 3]:
        return jsonify({'error': 'Invalid difficulty level'}), 400
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    paginated = Dictionary.query.filter_by(difficulty=level).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'words': [{
            'id': w.id,
            'nepali': w.nepali,
            'romanized': w.romanized,
            'english': w.english,
            'difficulty': w.difficulty
        } for w in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages
    })

# Get trending/popular words
@bp.route('/trending', methods=['GET'])
def get_trending():
    trending = Dictionary.query.order_by(Dictionary.views.desc()).limit(10).all()
    
    return jsonify([{
        'id': w.id,
        'nepali': w.nepali,
        'romanized': w.romanized,
        'english': w.english,
        'views': w.views
    } for w in trending])

# Bulk import words from CSV
@bp.route('/bulk-import', methods=['POST'])
def bulk_import():
    """Import multiple words from CSV format"""
    data = request.get_json()
    words = data.get('words', [])
    
    if not words:
        return jsonify({'error': 'No words provided'}), 400
    
    added_count = 0
    errors = []
    
    for word_data in words:
        try:
            # Check if word already exists
            existing = Dictionary.query.filter_by(nepali=word_data.get('nepali')).first()
            if existing:
                continue
            
            new_word = Dictionary(
                nepali=word_data.get('nepali'),
                romanized=word_data.get('romanized'),
                english=word_data.get('english'),
                part_of_speech=word_data.get('part_of_speech'),
                difficulty=word_data.get('difficulty', 1),
                category=word_data.get('category')
            )
            db.session.add(new_word)
            added_count += 1
        except Exception as e:
            errors.append(str(e))
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'added': added_count,
            'errors': errors
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
