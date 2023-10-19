import functools

from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from floskl.db import get_req_cursor

from psycopg2.errors import UniqueViolation

bp = Blueprint('auth', __name__, url_prefix='/auth')


# Add views to the auth blueprint

@bp.route('/register', methods=('GET', 'POST'))
def register():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    cursor = get_req_cursor()
    error = None

    if not username:
      error = 'Username is required'
    elif not password:
      error = 'Password is required'

    if error is None:
      try:
        cursor.execute(
          "INSERT INTO users (username,password) VALUES(%s, %s)",
          (username, generate_password_hash(password)),
        )
        cursor.connection.commit()
      except UniqueViolation:
        error = f"User {username} is already registered."
      else:
        return redirect(url_for("auth.login"))

    flash(error) # . flash() stores messages that can be retrieved when rendering the template.

  return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
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
      session.clear()
      session['user_id'] = user['id']
      return redirect(url_for('index'))
    
    flash(error)
  
  return render_template('auth/login.html')


@bp.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))


# Make the session available to other views (when logged in)
@bp.before_app_request
def load_logged_in_user():
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


# A decorator for ensuring authenticated state for views that require it
def login_required(view):
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      return redirect(url_for('auth.login'))
    
    return view(**kwargs)
  
  return wrapped_view
