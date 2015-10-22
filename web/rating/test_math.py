import unittest, collections, datetime
from datetime import date as date

import rating_math as rm

Player = collections.namedtuple('Player', ['user_id'])
Game = collections.namedtuple('Game', ['white', 'black', 'result', 'date_played'])
class RatingsMathTestCase(unittest.TestCase): 
    def setUp(self):
        pass

    def test_expect(self):
        self.assertEqual(rm.expect(0,0), 0.5)
        self.assertEqual(rm.expect(3,3), 0.5)
        self.assertGreater(rm.expect(0,3), 0.5)
        self.assertGreater(rm.expect(3, 2), rm.expect(30,29))

    def test_time_weight(self):
        t1 = date(1999,1,1) 
        t2 = date(2000,1,1)
        self.assertEqual(rm.time_weight(t2, t1, t2), 1)
        self.assertAlmostEqual(rm.time_weight(t1, t1, t2), 0, places=3) 

    def test_neighborhoods(self): 
        games = [Game(Player(1), Player(2), 'W+R', date(2000,1,1)),
                 Game(Player(1), Player(3), 'B+R', date(2000,1,2)),
                 Game(Player(1), Player(4), 'W+R', date(2000,1,3)),
                 Game(Player(3), Player(2), 'B+R', date(2000,1,4))]
        neighbors = rm.neighbors(games)

        self.assertEqual(len(neighbors[1]), 3)
        self.assertEqual(len(neighbors[2]), 2)
        self.assertEqual(len(neighbors[3]), 2)
        self.assertEqual(len(neighbors[4]), 1)

    def test_compute_avgs(self): 
        ratings = {1:2, 2:4, 3:2, 4:3}
        games = [Game(Player(1), Player(2), 'W+R', date(2000,1,1)),
                 Game(Player(1), Player(3), 'B+R', date(2000,1,1)),
                 Game(Player(1), Player(4), 'W+R', date(2000,1,1)),
                 Game(Player(3), Player(2), 'B+R', date(2000,1,1))]
        averages = rm.compute_avgs(games, ratings)

        self.assertEqual(averages, {1: 3.0, 2: 2.0, 3: 3.0, 4: 2.0})




