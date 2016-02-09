from tests import BaseTestCase

# http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-unit-testing
# http://flask.pocoo.org/docs/testing/#testing
# https://github.com/mjhea0/flaskr-tdd

class TestResultsEndpoint(BaseTestCase):

    results_endpoint = 'http://localhost:5000/api/v1/results'
    good_param_set = {
        'server_tok': 'secret_kgs',
        'b_tok': 'secret_foo_KGS',
        'w_tok': 'secret_bar_KGS',
        'rated': 'True',
        'result': 'B+0.5',
        'date': '2014-08-19T10:30:00Z',
        'sgf_data': '\n'.join(open('tests/testsgf.sgf').readlines())
    }

    def test_results_endpoint_success(self):
        r = self.client.post(self.results_endpoint, query_string=self.good_param_set)
        expected = dict(message='OK')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 200)

    def test_results_endpoint_sgf_link(self):
        sgf_link = "http://files.gokgs.com/games/2015/3/3/Clutter-underkey.sgf"
        params = self.good_param_set.copy()
        params.pop("sgf_data")
        params['sgf_link'] = sgf_link
        r = self.client.post(self.results_endpoint, query_string=params)
        expected = dict(message='OK')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 200)


    def test_results_endpoint_missing_param(self):
        for k in self.good_param_set.keys():
            q = self.good_param_set.copy()
            q.pop(k, None)  # on each iteration, remove 1 param
            r = self.client.post(self.results_endpoint, query_string=q)
            if k == 'sgf_data':
                expected = dict(message='One of sgf_data or sgf_link must be present')
            else:
                expected = dict(message='malformed request')

            actual = r.json
            self.assertEqual(expected, actual)
            self.assertEqual(r.status_code, 400)

    def test_results_endpoint_bad_server_token(self):
        q = self.good_param_set.copy()
        q['server_tok'] = 'bad_tok'
        r = self.client.post(self.results_endpoint, query_string=q)
        expected = dict(message='server access token unknown or expired: bad_tok')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 404)

    def test_results_endpoint_bad_user_token(self):
        for param in ['w_tok', 'b_tok']:
            # User token is bad
            q = self.good_param_set.copy()
            q[param] = 'bad_user_tok'
            r = self.client.post(self.results_endpoint, query_string=q)
            expected = dict(message='user access token unknown or expired: bad_user_tok')
            actual = r.json
            self.assertEqual(expected, actual)
            self.assertEqual(r.status_code, 404)

    def test_results_endpoint_rated(self):
        q = self.good_param_set.copy()
        for value in ['True', 'False']:
            q['rated'] = value
            r = self.client.post(self.results_endpoint, query_string=q)
            expected = dict(message='OK')
            actual = r.json
            self.assertEqual(expected, actual)
            self.assertEqual(r.status_code, 200)

        q['rated'] = '0'
        r = self.client.post(self.results_endpoint, query_string=q)
        expected = dict(message='rated must be set to True or False')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 400)

    def test_results_endpoint_result(self):
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
            r = self.client.post(self.results_endpoint, query_string=q)
            expected = dict(message='OK')
            actual = r.json
            self.assertEqual(expected, actual, msg=result)
            self.assertEqual(r.status_code, 200)

        q['result'] = 'B+W'
        r = self.client.post(self.results_endpoint, query_string=q)
        expected = dict(message='format of result is incorrect')
        actual = r.json
        self.assertEqual(expected, actual)
        self.assertEqual(r.status_code, 400)
