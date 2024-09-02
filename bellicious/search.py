from flask import Blueprint, request, redirect, url_for, flash,  g
import requests
from .config import API_KEY
from .headers import render_with_headers
search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('search')
    prov = request.args.get('prov', 'bellicious')  # Default to 'bellicious' if not specified

    if prov == 'bellicious':
        return redirect(url_for('bookmark.bookmarks_by_tag', tag_name=query))
    elif prov == 'marginalia':
        if g.user is None:
            flash('You need to be logged in to access this feature.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        results = search_api(query)
        return render_with_headers('search_results.html', results=results)
    else:
        flash('Invalid provider selected.', 'error')
        return redirect(url_for('search.search'))

# Función de búsqueda mediante API
def search_api(query):
    api_url = f'https://api.marginalia.nu/{API_KEY}/search/{query.replace(" ", "+")}'
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        results = response.json().get('results', [])
    except requests.exceptions.RequestException as e:
        flash(f'Error calling API: {e}', 'error')
        results = []

    return results
