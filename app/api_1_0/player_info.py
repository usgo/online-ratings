from flask import jsonify, request
from flask.ext.security import roles_required, roles_accepted
from app.api_1_0.api_exception import ApiException
from app.models import GoServer, User
from . import api


@api.route('/Player', methods=['GET'])
@roles_required('ratings_admin')
def allplayers():
    players = User.query.all()
    data = {
        "num_accounts": len(players),
        "accounts": []
    }
    for p in players:
        account = {'id': p.id, 'AGA ID': p.aga_id, 'email': p.email}
        data['accounts'].append(account)
    return jsonify(data)


@api.route('/Player/<string:player_id>', methods=['GET'])
@roles_accepted('ratings_admin', 'server_admin')
def player(player_id):
    """Verify that the specified user has a valid AGA account.

    This request takes the user and server access tokens as input.
    The method returns OK if and only if:
        - server token is valid
        - user token is valid for the given server
        - TODO: confirm that the user's AGA account is active
    """
    server_tok = request.args.get('server_tok')
    if player_id is None or server_tok is None:
        raise ApiException('malformed request')

    gs = GoServer.query.filter_by(token=server_tok).first()
    if gs is None:
        raise ApiException('server access token unknown or expired',
                           status_code=404)

    user_acct = User.query.filter_by(token=player_id).first()
    if user_acct is None:
        raise ApiException('user access token unknown or expired',
                           status_code=404)

    data = {
        "aga_id": user_acct.aga_id,
        "email": user_acct.email,
        "roles": [role.name for role in user_acct.roles]
    }
    return jsonify(data)
