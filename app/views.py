from flask import Blueprint, render_template
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask.ext.security import roles_required
from flask.ext.security import roles_accepted
from .tokengen import UUIDTokenGenerator as TokenGenerator
from .forms import AddGameServerForm
from .models import GoServer, Game, User
from . import db, user_datastore

ratings = Blueprint("ratings", __name__)


@ratings.route('/')
@login_required
def home():
    return render_template('index.html')


@ratings.route('/ViewProfile')
@login_required
def viewprofile():
    if current_user.is_ratings_admin():
        games = Game.query.limit(30).all()
    else: 
        games = Game.query.filter(Game.white_id == current_user.id).all()
        games.extend(Game.query.filter(Game.black_id == current_user.id).all())
    return render_template('profile.html', user=current_user, games=games)

@ratings.route('/LatestGames')
@login_required
def latestgames():
    if current_user.is_server_admin():
        games = Game.query.filter(Game.server_id == current_user.server_id).all()
    if current_user.is_ratings_admin():
        games = Game.query.limit(30).all()
    else: 
        games = Game.query.filter(Game.white_id == current_user.id).all()
        games.extend(Game.query.filter(Game.black_id == current_user.id).all())
    return render_template('latestgames.html', user=current_user, games=games)

@ratings.route('/Servers')
@login_required
@roles_required('ratings_admin')
def servers():
    if current_user.is_server_admin():
        #TODO: fetch games for admins' server.
        games = Game.query.filter(Game.server_id == current_user.server_id).all()
    if current_user.is_ratings_admin():
        games = Game.query.limit(30).all()
    else: 
        games = Game.query.filter(Game.white_id == current_user.id).all()
        games.extend(Game.query.filter(Game.black_id == current_user.id).all())
    return render_template('server.html', user=current_user, games=games)


@ratings.route('/Users')
@login_required
@roles_required('ratings_admin')
def users():
    users = User.query.limit(30).all()
    return render_template('users.html', user=current_user, users=users)

@ratings.route('/Players')
@login_required
@roles_accepted('ratings_admin', 'server_admin')
def players():
     #TODO: make this use bootstrap-table and load from /api/player_info
    if current_user.is_server_admin():
        #TODO: make /api/player_info fetch players for admins' server.
        users = [foo]
    if current_user.is_ratings_admin():
        users = User.query.limit(30).all()
    return render_template('users.html', user=current_user, users=users)



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
