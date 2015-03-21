from flask import Blueprint
import logging

verify = Blueprint('verify', __name__)

from . import views

