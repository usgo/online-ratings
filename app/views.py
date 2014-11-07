from flask import Blueprint, render_template
from flask.ext.login import current_user
from flask.ext.security import login_required
from .tokengen import UUIDTokenGenerator as TokenGenerator
from . import db, user_datastore

ratings = Blueprint("ratings", __name__)


@ratings.route('/')
@login_required
def home():
    return render_template('index.html')


@ratings.route('/ViewProfile')
@login_required
def viewprofile():
    return render_template('profile.html', user=current_user)


def user_registered_sighandler(app, user, confirm_token):
    '''
    Generate a token for the newly registered user.
    This signal handler is called every time a new user is registered.
    '''
    token = TokenGenerator()
    user.token = token.create()
    default_role = user_datastore.find_role('user')
    user_datastore.add_role_to_user(user, default_role)
    db.session.add(user)
    db.session.commit()
