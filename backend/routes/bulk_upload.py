from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import csv
import io
from models import Dictionary, Phrase, Video, PDFResource, Playlist, Alphabet
from database import db

bp = Blueprint('bulk_upload', __name__, url_prefix='/api/bulk')

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===== VALIDATION ENDPOINT (Check before upload) =====
@bp.route('/validate/<resource_type>', methods=['POST'])
def validate_csv(resource_type):
    """Validate CSV and check for duplicates before uploading"""
    # Only admins can validate bulk uploads
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files allowed'}), 400
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        # Validate based on resource type
        if resource_type == 'dictionary':
            validation_result = validate_dictionary(csv_reader)
        elif resource_type == 'phrases':
            validation_result = validate_phrases(csv_reader)
        elif resource_type == 'alphabet':
            validation_result = validate_alphabet(csv_reader)
        elif resource_type == 'videos':
            validation_result = validate_videos(csv_reader)
        else:
            return jsonify({'error': 'Invalid resource type'}), 400
        
        return jsonify(validation_result), 200
        
    except Exception as e:
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500

def validate_dictionary(csv_reader):
    """Validate dictionary CSV"""
    result = {
        'valid': [],
        'duplicates': [],
        'errors': [],
        'total_rows': 0,
        'valid_count': 0,
        'duplicate_count': 0,
        'error_count': 0
    }
    
    # Get all existing words for fast lookup
    existing_words = {word.nepali.strip().lower(): word for word in Dictionary.query.all()}
    seen_in_csv = set()
    
    for row_num, row in enumerate(csv_reader, start=2):
        result['total_rows'] += 1
        
        try:
            # Required fields validation
            required_fields = ['nepali', 'romanized', 'english']
            missing_fields = [field for field in required_fields if not row.get(field, '').strip()]
            
            if missing_fields:
                result['errors'].append({
                    'row': row_num,
                    'data': row,
                    'reason': f"Missing required fields: {', '.join(missing_fields)}"
                })
                result['error_count'] += 1
                continue
            
            nepali_word = row['nepali'].strip().lower()
            
            # Check database duplicates
            if nepali_word in existing_words:
                existing = existing_words[nepali_word]
                result['duplicates'].append({
                    'row': row_num,
                    'data': row,
                    'existing': {
                        'nepali': existing.nepali,
                        'romanized': existing.romanized,
                        'english': existing.english,
                        'id': existing.id
                    },
                    'reason': 'Already exists in database'
                })
                result['duplicate_count'] += 1
                continue
            
            # Check CSV internal duplicates
            if nepali_word in seen_in_csv:
                result['duplicates'].append({
                    'row': row_num,
                    'data': row,
                    'reason': 'Duplicate within CSV file'
                })
                result['duplicate_count'] += 1
                continue
            
            # Validate difficulty level
            try:
                difficulty = int(row.get('difficulty', 1))
                if difficulty not in [1, 2, 3]:
                    result['errors'].append({
                        'row': row_num,
                        'data': row,
                        'reason': 'Difficulty must be 1, 2, or 3'
                    })
                    result['error_count'] += 1
                    continue
            except ValueError:
                result['errors'].append({
                    'row': row_num,
                    'data': row,
                    'reason': 'Difficulty must be a number (1, 2, or 3)'
                })
                result['error_count'] += 1
                continue
            
            # Valid entry
            seen_in_csv.add(nepali_word)
            result['valid'].append({
                'row': row_num,
                'data': row
            })
            result['valid_count'] += 1
            
        except Exception as e:
            result['errors'].append({
                'row': row_num,
                'data': row,
                'reason': str(e)
            })
            result['error_count'] += 1
    
    return result

