
import os

from redis import Redis
from rq import Queue, Worker, Connection
from app import db
from app.models import Game, Ratings
from flask.ext.rq import job

@job
def elo(result_id):
    g = Game.query.get(result_id)
    if g.rated is False:
        last_white = Ratings.query.filter(g.white_id)
        last_black = Ratings.query.filter(g.black_id)

@job
def fetch_sgf(url, game_id): 
    pass

if __name__ == '__main__':
    redis = Redis('redis', os.environ['REDIS_PORT'])
    q = Queue('default', connection=redis)
    with Connection(redis):
        worker = Worker(map(Queue, ['default']))
        worker.work()
