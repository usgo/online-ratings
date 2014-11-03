from flask import Blueprint

api = Blueprint('api', __name__)

from . import api_exception, api_map, game_server
