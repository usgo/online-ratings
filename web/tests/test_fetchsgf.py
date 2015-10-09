from app.models import db, Game
from app import api_1_0 as api
from tests import BaseTestCase

class TestFetchSgf(BaseTestCase): 

    def test_Fetch_Sgf(self): 
        app = self.create_app()
        g = Game(server_id=1, white_id=1, black_id=2, rated=True, result="B+0.5",
             game_url="http://files.gokgs.com/games/2015/3/3/Clutter-underkey.sgf")
        db.session.add(g)
        db.session.commit()
        api.game_result.fetch_sgf(1, "http://files.gokgs.com/games/2015/3/3/Clutter-underkey.sgf") 

