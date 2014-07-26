
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin

from app import db, app

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
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


# Other models.
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(80))
    go_server_id = db.Column(db.Integer, db.ForeignKey('go_server.id'))
    go_server = db.relationship('GoServer', backref=db.backref('players', lazy='dynamic'))

class Key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    player = db.relationship('Player', backref=db.backref('keys', lazy='dynamic'))
    go_server_id = db.Column(db.Integer, db.ForeignKey('go_server.id'))
    go_server = db.relationship('GoServer')

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    white_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    black_id = db.Column(db.Integer, db.ForeignKey('player.id')) 
    date_played = db.Column(db.DateTime)
    reported = db.Column(db.DateTime)
    rated = db.Column(db.Boolean)
    sgf = db.Column(db.LargeBinary)

class GoServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    url = db.Column(db.String(180))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore) 

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='foo@foo.bar', password='baz')
    user_datastore.create_role(name='user', description='default role')
    user_datastore.create_role(name='server_admin', description='Admin of a Go Server')
    user_datastore.create_role(name='ratings_admin', description='Admin of AGA-Online Ratings')
    db.session.commit()

