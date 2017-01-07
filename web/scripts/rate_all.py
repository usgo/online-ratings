import random, datetime, time

from app.models import Game, User, Rating, db
from flask.ext.script import Command, Option
import rating.rating_math as rm

class RatingsAtCommand(Command):
    """ Class that holds the state for computing a single ratings run at a given point in time"""
    option_list = (
            Option('--from', '-f', dest='t_from'),
            Option('--to', '-t', dest='t_to'),
            Option('--iterations', '-i', dest='iters', default=200, type=int),
            Option('--neighborhood', '-n', dest='neighborhood', default=0.10, type=float),
            Option('--dryrun', '-d', dest='dryrun', default=False),
            Option('--continuous_mode', '-c', dest='continuous_mode', default=False, type=bool),
            Option('--predict', '-p', dest='predict', default=False, type=bool)
            )

    def setup(self, continuous_mode):
        start_time = time.clock()
        print("Continuous is: ", continuous_mode)
        print("Loading games... ", end="", flush=True)
        if(continuous_mode):
            self._games = Game.query.all()

            self._ranges = []
            this_to = self._t_from + datetime.timedelta(365*5) 
            while this_to < self._t_to:
                self._ranges.append((self._t_from, this_to))
                this_to += datetime.timedelta(100) 
        else:
            self._games = Game.query.filter(Game.date_played < self._t_to, Game.date_played > self._t_from) 
            self._ranges = [(self._t_from, self._t_to)] 
        print ("Done. (%.2f s)" % (time.clock() - start_time))

        start_time = time.clock()
        print("Loading users... ", end="", flush=True)
        self._users = User.query.all() 
        print ("Done. (%.2f s)" % (time.clock() - start_time))

        start_time = time.clock()
        print("Loading prior ratings... ", end="", flush=True)
        self._aga_ids_to_uids = dict([(int(u.aga_id), u.id) for u in self._users if u.aga_id is not None])
        ratings = {int(u.aga_id): u.last_rating() for u in self._users if u.aga_id}
        print ("Done. (%.2f s)" % (time.clock() - start_time))

        for r in list(ratings.values()):
            if r is not None and r.created is not None:
                self._last_to = r.created
                break
        print("Last run detected at: ", self._last_to)
        self._rating_priors = {id: v.rating if (v and v.rating) else 20 for id,v in ratings.items()} 

        start_time = time.clock()
        print("Loading games into result vector... ", end="", flush=True)
        self._all_g_vec = self.sanitize_games(self._games) 
        print ("Done. (%.2f s)" % (time.clock() - start_time))

    def run(self, t_from, t_to, iters, neighborhood, dryrun, continuous_mode, predict):
        self.parse_params(t_from, t_to, iters, neighborhood)
        self.setup(continuous_mode)

        print("Found %d users with %d valid games" % (len(self._users), len(self._all_g_vec)) ) 
        for idx, (this_from, this_to) in enumerate(self._ranges): # TODO set up _ranges correctly.
            start_time = time.clock()
            print("== ")
            print ("%d users not yet rated..." % len(list(filter(lambda v: v == 20, self._rating_priors.values()))))

            this_g_vec = list(filter(lambda g: g[3] > this_from.timestamp() and g[3] < this_to.timestamp(), self._all_g_vec))
            users_with_games = set([g[0] for g in this_g_vec]) | set([g[1] for g in this_g_vec])
            print("Rating %d games played among %d members, %s -- %s. " % (
                len(this_g_vec),
                len(users_with_games),
                this_from.strftime("%Y-%m-%d"),
                this_to.strftime("%Y-%m-%d")), end="") 
            print("%d iterations, neighborhood pull parameter %f" % (iters, neighborhood))

            ratings = dict([(_id,_r) for _id,_r in self._rating_priors.items() if _id in users_with_games])

            #TODO: ugly.
            if continuous_mode and idx == 0:
                print("1st iteration, neighborhood overridden to .03, iters 1k")
                self.rate(this_g_vec, ratings, 1000, 0.03)
            else: 
                if predict:
                    new_g_vec = list(filter(lambda g: g[3] > self._last_to.timestamp(), this_g_vec))
                    correct, not_applicable = self.check_predictions(new_g_vec, ratings)
                    print("Before training: %d/%d new (unseen) games predicted (%.2f) " % (
                        correct,
                        len(new_g_vec) - not_applicable,
                        (100.0 * correct)/(1.0 * (len(new_g_vec)-not_applicable))))

                self.rate(this_g_vec, ratings, iters, neighborhood)

                if predict:
                    correct, not_applicable = self.check_predictions(this_g_vec, ratings)
                    if not_applicable != 0:
                        print("uh, we still don't have some ratings?  Weird...")
                    print("After training: %d/%d of training data games predicted (%.2f) " % (
                        correct,
                        len(this_g_vec) - not_applicable,
                        (100.0 * correct)/(1.0 * (len(this_g_vec)-not_applicable))))




            self._rating_priors.update(ratings) 

            print ("Rated %.2f sec" % (time.clock() - start_time))
            if not dryrun:
                self.write_ratings(ratings, this_to)
            print ("Written %.2f sec" % (time.clock() - start_time))

            self._last_to = this_to

    def check_predictions(self, g_vec, ratings): 
        correct = 0
        not_applicable = 0
        for g in g_vec:
            if ratings[g[0]] == 20 or ratings[g[1]] == 20:
                not_applicable +=1 
                continue

            w, b, actual, t, handi, komi = g
            odds = rm.expect(ratings[b], ratings[w], handi, komi)
            if odds > 0.5 and actual == 1:
                correct += 1
            elif odds < 0.5 and actual == 0:
                correct += 1
        return correct, not_applicable


    def rate(self, g_vec, rating_priors, iters=200, lam=.22):
        """
        g_vec -- vector of game tuples (described in sanitize_games)
        rating_priors - prior ratings of all users referenced in g_vec
        iters -- number of iterations
        lam -- 'neighborhood pull' parameter.  higher = more error from moving a rank away from ranks in its neighborhood

        Updates rating_priors in place
        """ 
        neighbors = rm.neighbors(g_vec)
        neighbor_avgs = rm.compute_avgs(g_vec, rating_priors) 

        t_min = min([g[3] for g in g_vec])
        t_max = max([g[3] for g in g_vec])

        # Control the learning rate over time.  The exponent is a SWAG, as is the last constant.
        lrn = lambda i: ((1. + .1*iters)/(i + .1 * iters))**.3  + 0.2

        for i in range(iters):
            loss = 0
            # Accumulate the neighborhood loss prior to changing the ratings around
            for id, neighbor_wgt in neighbor_avgs.items():
                loss += lam * ((rating_priors[id] - neighbor_wgt) ** 2)

            # Shuffle the vector of result-tuples and step through them, accumulating error.
            random.shuffle(g_vec)
            for g in g_vec:
                w, b, actual, t, handi, komi = g
                odds = rm.expect(rating_priors[b], rating_priors[w], handi, komi)
                weight = rm.time_weight(t, t_min, t_max)
                rating_priors[w] -= lrn(i) * (weight*(odds - actual)*odds*(1-odds) + (lam/len(neighbors[w]) * (rating_priors[w] - neighbor_avgs[w])))
                rating_priors[b] -= lrn(i) * (-1.0 * weight*(odds - actual)*odds*(1-odds) + (lam/len(neighbors[b]) * (rating_priors[b] - neighbor_avgs[b])))
                loss += weight * ((odds - actual) ** 2)

            # Scale the ratings -- maybe only every x iterations?  this is probably pretty ineffecient code.
            r_min = min(rating_priors.values())
            r_max = max(rating_priors.values()) 
            if r_max != r_min:
                for k,v in rating_priors.items():
                    rating_priors[k] = (rating_priors[k] - r_min) / (r_max - r_min) * 40.0

            #update neighborhood averages.
            neighbor_avgs = rm.compute_avgs(g_vec, rating_priors) 
            if (i % int(iters/10.0) == 0):
                print("\n%d : %.4f   " % (i, loss), end="")
            else:
                print(".", end="", flush=True)

        # Update the ratings and show how we did.
        wins, losses = {}, {}
        for g in g_vec:
            wins[g[0]] = wins.get(g[0], 0) + g[2]
            losses[g[0]] = losses.get(g[0], 0) + 1-g[2]
            wins[g[1]] = wins.get(g[1], 0) + 1-g[2]
            losses[g[1]] = losses.get(g[1], 0) + g[2]

        print("")
        for k in sorted(rating_priors, key=lambda k: rating_priors[k])[-10:]: 
            print("%d (uid: %d): %f (%d - %d)" % (k, self._aga_ids_to_uids[k], rating_priors[k], wins.get(k,0), losses.get(k,0)) )

    def sanitized_users(self, g_vec):
        """ Returns a subset of User objects where u.aga_id appears in the game vector. """
        users_with_games = set([g[0] for g in g_vec]) | set([g[1] for g in g_vec])
        new_users = [u for u in self._users if u.aga_id and int(u.aga_id) in users_with_games] # aga_id is text?!?
        return new_users

    def write_ratings(self, new_ratings, timestamp):
        for k in new_ratings: 
            db.session.add(Rating(user_id=self._aga_ids_to_uids[k], rating=new_ratings[k], created=timestamp))
        db.session.commit()

    def parse_params(self, t_from, t_to, iters, neighborhood):
        if t_to is None:
            self._t_to = datetime.datetime.now()
        else:
            try: 
                self._t_to = datetime.datetime.utcfromtimestamp(float(t_to))
            except ValueError: 
                self._t_to = datetime.datetime.strptime(t_to, "%Y-%m-%d")

        if t_from is None:
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

    def sanitize_games(self, games):
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
                #print('No date played:  ', g)
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
