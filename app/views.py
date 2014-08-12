from flask.ext.security import login_required
from flask import Blueprint, render_template, jsonify
from .models import db, Game, GoServerAccount

ratings = Blueprint("ratings", __name__)


@ratings.route('/')
@login_required
def home():
    return render_template('index.html')


@ratings.route('/Player', methods=['GET'])
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
