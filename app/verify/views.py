from . import verify

from flask import abort, redirect, url_for
from itsdangerous import BadSignature, URLSafeSerializer
from app.models import Player
import app, logging


def get_serializer(secret_key=None):
    if secret_key is None:
        secret_key = app.app.secret_key #why app.app?
    return URLSafeSerializer(secret_key)

@verify.route('/verify/<payload>')
def verify_player(payload):
    s = get_serializer()
    try:
        player_id, aga_id = s.loads(payload)
    except BadSignature:
        logging.info('Verify called with invalid paylod')
        abort(404)

    player = Player.query.get_or_404(player_id)
    #TODO: verify that aga_id == player's user's aga id.  
    #TODO: something like player.activate(), maybe generate initial token?
    return redirect(url_for('app.index'))

def get_verify_link(player, aga_id):
    s = get_serializer()
    payload = s.dumps([player.id, aga_id])
    return url_for('verify_player', payload=payload, 
                   _external=True)
