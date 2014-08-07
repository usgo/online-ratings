from flask.ext.security import login_required
from flask import jsonify
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


@app.route('/VerifyUser', methods=['POST'])
def verifyuser():
    """Verify that the specified user has a valid AGA account."""
    # input: server token, user token
    # output: [valid | unknown | aga acct expired]
    return jsonify(error='service not yet implemented')


@app.route('/GetToken', methods=['POST'])
def getservertoken():
    """Obtain a new access token for the server."""
    # input: credentials (uname and pwd)
    # output: [token | error (invalid credentials]
    return jsonify(error='service not yet implemented')
