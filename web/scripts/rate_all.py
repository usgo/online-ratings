import random, datetime

from app.models import Game, User, Rating, db
from flask.ext.script import Command, Option
import rating.rating_math as rm

def sanitized_users(g_vec):
    """ Strip out users with no games from our list """
    users = User.query.all() 
    users_with_games = set([g[0] for g in g_vec])
    users_with_games = users_with_games.union(set([g[1] for g in g_vec]))
    new_users = [u for u in users if u.aga_id and int(u.aga_id) in users_with_games] # aga_id is text?!?
    return new_users

def sanitized_games(games):
    """ Sanitizes a list of games into result tuples for rating.
    A result tuple is the form (w, b, result, date, handicap, komi)
    Where 'result' is 1 if w won and 0 otherwise.
    """

    g_vec = []
    for g in games:
        if g.white.user_id is None or g.black.user_id is None:
            print('No ids        :  ', g) #should probably strip them from the db.
            pass
        elif g.handicap > 1 and (-1 > g.komi > 1):
            #print('bad komi      :  ', g)
            pass
        elif g.handicap > 6:
            continue
        elif g.komi < 0 or g.komi > 8.6:
            #print('bad komi      :  ', g)
            pass
        elif not (g.result.startswith('W') or g.result.startswith('B')):
            print('unknown result:  ', g)
            pass
        elif g.date_played is None:
            print('No date played:  ', g)
            pass
        else:
            # Vector of result_tuples.  Just what we need to compute ratings...
            g_vec.append( (g.white.id, 
                         g.black.id,
                         1.0 if g.result.startswith('W') else 0.0,
                         g.date_played.timestamp(),
                         g.handicap,
                         g.komi)) 
    return g_vec 

def rate_all(t_from=None, t_to=None, iters=200, lam=.22):
    """
    t_from -- datetime obj, rate all games after this 
    t_to -- datetime obj, rate all games up to this
    iters -- number of iterations
    lam -- 'neighborhood pull' parameter.  higher = more error from moving a rank away from ranks in its neighborhood
    """
    if t_to is None:
        t_to = datetime.datetime.now()
    if t_from is None:
        t_from = datetime.datetime.utcfromtimestamp(1.0)
    games = Game.query.filter(Game.date_played < t_to, Game.date_played > t_from) 
    g_vec = sanitized_games(games)
    users = sanitized_users(g_vec)

    print("found %d users with %d valid games" % (len(users), len(g_vec)) )

    aga_ids_to_uids = dict([(int(u.aga_id), u.id) for u in users])

    ratings = {int(u.aga_id): u.last_rating() for u in users}
    rating_prior = {id: v.rating if (v and v.rating) else 20 for id,v in ratings.items()} 
    print ("%d users with no priors" % len(list(filter(lambda v: v == 20, rating_prior.values()))))

    neighbors = rm.neighbors(g_vec)
    neighbor_avgs = rm.compute_avgs(g_vec, rating_prior) 

    t_min = min(g_vec, key=lambda g: g[3] or datetime.datetime.now().timestamp())[3]
    t_max = max(g_vec, key=lambda g: g[3] or datetime.datetime.now().timestamp())[3]

    lrn = lambda i: ((1. + .1*iters)/(i + .1 * iters))**.3 #Control the learning rate over time.

    for i in range(iters):
        loss = 0
        # Accumulate the neighborhood loss prior to changing the ratings around
        for id, neighbor_wgt in neighbor_avgs.items():
            loss += lam * ((rating_prior[id] - neighbor_wgt) ** 2)

        # Shuffle the vector of result-tuples
        random.shuffle(g_vec)
        for g in g_vec:
            w, b, actual, t, handi, komi = g
            odds = rm.expect(rating_prior[b], rating_prior[w], handi, komi)
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

        #update neighborhood averages?
        neighbor_avgs = rm.compute_avgs(g_vec, rating_prior) 
        if (i % 50 == 0):
            print('%d : %.4f' % (i, loss))

    # Update the ratings and show how we did.
    wins, losses = {}, {}
    for g in g_vec:
        wins[g[0]] = wins.get(g[0], 0) + g[2]
        losses[g[0]] = losses.get(g[0], 0) + 1-g[2]
        wins[g[1]] = wins.get(g[1], 0) + 1-g[2]
        losses[g[1]] = losses.get(g[1], 0) + g[2]

    for k in sorted(rating_prior, key=lambda k: rating_prior[k])[-10:]: 
        print("%d (uid: %d): %f (%d - %d)" % (k, aga_ids_to_uids[k], rating_prior[k], wins.get(k,0), losses.get(k,0)) )
    
    for k in sorted(rating_prior, key=lambda k: rating_prior[k]): 
        db.session.add(Rating(user_id=aga_ids_to_uids[k], rating=rating_prior[k]))
    db.session.commit()


class RatingsAtCommand(Command):
    """ Class that holds the state for computing a single ratings run at a given point in time"""
    option_list = (
            Option('--from', '-f', dest='t_from'),
            Option('--to', '-t', dest='t_to'),
            Option('--iterations', '-i', dest='iters', default=200),
            Option('--neighborhood', '-n', dest='neighborhood', default=0.15)
            
            )

    def run(self, t_from, t_to, iters, neighborhood):
        if t_to is None:
            t_to = datetime.datetime.now()
        else:
            try: 
                t_to = datetime.datetime.utcfromtimestamp(float(t_to))
            except ValueError: 
                t_to = datetime.datetime.strptime(t_to, "%Y-%m-%d")

        if t_from is None:
            t_from = datetime.datetime.utcfromtimestamp(1.0)
        else:
            try: 
                t_from = datetime.datetime.utcfromtimestamp(float(t_from))
            except ValueError: 
                t_from = datetime.datetime.strptime(t_from, "%Y-%m-%d")

        try:
            iters = int(iters)
        except ValueError:
            print("Iters should be an integer, defaulting to 200")
            iters = 200

        try:
            neighborhood = float(neighborhood)
        except ValueError:
            print("Neighborhood should be an integer, defaulting to .15")
            neighborhood = .15

        print("Generating ratings of games played between %s and %s" % (t_from, t_to)) 
        print("%d iterations, neighborhood pull parameter %f" % (iters, neighborhood))
        rate_all(t_from, t_to, iters, neighborhood)

