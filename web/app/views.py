import itertools

from sqlalchemy import or_
from flask import Blueprint, render_template, request, current_app
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask.ext.security import roles_required
from .tokengen import generate_token
from .forms import AddGameServerForm, SearchPlayerForm
from .models import GoServer, Game, User, Player, SERVER_ADMIN_ROLE, RATINGS_ADMIN_ROLE
from . import db, user_datastore
import logging

ratings = Blueprint("ratings", __name__)

@ratings.route('/')
def home():
    return render_template('index.html')

@ratings.route('/ViewProfile')
@login_required
def viewprofile():
    if current_user.is_ratings_admin():
        games = Game.query.limit(30).all()
        players = None
    else:
        players = Player.query.filter(Player.user_id == current_user.id).all()
        games = itertools.chain(*(Game.query.filter(or_(Game.white_id == player.id, Game.black_id == player.id)) for player in players))
    return render_template('profile.html', user=current_user, games=games, players=players)

@ratings.route('/Games', methods=['GET'])
def listgames():
    limit = 30
    player_games = []
    games = []

    if request.args:
        aga_id = request.args.get('aga_id')
        player_id = request.args.get('player_id')
        sid = request.args.get('server_id')
        limit = request.args.get('limit')

        if aga_id:
            user = User.query.filter(User.aga_id == aga_id).first()
            player_list = Player.query.filter(Player.user_id == user.id)
            if user and player_list:
                for p in player_list:
                    game_filter = ((Game.white_id==p.id) | (Game.black_id==p.id))
                    if sid:
                        game_filter = game_filter & (Game.server_id==sid)
                    player_games.append(Game.query.filter(game_filter))
        elif player_id:
            player_games.append(Game.query.filter((Game.white_id==player_id) | (Game.black_id==player_id)))
        elif sid:
            player_games.append(Game.query.filter(Game.server_id==sid))
        else:
            games = Game.query.limit(limit)
    else:
        games = Game.query.limit(limit)

    for p in player_games:
        games.extend(p.all())

    return render_template('latestgames.html', user=current_user, games=games)


@ratings.route('/GameDetail/<game_id>')
def gamedetail(game_id):
    game = Game.query.get(game_id)
    return render_template('gamedetail.html', user=current_user, game=game)


@ratings.route('/GoServers')
def servers():
    servers = GoServer.query.limit(30).all()
    return render_template('servers.html', user=current_user, servers=servers)

@ratings.route('/GoServer/<server_id>')
def server(server_id):
    server = GoServer.query.get(server_id)
    players = Player.query.filter(Player.server_id == server_id).limit(30).all()
    logging.info("Found server %s" % server)
    return render_template('server.html', user=current_user, server=server, players=players)

@ratings.route('/GoServer/<server_id>/reset_token', methods=['POST'])
@login_required
@roles_required(SERVER_ADMIN_ROLE.name)
def reset_server_token(server_id):
    server = GoServer.query.get(server_id)
    if not current_user.can_reset_server_token(server):
        return current_app.login_manager.unauthorized()
    server.token = generate_token()
    db.session.add(server)
    db.session.commit()
    logging.info("Reset server token for {}".format(server_id))
    return "Success"

@ratings.route('/Users')
@login_required
@roles_required(RATINGS_ADMIN_ROLE.name)
def users():
    users = User.query.limit(30).all()
    return render_template('users.html', user=current_user, users=users)

@ratings.route('/Players', methods=['GET', 'POST'])
def players():
    form = SearchPlayerForm()
    player_query = Player.query

    if form.validate_on_submit():
        if form.player_name.data:
            player_query = player_query.filter(Player.name.contains(form.player_name.data))
        if form.aga_id.data:
            player_query = player_query.join(User).filter(User.aga_id == form.aga_id.data)

    players = player_query.limit(30).all()

    return render_template('players.html', user=current_user, players=players, form=form)

@ratings.route('/Players/<player_id>')
def player(player_id):
    player = Player.query.get(player_id)
    games = []
    for p in player.user.players:
        games.extend(Game.query.filter(Game.white_id == p.id).all())
        games.extend(Game.query.filter(Game.black_id == p.id).all())
    return render_template('player.html', user=current_user, player=player, games=games)

@ratings.route('/Players/<player_id>/reset_token', methods=['POST'])
@login_required
def reset_player_token(player_id):
    player = Player.query.get(player_id)
    if not current_user.can_reset_player_token(player):
        return current_app.login_manager.unauthorized()
    player.token = generate_token()
    db.session.add(player)
    db.session.commit()
    logging.info("Reset player token for {}".format(player_id))
    return "Success"

@ratings.route('/AddGameServer', methods=['GET', 'POST'])
@login_required
@roles_required(RATINGS_ADMIN_ROLE.name)
def addgameserver():
    form = AddGameServerForm()
    gs = GoServer()
    if form.validate_on_submit():
        gs.name = form.gs_name.data
        gs.url = form.gs_url.data
        gs.token = generate_token()
        db.session.add(gs)
        db.session.commit()
        return server(gs.id)
    return render_template('gameserver.html', form=form, gs=gs)

def user_registered_sighandler(app, user, confirm_token):
    '''
    Generate a token for the newly registered user.
    This signal handler is called every time a new user is registered.
    '''
    user.token = generate_token()
    default_role = user_datastore.find_role('user')
    user_datastore.add_role_to_user(user, default_role)
    db.session.add(user)
    db.session.commit()
