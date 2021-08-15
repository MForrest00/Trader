from rq import Queue
from trader.connections.cache import cache


queue = Queue(connection=cache)
