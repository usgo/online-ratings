import logging

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.security import Security, user_registered
from flask_wtf.csrf import CsrfProtect
from flask_mail import Mail
from flask_migrate import Migrate
from .models import db, user_datastore
from .error_mail import email_exception
from .views import ratings as ratings_blueprint, user_registered_sighandler
from .api_1_0 import api as api_1_0_blueprint
from .tournament import tournament as tournament_blueprint
from .verify import verify as verify_blueprint
from flask.ext.rq import RQ

mail = Mail()

def get_app(config):
    app = Flask(__name__)

    app.config.from_object(config)
    mail.init_app(app)
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
    Migrate(app, db)
    bootstrap = Bootstrap(app)
    security = Security(app, user_datastore)
    user_registered.connect(user_registered_sighandler)


    app.register_blueprint(ratings_blueprint)
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1')
    app.register_blueprint(verify_blueprint, url_prefix='/v')
    app.register_blueprint(tournament_blueprint, url_prefix='/tournament')
    app.register_error_handler(500, email_exception)

    return app
