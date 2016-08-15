import datetime
import os
import random

from flask.ext.security.utils import encrypt_password 

from app import get_app
from app.models import user_datastore, Player, GoServer, Game, User, RATINGS_ADMIN_ROLE, SERVER_ADMIN_ROLE, USER_ROLE, db


def create_roles():
    role_user = user_datastore.create_role(**USER_ROLE._asdict())
    role_gs_admin = user_datastore.create_role(**SERVER_ADMIN_ROLE._asdict())
    role_aga_admin = user_datastore.create_role(**RATINGS_ADMIN_ROLE._asdict())
    db.session.commit()
    return role_user, role_gs_admin, role_aga_admin

def create_user(email, password, role, **kwargs):
    u = user_datastore.create_user(email=email, password=encrypt_password(password), **kwargs)
    user_datastore.add_role_to_user(u, role)
    db.session.commit()
    return u

def create_server(**kwargs):
    gs = GoServer(**kwargs)
    db.session.add(gs)
    db.session.commit()
    return gs

def create_test_data():
    role_user, role_gs_admin, role_aga_admin = create_roles()
    superadmin = create_user("admin@usgo.org", "usgo", role_aga_admin)
    kgs_admin = create_user("admin@gokgs.com", "kgs", role_gs_admin)
    ogs_admin = create_user("admin@ogs.com", "ogs", role_gs_admin)
    foo_user = create_user("foo@foo.com", "foo", role_user, aga_id=10)
    bar_user = create_user("bar@bar.com", "bar", role_user, aga_id=20)
    baz_user = create_user("baz@baz.com", "baz", role_user, aga_id=30)

    kgs_server = create_server(name="KGS", url="http://gokgs.com", token="secret_kgs")
    kgs_server.admins.append(kgs_admin)
    db.session.add(kgs_server)

    ogs_server = create_server(name="OGS", url="http://online-go.com", token="secret_ogs")
    ogs_server.admins.append(ogs_admin)
    db.session.add(ogs_server)

    db.session.commit()

    db.session.add(Player(id=1, name="FooPlayerKGS", server_id=kgs_server.id, user_id=foo_user.id,token="secret_foo_KGS"))
    db.session.add(Player(id=4, name="FooPlayerOGS", server_id=ogs_server.id, user_id=foo_user.id,token="secret_foo_OGS"))
    db.session.add(Player(id=2, name="BarPlayerKGS", server_id=kgs_server.id, user_id=bar_user.id,token="secret_bar_KGS"))
    db.session.add(Player(id=5, name="BarPlayerOGS", server_id=ogs_server.id, user_id=bar_user.id,token="secret_bar_OGS"))
    db.session.add(Player(id=3, name="BazPlayerKGS", server_id=kgs_server.id, user_id=baz_user.id,token="secret_baz_KGS"))
    db.session.add(Player(id=6, name="BazPlayerOGS", server_id=ogs_server.id, user_id=baz_user.id,token="secret_baz_OGS"))


    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, 'tests/testsgf.sgf'), 'rb') as sgf_file:
        sgf_data = sgf_file.read()

    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="B+0.5", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="W+39.5", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=2, white_id=5, black_id=4, rated=True, result="W+Resign", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=2, white_id=5, black_id=4, rated=True, result="W+Resign", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=2, white_id=6, black_id=5, rated=True, result="W+Resign", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="B+0.5", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=1, white_id=3, black_id=2, rated=True, result="W+39.5", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))
    db.session.add(Game(server_id=2, white_id=5, black_id=6, rated=True, result="W+Resign", game_record=sgf_data,
        date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,1000000))))

    db.session.commit()

    try:
        # needed to reset the postgresql autoincrement counter
        db.engine.execute("SELECT setval('myuser_id_seq', (SELECT MAX(id) FROM myuser))")
        db.engine.execute("SELECT setval('player_id_seq', (SELECT MAX(id) FROM player))")
    except:
        pass


def create_extra_data():
    basedir = os.path.abspath(os.path.dirname(__file__))

    #Make a bunch of example users
    with open(os.path.join(basedir, 'tests/testsgf.sgf')) as sgf_file:
        sgf_data = "\n".join(sgf_file.readlines()).encode()
    role_user = user_datastore.find_role('user')
    users = []
    for i in range(60):
        u = User(email='bla%d@example.com'%i, aga_id = 100000+i, password=encrypt_password('test'))
        user_datastore.add_role_to_user(u,role_user)
        db.session.add(u)
        users.append(u)
    db.session.commit()

    for u in users:
        for j in range(2):
            db.session.add(Player(name="Player-%d-%d" % (u.id,j), server_id=1, user_id=u.id, token="Player-%d-%d" % (u.id,j)))

    db.session.commit()

    users = User.query.all()
    players = Player.query.all()
    p_priors = {user.id: random.randint(0,40) for user in users}
    print("Prior ratings")
    for p in sorted(p_priors, key=lambda k: p_priors[k]):
        print("%d: %f" % (p,p_priors[p]))

    import rating.rating_math as rm
    def choose_pair():
        while True:
            pair = random.sample(users, 2)
            diff = abs(p_priors[pair[0].id] - p_priors[pair[1].id])
            if len(pair[0].players) > 0 and len(pair[1].players) > 0 and diff < 10:
                break
        return pair

    def make_game():
        user_pair = choose_pair()
        ps = (random.choice(user_pair[0].players).id, random.choice(user_pair[1].players).id)
        result = "B+5" if random.random() < rm.expect(p_priors[user_pair[0].id], p_priors[user_pair[1].id], 0, 6.5) else "W+5"
        g = Game(server_id=1, white_id=ps[0], black_id=ps[1],
                rated=False, result=result, game_record=sgf_data,
                date_played=datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0,10000000)))
        return g

    print("Games...")
    games = [make_game() for i in range(2000)]
    print("Saving games...")
    for g in games:
        db.session.add(g)
    db.session.commit() 
    strongest = max(p_priors, key = lambda k: p_priors[k])
    strongest_games = [str(g) for g in games if g.white.user_id == strongest or g.black.user_id == strongest]
    print("Strongest, %d (%f):\n%s"% (strongest, p_priors[strongest], strongest_games))

if __name__ == '__main__':
    app = get_app('config.DockerConfiguration')
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.get_engine(app).dispose()
        print('Creating tables...')
        db.create_all()
        print('Creating test data...')
        create_test_data()
        print('Creating rating data...')
        create_extra_data()
