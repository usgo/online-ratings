
from flask import current_app, render_template
from flask import jsonify, request, Response
from . import tournament
from app.models import db, Tournament


@tournament.route('/')
def index():
    tournaments = Tournament.query.all()
    x = tournaments[0]
    return x.event_name
