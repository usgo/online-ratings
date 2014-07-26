

from flask.ext.security import login_required
from flask import render_template
from app import app

# Views
@app.route('/')
@login_required
def home():
    return render_template('index.html')