def validate_phrases(csv_reader):
    """Validate phrases CSV"""
    result = {
        'valid': [],
        'duplicates': [],
        'errors': [],
        'total_rows': 0,
        'valid_count': 0,
        'duplicate_count': 0,
        'error_count': 0
    }
    
    # Get existing phrases
    existing_phrases = {(p.nepali.strip().lower(), p.english.strip().lower()): p 
                       for p in Phrase.query.all()}
    seen_in_csv = set()
    
    for row_num, row in enumerate(csv_reader, start=2):
        result['total_rows'] += 1
        
        try:
            required_fields = ['nepali', 'romanized', 'english']
            missing_fields = [field for field in required_fields if not row.get(field, '').strip()]
            
            if missing_fields:
                result['errors'].append({
                    'row': row_num,
                    'data': row,
                    'reason': f"Missing required fields: {', '.join(missing_fields)}"
                })
                result['error_count'] += 1
                continue
            
            phrase_key = (row['nepali'].strip().lower(), row['english'].strip().lower())
            
            # Check database duplicates
            if phrase_key in existing_phrases:
                existing = existing_phrases[phrase_key]
                result['duplicates'].append({
                    'row': row_num,
                    'data': row,
                    'existing': {
                        'nepali': existing.nepali,
                        'romanized': existing.romanized,
                        'english': existing.english,
                        'id': existing.id
                    },
                    'reason': 'Already exists in database'
                })
                result['duplicate_count'] += 1
                continue
            
            # Check CSV internal duplicates
            if phrase_key in seen_in_csv:
                result['duplicates'].append({
                    'row': row_num,
                    'data': row,
                    'reason': 'Duplicate within CSV file'
                })
                result['duplicate_count'] += 1
                continue
            
            # Validate difficulty
            try:
                difficulty = int(row.get('difficulty', 1))
                if difficulty not in [1, 2, 3]:
                    result['errors'].append({
                        'row': row_num,
                        'data': row,
                        'reason': 'Difficulty must be 1, 2, or 3'
                    })
                    result['error_count'] += 1
                    continue
            except ValueError:
                result['errors'].append({
                    'row': row_num,
                    'data': row,
                    'reason': 'Difficulty must be a number'
                })
                result['error_count'] += 1
                continue
            
            seen_in_csv.add(phrase_key)
            result['valid'].append({
                'row': row_num,
                'data': row
            })
            result['valid_count'] += 1
            
        except Exception as e:
            result['errors'].append({
                'row': row_num,
                'data': row,
                'reason': str(e)
            })
            result['error_count'] += 1
    
    return result

def validate_alphabet(csv_reader):
    """Validate alphabet CSV"""
    result = {
        'valid': [],
        'duplicates': [],
        'errors': [],
        'total_rows': 0,
        'valid_count': 0,
        'duplicate_count': 0,
        'error_count': 0
    }
    
    existing_letters = {letter.devanagari.strip(): letter for letter in Alphabet.query.all()}
    seen_in_csv = set()
    
    for row_num, row in enumerate(csv_reader, start=2):
        result['total_rows'] += 1
        
        try:
            required_fields = ['devanagari', 'romanized', 'sound', 'type']
            missing_fields = [field for field in required_fields if not row.get(field, '').strip()]
            
            if missing_fields:
                result['errors'].append({
                    'row': row_num,
                    'data': row,
                    'reason': f"Missing required fields: {', '.join(missing_fields)}"
                })
                result['error_count'] += 1
                continue
            
            devanagari = row['devanagari'].strip()
            letter_type = row['type'].strip().lower()
            
            # Validate type
            if letter_type not in ['vowel', 'consonant']:
                result['errors'].append({
                    'row': row_num,
                    'data': row,
                    'reason': 'Type must be "vowel" or "consonant"'
                })
                result['error_count'] += 1
                continue
            
            # Check database duplicates
            if devanagari in existing_letters:
                existing = existing_letters[devanagari]
                result['duplicates'].append({
                    'row': row_num,
                    'data': row,
                    'existing': {
                        'devanagari': existing.devanagari,
                        'romanized': existing.romanized,
                        'type': existing.type,
                        'id': existing.id
                    },
                    'reason': 'Already exists in database'
                })
                result['duplicate_count'] += 1
                continue
            
            # Check CSV internal duplicates
            if devanagari in seen_in_csv:
                result['duplicates'].append({
                    'row': row_num,
                    'data': row,
                    'reason': 'Duplicate within CSV file'
                })
                result['duplicate_count'] += 1
                continue
            
            seen_in_csv.add(devanagari)
            result['valid'].append({
                'row': row_num,
                'data': row
            })
            result['valid_count'] += 1
            
        except Exception as e:
            result['errors'].append({
                'row': row_num,
                'data': row,
                'reason': str(e)
            })
            result['error_count'] += 1
    
    return result

