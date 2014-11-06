from flask.ext.security import login_required
from flask import Blueprint, render_template
from .tokengen import UUIDTokenGenerator as TokenGenerator
from . import db

ratings = Blueprint("ratings", __name__)


@ratings.route('/')
@login_required
def home():
    return render_template('index.html')


def user_registered_sighandler(app, user, confirm_token):
    '''
    Generate a token for the newly registered user.
    This signal handler is called every time a new user is registered.
    '''
    token = TokenGenerator()
    user.token = token.create()
    db.session.add(user)
    db.session.commit()
