from flask.ext.security import login_required
from flask import render_template, jsonify
from app import app, db
from app.models import Game, GoServerAccount

@app.route('/')
@login_required
def home():
    return render_template('index.html')


@app.route('/Player', methods=['GET'])
def player():
    players = GoServerAccount.query.all()
    data = {
        "num_accounts": len(players),
        "accounts": []
    }
    for p in players:
        account = {'id': p.id, 'nick': p.nick, 'email': p.user.email}
        data['accounts'].append(account)
    return jsonify(data)
