from flask import Blueprint

verify = Blueprint('verify', __name__)

from . import views

