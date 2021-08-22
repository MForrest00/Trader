from datetime import datetime, timedelta
from time import sleep
from typing import Callable, Dict
from dateutil.relativedelta import relativedelta
from selenium.webdriver.remote.webdriver import WebDriver
from trader.utilities.constants import WEB_DRIVER_SCROLL_DELAY_SECONDS, WEB_DRIVER_SCROLL_INCREMENT


TIMEFRAME_UNIT_TO_TRANSFORM_FUNCTION: Dict[str, Callable[[datetime], datetime]] = {
    "s": lambda x: x.replace(microsecond=0),
    "m": lambda x: x.replace(second=0, microsecond=0),
    "h": lambda x: x.replace(minute=0, second=0, microsecond=0),
    "d": lambda x: x.replace(hour=0, minute=0, second=0, microsecond=0),
    "w": lambda x: x.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=x.weekday()),
    "M": lambda x: x.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
    "y": lambda x: x.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
}


TIMEFRAME_UNIT_TO_INCREMENT_FUNCTION: Dict[str, Callable[[datetime, int], datetime]] = {
    "s": lambda x, y: x + timedelta(seconds=y),
    "m": lambda x, y: x + timedelta(minutes=y),
    "h": lambda x, y: x + timedelta(hours=y),
    "d": lambda x, y: x + timedelta(days=y),
    "w": lambda x, y: x + relativedelta(weeks=y),
    "M": lambda x, y: x + relativedelta(months=y),
    "y": lambda x, y: x + relativedelta(years=y),
}


def clean_range_cap(range_cap: datetime, timeframe_unit: str) -> datetime:
    return TIMEFRAME_UNIT_TO_TRANSFORM_FUNCTION[timeframe_unit](range_cap)


def datetime_to_ms_timestamp(dt: datetime) -> int:
    return int(dt.timestamp()) * 1000


def ms_timestamp_to_datetime(ts: int) -> datetime:
    return datetime.utcfromtimestamp(ts // 1000)


def iso_time_string_to_datetime(time_string: str) -> datetime:
    return datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%f%z")


def fully_scroll_page(web_driver: WebDriver) -> None:
    current_y_offset = web_driver.execute_script("return window.pageYOffset")
    while True:
        web_driver.execute_script(f"window.scrollBy(0, {WEB_DRIVER_SCROLL_INCREMENT})")
        new_y_offset = web_driver.execute_script("return window.pageYOffset")
        if new_y_offset == current_y_offset:
            break
        current_y_offset = new_y_offset
        sleep(WEB_DRIVER_SCROLL_DELAY_SECONDS)
