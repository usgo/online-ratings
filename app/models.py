from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask.ext.security.utils import encrypt_password
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


#used by ext.security
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    aga_id = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(25))
    current_login_ip = db.Column(db.String(25))
    login_count = db.Column(db.Integer)
    players = relationship("Player")

    def is_server_admin(self):
        return self.has_role('server_admin')

    def is_ratings_admin(self):
        return self.has_role('ratings_admin')

    def __str__(self):
        return "AGA %s, %s" % (self.aga_id, self.email)

go_server_admins = db.Table(
    'go_server_admin',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('server_id', db.Integer, db.ForeignKey('go_server.id'))
)

class GoServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    url = db.Column(db.String(180))
    token = db.Column(db.Text, unique=True)
    players = db.relationship('Player')
    admins = db.relationship(
        'User',
        secondary=go_server_admins,
        backref=db.backref('servers', lazy='dynamic'),
        lazy='dynamic'
    )

    def __str__(self):
        return self.name

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    server_id = db.Column(db.Integer, db.ForeignKey('go_server.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=user_id)
    server = db.relationship('GoServer',
                              foreign_keys=server_id,
                              backref=db.backref('server_id',
                                                 lazy='dynamic'))
    token = db.Column(db.Text, unique=True)

    def __str__(self):
        return "Player %s on server %s, user %s" % (self.name, self.server_id, self.user_id)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    server_id = db.Column(db.Integer, db.ForeignKey('go_server.id'))
    game_server = db.relationship('GoServer',
                                  foreign_keys=server_id,
                                  backref=db.backref('game_server_id',
                                                     lazy='dynamic'))

    white_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    white = db.relationship('Player',
                            foreign_keys=white_id,
                            backref=db.backref('w_server_account',
                                               lazy='dynamic'))

    black_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    black = db.relationship('Player',
                            foreign_keys=black_id,
                            backref=db.backref('b_server_account',
                                               lazy='dynamic'))

    date_played = db.Column(db.DateTime)
    date_reported = db.Column(db.DateTime)

    result = db.Column(db.String(10))
    rated = db.Column(db.Boolean)
    game_record = db.Column(db.LargeBinary)
    game_url = db.Column(db.String(100))

    def __str__(self):
        return "%s (w) vs %s (b), played on %s, result %s" % (self.white.name, self.black.name, self.game_server, self.result)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


# Create data for testing
def create_test_data():
    role_user = user_datastore.create_role(
        name='user',
        description='default role'
    )
    role_gs_admin = user_datastore.create_role(
        name='server_admin',
        description='Admin of a Go Server'
    )
    role_aga_admin = user_datastore.create_role(
        name='ratings_admin',
        description='Admin of AGA-Online Ratings'
    )

    u = user_datastore.create_user(email='admin@usgo.org',
                                   password=encrypt_password('usgo'),
                                   id=99)
    user_datastore.add_role_to_user(u, role_aga_admin)

    kgs_admin = user_datastore.create_user(email='admin@kgs.com',
                                           password=encrypt_password('kgs'),
                                           id=109)
    user_datastore.add_role_to_user(kgs_admin, role_gs_admin)

    u = user_datastore.create_user(email='foo@foo.com',
                                   password=encrypt_password('foo'),
                                   id=1)
    db.session.add(Player(id=1,name="FooPlayerKGS",server_id=1,user_id=1,token="secret_foo_KGS"))
    db.session.add(Player(id=4,name="FooPlayerIGS",server_id=2,user_id=1,token="secret_foo_IGS"))
    user_datastore.add_role_to_user(u, role_user)

    u = user_datastore.create_user(email='bar@bar.com',
                                   password=encrypt_password('bar'),
                                   id=2)
    db.session.add(Player(id=2,name="BarPlayerKGS",server_id=1,user_id=2,token="secret_bar_KGS"))
    db.session.add(Player(id=5,name="BarPlayerIGS",server_id=2,user_id=2,token="secret_bar_IGS"))
    user_datastore.add_role_to_user(u, role_user)

    u = user_datastore.create_user(email='baz@baz.com',
                                   password=encrypt_password('baz'),
                                   id=3)
    db.session.add(Player(id=3,name="BazPlayerKGS",server_id=1,user_id=3,token="secret_baz_KGS"))
    db.session.add(Player(id=6,name="BazPlayerIGS",server_id=2,user_id=3,token="secret_baz_IGS"))
    user_datastore.add_role_to_user(u, role_user)


    gs = GoServer(id=1, name='KGS', url='http://gokgs.com', token='secret_kgs')
    gs.admins.append(kgs_admin)
    db.session.add(gs)
    db.session.add(GoServer(id=2, name='IGS',
                            url='http://pandanet.com',
                            token='secret_igs'))

    with open('tests/testsgf.sgf') as sgf_file:
        sgf_data = "\n".join(sgf_file.readlines()).encode()

    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="B+0.5", game_record=sgf_data))
    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="W+39.5", game_record=sgf_data))
    db.session.add(Game(server_id=2, white_id=5, black_id=4, rated=True, result="W+Resign", game_record=sgf_data))
    db.session.add(Game(server_id=2, white_id=5, black_id=4, rated=True, result="W+Resign", game_record=sgf_data))
    db.session.add(Game(server_id=2, white_id=6, black_id=5, rated=True, result="W+Resign", game_record=sgf_data))
    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="B+0.5", game_record=sgf_data))
    db.session.add(Game(server_id=1, white_id=3, black_id=2, rated=True, result="W+39.5", game_record=sgf_data))
    db.session.add(Game(server_id=2, white_id=5, black_id=6, rated=True, result="W+Resign", game_record=sgf_data))

    db.session.commit()
