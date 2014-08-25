from flask.ext.security import login_required
from flask import Blueprint, render_template, jsonify, current_app, url_for
from .models import GoServerAccount

ratings = Blueprint("ratings", __name__)


@ratings.route('/')
@login_required
def home():
    return render_template('index.html')


@ratings.route('/api')
def api_list():
    '''return a json list of api endpoints'''
    urls = {}
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint is not 'static':
            urls[rule.endpoint] = {
                'methods': ','.join(rule.methods),
                'url': url_for(rule.endpoint)
            }
    return jsonify(urls)


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
