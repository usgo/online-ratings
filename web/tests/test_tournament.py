import os

from tests import BaseTestCase

class TestTournament(BaseTestCase):

    tournament_endpoint = '/tournament/'

    def test_tournament_base_url(self):
        response = self.client.get(self.tournament_endpoint)
        self.assertEqual(response.status_code, 200)
