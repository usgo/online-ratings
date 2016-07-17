from flask import Blueprint

tournament = Blueprint('tournament', __name__)

from . import tournament
