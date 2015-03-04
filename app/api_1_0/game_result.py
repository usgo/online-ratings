from flask import jsonify, request
from . import api
from app.api_1_0.api_exception import ApiException
from app.models import db, Game, GoServer, User, Player
from datetime import datetime
from dateutil.parser import parse as parse_iso8601
import logging


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


@api.route('/PostResult', methods=['POST'])
def postresult():
    """Post a new game result to the database.

    TODO: Check for duplicates.
    """
    data = {
        'server_tok': request.args.get('server_tok'),
        'b_tok': request.args.get('b_tok'),
        'w_tok': request.args.get('w_tok'),
        'rated': request.args.get('rated'),
        'result': request.args.get('result'),
        'date': request.args.get('date')
    }
    if None in data.values():
        raise ApiException('malformed request')

    gs = GoServer.query.filter_by(token=data['server_tok']).first()
    if gs is None:
        raise ApiException('server access token unknown or expired: %s' % data['server_tok'],
                           status_code=404)

    b = Player.query.filter_by(token=data['b_tok']).first()
    if b is None or b.user_id is None:
        raise ApiException('user access token unknown or expired: %s' % data['b_tok'],
                           status_code=404)
    logging.info(str(b))
    b = User.query.get(b.user_id)
    logging.info(str(b))

    w = Player.query.filter_by(token=data['w_tok']).first()
    if w is None or w.user_id is None:
        raise ApiException('user access token unknown or expired: %s' % data['w_tok'],
                           status_code=404)
    logging.info(str(w))
    w = User.query.get(w.user_id)
    logging.info(str(w))

    if data['rated'] not in ['True', 'False']:
        raise ApiException('rated must be set to True or False')

    if not _result_str_valid(data['result']):
        raise ApiException('format of result is incorrect')

    try:
        date_played = parse_iso8601(data['date'])
    except TypeError:
        raise ApiException(error='date must be in ISO 8601 format')

    rated = data['rated'] == 'True'
    game = Game(white=w,
                black=b,
                rated=rated,
                date_played=date_played,
                date_reported=datetime.now(),
                result=data['result'])
    logging.info("saving game: %s " % str(game))
    db.session.add(game)
    db.session.commit()
    return jsonify(message='OK')
