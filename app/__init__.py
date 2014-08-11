from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config.DebugConfiguration')

db = SQLAlchemy(app)


from app.views import *
from app.api import *
