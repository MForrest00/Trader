from rq import Queue
from trader.connections.cache import cache


DATA_RETRIEVAL_QUEUE_NAME = "data_retrieval"
data_retrieval_queue = Queue(DATA_RETRIEVAL_QUEUE_NAME, connection=cache)
