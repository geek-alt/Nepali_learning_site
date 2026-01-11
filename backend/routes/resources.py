from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Resource, PDFResource, Video, Playlist
from database import db
from werkzeug.utils import secure_filename
import os

bp = Blueprint('resources', __name__, url_prefix='/api/resources')

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif'}
UPLOAD_FOLDER = 'frontend/static/pdfs'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_admin(f):
    """Decorator to require admin or superadmin role"""
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ===== GENERIC RESOURCES (Guides, Tips, Worksheets) =====

@bp.route('/', methods=['GET', 'POST'])
def get_or_create_resources():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        resource_type = request.args.get('type', type=str)
        category = request.args.get('category', type=str)
        
        query = Resource.query
        
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        if category:
            query = query.filter_by(category=category)
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'resources': [{
                'id': r.id,
                'title': r.title,
                'description': r.description,
                'resource_type': r.resource_type,
                'category': r.category,
                'thumbnail_url': r.thumbnail_url,
                'difficulty': r.difficulty,
                'downloads': r.downloads
            } for r in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        new_resource = Resource(
            title=data.get('title'),
            description=data.get('description'),
            resource_type=data.get('resource_type'),
            category=data.get('category'),
            file_url=data.get('file_url'),
            thumbnail_url=data.get('thumbnail_url'),
            difficulty=data.get('difficulty'),
            created_by=data.get('created_by', 'admin')
        )
        db.session.add(new_resource)
        db.session.commit()
        return jsonify({'id': new_resource.id}), 201

@bp.route('/<int:resource_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': resource.id,
            'title': resource.title,
            'description': resource.description,
            'resource_type': resource.resource_type,
            'category': resource.category,
            'file_url': resource.file_url,
            'thumbnail_url': resource.thumbnail_url,
            'difficulty': resource.difficulty,
            'downloads': resource.downloads
        })
    
    elif request.method == 'PUT':
        # Only admins can update
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        resource.title = data.get('title', resource.title)
        resource.description = data.get('description', resource.description)
        resource.category = data.get('category', resource.category)
        resource.difficulty = data.get('difficulty', resource.difficulty)
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        # Only admins can delete
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        db.session.delete(resource)
        db.session.commit()
        return jsonify({'success': True}), 204

@bp.route('/categories', methods=['GET'])
def get_categories():
    categories = db.session.query(Resource.category).distinct().filter(
        Resource.category != None
    ).all()
    return jsonify([cat[0] for cat in categories if cat[0]])

# ===== PDF SPECIFIC RESOURCES =====

@bp.route('/pdf', methods=['GET', 'POST'])
@require_admin
def get_or_create_pdfs():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        category = request.args.get('category', type=str)
        difficulty = request.args.get('difficulty', type=int)
        
        query = PDFResource.query
        
        if category:
            query = query.filter_by(category=category)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        
        paginated = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'pdfs': [{
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'category': p.category,
                'preview_url': p.preview_url,
                'pages': p.pages,
                'file_size': p.file_size,
                'difficulty': p.difficulty,
                'downloads': p.downloads,
                'created_at': p.created_at.isoformat()
            } for p in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        new_pdf = PDFResource(
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category'),
            file_path=data.get('file_path'),
            preview_url=data.get('preview_url'),
            pages=data.get('pages'),
            file_size=data.get('file_size'),
            difficulty=data.get('difficulty'),
            tags=data.get('tags'),
            created_by=data.get('created_by', 'admin')
        )
        db.session.add(new_pdf)
        db.session.commit()
        return jsonify({'id': new_pdf.id}), 201

@bp.route('/pdf/<int:pdf_id>', methods=['GET', 'PUT', 'DELETE'])
@require_admin
def manage_pdf(pdf_id):
    pdf = PDFResource.query.get_or_404(pdf_id)
    
    if request.method == 'GET':
        # Increment download count for tracking
        return jsonify({
            'id': pdf.id,
            'title': pdf.title,
            'description': pdf.description,
            'category': pdf.category,
            'file_path': pdf.file_path,
            'preview_url': pdf.preview_url,
            'pages': pdf.pages,
            'file_size': pdf.file_size,
            'difficulty': pdf.difficulty,
            'downloads': pdf.downloads,
            'tags': pdf.tags
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        pdf.title = data.get('title', pdf.title)
        pdf.description = data.get('description', pdf.description)
        pdf.category = data.get('category', pdf.category)
        pdf.difficulty = data.get('difficulty', pdf.difficulty)
        pdf.tags = data.get('tags', pdf.tags)
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        db.session.delete(pdf)
        db.session.commit()
        return jsonify({'success': True}), 204

@bp.route('/pdf/<int:pdf_id>/download', methods=['GET'])
def download_pdf(pdf_id):
    """Track PDF download"""
    pdf = PDFResource.query.get_or_404(pdf_id)
    pdf.downloads += 1
    db.session.commit()
    return jsonify({
        'file_path': pdf.file_path,
        'title': pdf.title,
        'downloads': pdf.downloads
    })

@bp.route('/pdf/categories', methods=['GET'])
def get_pdf_categories():
    categories = db.session.query(PDFResource.category).distinct().filter(
        PDFResource.category != None
    ).all()
    return jsonify([cat[0] for cat in categories if cat[0]])

# ===== VIDEOS & PLAYLISTS =====

@bp.route('/playlists', methods=['GET', 'POST'])
def get_or_create_playlists():
    if request.method == 'GET':
        playlists = Playlist.query.order_by(Playlist.created_at.desc()).all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'category': p.category,
            'thumbnail_url': p.thumbnail_url,
            'video_count': p.video_count,
            'difficulty': p.difficulty
        } for p in playlists])
    
    elif request.method == 'POST':
        data = request.get_json()
        new_playlist = Playlist(
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            thumbnail_url=data.get('thumbnail_url'),
            difficulty=data.get('difficulty')
        )
        db.session.add(new_playlist)
        db.session.commit()
        return jsonify({'id': new_playlist.id}), 201

