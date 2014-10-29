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


#TODO: remove the following init function, which destroys any existing app
#database and replaces it with default data
@app.before_first_request
def init_db():
    from .models import create_test_data
    db.drop_all()
    db.create_all()
    create_test_data()
