from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import SQLAlchemyUserDatastore, UserMixin, RoleMixin
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)

class User(db.Model, UserMixin):
    __tablename__="myuser"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aga_id = db.Column(db.String(25))
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), default="", nullable=False)
    password = db.Column(db.String(255))
    fake = db.Column(db.Boolean, default=False, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(25))
    current_login_ip = db.Column(db.String(25))
    login_count = db.Column(db.Integer, default=0, nullable=False)
    players = relationship("Player")

    # For every AGA member, a fake user (aga_id, fake=True) is created.
    # (This fake user holds onto their real life game history for them.)
    # When that AGA member signs up, they gets (aga_id, fake=False).
    # Thus, only one fake and one real user can ever exist for an aga_id.
    __table_args__ = (
        db.Index("aga_id__fake", "aga_id", "fake", unique=True),
    )

    def is_server_admin(self):
        return self.has_role(SERVER_ADMIN_ROLE.name)

    def is_ratings_admin(self):
        return self.has_role(RATINGS_ADMIN_ROLE.name)

    def can_reset_server_token(self, server):
        return (self.is_ratings_admin() or
            (self.is_server_admin() and server.admins.filter(User.id == self.id).count()))

    def can_reset_player_token(self, player):
        return (self.is_ratings_admin() or
                self.id == player.user_id)

    def last_rating(self):
        return Rating.query.filter(Rating.user_id == self.id).order_by(Rating.created.desc()).limit(1).first()

    def __str__(self):
        return "AGA %s, %s" % (self.aga_id, self.email)

class GoServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    url = db.Column(db.String(180), nullable=False)
    token = db.Column(db.Text, unique=True, nullable=False)
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
    name = db.Column(db.String(20), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('go_server.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('myuser.id'), nullable=False)
    user = db.relationship('User', foreign_keys=user_id)
    server = db.relationship('GoServer',
                              foreign_keys=server_id,
                              backref=db.backref('server_id',
                                                 lazy='dynamic'))
    token = db.Column(db.String(100), unique=True, nullable=False)

    def __str__(self):
        return "Player %s on server %s, user %s" % (self.name, self.server_id, self.user_id)

    def to_dict(self):
        last_rating = self.user.last_rating()
        return {
            "id": self.id,
            "name": self.name,
            "server_id": self.server_id,
            "rating": None if not last_rating else last_rating.rating
        }

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('myuser.id'), nullable=False)
    user = db.relationship('User',
                             foreign_keys=user_id,
                             backref=db.backref('user_rating', lazy='dynamic'))
    sigma = db.Column(db.Float, nullable=True) # Not all rating algorithms use sigma
    rating = db.Column(db.Float, nullable=False)
    created = db.Column(db.DateTime, onupdate=datetime.datetime.now, index=True)

    def __str__(self):
        return "(%f) for user %d" % (self.rating, self.user_id)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    server_id = db.Column(db.Integer, db.ForeignKey('go_server.id'), nullable=False)
    game_server = db.relationship('GoServer',
                                  foreign_keys=server_id,
                                  backref=db.backref('game_server_id',
                                                     lazy='dynamic'))

    white_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    white = db.relationship('Player',
                            foreign_keys=white_id,
                            backref=db.backref('w_server_account',
                                               lazy='dynamic'))

    black_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    black = db.relationship('Player',
                            foreign_keys=black_id,
                            backref=db.backref('b_server_account',
                                               lazy='dynamic'))

    date_played = db.Column(db.DateTime, nullable=False)
    date_reported = db.Column(db.DateTime, nullable=False, default=func.now())

    result = db.Column(db.String(10), nullable=False)
    rated = db.Column(db.Boolean, nullable=False, default=False) #has the game been rated.
    game_record = db.Column(db.LargeBinary)
    game_url = db.Column(db.String(100))

    handicap = db.Column(db.Integer, default=0, nullable=False)
    komi = db.Column(db.Float, default=7.5, nullable=False)

    def __str__(self):
        return "%s-%d (w) vs %s-%d (b) %s handicap, %s komi, played on %s, result %s" % (
                self.white.name, self.white_id,
                self.black.name, self.black_id,
                self.handicap, self.komi, self.game_server, self.result)

    def to_dict(self):
        return {
            "id": self.id,
            "white_id": self.white_id,
            "black_id": self.black_id,
            "server_id": self.server_id,
            "date_played": self.date_played.isoformat(),
            "date_reported": self.date_reported.isoformat(),
            "result": self.result,
            "handicap": self.handicap,
            "komi": self.komi,
        }

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
