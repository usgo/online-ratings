from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import SQLAlchemyUserDatastore, UserMixin, RoleMixin
from sqlalchemy.orm import relationship
import datetime
from collections import namedtuple

db = SQLAlchemy()

#used by ext.security
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('myuser.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
) 

go_server_admins = db.Table(
    'go_server_admin',
    db.Column('user_id', db.Integer, db.ForeignKey('myuser.id')),
    db.Column('server_id', db.Integer, db.ForeignKey('go_server.id'))
)

_Role = namedtuple("_Role", "name description")
RATINGS_ADMIN_ROLE = _Role("ratings_admin", "Admin of AGA-Online Ratings")
SERVER_ADMIN_ROLE = _Role("server_admin", "Admin of a Go Server")
USER_ROLE = _Role("user", "Default role")


# Define models
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__="myuser"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
        return self.has_role(SERVER_ADMIN_ROLE.name)

    def is_ratings_admin(self):
        return self.has_role(RATINGS_ADMIN_ROLE.name)

    def last_rating(self):
        return Rating.query.filter(Rating.user_id == self.id).order_by(Rating.created.desc()).limit(1).first()

    def __str__(self):
        return "AGA %s, %s" % (self.aga_id, self.email)

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
    user_id = db.Column(db.Integer, db.ForeignKey('myuser.id'))
    user = db.relationship('User', foreign_keys=user_id)
    server = db.relationship('GoServer',
                              foreign_keys=server_id,
                              backref=db.backref('server_id',
                                                 lazy='dynamic'))
    token = db.Column(db.Text, unique=True)

    def __str__(self):
        return "Player %s on server %s, user %s" % (self.name, self.server_id, self.user_id)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('myuser.id'))
    user = db.relationship('User',
                             foreign_keys=user_id,
                             backref=db.backref('user_rating', lazy='dynamic'))
    sigma = db.Column(db.Float)
    rating = db.Column(db.Float)
    created = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    def __str__(self):
        return "(%f, sigma %f) for player %d" % (self.rating, self.sigma, self.player_id) 

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
    rated = db.Column(db.Boolean) #has the game been rated.
    game_record = db.Column(db.LargeBinary)
    game_url = db.Column(db.String(100))

    handicap = db.Column(db.Integer, default=0)
    komi = db.Column(db.Float, default=7.5)

    def __str__(self):
        return "%s (w) vs %s (b) %dH (%f), played on %s, result %s" % (self.white.name, self.black.name, self.handicap, self.komi, self.game_server, self.result)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
