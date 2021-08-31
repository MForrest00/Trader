from redis import Redis
from trader.utilities.environment import CACHE_REDIS_DATABASE, CACHE_REDIS_HOST, CACHE_REDIS_PORT


cache = Redis(host=CACHE_REDIS_HOST, port=CACHE_REDIS_PORT, db=CACHE_REDIS_DATABASE)
