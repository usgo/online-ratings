from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.security import Security, user_registered
from .models import db, user_datastore
from .views import ratings, user_registered_sighandler
from .api_1_0 import api as api_1_0_blueprint

app = Flask(__name__)
app.config.from_object('config.DebugConfiguration')

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


#TODO: remove the following init function, which destroys any existing app
#database and replaces it with default data
@app.before_first_request
def init_db():
    from .models import create_test_data
    db.drop_all()
    db.create_all()
    create_test_data()
