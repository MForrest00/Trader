from redis import Redis
from trader.utilities.environment import REDIS_DATABASE, REDIS_HOST, REDIS_PORT


cache = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE)
