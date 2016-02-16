import os

from app.models import Player
from tests import BaseTestCase

class TestPlayerResource(BaseTestCase):

    players_endpoint = '/api/v1/players'

    def setUp(self):
        super().setUp()
        self.example_player = Player.query.get(1).to_dict()
        self.example_player_secret_token = Player.query.get(1).token

    def test_players_endpoint(self):
        player_by_id_response = self.client.get(
            os.path.join(
                self.players_endpoint,
                str(self.example_player['id'])))
        self.assertEqual(self.example_player, player_by_id_response.json)
        self.assertEqual(player_by_id_response.status_code, 200)
        player_by_secret_token_response = self.client.get(
            self.players_endpoint,
            query_string={"player_token": self.example_player_secret_token})
        self.assertEqual(self.example_player, player_by_secret_token_response.json)
        self.assertEqual(player_by_secret_token_response.status_code, 200)

    def test_players_endpoint_error_handling(self):
        response = self.client.get(
            self.players_endpoint,
            query_string={"player_token": "this definitely doesn't exist"})
        self.assertEqual(response.status_code, 404)
        response = self.client.get(self.players_endpoint)
        self.assertEqual(response.status_code, 400)



