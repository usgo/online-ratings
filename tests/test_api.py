from tests import BaseTestCase

# http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-unit-testing
# http://flask.pocoo.org/docs/testing/#testing
# https://github.com/mjhea0/flaskr-tdd


class TestCase_PostResult(BaseTestCase):

    PostResult = 'http://localhost:5000/api/v1.0/PostResult'
    good_param_set = {
        'server_tok': 'secret_kgs',
        'b_tok': 'secret_foo',
        'w_tok': 'secret_bar',
        'rated': 'True',
        'result': 'B+0.5',
        'date': '2014-08-19T10:30:00Z'
    }

    def test_PostResult_Success(self):
        from app.models import create_test_data
        create_test_data()

        r = self.client.post(self.PostResult, query_string=self.good_param_set)
        expected = dict(message='OK')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 200)

    def test_PostResult_MissingParam(self):
        from app.models import create_test_data
        create_test_data()

        for k in self.good_param_set.keys():
            q = self.good_param_set.copy()
            q.pop(k, None)  # on each iteration, remove 1 param
            r = self.client.post(self.PostResult, query_string=q)
            expected = dict(message='malformed request')
            actual = r.json
            self.assertEqual(expected, actual)
            self.assertEqual(r.status_code, 400)

    def test_PostResult_BadServerTok(self):
        from app.models import create_test_data
        create_test_data()

        q = self.good_param_set.copy()
        q['server_tok'] = 'bad_tok'
        r = self.client.post(self.PostResult, query_string=q)
        expected = dict(message='server access token unknown or expired')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 404)

    def test_PostResult_BadUserTok(self):
        from app.models import create_test_data
        create_test_data()

        for param in ['w_tok', 'b_tok']:
            # User token is bad
            q = self.good_param_set.copy()
            q[param] = 'bad_user_tok'
            r = self.client.post(self.PostResult, query_string=q)
            expected = dict(message='user access token unknown or expired')
            actual = r.json
            self.assertEqual(expected, actual)
            self.assertEqual(r.status_code, 404)

    def test_PostResult_Rated(self):
        from app.models import create_test_data
        create_test_data()

        q = self.good_param_set.copy()
        for value in ['True', 'False']:
            q['rated'] = value
            r = self.client.post(self.PostResult, query_string=q)
            expected = dict(message='OK')
            actual = r.json
            self.assertEqual(expected, actual)
            self.assertEqual(r.status_code, 200)

        q['rated'] = '0'
        r = self.client.post(self.PostResult, query_string=q)
        expected = dict(message='rated must be set to True or False')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 400)

    def test_PostResult_Result(self):
        from app.models import create_test_data
        create_test_data()

        q = self.good_param_set.copy()
        good_results = [
            'W+0.5', 'B+100',
            'B+0.5', 'B+42',
            'W+R', 'W+Resign', 'W+T', 'W+Time', 'W+F', 'W+Forfeit',
            'B+R', 'B+Resign', 'B+T', 'B+Time', 'B+F', 'B+Forfeit',
            'Void', '?', '0', 'Draw'
        ]
        for result in good_results:
            q['result'] = result
            r = self.client.post(self.PostResult, query_string=q)
            expected = dict(message='OK')
            actual = r.json
            self.assertEqual(expected, actual, msg=result)
            self.assertEqual(r.status_code, 200)

        q['result'] = 'B+W'
        r = self.client.post(self.PostResult, query_string=q)
        expected = dict(message='format of result is incorrect')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 400)
