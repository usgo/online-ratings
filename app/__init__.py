from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_TRACKABLE'] = True

# Create database connection object
db = SQLAlchemy(app)

from app import models as _
from app import views as _
