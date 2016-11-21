import itertools

from sqlalchemy import or_
from flask import Blueprint, render_template, request, current_app, redirect, url_for
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask.ext.security import roles_required
from .tokengen import generate_token
from .forms import AddGameServerForm, SearchPlayerForm, AddPlayerForm
from .models import GoServer, Game, User, Player, SERVER_ADMIN_ROLE, RATINGS_ADMIN_ROLE
from . import db, user_datastore

ratings = Blueprint("ratings", __name__)

@ratings.route('/')
def home():
    return render_template('index.html')

@ratings.route('/help')
def help():
    return render_template('help.html')

@ratings.route('/profile')
@login_required
def profile():
    form = AddPlayerForm()
    form.server.choices = [(server.id, server.name) for server in GoServer.query.all()]
    players = Player.query.filter(Player.user_id == current_user.id).order_by(Player.name.asc()).all()
    if current_user.is_ratings_admin():
        games = Game.query.limit(30).all()
    else:
        games = itertools.chain(*(Game.query.filter(or_(Game.white_id == player.id, Game.black_id == player.id)) for player in players))
    return render_template('profile.html', user=current_user, games=games, players=players, form=form)

@ratings.route('/games', methods=['GET'])
def listgames():
    limit = request.args.get('limit', 30)
    aga_id = request.args.get('aga_id')
    player_id = request.args.get('player_id')
    sid = request.args.get('server_id')

    players = []
    games = []

    if aga_id:
        user_ids = [tup[0] for tup in User.query.filter(User.aga_id == aga_id).with_entities(User.id).all()]
        players = Player.query.filter(Player.user_id.in_(user_ids)).all()
    elif player_id:
        players = Player.query.filter(Player.id == player_id).all()

    if players:
        for p in players:
            game_filter = ((Game.white_id==p.id) | (Game.black_id==p.id))
            if sid:
                game_filter = game_filter & (Game.server_id==sid)
            games.extend(Game.query.filter(game_filter).all())
    else:
        query = Game.query.order_by(Game.date_reported.desc()).limit(limit)
        if sid:
            query = query.filter(Game.server_id == sid)
        games = query.all()

    return render_template('latestgames.html', user=current_user, games=games)


@ratings.route('/games/<game_id>')
def gamedetail(game_id):
    game = Game.query.get_or_404(game_id)
    return render_template('gamedetail.html', user=current_user, game=game)


@ratings.route('/game_servers', methods=['GET'])
def servers():
    servers = GoServer.query.limit(30).all()
    return render_template('servers.html', user=current_user, servers=servers)

@ratings.route('/game_servers/<server_id>', methods=['GET'])
def server(server_id):
    server = GoServer.query.get_or_404(server_id)
    players = Player.query.filter(Player.server_id == server_id).limit(30).all()
    return render_template('server.html', user=current_user, server=server, players=players)

@ratings.route('/game_servers/<server_id>/reset_token', methods=['POST'])
@login_required
@roles_required(SERVER_ADMIN_ROLE.name)
def reset_server_token(server_id):
    server = GoServer.query.get_or_404(server_id)
    if not current_user.can_reset_server_token(server):
        return current_app.login_manager.unauthorized()
    server.token = generate_token()
    db.session.add(server)
    db.session.commit()
    current_app.logger.info("Reset server token for {}".format(server_id))
    return "Success"

@ratings.route('/users')
@login_required
@roles_required(RATINGS_ADMIN_ROLE.name)
def users():
    users = User.query.limit(30).all()
    return render_template('users.html', user=current_user, users=users)

@ratings.route('/players', methods=['POST'])
@login_required
def create_player():
    form = AddPlayerForm()
    form.server.choices = [(server.id, server.name) for server in GoServer.query.all()]
    if form.validate_on_submit():
        server_id = form.server.data
        name = form.name.data
        db.session.add(Player(name=name, server_id=server_id, user_id=current_user.id, token=generate_token()))
        db.session.commit()

    return redirect(url_for('ratings.profile'))


@ratings.route('/players/search', methods=['GET', 'POST'])
def players():
    form = SearchPlayerForm()
    player_query = Player.query

    if form.validate_on_submit():
        if form.player_name.data:
            player_query = player_query.filter(Player.name.contains(form.player_name.data))
        if form.aga_id.data:
            player_query = player_query.join(User).filter(User.aga_id == form.aga_id.data)

    players = player_query.limit(30).all()

    return render_template('players.html', players=players, form=form)

@ratings.route('/players/<player_id>')
def player(player_id):
    player = Player.query.get_or_404(player_id)
    games = Game.query.filter(or_(Game.white_id == player_id, Game.black_id == player_id)).all()
    return render_template('player.html', user=current_user, player=player, games=games)

@ratings.route('/players/<player_id>/reset_token', methods=['POST'])
@login_required
def reset_player_token(player_id):
    player = Player.query.get_or_404(player_id)
    if not current_user.can_reset_player_token(player):
        return current_app.login_manager.unauthorized()
    player.token = generate_token()
    db.session.add(player)
    db.session.commit()
    current_app.logger.info("Reset player token for {}".format(player_id))
    return "Success"

@ratings.route('/game_servers/new', methods=['GET', 'POST'])
@login_required
@roles_required(RATINGS_ADMIN_ROLE.name)
def create_game_server():
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
    default_role = user_datastore.find_role('user')
    user_datastore.add_role_to_user(user, default_role)
    db.session.add(user)
    db.session.commit()
