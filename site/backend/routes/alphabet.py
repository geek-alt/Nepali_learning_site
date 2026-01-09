from flask import Blueprint, jsonify, request
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
            'audio_url': l.audio_url
        } for l in letters])
    
    elif request.method == 'POST':
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
        data = request.get_json()
        letter.devanagari = data.get('devanagari', letter.devanagari)
        letter.romanized = data.get('romanized', letter.romanized)
        letter.sound = data.get('sound', letter.sound)
        letter.type = data.get('type', letter.type)
        letter.pronunciation = data.get('pronunciation', letter.pronunciation)
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        db.session.delete(letter)
        db.session.commit()
        return jsonify({'success': True}), 204