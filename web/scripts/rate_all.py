import random, datetime

from app.models import Game, User, Rating, db
from flask.ext.script import Command, Option
import rating.rating_math as rm

def sanitized_users(g_vec):
    """ Strip out users with no games from our list """
    users = User.query.all() 
    users_with_games = set([g[0] for g in g_vec])
    users_with_games = users_with_games | set([g[1] for g in g_vec])
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
        elif g.date_played is None or g.date_played.timestamp() == 0.0:
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

def rate_all(t_from=datetime.datetime.utcfromtimestamp(1.0), 
             t_to=datetime.datetime.now(),
             iters=200, lam=.22):
    """
    t_from -- datetime obj, rate all games after this 
    t_to -- datetime obj, rate all games up to this
    iters -- number of iterations
    lam -- 'neighborhood pull' parameter.  higher = more error from moving a rank away from ranks in its neighborhood
    """
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

    t_min = min([g[3] for g in g_vec])
    t_max = max([g[3] for g in g_vec])

    lrn = lambda i: ((1. + .1*iters)/(i + .1 * iters))**.3 #Control the learning rate over time.

    for i in range(iters):
        loss = 0
        # Accumulate the neighborhood loss prior to changing the ratings around
        for id, neighbor_wgt in neighbor_avgs.items():
            loss += lam * ((rating_prior[id] - neighbor_wgt) ** 2)

        # Shuffle the vector of result-tuples and step through them, accumulating error.
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
        db.session.add(Rating(user_id=aga_ids_to_uids[k], rating=rating_prior[k], created=t_to))
    db.session.commit()


class RatingsAtCommand(Command):
    """ Class that holds the state for computing a single ratings run at a given point in time"""
    option_list = (
            Option('--from', '-f', dest='t_from'),
            Option('--to', '-t', dest='t_to'),
            Option('--iterations', '-i', dest='iters', default=200),
            Option('--neighborhood', '-n', dest='neighborhood', default=0.10),
            Option('--dryrun', '-d', dest='dryrun', default=False)
            )

    def run(self, t_from, t_to, iters, neighborhood, dryrun):
        parse_params(t_from, t_to, iters, neighborhood)
        setup()
        while keep_rating:
            these_games = Game.query.filter(Game.date_played < t_to, Game.date_played > t_from) 
            g_vec = filter(self._all_g_vecsanitized_games(games)
            these_users = sanitized_users(g_vec)
            new_ratings = rate...

            #while this_to < t_to:
            #    this_to += datetime.timedelta(100) 
            #    print("==")
            #    print("Generating ratings of games played between %s and %s" % (t_from, this_to)) 
            #    print("%d iterations, neighborhood pull parameter %f" % (iters, neighborhood))
            #    rate_all(t_from, this_to, iters, neighborhood)

            if not dryrun:
                write(new_ratings)



    def sanitized_users(self, g_vec):
        """ Returns a subset of User objects where u.aga_id appears in the game vector. """
        users_with_games = set([g[0] for g in g_vec])
        users_with_games = users_with_games | set([g[1] for g in g_vec])
        new_users = [u for u in self._users if u.aga_id and int(u.aga_id) in users_with_games] # aga_id is text?!?
        return new_users

    def setup(self):
        self._games = Game.query.all()
        self._users = User.query.all() 
        self._aga_ids_to_uids = dict([(int(u.aga_id), u.id) for u in self._users if u.aga_id is not None])

        self._all_g_vec = sanitized_games(self._games)
        print("found %d users with %d valid games" % (len(self._users), len(self._all_g_vec)) ) 

    def write_ratings(self, new_ratings, timestamp):
        for k in new_ratings: 
            db.session.add(Rating(user_id=aga_ids_to_uids[k], rating=new_ratings[k], created=timestamp))
        db.session.commit()

    def parse_params(t_from, t_to, iters, neighborhood, dry_run):
        if t_to is None:
            self._t_to = datetime.datetime.now()
        else:
            try: 
                self._t_to = datetime.datetime.utcfromtimestamp(float(t_to))
            except ValueError: 
                self._t_to = datetime.datetime.strptime(t_to, "%Y-%m-%d")

        if self._t_from is None:
            self._t_from = datetime.datetime.utcfromtimestamp(1.0)
        else:
            try: 
                self._t_from = datetime.datetime.utcfromtimestamp(float(t_from))
            except ValueError: 
                self._t_from = datetime.datetime.strptime(t_from, "%Y-%m-%d")

        try:
            self._iters = int(iters)
        except ValueError:
            print("Iters should be an integer, defaulting to 200")
            self._iters = 200

        try:
            self._neighborhood = float(neighborhood)
        except ValueError:
            print("Neighborhood should be a float, defaulting to .15")
            self._neighborhood = .15 
