""" Views for authentication and user registration operations
"""

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from psycopg2.errors import UniqueViolation  # pylint: disable=no-name-in-module

from floskl.db import get_req_cursor

bp = Blueprint('auth', __name__, url_prefix='/auth')


# Add views to the auth blueprint

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = get_req_cursor()
        error = None
        user = None  # Will be known after successful INSERT

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'

        if error is None:
            try:
                cursor.execute(
                    "INSERT INTO users (username,password) VALUES(%s, %s) RETURNING id",
                    (username, generate_password_hash(password)),
                )
                cursor.connection.commit()
                user = cursor.fetchone()
            except UniqueViolation:
                error = f"User {username} is already registered."
            else:
                set_login_session(user['id'])
                return redirect(url_for("index"))

        flash(error)  # flash() stores messages that can be retrieved when rendering the template.

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = get_req_cursor()
        error = None
        cursor.execute(
            'SELECT * FROM users WHERE username = %s', (username,)
        )
        user = cursor.fetchone()

        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            set_login_session(user['id'])
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


def set_login_session(user_id):
    """Set/switch logged in user"""
    session.clear()
    session['user_id'] = user_id


@bp.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    """Make the session available to other views (when logged in)"""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        cursor = get_req_cursor()
        cursor.execute(
            'SELECT * FROM users WHERE id = %s', (user_id,)
        )
        g.user = cursor.fetchone()

        if g.user is None:
            print(f"WARNING: DB inconsistency, user {user_id} not found")


def login_required(view):
    """A decorator for ensuring authenticated state for views that require it"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
