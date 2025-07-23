#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
from datetime import datetime
from config import Config
from readwise_client import ReadwiseClient
from document_manager import DocumentManager
from tag_manager import TagManager

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global manager instances
doc_manager = None
tag_manager = None
client = None

def init_managers():
    """Initialize manager instances"""
    global doc_manager, tag_manager, client
    try:
        config = Config()
        client = ReadwiseClient(config)
        doc_manager = DocumentManager(client)
        tag_manager = TagManager(client)
        return True
    except Exception as e:
        print(f"Initialization failed: {e}")
        return False

@app.route('/')
def index():
    """Home page"""
    if not init_managers():
        return render_template('setup.html')
    
    try:
        # Get statistics
        stats = doc_manager.get_stats()
        recent_docs = doc_manager.get_documents(limit=10)
        
        return render_template('index.html', 
                             stats=stats, 
                             recent_docs=recent_docs)
    except Exception as e:
        flash(f'Failed to get data: {e}', 'error')
        return render_template('index.html', stats={}, recent_docs=[])

@app.route('/documents')
def documents():
    """Document list page"""
    if not doc_manager:
        return redirect(url_for('index'))
    
    location = request.args.get('location')
    category = request.args.get('category')
    search = request.args.get('search')
    
    try:
        if search:
            docs = doc_manager.search_documents(search, location)
        else:
            docs = doc_manager.get_documents(location=location, category=category, limit=50)
        
        return render_template('documents.html', 
                             documents=docs, 
                             current_location=location,
                             current_category=category,
                             search_term=search)
    except Exception as e:
        flash(f'Failed to get documents: {e}', 'error')
        return render_template('documents.html', documents=[])

@app.route('/add_document', methods=['GET', 'POST'])
def add_document():
    """Add document page"""
    if not doc_manager:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            url = request.form['url']
            title = request.form.get('title')
            tags_str = request.form.get('tags', '')
            location = request.form.get('location', 'new')
            
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            
            result = doc_manager.add_article(
                url=url,
                title=title,
                tags=tags if tags else None,
                location=location
            )
            
            flash('Document added successfully!', 'success')
            return redirect(url_for('documents'))
            
        except Exception as e:
            flash(f'Failed to add document: {e}', 'error')
    
    return render_template('add_document.html')

@app.route('/document/<document_id>')
def document_detail(document_id):
    """Document detail page"""
    if not doc_manager:
        return redirect(url_for('index'))
    
    try:
        document = doc_manager.get_document_by_id(document_id)
        if not document:
            flash('Document not found', 'error')
            return redirect(url_for('documents'))
        
        return render_template('document_detail.html', document=document)
    except Exception as e:
        flash(f'Failed to get document details: {e}', 'error')
        return redirect(url_for('documents'))

@app.route('/update_document/<document_id>', methods=['POST'])
def update_document(document_id):
    """Update document"""
    if not doc_manager:
        return jsonify({'success': False, 'error': 'Manager not initialized'})
    
    try:
        action = request.json.get('action')
        
        if action == 'move':
            location = request.json.get('location')
            doc_manager.move_document(document_id, location)
            return jsonify({'success': True, 'message': f'Document moved to {location}'})
        
        elif action == 'update_metadata':
            title = request.json.get('title')
            author = request.json.get('author')
            summary = request.json.get('summary')
            
            doc_manager.update_document_metadata(
                document_id=document_id,
                title=title,
                author=author,
                summary=summary
            )
            return jsonify({'success': True, 'message': 'Document updated'})
        
        else:
            return jsonify({'success': False, 'error': 'Invalid operation'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete_document/<document_id>', methods=['POST'])
def delete_document(document_id):
    """Delete document"""
    if not doc_manager:
        return jsonify({'success': False, 'error': 'Manager not initialized'})
    
    try:
        success = doc_manager.delete_document(document_id)
        if success:
            return jsonify({'success': True, 'message': 'Document deleted'})
        else:
            return jsonify({'success': False, 'error': 'Delete failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/tags')
def tags():
    """Tags page"""
    if not tag_manager:
        return redirect(url_for('index'))
    
    search = request.args.get('search')
    
    try:
        if search:
            tags_list = tag_manager.search_tags(search)
        else:
            tags_list = tag_manager.list_tags()
        
        # Get usage statistics
        usage_stats = tag_manager.get_tag_usage_stats()
        
        # Add usage count for each tag
        for tag in tags_list:
            tag['usage_count'] = usage_stats.get(tag.get('key', ''), 0)
        
        return render_template('tags.html', 
                             tags=tags_list, 
                             search_term=search)
    except Exception as e:
        flash(f'Failed to get tags: {e}', 'error')
        return render_template('tags.html', tags=[])

@app.route('/tag/<tag_key>')
def tag_detail(tag_key):
    """Tag detail page"""
    if not tag_manager:
        return redirect(url_for('index'))
    
    try:
        documents = tag_manager.get_documents_by_tag(tag_key)
        
        # Get tag information
        all_tags = tag_manager.get_all_tags()
        tag_info = next((tag for tag in all_tags if tag.get('key') == tag_key), 
                       {'key': tag_key, 'name': tag_key})
        
        return render_template('tag_detail.html', 
                             tag=tag_info, 
                             documents=documents)
    except Exception as e:
        flash(f'Failed to get tag details: {e}', 'error')
        return redirect(url_for('tags'))

@app.route('/stats')
def stats():
    """Statistics page"""
    if not doc_manager or not tag_manager:
        return redirect(url_for('index'))
    
    try:
        doc_stats = doc_manager.get_stats()
        popular_tags = tag_manager.get_popular_tags(10)
        
        return render_template('stats.html', 
                             doc_stats=doc_stats, 
                             popular_tags=popular_tags)
    except Exception as e:
        flash(f'Failed to get statistics: {e}', 'error')
        return render_template('stats.html', doc_stats={}, popular_tags=[])

@app.route('/export')
def export():
    """Export page"""
    if not doc_manager:
        return redirect(url_for('index'))
    
    location = request.args.get('location')
    
    try:
        filename = doc_manager.export_documents(location=location)
        flash(f'Documents exported to: {filename}', 'success')
    except Exception as e:
        flash(f'Export failed: {e}', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/verify', methods=['POST'])
def api_verify():
    """API verification endpoint"""
    try:
        if client and client.verify_token():
            return jsonify({'success': True, 'message': 'API connection OK'})
        else:
            return jsonify({'success': False, 'error': 'API connection failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Template filters
@app.template_filter('datetime')
def datetime_filter(value):
    """Format datetime"""
    if not value:
        return 'N/A'
    try:
        # Try to parse ISO format
        if isinstance(value, str):
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            dt = value
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return value

@app.template_filter('truncate_title')
def truncate_title(title, length=50):
    """Truncate title"""
    if not title:
        return 'N/A'
    return title[:length] + '...' if len(title) > length else title

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', 
                         error_code=404, 
                         error_message='Page not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', 
                         error_code=500, 
                         error_message='Internal server error'), 500

if __name__ == '__main__':
    # Check if templates directory exists
    if not os.path.exists('templates'):
        print("Warning: templates directory not found, please ensure necessary HTML templates are created")
    
    print("Starting Readwise Reader Management Tool...")
    print("Visit http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 