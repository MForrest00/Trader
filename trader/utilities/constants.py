from datetime import datetime, timezone
import os
import pathlib


PROJECT_BASE_PATH = os.path.split(os.path.split(pathlib.Path(__file__).parent.absolute())[0])[0]

WEB_DRIVER_ELEMENT_WAIT_DELAY_SECONDS = 5
WEB_DRIVER_SCROLL_INCREMENT = 500
WEB_DRIVER_SCROLL_DELAY_SECONDS = 0.5

CRYPTOCURRENCY_RANK_LIMIT = 500

GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE = datetime(2004, 1, 1, tzinfo=timezone.utc)
GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE = datetime(2008, 1, 1, tzinfo=timezone.utc)
