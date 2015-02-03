from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask.ext.security.utils import encrypt_password

db = SQLAlchemy()

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


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
    token = db.Column(db.Text, unique=True)


class GoServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    url = db.Column(db.String(180))
    token = db.Column(db.Text, unique=True)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    server_id = db.Column(db.Integer, db.ForeignKey('go_server.id'))
    game_server = db.relationship('GoServer',
                                  foreign_keys=server_id,
                                  backref=db.backref('game_server_id',
                                                     lazy='dynamic'))

    white_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    white = db.relationship('User',
                            foreign_keys=white_id,
                            backref=db.backref('w_server_account',
                                               lazy='dynamic'))

    black_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    black = db.relationship('User',
                            foreign_keys=black_id,
                            backref=db.backref('b_server_account',
                                               lazy='dynamic'))

    date_played = db.Column(db.DateTime)
    date_reported = db.Column(db.DateTime)

    result = db.Column(db.String(10))
    rated = db.Column(db.Boolean)
    game_record = db.Column(db.LargeBinary)

    def __str__(self):
        return "Game between %d (b) and %d (w), result %s" % (self.black_id, self.white_id, self.result)


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
                                   token='secret_usgo', id=99)
    user_datastore.add_role_to_user(u, role_aga_admin)

    u = user_datastore.create_user(email='admin@kgs.com',
                                   password=encrypt_password('kgs'),
                                   token='secret_kgs', id=109)
    user_datastore.add_role_to_user(u, role_gs_admin)

    u = user_datastore.create_user(email='foo@foo.com',
                                   password=encrypt_password('foo'),
                                   token='secret_foo',
                                   id=1)
    user_datastore.add_role_to_user(u, role_user)

    u = user_datastore.create_user(email='bar@bar.com',
                                   password=encrypt_password('bar'),
                                   token='secret_bar',
                                   id=2)
    user_datastore.add_role_to_user(u, role_user)

    u = user_datastore.create_user(email='baz@baz.com',
                                   password=encrypt_password('baz'),
                                   token='secret_baz')
    user_datastore.add_role_to_user(u, role_user)


    db.session.add(GoServer(name='KGS',
                            url='http://gokgs.com',
                            token='secret_kgs'))
    db.session.add(GoServer(name='IGS',
                            url='http://pandanet.com',
                            token='secret_igs'))

    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="B+0.5"))
    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="W+39.5"))
    db.session.add(Game(server_id=2, white_id=1, black_id=2, rated=True, result="W+Resign"))

    db.session.commit()
