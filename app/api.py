from flask.ext.security import login_required
from flask import jsonify, request
from app import app, db, models
from datetime import datetime


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


@app.route('/PostResult', methods=['POST'])
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
        return jsonify(error='malformed request')

    gs = models.GoServer.query.filter_by(token=data['server_tok']).first()
    if gs is None:
        return jsonify(error='server access token unknown or expired')

    b = models.GoServerAccount.query.filter_by(token=data['b_tok']).first()
    if b is None or b.go_server_id != gs.id:
        return jsonify(error='user access token unknown or expired')

    w = models.GoServerAccount.query.filter_by(token=data['w_tok']).first()
    if w is None or w.go_server_id != gs.id:
        return jsonify(error='user access token unknown or expired')

    if data['rated'] not in ['True', 'False']:
        return jsonify(error='rated must be set to True or False')

    if not _result_str_valid(data['result']):
        return jsonify(error='format of result is incorrect')

    try:
        date_played = datetime.strptime(data['date'], '%Y-%m-%d')
    except:
        return jsonify(error='date must be of the form year-month-day')

    rated = data['rated'] == 'True'
    game = models.Game(white=w,
                       black=b,
                       rated=rated,
                       date_played=date_played,
                       date_reported=datetime.now(),
                       result=data['result'])
    db.session.add(game)
    db.session.commit()
    return jsonify(message='OK')


@app.route('/VerifyUser', methods=['GET'])
def verifyuser():
    """Verify that the specified user has a valid AGA account.

    This request takes the user and server access tokens as input.
    The method returns OK if and only if:
        - server token is valid
        - user token is valid for the given server
        - TODO: user's AGA is active
    """
    user_tok = request.args.get('user_tok')
    server_tok = request.args.get('server_tok')
    if user_tok is None or server_tok is None:
        return jsonify(error='malformed request')

    gs = models.GoServer.query.filter_by(token=server_tok).first()
    if gs is None:
        return jsonify(error='server access token unknown or expired')

    user_acct = models.GoServerAccount.query.filter_by(token=user_tok).first()
    if user_acct is None:
        return jsonify(error='user access token unknown or expired')

    if user_acct.go_server_id != gs.id:
        return jsonify(error='user/server access token mismatch')

    return jsonify(message='OK')


@app.route('/GetToken', methods=['POST'])
def getservertoken():
    """Obtain a new access token for the server."""
    # input: credentials (uname and pwd)
    # output: [token | error (invalid credentials]
    return jsonify(error='service not yet implemented')