def validate_videos(csv_reader):
    """Validate videos CSV"""
    result = {
        'valid': [],
        'duplicates': [],
        'errors': [],
        'total_rows': 0,
        'valid_count': 0,
        'duplicate_count': 0,
        'error_count': 0
    }
    
    existing_videos = {video.youtube_id.strip(): video for video in Video.query.all()}
    seen_in_csv = set()
    
    for row_num, row in enumerate(csv_reader, start=2):
        result['total_rows'] += 1
        
        try:
            required_fields = ['title', 'youtube_id']
            missing_fields = [field for field in required_fields if not row.get(field, '').strip()]
            
            if missing_fields:
                result['errors'].append({
                    'row': row_num,
                    'data': row,
                    'reason': f"Missing required fields: {', '.join(missing_fields)}"
                })
                result['error_count'] += 1
                continue
            
            youtube_id = row['youtube_id'].strip()
            
            # Validate YouTube ID format (basic check)
            if len(youtube_id) != 11:
                result['errors'].append({
                    'row': row_num,
                    'data': row,
                    'reason': 'YouTube ID must be 11 characters'
                })
                result['error_count'] += 1
                continue
            
            # Check database duplicates
            if youtube_id in existing_videos:
                existing = existing_videos[youtube_id]
                result['duplicates'].append({
                    'row': row_num,
                    'data': row,
                    'existing': {
                        'title': existing.title,
                        'youtube_id': existing.youtube_id,
                        'id': existing.id
                    },
                    'reason': 'Already exists in database'
                })
                result['duplicate_count'] += 1
                continue
            
            # Check CSV internal duplicates
            if youtube_id in seen_in_csv:
                result['duplicates'].append({
                    'row': row_num,
                    'data': row,
                    'reason': 'Duplicate within CSV file'
                })
                result['duplicate_count'] += 1
                continue
            
            # Validate difficulty if provided
            if row.get('difficulty'):
                try:
                    diff = int(row['difficulty'])
                    if diff not in [1, 2, 3]:
                        result['errors'].append({
                            'row': row_num,
                            'data': row,
                            'reason': 'Difficulty must be 1, 2, or 3'
                        })
                        result['error_count'] += 1
                        continue
                except ValueError:
                    result['errors'].append({
                        'row': row_num,
                        'data': row,
                        'reason': 'Difficulty must be a number'
                    })
                    result['error_count'] += 1
                    continue
            
            seen_in_csv.add(youtube_id)
            result['valid'].append({
                'row': row_num,
                'data': row
            })
            result['valid_count'] += 1
            
        except Exception as e:
            result['errors'].append({
                'row': row_num,
                'data': row,
                'reason': str(e)
            })
            result['error_count'] += 1
    
    return result

# ===== UPLOAD ENDPOINTS =====
@bp.route('/dictionary', methods=['POST'])
def upload_dictionary():
    """Upload dictionary words from CSV"""
    # Only admins can bulk upload
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    skip_duplicates = request.form.get('skip_duplicates', 'true').lower() == 'true'
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files allowed'}), 400
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        added = 0
        errors = []
        skipped = 0
        
        # Get existing words for fast lookup
        existing_words = {word.nepali.strip().lower() for word in Dictionary.query.all()}
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                nepali_word = row['nepali'].strip()
                
                # Check for duplicates
                if nepali_word.lower() in existing_words:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    else:
                        errors.append(f"Row {row_num}: Duplicate word '{nepali_word}'")
                        continue
                
                word = Dictionary(
                    nepali=nepali_word,
                    romanized=row['romanized'].strip(),
                    english=row['english'].strip(),
                    part_of_speech=row.get('part_of_speech', '').strip() or None,
                    usage_example=row.get('usage_example', '').strip() or None,
                    nepali_example=row.get('nepali_example', '').strip() or None,
                    category=row.get('category', 'general').strip(),
                    difficulty=int(row.get('difficulty', 1)),
                    synonyms=row.get('synonyms', '').strip() or None,
                    antonyms=row.get('antonyms', '').strip() or None,
                )
                
                db.session.add(word)
                existing_words.add(nepali_word.lower())
                added += 1
                
                if added % 100 == 0:
                    db.session.commit()
                    
            except KeyError as e:
                errors.append(f"Row {row_num}: Missing required field {str(e)}")
            except ValueError as e:
                errors.append(f"Row {row_num}: Invalid value - {str(e)}")
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'added': added,
            'skipped': skipped,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@bp.route('/phrases', methods=['POST'])
