from flask.ext.security import login_required
from flask import jsonify, request
from app import app, db, models


@app.route('/PostResult', methods=['POST'])
def postresult():
    """Post a new game result to the database."""
    # input: server token, w token, b token
    #        result, rated, date played
    #        game record (write to file system?)
    # output: [game added | invalid server |
    #          invalid player w | invalid player b]
    return jsonify(error='service not yet implemented')


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
