import os, random, datetime

from app.models import user_datastore, Player, Game, User, Rating
from app import app, db
import rating.rating_math as rm

def rate_all():
    users = User.query.all()
    games = Game.query.all()

    ratings = {u.id: u.last_rating() for u in users}
    rating_prior = {u: v.rating if (v and v.rating) else 0 for u,v in ratings.items()}

    for g in games:
        if g.white.user_id is None or g.black.user_id is None:
            print(g)

    g_vec = [(g.white.user_id, 
             g.black.user_id,
             1.0 if g.result.startswith('W') else 0.0,
             g.date_played) for g in games]

    neighbors = rm.neighbors(games)
    neighbor_avgs = rm.compute_avgs(games, rating_prior) 

    tmin = min(games, key=lambda g: g.date_played or datetime.datetime.now()).date_played
    tmax = max(games, key=lambda g: g.date_played or datetime.datetime.now()).date_played

    iters = 100
    lam = .27
    lrn = lambda i: ((1. + .1*iters)/(i + .1 * iters))**.6
    for i in range(iters):
        random.shuffle(g_vec)
        loss = 0
        for id, neighbor_wgt in neighbor_avgs.items():
            loss += lam * ((rating_prior[id] - neighbor_wgt) ** 2)
        for g in g_vec:
            w, b, actual, t = g
            odds = rm.expect(rating_prior[b], rating_prior[w])
            weight = rm.time_weight(t, tmin, tmax)
            rating_prior[w] -= lrn(i) * (weight*(odds - actual)*odds*(1-odds) + (lam/len(neighbors[w]) * (rating_prior[w] - neighbor_avgs[w])))
            rating_prior[b] -= lrn(i) * (-1.0 * weight*(odds - actual)*odds*(1-odds) + (lam/len(neighbors[b]) * (rating_prior[b] - neighbor_avgs[b])))
            loss += weight * ((odds - actual) ** 2)

        min_r = min(rating_prior.values())
        max_r = max(rating_prior.values())
        if max_r != min_r:
            for k,v in rating_prior.items():
                rating_prior[k] = (rating_prior[k] - min_r) / (max_r - min_r) * 40.0

        neighbor_avgs = rm.compute_avgs(games, rating_prior) 
        print('%d : %.4f' % (i, loss))

    for k in sorted(rating_prior, key=lambda k: rating_prior[k]): 
        db.session.add(Rating(user_id=k, rating=rating_prior[k]))
        print(k,rating_prior[k])
    db.session.commit()

if __name__ == '__main__': 
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--service", help="The DB service")
    args = parser.parse_args()
    app.config.from_object('config.DebugConfiguration')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
    DB_SERVICE = args.service or os.environ.get('DB_SERVICE')
    DB_PORT = os.environ.get('DB_PORT')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI 
    with app.app_context():
        #db.session.remove()
        #Rating.__table__.drop(db.engine)
        #db.get_engine(app).dispose()
        #db.create_all()
        rate_all()

