import os
import datetime


from flask import url_for
from tests import BaseTestCase
from app.models import Tournament, TournamentPlayer, db

class TestTournament(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.tournament_endpoint = '/tournament/'
        self.tournament_1 = Tournament(
            event_name="The Ultimate Go-ing Chamionship",
            start_date=datetime.datetime.now(),
            venue="LasVegas",
            director="Donald J. Trump",
            director_phone="555-5555",
            director_email="dj@example.com",
            pairing="McMahon",
            rule_set="AGA",
            time_controls="filler text",
            basic_time="filler text",
            overtime_format="filler text",
            overtime_conditions="filler text",
            komi="7",
            tie_break1="SOS",
            tie_break2="SODOS")
        db.session.add(self.tournament_1)
        db.session.commit()

        self.tournament_1_player = TournamentPlayer(
            name="Tester Testington",
            aga_num="12345",
            rating="100",
            affiliation="Joe's house of Go",
            state="AZ",
            address="1111 Main St.",
            email="test@example.com",
            phone="123-456-7890",
            citizenship="USA",
            dob="01/01/01",
            tournament_id=1) #  tournament_1.id)

        db.session.add(self.tournament_1_player)
        db.session.commit()

###  TournamentPlayer Tests
    # players index
    def test_tournament_player_index_url(self):
        url = self.tournament_endpoint + \
            str(self.tournament_1.id) + \
            "/players/"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    # player edit
    def test_tournament_player_edit_url(self):
        url = self.tournament_endpoint + \
            str(self.tournament_1.id) + \
            "/player/" + str(self.tournament_1_player.id) + \
            "/edit/"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    # new player
    def test_add_new_tournament_player_url(self):
        url = self.tournament_endpoint + \
            str(self.tournament_1.id) + \
            "/player/new/"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    # delete player
    def test_delete_player_url(self):
        url = self.tournament_endpoint + \
            str(self.tournament_1.id) + \
            "/player/" + str(self.tournament_1_player.id) + \
            "/delete/"
        before = TournamentPlayer.query.count()
        self.assertEqual(1, before)
        response = self.client.post(url)
        after = TournamentPlayer.query.count()
        self.assertEqual(0, after)

    # new player - post
    def test_can_create_new_tournament_player(self):
        url = self.tournament_endpoint + \
            str(self.tournament_1.id) + \
            "/player/new/"
        before = TournamentPlayer.query.count()
        self.assertEqual(1, before)
        response = self.client.post(
            url,
            data={ "name": 'player 2',
                   "aga_num": '23456',
                   "rating": '11',
                   "affiliation": 'The Go Getters',
                   "state": 'WY',
                   "address": '101 Broadway',
                   "email": 'player2@example.com',
                   "phone": '234-567-8901',
                   "citizenship": 'usa',
                   "dob": '11/11/11',
                  "tournament_id": self.tournament_1.id })
        self.assertEqual(302, response.status_code)
        after = TournamentPlayer.query.count()
        self.assertEqual(2, after)
        new_player = TournamentPlayer.query.all()[-1]
        self.assertEqual(new_player.name, 'player 2')

    #  edit player - post
    def test_it_can_edit_an_existing_tournament_player(self):
        url = self.tournament_endpoint + \
            str(self.tournament_1.id) + \
            "/player/" + str(self.tournament_1_player.id) + \
            "/edit/"
        player = TournamentPlayer.query.get(self.tournament_1_player.id)
        player.name = "Test Edit"
        response = self.client.post(
            url,
            data={'name': player.name,
                  "aga_num": player.aga_num,
                  "rating": player.rating,
                    "affiliation": player.affiliation,
                    "state": player.state,
                    "address": player.address,
                    "email": player.email,
                    "phone": player.phone,
                    "citizenship": player.citizenship,
                    "dob": player.dob })
        player = TournamentPlayer.query.get(self.tournament_1_player.id)
        self.assertEqual("Test Edit", player.name)

    # sad path - cannot create, edit, or delete player if tournament submitted
    def test_it_cannot_add_new_player_if_tournament_marked_submitted(self):
        tournament_edit_endpoint = self.tournament_endpoint + \
            str(self.tournament_1.id) + '/edit'
        t = Tournament.query.first()
        #  mark tournament as submitted
        response = self.client.post(
            '/tournament/'+ str(t.id)+'/edit/', #  url_for()
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
                   "tie_break1": t.tie_break1,
                   "tie_break2": t.tie_break2,
                   "submitted": True })
        t = Tournament.query.first()
        self.assertEqual(True, t.submitted)
        #  TournamentPlayer test
        url = self.tournament_endpoint + \
            str(self.tournament_1.id) + \
            "/player/new/"
        before = TournamentPlayer.query.count()
        self.assertEqual(1, before)
        response = self.client.post(
            url,
            data={ "name": 'player 2',
                   "aga_num": '23456',
                   "rating": '11',
                   "affiliation": 'The Go Getters',
                   "state": 'WY',
                   "address": '101 Broadway',
                   "email": 'player2@example.com',
                   "phone": '234-567-8901',
                   "citizenship": 'usa',
                   "dob": '11/11/11',
                  "tournament_id": self.tournament_1.id })
        after = TournamentPlayer.query.count()
        self.assertEqual(1, after)
        no_new_player = TournamentPlayer.query.filter_by(name="player 2")
        self.assertEqual(0, no_new_player.count())

    def test_it_cannot_edit_player_if_tournament_marked_submitted(self):
        tournament_edit_endpoint = self.tournament_endpoint + \
            str(self.tournament_1.id) + '/edit'
        t = Tournament.query.first()
        #  mark tournament as submitted
        response = self.client.post(
            '/tournament/'+ str(t.id)+'/edit/', #  url_for()
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
                   "tie_break1": t.tie_break1,
                   "tie_break2": t.tie_break2,
                   "submitted": True })
        t = Tournament.query.first()
        self.assertEqual(True, t.submitted)
        #  TournamentPlayer test
        url = self.tournament_endpoint + \
            str(self.tournament_1.id) + \
            "/player/" + str(self.tournament_1_player.id) + \
            "/edit/"
        player = TournamentPlayer.query.get(self.tournament_1_player.id)
        failed_update = "Test Edit"
        response = self.client.post(
            url,
            data={ 'name': player.name,
                   "aga_num": failed_update,
                   "rating": player.rating,
                    "affiliation": player.affiliation,
                    "state": player.state,
                    "address": player.address,
                    "email": player.email,
                    "phone": player.phone,
                    "citizenship": player.citizenship,
                    "dob": player.dob })
        player = TournamentPlayer.query.get(self.tournament_1_player.id)
        self.assertNotEqual("Test Edit", player.name)
        self.assertEqual("Tester Testington", player.name)

    def test_it_cannot_delete_player_if_tournament_marked_submitted(self):
        tournament_edit_endpoint = self.tournament_endpoint + \
        str(self.tournament_1.id) + '/edit'
        t = Tournament.query.first()
        #  mark tournament as submitted
        response = self.client.post(
            '/tournament/'+ str(t.id)+'/edit/', #  url_for()
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
                   "tie_break1": t.tie_break1,
                   "tie_break2": t.tie_break2,
                   "submitted": True })
        t = Tournament.query.first()
        self.assertEqual(True, t.submitted)
        #  TournamentPlayer test
        url = self.tournament_endpoint + \
            str(self.tournament_1.id) + \
            "/player/" + str(self.tournament_1_player.id) + \
            "/delete/"
        before = TournamentPlayer.query.count()
        self.assertEqual(1, before)
        response = self.client.post(url)
        after = TournamentPlayer.query.count()
        self.assertEqual(1, after)
        player = TournamentPlayer.query.get(self.tournament_1_player.id)
        self.assertEqual("Tester Testington", player.name)

