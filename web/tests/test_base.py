from flask.ext.testing import TestCase

from app import get_app
from app.models import db
from create_db import create_test_data

# The test strategy is based on the tutorial found here:
# https://realpython.com/blog/python/python-web-applications-with-flask-part-iii/


class BaseTestCase(TestCase):
    def create_app(self):
        app = get_app('config.TestConfiguration')
        return app

    def setUp(self):
        with self.app.app_context():
            db.create_all()
            create_test_data()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
