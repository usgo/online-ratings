import os
import datetime


from flask import url_for
from tests import BaseTestCase
from app.models import Tournament, db

class TestTournament(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.tournament_endpoint = '/tournament/'
        self.tournament_1 = Tournament(event_name="The Ultimate Go-ing Chamionship",
                                       start_date=datetime.datetime.now(),
                                       venue="LasVegas",
                                       director="Donald J. Trump",
                                       pairing="Completely Random - It's Madness!",
                                       rule_set="To the death!")
        db.session.add(self.tournament_1)
        db.session.commit()

    #  index
    def test_tournament_base_url(self):
        response = self.client.get(self.tournament_endpoint)
        self.assertEqual(response.status_code, 200)

    #  show
    def test_it_returns_an_individual_tournament(self):
        tournament_endpoint_1 = self.tournament_endpoint + str(self.tournament_1.id)
        response = self.client.get(tournament_endpoint_1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('LasVegas' in str(response.data))

    #  edit
    # def test_it_can_edit_tournament_info(self):
    #     tournament_edit_endpoint = self.tournament_endpoint + str(self.tournament_1.id) + '/edit'
    #     t = Tournament.query.first()
    #     self.assertEqual(t.event_name, self.tournament_1.event_name)
    #     test_string = "This event name changed for testing"
    #     t.event_name = test_string
    #     db.session.commit()
    #     t = Tournament.query.first()
    #     self.assertEqual(t.event_name, test_string)

    #  new
    # def test_it_can_create_new_instance_of_tournament(self):
    #     before = Tournament.query.count()
    #     self.assertEqual(before, 1)
    #     response1 = self.client.post('tournament/new',
    #         data={'event_name': 'testing'})
    #     print('XXXX', response1.data, 'XXXX')
    #     # self.client.post('/tournament/new',
    #     #     data=json.dumps({
    #     #         "event_name": "testing "
    #     #         }), content_type="application/json",
    #     #         environ_base={
    #     #             'HTTP_USER_AGENT':'Chrome',
    #     #             'REMOTE_ADDR': '127.0.0.1'
    #     #         })
    #     after = Tournament.query.count()
    #     t = Tournament.query.all()
    #     t = t[-1]
    #     # self.assertEqual(after, 2)
    #     self.assertEqual(t.event_name, 'testing')
