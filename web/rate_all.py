import os, random, datetime

from app.models import user_datastore, Player, Game, User, Rating
from app import app, db
import rating.rating_math as rm

def rate_all():
    users = User.query.all()
    games = Game.query.all() 

    for g in games:
        if g.white.user_id is None or g.black.user_id is None:
            print(g) #should probably strip them.

    # Vector of result_tuples.  Just what we need to compute stuff...
    g_vec = [(g.white.user_id, 
             g.black.user_id,
             1.0 if g.result.startswith('W') else 0.0,
             g.date_played) for g in games]

    users_with_games = set([g[1] for g in g_vec])
    users_with_games.union(set([g[0] for g in g_vec]))
    print('before:', len(users))
    users = [u for u in users if u.id in users_with_games]
    print('after:', len(users))

    ratings = {u.id: u.last_rating() for u in users}
    rating_prior = {u: v.rating if (v and v.rating) else 0 for u,v in ratings.items()}


    neighbors = rm.neighbors(games)
    neighbor_avgs = rm.compute_avgs(games, rating_prior) 

    t_min = min(games, key=lambda g: g.date_played or datetime.datetime.now()).date_played
    t_max = max(games, key=lambda g: g.date_played or datetime.datetime.now()).date_played

    iters = 100
    lam = .37 # Weight for controlling 'pull' of neighborhood weighted average. Higher = stays in the neighborhood.  
    lrn = lambda i: ((1. + .1*iters)/(i + .1 * iters))**.6 #Control the learning rate over time.

    for i in range(iters):
        loss = 0
        # Accumulate the neighborhood loss prior to changing the ratings around
        for id, neighbor_wgt in neighbor_avgs.items():
            loss += lam * ((rating_prior[id] - neighbor_wgt) ** 2)

        # Shuffle the vector of result-tuples
        random.shuffle(g_vec)
        for g in g_vec:
            w, b, actual, t = g
            odds = rm.expect(rating_prior[b], rating_prior[w])
            weight = rm.time_weight(t, t_min, t_max)
            rating_prior[w] -= lrn(i) * (weight*(odds - actual)*odds*(1-odds) + (lam/len(neighbors[w]) * (rating_prior[w] - neighbor_avgs[w])))
            rating_prior[b] -= lrn(i) * (-1.0 * weight*(odds - actual)*odds*(1-odds) + (lam/len(neighbors[b]) * (rating_prior[b] - neighbor_avgs[b])))
            loss += weight * ((odds - actual) ** 2)

        # Scale the ratings
        r_min = min(rating_prior.values())
        r_max = max(rating_prior.values()) 
        if r_max != r_min:
            for k,v in rating_prior.items():
                rating_prior[k] = (rating_prior[k] - r_min) / (r_max - r_min) * 40.0

        neighbor_avgs = rm.compute_avgs(games, rating_prior) 
        print('%d : %.4f' % (i, loss))

    # Update the ratings and show how we did.
    wins, losses = {}, {}
    for g in g_vec:
        wins[g[0]] = wins.get(g[0], 0) + g[2]
        losses[g[0]] = losses.get(g[0], 0) + 1-g[2]
        wins[g[1]] = wins.get(g[1], 0) + 1-g[2]
        losses[g[1]] = losses.get(g[1], 0) + g[2]

    
    for k in sorted(rating_prior, key=lambda k: rating_prior[k]): 
        db.session.add(Rating(user_id=k, rating=rating_prior[k]))
        print("%d: %f (%d - %d)" % (k,rating_prior[k], wins.get(k,0), losses.get(k,0)) )
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

