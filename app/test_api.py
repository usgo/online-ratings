from app.test_base import BaseTestCase

# http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-unit-testing
# http://flask.pocoo.org/docs/testing/#testing
# https://github.com/mjhea0/flaskr-tdd


class FlaskTestCase(BaseTestCase):

    VerifyUser = 'http://localhost:5000/VerifyUser'

    def test_VerifyUser_GoodUser(self):
        from app.models import create_test_data
        create_test_data()

        q = {'server_tok': 'secret_kgs', 'user_tok': 'secret_foo'}
        r = self.client.get(self.VerifyUser, query_string=q)
        expected = dict(message='OK')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 200)

    def test_VerifyUser_BadServerTok(self):
        from app.models import create_test_data
        create_test_data()

        q = {'server_tok': 'bad', 'user_tok': 'secret_baz'}
        r = self.client.get(self.VerifyUser, query_string=q)
        expected = dict(message='server access token unknown or expired')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 404)

    def test_VerifyUser_UnknownUser(self):
        from app.models import create_test_data
        create_test_data()

        q = {'server_tok': 'secret_kgs', 'user_tok': 'bad'}
        r = self.client.get(self.VerifyUser, query_string=q)
        expected = dict(message='user access token unknown or expired')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 404)

    def test_VerifyUser_UserMismatch(self):
        from app.models import create_test_data
        create_test_data()

        q = {'server_tok': 'secret_kgs', 'user_tok': 'secret_baz'}
        r = self.client.get(self.VerifyUser, query_string=q)
        expected = dict(message='user/server access token mismatch')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 404)

    def test_VerifyUser_BadRequest(self):
        from app.models import create_test_data
        create_test_data()

        q = {'server_tok': 'secret_kgs'}
        r = self.client.get(self.VerifyUser, query_string=q)
        expected = dict(message='malformed request')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 400)

        q = {'user_tok': 'secret_foo'}
        r = self.client.get(self.VerifyUser, query_string=q)
        expected = dict(message='malformed request')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 400)

        q = 'invalid_request_param'
        r = self.client.get(self.VerifyUser, query_string=q)
        expected = dict(message='malformed request')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 400)