### End TournamentPlayer Tests

    #  index
    def test_tournament_base_url(self):
        response = self.client.get(self.tournament_endpoint)
        self.assertEqual(200, response.status_code)

    #  show
    def test_it_returns_an_individual_tournament(self):
        tournament_endpoint_1 = self.tournament_endpoint + \
            str(self.tournament_1.id) + "/"
        response = self.client.get(tournament_endpoint_1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('LasVegas' in str(response.data))

    #  edit
    def test_it_can_edit_tournament_info(self):
        tournament_edit_endpoint = self.tournament_endpoint + \
            str(self.tournament_1.id) + '/edit'
        t = Tournament.query.first()
        self.assertEqual(t.event_name, self.tournament_1.event_name)
        test_string = "This event name changed for testing"
        t.event_name = test_string
        response = self.client.post(
            '/tournament/'+str(t.id)+'/edit/', #  url_for()
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
            '/tournament/new/', #  url_for()
            data={ "event_name": "new_event",
                   "start_date": datetime.datetime.now().strftime('%Y-%m-%d'),
                   "venue": "Not LasVegas",
                   "director": "Donald J. Trump",
                   "director_phone": "555-5555",
                   "director_email": "dj@example.com",
                   "pairing": "McMahon",
                   "rule_set": "AGA",
                   "time_controls": "filler text",
                   "basic_time": "filler text",
                   "overtime_format": "filler text",
                   "overtime_conditions": "filler text",
                   "komi": "6",
                   "tie_break1": "SOS",
                   "tie_break2": "SODOS" })
        count = Tournament.query.count()
        self.assertEqual(count, 2)
        t = Tournament.query.all()[-1]
        self.assertEqual("new_event", t.event_name)

    def test_it_can_delete_a_non_submitted_tournament(self):
        t =Tournament.query.first()
        response = self.client.post('/tournament/'+str(t.id)+'/delete/')
        self.assertEqual(0, Tournament.query.count())

    def test_it_can_not_edit_tournament_marked_submitted(self):
        tournament_edit_endpoint = self.tournament_endpoint + \
            str(self.tournament_1.id) + '/edit'
        t = Tournament.query.first()
        #  mark tournament as submitted
        response = self.client.post(
            '/tournament/'+ str(t.id)+'/edit/', #  url_for()
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
                   "tie_break1": t.tie_break1,
                   "tie_break2": t.tie_break2,
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
            '/tournament/'+ str(t.id)+'/edit/', #  url_for()
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
                   "tie_break1": t.tie_break1,
                   "tie_break2": t.tie_break2,
                   "submitted": True })
        response = self.client.post('/tournament/'+str(t.id)+'/delete/')
        tournaments_after = Tournament.query.count()
        self.assertEqual(tournaments_before, tournaments_after)
