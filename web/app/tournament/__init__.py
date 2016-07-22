from flask import Blueprint

tournament = Blueprint('tournament', __name__)
# tournament.secret_key = "this is a temporary secret key"
from . import tourny
