from flask import Blueprint, render_template, flash, redirect, url_for
from .database import get_top_10_bookmarks, get_top_10_tags
from .headers import render_with_headers

mainpage_bp = Blueprint('mainpage', __name__)

@mainpage_bp.route('/')
def index():
    try:
        bookmarks = get_top_10_bookmarks()
        tags = get_top_10_tags()
        return render_with_headers('index.html', bookmarks=bookmarks, tags=tags)
    except Exception as e:
        return 500

# redirections for favicons
@mainpage_bp.route('/favicon.png')
def favicon_png():
    return redirect(url_for('static', filename='img/favicon.png'))

@mainpage_bp.route('/favicon.ico')
def favicon_ico():
    return redirect(url_for('static', filename='img/favicon.ico'))

@mainpage_bp.route('/apple-touch-icon.png')
def apple_touch_icon():
    return redirect(url_for('static', filename='img/favicon.png'))

@mainpage_bp.route('/help')
def help_page():
    return render_with_headers('help.html')