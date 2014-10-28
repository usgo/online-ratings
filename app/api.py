from flask.ext.security import login_required
from flask import jsonify, request
from .api_exception import ApiException
from .models import db, Game, GoServer, User
from .views import ratings
from datetime import datetime
from dateutil.parser import parse as parse_iso8601


@ratings.errorhandler(ApiException)
def handle_api_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


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
            numeric_score = float(score)
            return True
        except ValueError:
            return False
    return False


@ratings.route('/PostResult', methods=['POST'])
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
        raise ApiException('server access token unknown or expired',
                           status_code=404)

    b = User.query.filter_by(token=data['b_tok']).first()
    if b is None:
        raise ApiException('user access token unknown or expired',
                           status_code=404)

    w = User.query.filter_by(token=data['w_tok']).first()
    if w is None:
        raise ApiException('user access token unknown or expired',
                           status_code=404)

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
    db.session.add(game)
    db.session.commit()
    return jsonify(message='OK')


@ratings.route('/VerifyUser', methods=['GET'])
def verifyuser():
    """Verify that the specified user has a valid AGA account.

    This request takes the user and server access tokens as input.
    The method returns OK if and only if:
        - server token is valid
        - user token is valid for the given server
        - TODO: confirm that the user's AGA account is active
    """
    user_tok = request.args.get('user_tok')
    server_tok = request.args.get('server_tok')
    if user_tok is None or server_tok is None:
        raise ApiException('malformed request')

    gs = GoServer.query.filter_by(token=server_tok).first()
    if gs is None:
        raise ApiException('server access token unknown or expired',
                           status_code=404)

    user_acct = User.query.filter_by(token=user_tok).first()
    if user_acct is None:
        raise ApiException('user access token unknown or expired',
                           status_code=404)

    return jsonify(message='OK')


@ratings.route('/GetToken', methods=['POST'])
def getservertoken():
    """Obtain a new access token for the server."""
    # input: credentials (uname and pwd)
    # output: [token | error (invalid credentials]
    raise ApiException('service not yet implemented')
