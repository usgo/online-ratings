from flask import current_app
from . import tournament

@tournament.route('/')
def index():
    return "Hello, World"
