from flask import Blueprint, render_template, redirect, url_for, flash, g
from .database import get_unconfirmed_users, delete_user, confirm_user, change_bookmark_privacy, get_bookmark_by_id
from .auth import login_required, admin_required
from .headers import render_with_headers
from flask_mail import Message
bp = Blueprint('admin', __name__)

@bp.route('/admin')
@login_required
@admin_required
def admin():
    try:
        users = get_unconfirmed_users()
        return render_with_headers('admin.html', users=users)
    except e:
        return e

@bp.route('/admin/delete/<int:user_id>')
@login_required
@admin_required
def delete(user_id):
    try:
        delete_user(user_id)
        flash('User deleted successfully.', 'success')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
    return redirect(url_for('admin.admin'))

@bp.route('/admin/confirm/<int:user_id>')
@login_required
@admin_required
def confirm(user_id):
    try:
        confirm_user(user_id)
        send_confirmation_email(user['email'], user['name'])
        flash('User confirmed successfully.', 'success')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
    return redirect(url_for('admin.admin'))

def send_confirmation_email(email, username):
    mail = Mail()
    msg = Message('Your account has been confirmed',
                  recipients=[email])
    msg.body = f"Hello {username},\n\nYour account has been successfully confirmed. You can now log in and use all the features of our service.\n\nBest regards,\nThe Bellicious Team"
    mail.send(msg)

@bp.route('/admin/mp/<int:bookmark_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def mp(bookmark_id):
    user_id = g.user['id']  # get the id of logged user

    try:
        
        bookmark = get_bookmark_by_id(bookmark_id)
        
        if not bookmark:
            flash("Bookmark not found", "error")
            return redirect(url_for('register.register'))

        # change bookmark privacy
        change_bookmark_privacy(bookmark_id)
        flash('Bookmark privacy changed successfully!', 'success')
    except Exception as e:
        flash(str(e), 'error')
    
    return redirect(url_for('register.register'))
