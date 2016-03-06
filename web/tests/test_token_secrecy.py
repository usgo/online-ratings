import os

from app.models import user_datastore, GoServer
from tests import BaseTestCase

class TestTokenSecrecy(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.ratings_admin = user_datastore.get_user("admin@usgo.org")
        self.kgs_admin = user_datastore.get_user("admin@kgs.com")
        self.random_user = user_datastore.get_user("foo@foo.com")
        self.kgs_game_server = GoServer.query.filter(GoServer.name=="KGS").first()
        self.igs_game_server = GoServer.query.filter(GoServer.name=="IGS").first()

    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_ratings_admin_can_see_all_server_tokens(self):
        self.login(self.ratings_admin.email, self.ratings_admin.password)
        kgs_game_page = os.path.join('/game_servers/', str(self.kgs_game_server.id))
        response = self.client.get(kgs_game_page)
        self.assertIn(self.kgs_game_server.token, response.data.decode('utf8'))
        self.logout()

    def test_kgs_admin_can_see_own_server_token(self):
        self.login(self.kgs_admin.email, self.kgs_admin.password)
        kgs_game_page = os.path.join('/game_servers/', str(self.kgs_game_server.id))
        response = self.client.get(kgs_game_page)
        self.assertIn(self.kgs_game_server.token, response.data.decode('utf8'))
        igs_game_page = os.path.join('/game_servers/', str(self.igs_game_server.id))
        response = self.client.get(igs_game_page)
        self.assertNotIn(self.igs_game_server.token, response.data.decode('utf8'))
        self.logout()

    def test_random_person_cant_see_tokens(self):
        self.login(self.random_user.email, self.random_user.password)
        kgs_game_page = os.path.join('/game_servers/', str(self.kgs_game_server.id))
        response = self.client.get(kgs_game_page)
        self.assertNotIn(self.kgs_game_server.token, response.data.decode('utf8'))
        igs_game_page = os.path.join('/game_servers/', str(self.igs_game_server.id))
        response = self.client.get(igs_game_page)
        self.assertNotIn(self.igs_game_server.token, response.data.decode('utf8'))
        self.logout()
