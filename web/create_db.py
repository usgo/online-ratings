from app.models import user_datastore, Player, GoServer, Game
from app import app, db
from flask.ext.security.utils import encrypt_password 

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
                                   aga_id=10,
                                   password=encrypt_password('foo'),
                                   id=1)
    db.session.add(Player(id=1,name="FooPlayerKGS",server_id=1,user_id=1,token="secret_foo_KGS"))
    db.session.add(Player(id=4,name="FooPlayerIGS",server_id=2,user_id=1,token="secret_foo_IGS"))
    user_datastore.add_role_to_user(u, role_user)

    u = user_datastore.create_user(email='bar@bar.com',
                                   aga_id=20,
                                   password=encrypt_password('bar'),
                                   id=2)
    db.session.add(Player(id=2,name="BarPlayerKGS",server_id=1,user_id=2,token="secret_bar_KGS"))
    db.session.add(Player(id=5,name="BarPlayerIGS",server_id=2,user_id=2,token="secret_bar_IGS"))
    user_datastore.add_role_to_user(u, role_user)

    u = user_datastore.create_user(email='baz@baz.com',
                                   aga_id=30,
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

    with open('../tests/testsgf.sgf') as sgf_file:
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


if __name__ == '__main__': 
    with app.app_context():
        db.drop_all()
        db.session.commit()
        db.create_all()
        create_test_data()
