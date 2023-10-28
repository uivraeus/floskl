from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from floskl.auth import login_required
from floskl.db import get_req_cursor

bp = Blueprint('blog', __name__)

# Add views to blog blueprint

@bp.route('/')
def index():
  cursor = get_req_cursor()
  cursor.execute(
    'SELECT p.id, title, body, created, author_id, username'
    ' FROM post p JOIN users u ON p.author_id = u.id'
    ' ORDER BY created DESC'
  )
  posts = cursor.fetchall()
  return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']
    error = None

    if not title:
      error = 'Title is required.'

    if error is not None:
      flash(error)
    else:
      cursor = get_req_cursor()
      cursor.execute(
          'INSERT INTO post (title, body, author_id)'
          ' VALUES (%s, %s, %s)',
          (title, body, g.user['id'])
      )
      cursor.connection.commit()
      return redirect(url_for('blog.index'))

  return render_template('blog/create.html')

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
  post = get_post(id)

  if request.method == 'POST':
    title = request.form['title']
    body = request.form['body']
    error = None

    if not title:
      error = 'Title is required.'

    if error is not None:
      flash(error)
    else:
      cursor = get_req_cursor()
      cursor.execute(
          'UPDATE post SET title = %s, body = %s'
          ' WHERE id = %s',
          (title, body, id)
      )
      cursor.connection.commit()
      return redirect(url_for('blog.index'))

  return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
  get_post(id)
  cursor = get_req_cursor()
  cursor.execute('DELETE FROM post WHERE id = %s', (id,))
  cursor.connection.commit()
  return redirect(url_for('blog.index'))


# Common helper-function
def get_post(id, check_author=True):
  cursor = get_req_cursor()
  cursor.execute(
    'SELECT p.id, title, body, created, author_id, username'
    ' FROM post p JOIN users u ON p.author_id = u.id'
    ' WHERE p.id = %s',
    (id,)
  )
  post = cursor.fetchone()
  
  if post is None:
    abort(404, f"Post id {id} doesn't exist.")

  if check_author and post['author_id'] != g.user['id']:
    abort(403)

  return post
