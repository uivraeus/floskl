""" Views for reading/posting blog entries
"""

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
    """Handle the main page"""
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
    """Handle creation of new blog posts"""
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

@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
@login_required
def update(post_id):
    """Update an existing blog post"""
    post = get_post(post_id)

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
                    (title, body, post_id)
            )
            cursor.connection.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:post_id>/delete', methods=('POST',))
@login_required
def delete(post_id):
    """Delete an existing blog post"""
    get_post(post_id)
    cursor = get_req_cursor()
    cursor.execute('DELETE FROM post WHERE id = %s', (post_id,))
    cursor.connection.commit()
    return redirect(url_for('blog.index'))


def get_post(post_id, check_author=True):
    """Common helper-function for getting a specific post from the database"""
    cursor = get_req_cursor()
    cursor.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN users u ON p.author_id = u.id'
        ' WHERE p.id = %s',
        (post_id,)
    )
    post = cursor.fetchone()

    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post