def upload_phrases():
    """Upload phrases from CSV"""
    # Only admins can bulk upload
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files allowed'}), 400
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        added = 0
        errors = []
        skipped = 0
        
        existing_phrases = {(p.nepali.strip().lower(), p.english.strip().lower()) 
                           for p in Phrase.query.all()}
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                phrase_key = (row['nepali'].strip().lower(), row['english'].strip().lower())
                
                if phrase_key in existing_phrases:
                    skipped += 1
                    continue
                
                phrase = Phrase(
                    nepali=row['nepali'].strip(),
                    romanized=row['romanized'].strip(),
                    english=row['english'].strip(),
                    category=row.get('category', 'general').strip(),
                    difficulty=int(row.get('difficulty', 1)),
                    audio_url=row.get('audio_url', '').strip() or None
                )
                
                db.session.add(phrase)
                existing_phrases.add(phrase_key)
                added += 1
                
                if added % 100 == 0:
                    db.session.commit()
                    
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'added': added,
            'skipped': skipped,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@bp.route('/alphabet', methods=['POST'])
def upload_alphabet():
    """Upload alphabet letters from CSV"""
    # Only admins can bulk upload
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files allowed'}), 400
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        added = 0
        errors = []
        skipped = 0
        
        existing_letters = {letter.devanagari.strip() for letter in Alphabet.query.all()}
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                devanagari = row['devanagari'].strip()
                
                if devanagari in existing_letters:
                    skipped += 1
                    continue
                
                letter = Alphabet(
                    devanagari=devanagari,
                    romanized=row['romanized'].strip(),
                    sound=row['sound'].strip(),
                    type=row['type'].strip(),
                    pronunciation=row.get('pronunciation', '').strip() or None,
                    audio_url=row.get('audio_url', '').strip() or None,
                    order_index=int(row.get('order_index', 0)) if row.get('order_index') else None
                )
                
                db.session.add(letter)
                existing_letters.add(devanagari)
                added += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'added': added,
            'skipped': skipped,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@bp.route('/videos', methods=['POST'])
def upload_videos():
    """Upload YouTube videos from CSV"""
    # Only admins can bulk upload
    if not current_user.is_authenticated or not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files allowed'}), 400
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        added = 0
        errors = []
        skipped = 0
        
        existing_videos = {video.youtube_id.strip() for video in Video.query.all()}
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                youtube_id = row['youtube_id'].strip()
                
                if youtube_id in existing_videos:
                    skipped += 1
                    continue
                
                video = Video(
                    title=row['title'].strip(),
                    youtube_id=youtube_id,
                    description=row.get('description', '').strip() or None,
                    category=row.get('category', 'general').strip(),
                    difficulty=int(row.get('difficulty', 1)) if row.get('difficulty') else 1,
                    duration=int(row.get('duration', 0)) if row.get('duration') else None,
                    thumbnail_url=row.get('thumbnail_url', '').strip() or None,
                )
                
                db.session.add(video)
                existing_videos.add(youtube_id)
                added += 1
                
                if added % 50 == 0:
                    db.session.commit()
                    
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'added': added,
            'skipped': skipped,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

# ===== DOWNLOAD CSV TEMPLATES =====
@bp.route('/template/<resource_type>', methods=['GET'])
def download_template(resource_type):
    """Download CSV template for bulk upload"""
    templates = {
        'dictionary': 'nepali,romanized,english,part_of_speech,usage_example,nepali_example,category,difficulty,synonyms,antonyms\nनमस्ते,namaste,hello,interjection,Say namaste to greet someone,मलाई नमस्ते भन,greetings,1,,\nधन्यवाद,dhanyabad,thank you,interjection,Express gratitude,धन्यवाद भन्नुहोस्,greetings,1,,\n',
        'phrases': 'nepali,romanized,english,category,difficulty,audio_url\nधन्यवाद,dhanyabad,thank you,greetings,1,\nम भोकाएको छु,ma bhokaeko chu,I am hungry,food,1,\n',
        'alphabet': 'devanagari,romanized,sound,type,pronunciation,audio_url,order_index\nअ,a,a,vowel,like a in about,,1\nआ,aa,aa,vowel,like a in father,,2\n',
        'videos': 'title,youtube_id,description,category,difficulty,duration,thumbnail_url\nLearn Nepali Alphabet,dQw4w9WgXcQ,Introduction to Nepali letters,alphabet,1,300,\nNepali for Beginners,aBc123XyZ45,Basic phrases and words,beginner,1,600,\n'
    }
    
    if resource_type not in templates:
        return jsonify({'error': 'Invalid template type'}), 400
    
    return templates[resource_type], 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': f'attachment; filename={resource_type}_template.csv'
    }
