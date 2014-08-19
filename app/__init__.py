from flask import Flask
from flask.ext.security import Security
from .models import db, user_datastore
from .views import ratings
from .api import *

app = Flask(__name__)
app.config.from_object('config.DebugConfiguration')
db.init_app(app)
security = Security(app, user_datastore)
app.register_blueprint(ratings)
