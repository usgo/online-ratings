from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.security import Security, user_registered
from flask_mail import Mail
from .models import db, user_datastore
from .views import ratings, user_registered_sighandler
from .api_1_0 import api as api_1_0_blueprint
from .verify import verify as verify_blueprint

app = Flask(__name__)
app.config.from_object('config.BaseConfig')
mail = Mail(app)

if app.debug:
    import logging
    import sys
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO,stream=sys.stderr) 
    app.logger.addHandler(logging.StreamHandler())
    logging.info("set up logging")

db.init_app(app)
bootstrap = Bootstrap(app)

security = Security(app, user_datastore)
user_registered.connect(user_registered_sighandler)

app.register_blueprint(ratings)
app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')
app.register_blueprint(verify_blueprint, url_prefix='/v')

if __name__ == '__main__':
    app.run()
