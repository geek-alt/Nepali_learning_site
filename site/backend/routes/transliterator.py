from flask import Blueprint, jsonify, request
import re

bp = Blueprint('transliterator', __name__, url_prefix='/api/transliterator')

# Roman to Devanagari mapping
ROMAN_TO_DEVANAGARI = {
    'a': 'अ', 'aa': 'आ', 'i': 'इ', 'ii': 'ई', 'u': 'उ', 'uu': 'ऊ',
    'e': 'ए', 'ai': 'ऐ', 'o': 'ओ', 'au': 'औ', 'am': 'अं', 'ah': 'अः',
    'ka': 'क', 'kha': 'ख', 'ga': 'ग', 'gha': 'घ', 'nga': 'ङ',
    'cha': 'च', 'chha': 'छ', 'ja': 'ज', 'jha': 'झ', 'nya': 'ञ',
    'ta': 'ट', 'tha': 'ठ', 'da': 'ड', 'dha': 'ढ', 'na': 'ण',
    'ta': 'त', 'tha': 'थ', 'da': 'द', 'dha': 'ध', 'na': 'न',
    'pa': 'प', 'pha': 'फ', 'ba': 'ब', 'bha': 'भ', 'ma': 'म',
    'ya': 'य', 'ra': 'र', 'la': 'ल', 'va': 'व',
    'sha': 'श', 'sha': 'ष', 'sa': 'स', 'ha': 'ह',
    'ksha': 'क्ष', 'tra': 'त्र', 'gya': 'ज्ञ'
}

@bp.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    romanized = data.get('text', '').lower()
    
    if not romanized:
        return jsonify({'error': 'No text provided'}), 400
    
    # Simple conversion logic (can be improved)
    devanagari = romanized
    
    # Convert syllables
    for roman, deva in sorted(ROMAN_TO_DEVANAGARI.items(), key=lambda x: -len(x[0])):
        devanagari = devanagari.replace(roman, deva)
    
    return jsonify({
        'romanized': romanized,
        'devanagari': devanagari
    })

@bp.route('/rules', methods=['GET'])
def get_rules():
    return jsonify({
        'vowels': {k: v for k, v in ROMAN_TO_DEVANAGARI.items() if len(k) <= 2 and k in ['a', 'aa', 'i', 'ii', 'u', 'uu', 'e', 'ai', 'o', 'au']},
        'consonants': {k: v for k, v in ROMAN_TO_DEVANAGARI.items() if len(k) > 1 and k not in ['aa', 'ii', 'uu', 'ai', 'au', 'am', 'ah']}
    })