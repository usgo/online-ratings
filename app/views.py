from flask.ext.security import login_required
from flask import render_template, jsonify
from app import app, db, models


# Views
@app.route('/')
@login_required
def home():
    return render_template('index.html')


@app.route('/Player', methods=['GET'])
def player():
    players = models.GoServerAccount.query.all()
    data = {
        "num_accounts": len(players),
        "accounts": []
    }
    for p in players:
        data['accounts'].append({'id': p.id, 'nick': p.nick, 'email': p.user.email})
    return jsonify(data)
