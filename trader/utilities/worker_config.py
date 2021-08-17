from trader.connections.queue import DATA_RETRIEVAL_QUEUE_NAME
from trader.utilities.environment import REDIS_DATABASE, REDIS_HOST, REDIS_PORT


REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DATABASE}"

QUEUES = [DATA_RETRIEVAL_QUEUE_NAME]
