import datetime
import collections

def expect(r1, r2):
    # r1 and r2 are floats, black rating, white rating
    # 2.0 is the 'width' of a rank.  ranks go 0-40, 3d beats 2d at 75%, 4d beats 2d at 90%
    return (1.0 / (1.0 + pow(10, ((float(r1) - float(r2))/2.0)))) 

def neighbors(games):
    """return a dict of neighborhoods keyed by id, where the neighborhood is defined as
    games is a set of game objectsh
    ratings is a dictionary keyed by user id to floats.
    """ 
    
    neighbors = collections.defaultdict(set)
    for g in games:
        neighbors[g.black.user_id].add(g.white.user_id)
        neighbors[g.white.user_id].add(g.black.user_id) 
    return neighbors

def time_weight(t, tmin, tmax):
    return ((1.0 + (t - tmin).total_seconds()) / (1.0 + (tmax - tmin).total_seconds())) ** 1.2

def compute_avgs(games, ratings):
    tmin = min(games, key=lambda g: g.date_played or datetime.datetime.now()).date_played
    tmax = max(games, key=lambda g: g.date_played or datetime.datetime.now()).date_played

    ids = set([g.black.user_id for g in games]).union(set([g.white.user_id for g in games]))
    rate_weight_accums = dict(zip(ids, [0.0] * len(ids)))
    weight_accums = dict(zip(ids, [0.0] * len(ids)))
    for g in games:
        weight = time_weight(g.date_played, tmin, tmax) 
        weight_accums[g.black.user_id] += weight 
        weight_accums[g.white.user_id] += weight
        rate_weight_accums[g.black.user_id] += weight * ratings[g.white.user_id]
        rate_weight_accums[g.white.user_id] += weight * ratings[g.black.user_id]

    averages = {k: rate_weight_accums[k]/weight_accums[k] for k in weight_accums.keys()}
    return averages


