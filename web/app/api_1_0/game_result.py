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

@api.route('/results', methods=['POST'])
def create_result():
    """Post a new game result to the database.

    TODO: Check for duplicates.
    """
    #required
    data = {
        'server_tok': request.args.get('server_tok'),
        'b_tok': request.args.get('b_tok'),
        'w_tok': request.args.get('w_tok'),
        'rated': request.args.get('rated'),
        'result': request.args.get('result'),
        'date_played': request.args.get('date_played'),
    }
    if None in data.values():
        raise ApiException('malformed request')

    #optional
    data.update({
        'sgf_data': request.args.get('sgf_data'),
        'sgf_link': request.args.get('sgf_link')
    })

    gs = GoServer.query.filter_by(token=data['server_tok']).first()
    if gs is None:
        raise ApiException('server access token unknown or expired: %s' % data['server_tok'],
                           status_code=404)

    b = Player.query.filter_by(token=data['b_tok']).first()
    if b is None or b.user_id is None:
        raise ApiException('user access token unknown or expired: %s' % data['b_tok'],
                           status_code=404)

    w = Player.query.filter_by(token=data['w_tok']).first()
    if w is None or w.user_id is None:
        raise ApiException('user access token unknown or expired: %s' % data['w_tok'],
                           status_code=404)

    if data['rated'] not in ['True', 'False']:
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

    rated = data['rated'] == 'True'
    logging.info(" White: %s, Black: %s " % (w,b))
    game = Game(server_id=gs.id,
                white=w,
                white_id = w.id,
                black=b,
                black_id = b.id,
                rated=rated,
                date_played=date_played,
                date_reported=datetime.now(),
                result=data['result'],
                game_record=game_data
                )
    logging.info("saving game: %s " % str(game))
    print("saving game: %s " % str(game))
    db.session.add(game)
    db.session.commit()
    return jsonify(game.to_dict())
