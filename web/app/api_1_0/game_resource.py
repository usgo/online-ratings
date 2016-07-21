from datetime import datetime
from dateutil.parser import parse as parse_iso8601
import logging
import requests

from flask import jsonify, request, Response
from . import api
from app.api_1_0.api_exception import ApiException
from app.api_1_0.utils import requires_json
from app.models import db, Game, GoServer, Player

def _result_str_valid(result):
    """Check the format of a result string per the SGF file format.

    See http://www.red-bean.com/sgf/ for details.
    """
    if result in ['0', 'Draw', 'Void', '?']:
        return True

    if result.startswith('B') or result.startswith('W'):
        score = result[2:]
        if score in ['R', 'Resign', 'T', 'Time', 'F', 'Forfeit']:
            return True
        try:
            score = float(score)
            return True
        except ValueError:
            return False
    return False


def validate_game_submission(headers, body_json):
    #required
    data = {
        'server_id': body_json.get('server_id'),
        'black_id': body_json.get('black_id'),
        'white_id': body_json.get('white_id'),
        'result': body_json.get('result'),
        'date_played': body_json.get('date_played'),
    }

    if None in data.values():
        missing_fields = ", ".join(k for k,v in data.items() if v is None)
        raise ApiException('Missing required parameters: %s' % missing_fields)

    #optional
    data.update({
        'game_record': body_json.get('game_record'),
        'game_url': body_json.get('game_url')
    })

    server_token = headers.get('X-Auth-Server-Token')
    black_token = headers.get('X-Auth-Black-Player-Token')
    white_token = headers.get('X-Auth-White-Player-Token')

    if any(token is None for token in (server_token, black_token, white_token)):
        raise ApiException('Did not submit required X-Auth-(Server-Token|Black-Player-Token|White_Player-Token) headers.', 403)

    gs = GoServer.query.filter_by(id=data['server_id'], token=server_token).first()
    if gs is None:
        raise ApiException('server access token unknown or expired: %s' % server_token,
                           status_code=404)

    b = Player.query.filter_by(id=data['black_id'], token=black_token).first()
    if b is None or b.user_id is None:
        raise ApiException('black player access token unknown or expired: %s' % black_token,
                           status_code=404)

    w = Player.query.filter_by(id=data['white_id'], token=white_token).first()
    if w is None or w.user_id is None:
        raise ApiException('white player token unknown or expired: %s' % white_token,
                           status_code=404)

    if not _result_str_valid(data['result']):
        raise ApiException('format of result is incorrect')

    if data['game_record'] is None and data['game_url'] is None:
        raise ApiException('One of game_record or game_url must be present')

    if data['game_record'] is not None:
        game_record = data['game_record'].encode()
    else:
        try:
            response = requests.get(data['game_url'], verify=False)
            game_record = response.content
        except Exception as e:
            logging.info("Got invalid game_url %s" % data.get("game_url", ""))
            logging.info(e)
            raise ApiException('game_url provided (%s) was invalid!' % data.get('game_url', '<None>'))

    try:
        date_played = parse_iso8601(data['date_played'])
    except TypeError:
        raise ApiException(error='date_played must be in ISO 8601 format')

    logging.info(" White: %s, Black: %s " % (w,b))
    game = Game(server_id=gs.id,
                white_id=w.id,
                black_id=b.id,
                rated=False,
                date_played=date_played,
                date_reported=datetime.now(),
                result=data['result'],
                game_record=game_record
                )
    return game

@api.route('/games', methods=['POST'])
@requires_json
def create_game():
    """Post a new game result to the database."""
    game = validate_game_submission(request.headers, request.json)
    db.session.add(game)
    db.session.commit()
    print("New game: %s " % str(game))
    return jsonify(game.to_dict()), 201

@api.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = Game.query.get_or_404(game_id)
    return jsonify(game.to_dict())

@api.route('/games/<int:game_id>/sgf', methods=['GET'])
def get_game_sgf(game_id):
    game = Game.query.get_or_404(game_id)
    return Response(game.game_record, mimetype='application/x-go-sgf')
