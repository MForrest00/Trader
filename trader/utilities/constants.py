import os
import pathlib


PROJECT_BASE_PATH = os.path.split(os.path.split(pathlib.Path(__file__).parent.absolute())[0])[0]

WEB_DRIVER_ELEMENT_WAIT_DELAY_SECONDS = 5
WEB_DRIVER_SCROLL_INCREMENT = 500
WEB_DRIVER_SCROLL_DELAY_SECONDS = 0.5

TOP_CRYPTOCURRENCY_LIMIT = 500
