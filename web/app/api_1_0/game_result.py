from flask import jsonify, request
from . import api
from app.api_1_0.api_exception import ApiException
from app.models import db, Game, GoServer, Player
from datetime import datetime
from dateutil.parser import parse as parse_iso8601
import logging
import requests

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


def validate_game_submission(request_body):
    #required
    data = {
        'server_tok': request_body.get('server_tok'),
        'b_tok': request_body.get('b_tok'),
        'w_tok': request_body.get('w_tok'),
        'game_server': request_body.get('game_server'),
        'black_id': request_body.get('black_id'),
        'white_id': request_body.get('white_id'),
        'rated': request_body.get('rated'),
        'result': request_body.get('result'),
        'date_played': request_body.get('date_played'),
    }
    if None in data.values():
        raise ApiException('malformed request')

    #optional
    data.update({
        'sgf_data': request_body.get('sgf_data'),
        'sgf_link': request_body.get('sgf_link')
    })

    gs = GoServer.query.filter_by(name=data['game_server'], token=data['server_tok']).first()
    if gs is None:
        raise ApiException('server access token unknown or expired: %s' % data['server_tok'],
                           status_code=404)

    b = Player.query.filter_by(id=data['black_id'], token=data['b_tok']).first()
    if b is None or b.user_id is None:
        raise ApiException('user access token unknown or expired: %s' % data['b_tok'],
                           status_code=404)

    w = Player.query.filter_by(id=data['white_id'], token=data['w_tok']).first()
    if w is None or w.user_id is None:
        raise ApiException('user access token unknown or expired: %s' % data['w_tok'],
                           status_code=404)

    if type(data['rated']) != bool:
        raise ApiException('rated must be set to True or False')

    if not _result_str_valid(data['result']):
        raise ApiException('format of result is incorrect')

    if data['sgf_data'] is None and data['sgf_link'] is None:
        raise ApiException('One of sgf_data or sgf_link must be present')

    if data['sgf_data'] is not None:
        game_data = data['sgf_data'].encode()
    else:
        try:
            response = requests.get(data['sgf_link'])
            game_data = response.content
        except Exception as e:
            logging.info("Got invalid sgf_link %s" % data.get("sgf_link", ""))
            logging.info(e)
            raise ApiException('sgf_link provided (%s) was invalid!' % data.get('sgf_link', '<None>'))

    try:
        date_played = parse_iso8601(data['date_played'])
    except TypeError:
        raise ApiException(error='date_played must be in ISO 8601 format')

    rated = data['rated']
    logging.info(" White: %s, Black: %s " % (w,b))
    game = Game(server_id=gs.id,
                white_id=w.id,
                black_id=b.id,
                rated=rated,
                date_played=date_played,
                date_reported=datetime.now(),
                result=data['result'],
                game_record=game_data
                )
    return game

@api.route('/results', methods=['POST'])
def create_result():
    """Post a new game result to the database."""
    game = validate_game_submission(request.args, request.body)
    db.session.add(game)
    db.session.commit()
    print("New game: %s " % str(game))
    return jsonify(game.to_dict())
