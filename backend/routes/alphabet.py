from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Alphabet
from database import db

bp = Blueprint('alphabet', __name__, url_prefix='/api/alphabet')

@bp.route('/', methods=['GET', 'POST'])
def get_or_create_alphabet():
    if request.method == 'GET':
        letter_type = request.args.get('type')
        
        query = Alphabet.query.order_by(Alphabet.order_index)
        if letter_type:
            query = query.filter_by(type=letter_type)
        
        letters = query.all()
        return jsonify([{
            'id': l.id,
            'devanagari': l.devanagari,
            'romanized': l.romanized,
            'sound': l.sound,
            'type': l.type,
            'pronunciation': l.pronunciation,
            'audio_url': l.audio_url,
            'order_index': l.order_index
        } for l in letters])
    
    elif request.method == 'POST':
        # Only admins can create alphabet letters
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        new_letter = Alphabet(
            devanagari=data.get('devanagari'),
            romanized=data.get('romanized'),
            sound=data.get('sound', data.get('romanized')),
            type=data.get('type'),
            pronunciation=data.get('pronunciation')
        )
        db.session.add(new_letter)
        db.session.commit()
        return jsonify({'id': new_letter.id}), 201

@bp.route('/<int:letter_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_letter(letter_id):
    letter = Alphabet.query.get_or_404(letter_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': letter.id,
            'devanagari': letter.devanagari,
            'romanized': letter.romanized,
            'sound': letter.sound,
            'type': letter.type,
            'pronunciation': letter.pronunciation,
            'audio_url': letter.audio_url
        })
    
    elif request.method == 'PUT':
        # Only admins can update alphabet letters
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        letter.devanagari = data.get('devanagari', letter.devanagari)
        letter.romanized = data.get('romanized', letter.romanized)
        letter.sound = data.get('sound', letter.sound)
        letter.type = data.get('type', letter.type)
        letter.pronunciation = data.get('pronunciation', letter.pronunciation)
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        # Only admins can delete alphabet letters
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        db.session.delete(letter)
        db.session.commit()
        return jsonify({'success': True}), 204

@bp.route('/reorder', methods=['POST', 'OPTIONS'])
def reorder_alphabet():
    """Update the order_index for multiple alphabet letters"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    # Only admins can reorder alphabet
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        order_list = data.get('order', [])
        
        if not order_list:
            return jsonify({'error': 'No order data provided'}), 400
        
        # Update each letter's order_index
        for item in order_list:
            letter_id = item.get('id')
            order_index = item.get('order_index')
            
            if letter_id and order_index is not None:
                letter = Alphabet.query.get(letter_id)
                if letter:
                    letter.order_index = order_index
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Updated order for {len(order_list)} letters'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
