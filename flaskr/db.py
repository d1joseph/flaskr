# sqlite3 supported as a builtin of python. 
# sqlite3 is sequential in crud operations therefore we are limited in concurrency
# g is a unique object for each request. The connection is stored and reused for each unique request in g
# current_app points to the Flask app handling the request
# sqlite3.connect() establishes a db connection
# sqlite3.Row returns rows that behave like dicts
import sqlite3
import click

from flask import current_app, g
from flask.cli import with_appcontext


# get db and connect on request
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db


# close db connection
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# initialise db
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# confirm db initialised and echo to cmd
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database.')


# initialise app
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

