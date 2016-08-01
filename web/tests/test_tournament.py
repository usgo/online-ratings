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
                                       director_phone="555-5555",
                                       director_email="dj@example.com",
                                       pairing="Completely Random - It's Madness!",
                                       rule_set="To the death!",
                                       time_controls="filler text",
                                       basic_time="filler text",
                                       overtime_format="filler text",
                                       overtime_conditions="filler text",
                                       komi="filler text",
                                       tie_break="filler text")
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
            data={ "event_name": "new_event",
                   "start_date": "date as string",
                   "venue": "Not LasVegas",
                   "director": "Donald J. Trump",
                   "director_phone": "555-5555",
                   "director_email": "dj@example.com",
                   "pairing": "Completely Random - It's Madness!",
                   "rule_set": "Irish Dueling",
                   "time_controls": "filler text",
                   "basic_time": "filler text",
                   "overtime_format": "filler text",
                   "overtime_conditions": "filler text",
                   "komi": "filler text",
                   "tie_break": "filler text" })
        count = Tournament.query.count()
        self.assertEqual(count, 2)
        t = Tournament.query.all()[-1]
        self.assertEqual("new_event", t.event_name)

    def test_it_can_delete_a_non_submitted_tournament(self):
        t =Tournament.query.first()
        response = self.client.post('/tournament/'+str(t.id)+'/delete')
        self.assertEqual(0, Tournament.query.count())

    def test_it_can_not_edit_tournament_marked_submitted(self):
        tournament_edit_endpoint = self.tournament_endpoint + str(self.tournament_1.id) + '/edit'
        t = Tournament.query.first()
        #  mark tournament as submitted
        response = self.client.post(
            '/tournament/'+ str(t.id)+'/edit', #  url_for()
            data={"event_name": t.event_name,
                   "start_date": t.start_date,
                   "venue": t.venue,
                   "director": t.director,
                   "director_phone": t.director_phone,
                   "director_email": t.director_email,
                   "pairing": t.pairing,
                   "rule_set": t.rule_set,
                   "time_controls": t.time_controls,
                   "basic_time": t.basic_time,
                   "overtime_format": t.overtime_format,
                   "overtime_conditions": t.overtime_conditions,
                   "komi": t.komi,
                   "tie_break": t.tie_break,
                   "submitted": True })
        t = Tournament.query.first()
        self.assertEqual(True, t.submitted)
        t = Tournament.query.first()
        self.assertNotEqual("this will fail to change", t.event_name)
        self.assertEqual("The Ultimate Go-ing Chamionship", t.event_name)

    def test_it_can_not_delete_tournament_marked_submitted(self):
        tournaments_before = Tournament.query.count()
        t = Tournament.query.first()
        self.client.post(
            '/tournament/'+ str(t.id)+'/edit', #  url_for()
            data={"event_name": t.event_name,
                   "start_date": t.start_date,
                   "venue": t.venue,
                   "director": t.director,
                   "director_phone": t.director_phone,
                   "director_email": t.director_email,
                   "pairing": t.pairing,
                   "rule_set": t.rule_set,
                   "time_controls": t.time_controls,
                   "basic_time": t.basic_time,
                   "overtime_format": t.overtime_format,
                   "overtime_conditions": t.overtime_conditions,
                   "komi": t.komi,
                   "tie_break": t.tie_break,
                   "submitted": True })
        response = self.client.post('/tournament/'+str(t.id)+'/delete')
        tournaments_after = Tournament.query.count()
        self.assertEqual(tournaments_before, tournaments_after)
