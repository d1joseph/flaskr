# authorisation module for auth view utilizing blueprints
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template,
    request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db


# initialise blueprint for auth view
bp = Blueprint(
    'auth',
    __name__,
    url_prefix='/auth'
)


# register a new user 
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # form validation and existing record query
        if not username:
            error = 'Username is required.'
        
        elif not password:
            error = 'Password is required.'
        
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', 
            (username,)
        ).fetchone() is not None:
            error = '{} is already registered.'.format(username)

        # if new user update the db, hash the password and create record
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()

            # redirect the user to login once registered
            return redirect(url_for('auth.login'))
        
        flash(error)
    
    return render_template('auth/register.html')


# user login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'

        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# load stored session data before any request - cookies
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# log the user out and end session
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# require login for any user CRUD operations
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view

