from flask import Blueprint, render_template
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask.ext.security import roles_required
from .tokengen import UUIDTokenGenerator as TokenGenerator
from .forms import AddGameServerForm
from .models import GoServer, Game
from . import db, user_datastore

ratings = Blueprint("ratings", __name__)


@ratings.route('/')
@login_required
def home():
    return render_template('index.html')


@ratings.route('/ViewProfile')
@login_required
def viewprofile():
    if current_user.is_server_admin():
        games = ['woot']
    if current_user.is_ratings_admin():
        games = Game.query.limit(30).all()
    else: 
        games = Game.query.filter(Game.white_id == current_user.id).all()
        games.extend(Game.query.filter(Game.black_id == current_user.id).all())
    return render_template('profile.html', user=current_user, games=games)


@ratings.route('/AddGameServer', methods=['GET', 'POST'])
@login_required
@roles_required('ratings_admin')
def addgameserver():
    form = AddGameServerForm()
    gs = GoServer()
    if form.validate_on_submit():
        token = TokenGenerator()
        gs.name = form.gs_name.data
        gs.url = form.gs_url.data
        gs.token = token.create()
        db.session.add(gs)
        db.session.commit()
    return render_template('gameserver.html', form=form, gs=gs)


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
