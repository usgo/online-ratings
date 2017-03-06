import unittest, collections
from datetime import datetime as date
import rating.rating_math as rm

Player = collections.namedtuple('Player', ['user_id'])
Game = collections.namedtuple('Game', ['white', 'black', 'result', 'date_played'])

class RatingsMathTestCase(unittest.TestCase): 
    def setUp(self):
        pass

    def test_expect(self):
        self.assertEqual(rm.expect(0, 0, 0, 7.5), 0.5)
        self.assertEqual(rm.expect(3, 3, 0, 6.5), 0.5)
        self.assertGreater(rm.expect(0, 3, 0, 6.5), 0.5)

        #the odds of a 28k beating a 27k should be better than the odds of a 6d beating a 7d.
        self.assertGreater(rm.expect(3, 2, 0, 6.5), rm.expect(30, 29, 0, 6.5))

        # Handicaps should make a fair game.
        self.assertEqual(rm.expect(3, 5, 2, 0.5), 0.5)

        # Same rating but no komi, expect white has lower odds of winning.
        self.assertLess(rm.expect(3, 3, 0, 0.5), 0.5)

        # Handicap greater than ratings suggest, expect white has lower odds of winning.
        self.assertLess(rm.expect(3, 4, 3, 0.5), 0.5)

    def test_time_weight(self):
        t1 = date(1999,1,1) 
        t2 = date(2000,1,1)
        self.assertEqual(rm.time_weight_dt(t2, t1, t2), 1)
        self.assertAlmostEqual(rm.time_weight_dt(t1, t1, t2), 0, places=3) 

    def test_neighborhoods(self): 
        games = [(1, 2, 'W+R', date(2000,1,1)),
                 (1, 3, 'B+R', date(2000,1,2)),
                 (1, 4, 'W+R', date(2000,1,3)),
                 (3, 2, 'B+R', date(2000,1,4))]
        neighbors = rm.neighbors(games)

        self.assertEqual(len(neighbors[1]), 3)
        self.assertEqual(len(neighbors[2]), 2)
        self.assertEqual(len(neighbors[3]), 2)
        self.assertEqual(len(neighbors[4]), 1)

    def test_compute_avgs(self): 
        ratings = {1:2, 2:4, 3:2, 4:3, 5:2}
        games = [(1, 2, '1', date(2000,1,1).timestamp(), 0, 7),
                 (1, 3, '0', date(2000,1,2).timestamp(), 0, 7),
                 (1, 4, '1', date(2000,1,3).timestamp(), 0, 7),
                 (2, 5, '1', date(2000,1,3).timestamp(), 0, 7),
                 (3, 2, '0', date(2000,1,4).timestamp(), 0, 7)]
        averages = rm.compute_avgs(games, ratings)

        # 2 & 4 both only played people with the same rating,
        # so they should have the same weighted average opponent rating
        self.assertEqual(averages[2], averages[4]) 

        # 1 faced lower average opposition than 3 did, so 3's average opponent rating should be higher.
        self.assertLess(averages[1], averages[3]) 

        # a clear strongest player, two equal players
        ratings = {1:10, 2:3, 3:3}
        games = [(1, 2, '1', date(2000,1,1).timestamp(), 0, 7),
                 (1, 3, '0', date(2000,1,3).timestamp(), 0, 7),
                 (2, 3, '1', date(2000,1,5).timestamp(), 0, 7)]
        averages = rm.compute_avgs(games, ratings)

        #the player who faced the strongest player most recently should have the higher average
        self.assertLess(averages[2], averages[3])

        # all the same strength, but 2 gave 3 a 3-handicap game.
        ratings = {1:3, 2:3, 3:3}
        games = [(1, 2, '1', date(2000,1,1).timestamp(), 0, 7),
                 (1, 3, '0', date(2000,1,1).timestamp(), 0, 7),
                 (2, 3, '1', date(2000,1,1).timestamp(), 3, 0)]
        averages = rm.compute_avgs(games, ratings)

        # The player who gave stones should have a higher average
        self.assertGreater(averages[2], averages[3])

        # the player who received them should have a lower one
        self.assertGreater(averages[1], averages[3])
