from . import verify

from flask import abort, redirect, url_for
from itsdangerous import URLSafeSerializer, BadSignature
from app.models import Player

def get_serializer(secret_key=None):
    if secret_key is None:
        secret_key = verify.secret_key
    return URLSafeSerializer(secret_key)

@verify.route('/verify/<payload>')
def verify_player(payload):
    s = get_serializer()
    try:
        player_id = s.loads(payload)
    except BadSignature:
        abort(404)

    player = Player.query.get_or_404(player_id)
    player.activate()
    return redirect(url_for('app.index'))

def get_verify_link(player):
    s = get_serializer()
    payload = s.dumps(player.id)
    return url_for('verify_player', payload=payload, 
                   _external=True)