@bp.route('/videos', methods=['GET', 'POST'])
def get_or_create_videos():
    if request.method == 'GET':
        # Public access for viewing videos
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        category = request.args.get('category', type=str)
        playlist_id = request.args.get('playlist_id', type=int)
        
        query = Video.query
        
        if category:
            query = query.filter_by(category=category)
        if playlist_id:
            query = query.filter_by(playlist_id=playlist_id)
        
        paginated = query.order_by(Video.order_index).paginate(page=page, per_page=per_page)
        
        return jsonify({
            'videos': [{
                'id': v.id,
                'title': v.title,
                'youtube_id': v.youtube_id,
                'thumbnail_url': v.thumbnail_url,
                'duration': v.duration,
                'category': v.category,
                'difficulty': v.difficulty,
                'view_count': v.view_count
            } for v in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages
        })
    
    elif request.method == 'POST':
        # Only admins can create videos
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        new_video = Video(
            title=data.get('title'),
            description=data.get('description'),
            youtube_id=data.get('youtube_id'),
            duration=data.get('duration'),
            thumbnail_url=data.get('thumbnail_url'),
            category=data.get('category'),
            playlist_id=data.get('playlist_id'),
            difficulty=data.get('difficulty'),
            transcript=data.get('transcript'),
            notes=data.get('notes')
        )
        db.session.add(new_video)
        db.session.commit()
        return jsonify({'id': new_video.id}), 201

@bp.route('/videos/<int:video_id>', methods=['GET', 'PUT', 'DELETE'])
@require_admin
def manage_video(video_id):
    video = Video.query.get_or_404(video_id)
    
    if request.method == 'GET':
        video.view_count += 1
        db.session.commit()
        
        return jsonify({
            'id': video.id,
            'title': video.title,
            'description': video.description,
            'youtube_id': video.youtube_id,
            'thumbnail_url': video.thumbnail_url,
            'category': video.category,
            'difficulty': video.difficulty,
            'transcript': video.transcript,
            'notes': video.notes,
            'view_count': video.view_count
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        video.title = data.get('title', video.title)
        video.description = data.get('description', video.description)
        video.category = data.get('category', video.category)
        video.difficulty = data.get('difficulty', video.difficulty)
        video.transcript = data.get('transcript', video.transcript)
        video.notes = data.get('notes', video.notes)
        db.session.commit()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        db.session.delete(video)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Video deleted successfully'})

@bp.route('/videos/bulk-delete', methods=['POST'])
@require_admin
def bulk_delete_videos():
    """Delete multiple videos at once"""
    data = request.get_json()
    video_ids = data.get('ids', [])
    
    if not video_ids:
        return jsonify({'error': 'No video IDs provided'}), 400
    
    try:
        deleted_count = Video.query.filter(Video.id.in_(video_ids)).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({
            'success': True,
            'deleted': deleted_count,
            'message': f'{deleted_count} video(s) deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/videos/trending', methods=['GET'])
def get_trending_videos():
    trending = Video.query.order_by(Video.view_count.desc()).limit(10).all()
    return jsonify([{
        'id': v.id,
        'title': v.title,
        'youtube_id': v.youtube_id,
        'view_count': v.view_count
    } for v in trending])
