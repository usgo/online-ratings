from flask import jsonify
from flask.ext.security import roles_required
from app.models import GoServer, RATINGS_ADMIN_ROLE
from . import api


@api.route('/GameServer', methods=['GET'])
@roles_required(RATINGS_ADMIN_ROLE.name)
def allgameservers():
    game_servers = GoServer.query.all()
    data = {
        "num_servers": len(game_servers),
        "servers": []
    }
    for gs in game_servers:
        server = {'name': gs.name, 'URL': gs.url, 'token': gs.token}
        data['servers'].append(server)
    return jsonify(data)
