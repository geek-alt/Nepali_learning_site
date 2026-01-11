from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Dictionary
from database import db
from validation import validate_dictionary_entry, validation_error_response

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
        
        # Order by custom order_index (for drag-drop reordering)
        query = query.order_by(Dictionary.order_index)
        
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
        # Only admins can create dictionary words
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate input data
        validation_errors = validate_dictionary_entry(data)
        if validation_errors:
            return validation_error_response(validation_errors)
        
        # Check if word already exists
        nepali_text = data.get('nepali', '').strip()
        if nepali_text:
            existing = Dictionary.query.filter_by(nepali=nepali_text).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': f'A word with Nepali text "{nepali_text}" already exists (ID: {existing.id})'
                }), 400
        
        new_word = Dictionary(
            nepali=nepali_text,
            romanized=data.get('romanized', '').strip() if data.get('romanized') else None,
            english=data.get('english', '').strip(),
            part_of_speech=data.get('part_of_speech'),
            usage_example=data.get('usage_example', '').strip() if data.get('usage_example') else None,
            nepali_example=data.get('nepali_example', '').strip() if data.get('nepali_example') else None,
            audio_url=data.get('audio_url'),
            difficulty=data.get('difficulty', 1),
            category=data.get('category'),
            synonyms=data.get('synonyms'),
            antonyms=data.get('antonyms')
        )
        
        try:
            db.session.add(new_word)
            db.session.commit()
            return jsonify({'success': True, 'id': new_word.id, 'message': 'Word added successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

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
        # Only admins can update dictionary words
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Check if nepali text is being changed to one that already exists
        new_nepali = data.get('nepali', word.nepali)
        if new_nepali != word.nepali:
            existing = Dictionary.query.filter_by(nepali=new_nepali).first()
            if existing:
                return jsonify({
                    'success': False, 
                    'error': f'A word with Nepali text "{new_nepali}" already exists (ID: {existing.id})'
                }), 400
        
        word.nepali = new_nepali
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
        
        try:
            db.session.commit()
            return jsonify({'success': True, 'message': 'Word updated'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        # Only admins can delete dictionary words
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        try:
            db.session.delete(word)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Word deleted'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

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
    # Only admins can bulk import
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
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

# Reorder Dictionary
@bp.route('/reorder', methods=['POST', 'OPTIONS'])
def reorder_dictionary():
    """Update the order_index for multiple dictionary entries"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        order_list = data.get('order', [])
        
        if not order_list:
            return jsonify({'error': 'No order data provided'}), 400
        
        # Update each word's order_index
        for item in order_list:
            word_id = item.get('id')
            order_index = item.get('order_index')
            
            if word_id and order_index is not None:
                word = Dictionary.query.get(word_id)
                if word:
                    word.order_index = order_index
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Updated order for {len(order_list)} words'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========== ADVANCED FEATURES ==========

# Global Search Across All Tables
@bp.route('/global-search', methods=['GET'])
def global_search():
    """Search across Dictionary, Alphabet, and Phrases tables"""
    from models import Alphabet, Phrase
    
    query = request.args.get('q', '').lower()
    if not query or len(query) < 2:
        return jsonify({'error': 'Query too short'}), 400
    
    # Search Dictionary
    dict_results = Dictionary.query.filter(
        db.or_(
            Dictionary.nepali.contains(query),
            Dictionary.romanized.ilike(f'%{query}%'),
            Dictionary.english.ilike(f'%{query}%')
        )
    ).limit(20).all()
    
    # Search Alphabet
    alphabet_results = Alphabet.query.filter(
        db.or_(
            Alphabet.devanagari.contains(query),
            Alphabet.romanized.ilike(f'%{query}%'),
            Alphabet.sound.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    # Search Phrases
    phrase_results = Phrase.query.filter(
        db.or_(
            Phrase.nepali.contains(query),
            Phrase.romanized.ilike(f'%{query}%'),
            Phrase.english.ilike(f'%{query}%')
        )
    ).limit(20).all()
    
    return jsonify({
        'dictionary': [{
            'id': w.id,
            'nepali': w.nepali,
            'romanized': w.romanized,
            'english': w.english,
            'category': w.category,
            'type': 'dictionary'
        } for w in dict_results],
        'alphabet': [{
            'id': l.id,
            'devanagari': l.devanagari,
            'romanized': l.romanized,
            'sound': l.sound,
            'type': 'alphabet'
        } for l in alphabet_results],
        'phrases': [{
            'id': p.id,
            'nepali': p.nepali,
            'romanized': p.romanized,
            'english': p.english,
            'category': p.category,
            'type': 'phrase'
        } for p in phrase_results],
        'total_results': len(dict_results) + len(alphabet_results) + len(phrase_results)
    })

# Statistics Dashboard
@bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get comprehensive statistics for admin dashboard"""
    from models import Alphabet, Phrase
    from sqlalchemy import func
    
    # Dictionary statistics
    dict_total = Dictionary.query.count()
    dict_by_difficulty = db.session.query(
        Dictionary.difficulty,
        func.count(Dictionary.id)
    ).group_by(Dictionary.difficulty).all()
    
    dict_by_category = db.session.query(
        Dictionary.category,
        func.count(Dictionary.id)
    ).filter(Dictionary.category != None).group_by(Dictionary.category).all()
    
    dict_recent = Dictionary.query.order_by(Dictionary.created_at.desc()).limit(5).all()
    dict_popular = Dictionary.query.order_by(Dictionary.views.desc()).limit(5).all()
    
    # Alphabet statistics
    alphabet_total = Alphabet.query.count()
    alphabet_vowels = Alphabet.query.filter_by(type='vowel').count()
    alphabet_consonants = Alphabet.query.filter_by(type='consonant').count()
    
    # Phrase statistics
    phrase_total = Phrase.query.count()
    phrase_by_category = db.session.query(
        Phrase.category,
        func.count(Phrase.id)
    ).group_by(Phrase.category).all()
    
    phrase_by_formality = db.session.query(
        Phrase.formality_level,
        func.count(Phrase.id)
    ).filter(Phrase.formality_level != None).group_by(Phrase.formality_level).all()
    
    return jsonify({
        'dictionary': {
            'total': dict_total,
            'by_difficulty': {str(level): count for level, count in dict_by_difficulty},
            'by_category': {cat: count for cat, count in dict_by_category},
            'recent': [{
                'id': w.id,
                'nepali': w.nepali,
                'english': w.english,
                'created_at': w.created_at.isoformat()
            } for w in dict_recent],
            'popular': [{
                'id': w.id,
                'nepali': w.nepali,
                'views': w.views
            } for w in dict_popular]
        },
        'alphabet': {
            'total': alphabet_total,
            'vowels': alphabet_vowels,
            'consonants': alphabet_consonants
        },
        'phrases': {
            'total': phrase_total,
            'by_category': {cat: count for cat, count in phrase_by_category},
            'by_formality': {level: count for level, count in phrase_by_formality}
        },
        'totals': {
            'all_content': dict_total + alphabet_total + phrase_total,
            'dictionary': dict_total,
            'alphabet': alphabet_total,
            'phrases': phrase_total
        }
    })

# Bulk Operations
@bp.route('/bulk-delete', methods=['POST'])
def bulk_delete():
    """Delete multiple dictionary entries by IDs"""
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    ids = data.get('ids', [])
    
    if not ids:
        return jsonify({'error': 'No IDs provided'}), 400
    
    try:
        deleted_count = Dictionary.query.filter(Dictionary.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({
            'success': True,
            'deleted': deleted_count,
            'message': f'Deleted {deleted_count} entries'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/bulk-update-category', methods=['POST'])
def bulk_update_category():
    """Update category for multiple dictionary entries"""
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    ids = data.get('ids', [])
    new_category = data.get('category')
    
    if not ids or not new_category:
        return jsonify({'error': 'IDs and category required'}), 400
    
    try:
        updated_count = Dictionary.query.filter(Dictionary.id.in_(ids)).update(
            {'category': new_category},
            synchronize_session=False
        )
        db.session.commit()
        return jsonify({
            'success': True,
            'updated': updated_count,
            'message': f'Updated {updated_count} entries to category "{new_category}"'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/bulk-update-difficulty', methods=['POST'])
def bulk_update_difficulty():
    """Update difficulty for multiple dictionary entries"""
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    ids = data.get('ids', [])
    new_difficulty = data.get('difficulty')
    
    if not ids or new_difficulty not in [1, 2, 3]:
        return jsonify({'error': 'IDs and valid difficulty (1-3) required'}), 400
    
    try:
        updated_count = Dictionary.query.filter(Dictionary.id.in_(ids)).update(
            {'difficulty': new_difficulty},
            synchronize_session=False
        )
        db.session.commit()
        return jsonify({
            'success': True,
            'updated': updated_count,
            'message': f'Updated {updated_count} entries to difficulty {new_difficulty}'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
