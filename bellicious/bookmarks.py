from flask import Blueprint, render_template, request, redirect, url_for, flash, g, make_response
from .database import (update_bookmark, get_user_bookmarks, get_user_by_username_or_email,
                      get_public_bookmarks_by_tag, get_liked_bookmarks, 
                      like_bookmark, delete_bookmark, get_top_10_bookmarks,
                      add_bookmark, import_bookmarks_html, import_bookmarks_xml, get_tags_by_bookmark_id,
                      export_bookmarks_html, export_bookmarks_xml, get_bookmark_by_id)
from .headers import render_with_headers
import datetime
import urllib.parse
from .auth import login_required, admin_required
bookmark_bp = Blueprint('bookmark', __name__)
current_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M") #define the current date for future usage in atom feeds

@bookmark_bp.route('/user/<username>')
def user_bookmarks(username):
    # get user information from username or email
    user = get_user_by_username_or_email(username)
    if not user:
        # if user don't exist
        return "User not found", 404
    
    user_id = user['id']
    
    if not g.user:
        bookmarks = get_user_bookmarks(user_id)
    else:
        bookmarks = get_user_bookmarks(user_id, g.user['id'])
    
    return render_with_headers('user_bookmarks.html', bookmarks=bookmarks, user_id=user_id)

@bookmark_bp.route('/tag/<tag_name>')
def bookmarks_by_tag(tag_name):
    bookmarks = get_public_bookmarks_by_tag(tag_name)
    return render_with_headers('bookmarks_by_tag.html', bookmarks=bookmarks, tag_name=tag_name)

# Other routes

@bookmark_bp.route('/bookmark/like/<int:bookmark_id>')
@login_required
def like(bookmark_id):
    user_id = g.user['id']
    try:
        like_bookmark(user_id, bookmark_id)
        flash('Bookmark liked successfully!', 'success')
    except ValueError as e:
        flash("bookmark already liked", 'error')
    return redirect(request.referrer)

#function to edit the bookmark
@bookmark_bp.route('/bookmark/edit/<int:bookmark_id>', methods=['GET', 'POST'])
@login_required
def edit_bookmark(bookmark_id):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        annotation = request.form['annotation']
        bookmark_type = request.form['type']
        tags = request.form['tags']  # New line to get the tags from the form
        user_id = g.user['id']
        try:
            update_bookmark(bookmark_id, title, description, annotation, bookmark_type, user_id, tags)
            flash('Bookmark updated successfully!', 'success')
            return redirect(url_for('register.register'))
        except Exception as e:
            flash("Error while updating", 'error')
    
    bookmark = get_bookmark_by_id(bookmark_id)
    if bookmark:
        # Fetch tags associated with the bookmark
        tags = get_tags_by_bookmark_id(bookmark_id)
        bookmark['tags'] = tags
        return render_with_headers('edit_bookmark.html', bookmark=bookmark, bookmark_id=bookmark_id)
    else:
        flash('Bookmark not found', 'error')
        return redirect(url_for('register.register'))


@bookmark_bp.route('/bookmark/delete/<int:bookmark_id>', methods=['GET', 'POST'])
@login_required
def delete(bookmark_id):
    user_id = g.user['id']
    try:
        delete_bookmark(bookmark_id, user_id)
        flash('Bookmark deleted successfully!', 'success')
    except ValueError as e:
        flash("bookmark already deleted", 'error')
    return redirect(url_for('register.register'))

@bookmark_bp.route('/feed.atom')
def atom_feed():
    bookmarks = get_top_10_bookmarks()
    feed = render_template('atom_feed.xml', bookmarks=bookmarks, current_date=current_date)
    response = make_response(feed)
    response.headers['Content-Type'] = 'application/xml'
    return response

@bookmark_bp.route('/user/<user_name>/feed.atom')
def user_bookmarks_atom(user_name):
    user = get_user_by_username_or_email(user_name)
    if not user:
        # if user don't exist
        return "User not found", 404
    
    user_id = user['id']
    bookmarks = get_user_bookmarks(user_id)
    feed = render_template('atom_feed.xml', bookmarks=bookmarks, current_date=current_date)
    response = make_response(feed)
    response.headers['Content-Type'] = 'application/xml'
    return response

@bookmark_bp.route('/tag/<tag_name>/feed.atom')
def bookmarks_by_tag_atom(tag_name):
    bookmarks = get_public_bookmarks_by_tag(tag_name)
    feed = render_template('atom_feed.xml', bookmarks=bookmarks, current_date=current_date)
    response = make_response(feed)
    response.headers['Content-Type'] = 'application/xml'
    return response

@bookmark_bp.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    if request.method == 'POST':
        url = request.form['url']
        title = request.form['title']
        description = request.form['description']
        annotation = request.form['annotation']
        tags = request.form['tags']
        type = int(request.form.get('type', 0))  # Default to private if not specified
        user_id = g.user['id']
        try:
            add_bookmark(url, title, annotation, description, user_id, tags, type)
            flash('Bookmark added successfully!', 'success')
            return redirect(url_for('bookmark.user_bookmarks', username=g.user['name']))
        except Exception as e:
            flash("Error while adding bookmark", 'error')
            return redirect(url_for('mainpage.index'))
    
    # For GET requests, render the form with any provided URL and title
    url = request.args.get('url', '')
    title = request.args.get('title', '')
    return render_with_headers('post.html', url=url, title=title)


@bookmark_bp.route('/export/html', methods=['GET'])
@login_required
def export_html():
    user_id = g.user['id']
    bookmarks_html = export_bookmarks_html(user_id)
    return Response(bookmarks_html, mimetype='text/html', headers={'Content-Disposition': 'attachment;filename=bookmarks.html'})

@bookmark_bp.route('/export/xml', methods=['GET'])
@login_required
def export_xml():
    user_id = g.user['id']
    bookmarks_xml = export_bookmarks_xml(user_id)
    return Response(bookmarks_xml, mimetype='application/xml', headers={'Content-Disposition': 'attachment;filename=bookmarks.xml'})

@bookmark_bp.route('/import/html', methods=['GET', 'POST'])
@login_required
def import_html():
    if 'file' not in request.files:
        flash('No file part')
        return render_with_headers("import_html.html")
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return render_with_headers("import_html.html")
    if file and file.filename.endswith('.html'):
        user_id = g.user['id']
        import_bookmarks_html(file.read().decode('utf-8'), user_id)
        flash('Bookmarks imported successfully')
        return render_with_headers("import_html.html")
    flash('Invalid file format')
    return render_with_headers("import_html.html")

@bookmark_bp.route('/import/xml', methods=['GET', 'POST'])
@login_required
def import_xml():
    if 'file' not in request.files:
        flash('No file part')
        return render_with_headers("import_xml.html")
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return render_with_headers("import_xml.html")
    if file and file.filename.endswith('.xml'):
        user_id = g.user['id']
        import_bookmarks_xml(file.read().decode('utf-8'), user_id)
        flash('Bookmarks imported successfully')
        return render_with_headers("import_xml.html")
    flash('Invalid file format')
    return render_with_headers("import_xml.html")

@bookmark_bp.route('/liked')
@login_required
def show_liked_bookmarks():
    try:
        user_id = g.user['id']
        liked_bookmarks = get_liked_bookmarks(user_id)
        return render_with_headers('liked_bookmarks.html', bookmarks=liked_bookmarks)
    except Exception as e:
        flash('An error occurred while fetching liked bookmarks.', 'error')
        return redirect(url_for('mainpage.index'))