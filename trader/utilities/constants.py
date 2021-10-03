from datetime import datetime
import os
import pathlib


PROJECT_BASE_PATH = os.path.split(os.path.split(pathlib.Path(__file__).parent.absolute())[0])[0]


US_DOLLAR_SYMBOL = "USD"


DATA_FEED_MONITOR_QUEUE_KEY = "data_feed_monitor_queue"
DATA_FEED_MESSAGE_DELIMITER = ":"


DATA_DEFAULT_FLOOR = datetime(2017, 1, 1)
