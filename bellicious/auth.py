from flask import Blueprint, request, session, redirect, url_for, flash, make_response, g
from werkzeug.security import check_password_hash
from .database import get_user_by_username_or_email
from .headers import render_with_headers
from functools import wraps
#here are the decorators, these allow to redirect a user to the login page if he wants to view a protected page. The other decorator will prevent non-admin user to view pages that require admin privileges.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to view this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['user_type'] == 1:
            return "not authorized"
        return f(*args, **kwargs)
    return decorated_function
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['user']
        password = request.form['password']
        remember = 'remember' in request.form
        user = get_user_by_username_or_email(username_or_email)
        #here we save the user in the session if the data is correct
        if user and check_password_hash(user['password'], password) and user['confirmed']==1:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_type'] = user['type']

            if remember:
                resp = make_response(redirect(request.args.get('next') or url_for('register.register')))
                resp.set_cookie('user_id', str(user['id']), max_age=30*24*60*60, httponly=True)  #here we save the cookie for 30 days
                resp.set_cookie('user_name', str(user['name']), max_age=30*24*60*60, httponly=True)
                resp.set_cookie('user_type', str(user['type']), max_age=30*24*60*60, httponly=True)
                return resp

            return redirect(request.args.get('next') or url_for('mainpage.index'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_with_headers('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('auth.login')))
    resp.delete_cookie('user_id')
    resp.delete_cookie('user_type')
    #resp.delete_cookie('user_name')
    return resp
#this function is to save the user in flask global object (g), this will allow me to write specific code in my jinja template if the user is logged or not
@auth.before_app_request
def load_logged_in_user():
    try:
        user_id = session.get('user_id')
        if user_id is None and request.cookies.get('user_id'):
            session['user_id'] = request.cookies.get('user_id')
            session['user_name'] = request.cookies.get('user_name')
            session['user_type'] = int(request.cookies.get('user_type'))

    
        g.user = None
        if 'user_id' in session:
            g.user = {
                'id': session['user_id'],
                'name': session['user_name'],
                'type': session['user_type']
            }

    except KeyError as e:
        print("KeyError:", e)
    except Exception as f:
        print("Exception:", f)