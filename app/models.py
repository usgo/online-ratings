from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin
from app import db, app

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


class GoServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    url = db.Column(db.String(180))
    token = db.Column(db.String(80))


class GoServerAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(80))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('user', lazy='dynamic'))

    go_server_id = db.Column(db.Integer, db.ForeignKey('go_server.id'))
    go_server = db.relationship('GoServer',
                                backref=db.backref('go_server',
                                                   lazy='dynamic'))

    token = db.Column(db.String(80))


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    white_id = db.Column(db.Integer, db.ForeignKey('go_server_account.id'))
    white = db.relationship('GoServerAccount',
                            foreign_keys=white_id,
                            backref=db.backref('w_server_account',
                                               lazy='dynamic'))

    black_id = db.Column(db.Integer, db.ForeignKey('go_server_account.id'))
    black = db.relationship('GoServerAccount',
                            foreign_keys=black_id,
                            backref=db.backref('b_server_account',
                                               lazy='dynamic'))

    date_played = db.Column(db.DateTime)
    date_reported = db.Column(db.DateTime)

    result = db.Column(db.String(10))
    rated = db.Column(db.Boolean)
    game_record = db.Column(db.LargeBinary)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create data for testing
@app.before_first_request
def create_test_data():
    db.create_all()

    user_datastore.create_user(email='foo@foo.com', password='foo')
    user_datastore.create_user(email='bar@bar.com', password='bar')
    user_datastore.create_user(email='baz@baz.com', password='baz')
    user_datastore.create_role(name='user', description='default role')
    user_datastore.create_role(name='server_admin',
                               description='Admin of a Go Server')
    user_datastore.create_role(name='ratings_admin',
                               description='Admin of AGA-Online Ratings')

    db.session.add(GoServer(name='KGS',
                            url='http://gokgs.com',
                            token='secret-kgs'))
    db.session.add(GoServer(name='IGS',
                            url='http://pandanet.com',
                            token='secret-igs'))

    db.session.add(GoServerAccount(nick='Foo',
                                   user_id=1,
                                   go_server_id=1,
                                   token='secret_foo'))
    db.session.add(GoServerAccount(nick='Bar',
                                   user_id=2,
                                   go_server_id=1,
                                   token='secret_bar'))
    db.session.add(GoServerAccount(nick='Baz',
                                   user_id=3,
                                   go_server_id=2,
                                   token='secret_baz'))

    db.session.add(Game(white_id=1, black_id=2, rated=True, result="B+0.5"))
    db.session.add(Game(white_id=1, black_id=2, rated=True, result="W+39.5"))
    db.session.add(Game(white_id=1, black_id=2, rated=True, result="W+Resign"))

    db.session.commit()
