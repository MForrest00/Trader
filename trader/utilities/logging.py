import logging
from logging.handlers import RotatingFileHandler
import os
from trader.utilities.constants import PROJECT_BASE_PATH


logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)


stream_format = logging.Formatter("%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s | %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(stream_format)
logger.addHandler(stream_handler)


log_file_path = os.path.join(PROJECT_BASE_PATH, "process.log")
file_format = logging.Formatter("%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s | %(message)s")
file_handler = RotatingFileHandler(log_file_path, maxBytes=1000 * 1000 * 5, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(file_format)
