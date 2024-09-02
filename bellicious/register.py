from flask import Blueprint, render_template, make_response, flash, g, redirect, url_for, request, abort
from werkzeug.security import check_password_hash, generate_password_hash
from re import search
from .headers import render_with_headers
from .database import insert_user
bp = Blueprint('register', __name__)
@bp.errorhandler(500)
def internal_error(error):
      return render_template('500.html'), 500
@bp.errorhandler(403)
def access_denied(access_denied):
      return render_template('403.html'), 403

@bp.route('/register/', methods=['GET', 'POST'])
def register():
    #here I validate the form
    if request.method=='POST':
        username=request.form['username']
        pass1=request.form['password']
        pass2=request.form['password2']
        email=request.form['email']
        realname=request.form['realname']
        
        security=request.form['sec']
        errors = {} #we will save the errors on a dictionary with their asociated fields, this way it will be easier to create a more custom validation.
        usermatch=search("[a-zA-Z0-9]{3,50}$", username)
        passmatch=search("[A-Za-z0-9@#$%^&+=]{6,50}", pass1)
        emailmatch=search('([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email)
        if realname:
            abort(403) #if someone complete this field, it will probably be a bot
        if not usermatch:
            errors['username'] = "Invalid username"
        if not emailmatch:
            errors['email'] = "Invalid email"
        if not passmatch:
            errors['password'] = "Invalid password"
        if pass1!=pass2:
            errors['password2'] = "passwords not match"
        if not errors:
            try:
                insert_user(username, email, generate_password_hash(pass1), security)
                flash("Registration successful! Please wait now until the administrators validate your account. When it will be validated, you will be able to log in.", category="info")
            except Exception as e:
                flash(e, category="error")
        else:
            flash("some errors where detected. Please review them and try again.", category="error")
            return render_with_headers('register.html', allow_scripts=True, errors=errors)

    return render_with_headers('register.html', allow_scripts=True)