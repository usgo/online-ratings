from app import get_app
from app.models import db, Game, GoServer, Player, User
from app.tokengen import generate_token
from flask.ext.script import Command, Option
from scripts.parsing import agagd_parser, pin_change_parser
from uuid import uuid4

'''
Script which loads game and user data from an AGAGD SQL dump and file with PIN changes.
'''


def create_server(name):
        server = GoServer()
        server.name = name
        server.url = ''
        server.token = generate_token()
        db.session.add(server)
        db.session.commit()
        return server.id


class RealLifeGoServerLoader(Command):
    '''
    Class which holds a little bit of state used while loading the AGAGD data.
    '''

    option_list = (
                   Option('--sql_dump', '-d', dest='agagd_dump_filename'),
                   Option('--pin_changes', '-p', dest='pin_change_dump_filename')
                  )

    def setup(self, pin_change_dump_filename):
        '''
        Stand-in for __init__ because we don't have necessary information
        at construction time, and we are constructed regardless of whether
        this script is being run or not.
        '''
        name = 'Real Life Go Server'
        server = db.session.query(GoServer).filter_by(name=name).first()
        if server:
            self.server_id = server.id
        else:
            print('Creating RLGS Server object')
            self.server_id = create_server(name)

        self._users = {}

        # map: old_pin -> new_pin
        with open(pin_change_dump_filename) as f:
            self._pin_changes = {line['old']: line['new'] for line in pin_change_parser(f)
                                 if line['old'] != line['new']}  # Prevents infinite lookup loops

    def get_or_make_user(self, aga_id):
        '''
        Returns the User object for the given AGA ID or creates it and an RLGS
        player if it does not exist.
        If the AGA ID has had one or more PIN changes, the most recent ID will
        be used.
        '''
        while aga_id in self._pin_changes:
            aga_id = self._pin_changes[aga_id]
        if aga_id in self._users:
            return self._users[aga_id]
        else:
            user = User(aga_id=aga_id, email=uuid4())
            player = Player(id=aga_id, name='', user_id=user.id, server_id=self.server_id)

            db.session.add(user)
            db.session.add(player)

            self._users[aga_id] = user
            return user

    def store_game(self, row):
        user1 = self.get_or_make_user(row['Pin_Player_1'])
        user2 = self.get_or_make_user(row['Pin_Player_2'])

        white_user, black_user = (user1, user2) if row['Color_1'] == 'W' else (user2, user1)
        game = Game(id=row['Game_ID'],
                    server_id=self.server_id,
                    white_id=white_user.aga_id,
                    black_id=black_user.aga_id,
                    date_played=row['Game_Date'],
                    date_reported=row['Game_Date'],
                    result=row['Result'],
                    rated=row['Rated'],
                    handicap=row['Handicap'],
                    komi=row['Komi'])
        db.session.add(game)

    def load_data(self, filename):
        # server_id = create_server()
        with open(filename) as f:
            for i, row in enumerate(agagd_parser(f)):
                if i % 1000 == 0:
                    print('Loading row', i)
                self.store_game(row)

    def run(self, agagd_dump_filename, pin_change_dump_filename, app=None):
        if app is None:
            app = get_app('config.DockerConfiguration')
        with app.app_context():
            self.setup(pin_change_dump_filename)
            self.load_data(agagd_dump_filename)


def main():
    import sys
    loader = RealLifeGoServerLoader()
    app = get_app('config.TestConfiguration')
    with app.app_context():
        db.create_all()

    loader.run(sys.argv[1], sys.argv[2], app=app)

if __name__ == '__main__':
    main()
