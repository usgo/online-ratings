import logging

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.security import Security, user_registered
from flask_wtf.csrf import CsrfProtect
from flask_mail import Mail
from .models import db, user_datastore
from .views import ratings as ratings_blueprint, user_registered_sighandler
from .api_1_0 import api as api_1_0_blueprint
from .verify import verify as verify_blueprint
from flask.ext.rq import RQ

def get_app(config):
    app = Flask(__name__)

    app.config.from_object(config)
    mail = Mail(app)
    RQ(app)
    csrf = CsrfProtect(app)
    csrf.exempt(api_1_0_blueprint)

    stream_handler = logging.StreamHandler()
    if app.debug:
        stream_handler.setLevel(logging.INFO)
    else:
        stream_handler.setLevel(logging.WARN)
    app.logger.addHandler(stream_handler)

    db.init_app(app)
    bootstrap = Bootstrap(app)
    security = Security(app, user_datastore)
    user_registered.connect(user_registered_sighandler)


    app.register_blueprint(ratings_blueprint)
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1')
    app.register_blueprint(verify_blueprint, url_prefix='/v')

    return app
