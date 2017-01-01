

def rating_to_traditional_range(rating_f):
    """ Returns a rating from 0-40 in the traditional -30 to 10ish,
    with the -1 to 1 kyu/dan boundary expanded.
    """
    rating = rating_f - 30.0
    if (rating > -1.0):
        rating += 2.0
    return rating

def rating_to_rank(rating_f):
    """ Returns a rating from 0-40 as a string of the rank, e.g. "30k" or "7d"
    """

    rating = rating_to_traditional_range(rating_f)
    if rating < 0:
        return "%dk" % abs(int(rating))
    elif rating < 7:
        return "%dd" % int(rating)
    else:
        return "7d"
