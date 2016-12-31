import datetime
import collections
import math

def expect(r1, r2, handi, komi):
    # r1 and r2 are floats, black rating, white rating
    # a 'scales' the odds by rank.  i.e., a 7d is more likely to beat a 5d than a 8k is to beat a 10k.
    # it's expected that r1 < r2, but not enforced,
    if 5 < komi < 9:
        handi = 0
    if (0 < komi < 2) and handi == 0:
        handi = 1
    d = float(r1) - float(r2) + handi
    a = 5 - ((r1 + r2) /20)
    return (1.0 / (1.0 + pow(math.e, d/a ))) 

def neighbors(g_vec):
    """Return a dict of neighborhoods keyed by id, where the neighborhood is defined as all the user ids a given user played.
    g_vec is a set of tuples (w_id, b_id, ...other stuff)
    ratings is a dictionary keyed by user id to floats.
    """ 
    
    neighbors = collections.defaultdict(set)
    for g in g_vec:
        neighbors[g[0]].add(g[1])
        neighbors[g[1]].add(g[0]) 
    return neighbors

def time_weight(t, tmin, tmax):
    return ((1.0 + (t - tmin).total_seconds()) / (1.0 + (tmax - tmin).total_seconds())) ** 1.2

def compute_avgs(games, ratings):
    """
    games is a vector of tuples (w_id, b_id, 1-if-W+else-0, datetime, handi, komi)

    Computes the time-weighted average rating of opponents.
    """
    tmin = min(games, key=lambda g: g[3] or datetime.datetime.now())[3]
    tmax = max(games, key=lambda g: g[3] or datetime.datetime.now())[3]

    ids = set([g[0] for g in games]).union(set([g[1] for g in games]))
    rate_weight_accums = dict(zip(ids, [0.0] * len(ids)))
    weight_accums = dict(zip(ids, [0.0] * len(ids)))
    for g in games:
        weight = time_weight(g[3], tmin, tmax) 
        weight_accums[g[0]] += weight 
        weight_accums[g[1]] += weight
        rate_weight_accums[g[0]] += weight * ratings[g[1]]
        rate_weight_accums[g[1]] += weight * ratings[g[0]]

    averages = {k: rate_weight_accums[k]/weight_accums[k] for k in weight_accums.keys()}
    return averages


