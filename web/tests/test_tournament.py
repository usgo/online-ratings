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
        self.assertEqual(200, response.status_code)

    #  show
    def test_it_returns_an_individual_tournament(self):
        tournament_endpoint_1 = self.tournament_endpoint + str(self.tournament_1.id)
        response = self.client.get(tournament_endpoint_1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('LasVegas' in str(response.data))

    #  edit
    def test_it_can_edit_tournament_info(self):
        tournament_edit_endpoint = self.tournament_endpoint + str(self.tournament_1.id) + '/edit'
        t = Tournament.query.first()
        self.assertEqual(t.event_name, self.tournament_1.event_name)
        test_string = "This event name changed for testing"
        t.event_name = test_string
        response = self.client.post(
            '/tournament/'+str(t.id)+'/edit', #  url_for()
            data={"event_name" : t.event_name,
                  "start_date" : t.start_date,
                  "venue" : t.venue,
                  "director" : t.director,
                  "pairing" : t.pairing,
                  "rule_set" : t.rule_set})
        t = Tournament.query.first()
        self.assertEqual(test_string, t.event_name)

    #  new
    def test_it_can_add_a_new_tournament(self):
        tournament_new_endpoint = self.tournament_endpoint + '/new'
        count = Tournament.query.count()
        self.assertEqual(1, count)

        response = self.client.post(
            '/tournament/new', #  url_for()
            data={"event_name" : "new_event",
                  "start_date" : datetime.datetime.now(),
                  "venue" : "right here",
                  "director" : "new director",
                  "pairing" : "two on two",
                  "rule_set" : "irish dueling"})
        count = Tournament.query.count()
        self.assertEqual(count, 2)
        t = Tournament.query.all()[-1]
        self.assertEqual("new_event", t.event_name)
