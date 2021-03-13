# authorisation function for /auth view

import functools

from flask import (
    Blueprint, flask, g, redirect, render_template,
    request, session,
)

from werkzeug.security import check_password_hash, generate_password_hash
from flask.db import get_db

bp = Blueprint(
    'auth',
    __name__,
    url_prefix='/auth'
)    