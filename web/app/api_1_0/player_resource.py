from flask import jsonify, request
from flask.ext.security import roles_required, roles_accepted
from app.api_1_0.api_exception import ApiException
from app.models import GoServer, Player, User, RATINGS_ADMIN_ROLE, SERVER_ADMIN_ROLE
from . import api


@api.route('/Player', methods=['GET'])
@roles_required(RATINGS_ADMIN_ROLE.name)
def allplayers():
    users = User.query.all()
    data = {
        "num_accounts": len(users),
        "aga_accounts": []
    }
    for u in users:
        person = {
            'id': u.id,
            'AGA ID': u.aga_id,
            'email': u.email,
            'game_server_accounts': []
        }
        gs_accounts = Player.query.filter_by(user_id=u.id)
        if gs_accounts is not None:
            for a in gs_accounts:
                player_acct = {'server': a.server.name, 'player_name': a.name}
                person['game_server_accounts'].append(player_acct)
        data['aga_accounts'].append(person)
    return jsonify(data)


@api.route('/Player/<string:player_tok>', methods=['GET'])
@roles_accepted(RATINGS_ADMIN_ROLE.name, SERVER_ADMIN_ROLE.name)
def player(player_tok):
    """Verify that the specified user has a valid AGA account.

    This request takes the user and server access tokens as input.
    The method returns OK if and only if:
        - server token is valid
        - user token is valid for the given server
        - TODO: confirm that the user's AGA account is active
    """
    server_tok = request.args.get('server_tok')
    if player_tok is None or server_tok is None:
        raise ApiException('malformed request')

    gs = GoServer.query.filter_by(token=server_tok).first()
    if gs is None:
        raise ApiException('server access token unknown or expired',
                           status_code=404)

    player_acct = Player.query.filter_by(token=player_tok).first()
    if player_acct is None:
        raise ApiException('user access token unknown or expired',
                           status_code=404)

    data = {
        "aga_id": player_acct.user.aga_id,
        "email": player_acct.user.email,
        "roles": [role.name for role in player_acct.user.roles]
    }
    return jsonify(data)
