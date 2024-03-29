from datetime import datetime, timezone
import pytest
from trader.data.initial.google_trends_gprop import GOOGLE_TRENDS_GPROP_NEWS_SEARCH, GOOGLE_TRENDS_GPROP_WEB_SEARCH
from trader.data.initial.timeframe import (
    TIMEFRAME_EIGHT_MINUTE,
    TIMEFRAME_ONE_DAY,
    TIMEFRAME_ONE_MINUTE,
    TIMEFRAME_ONE_MONTH,
)
from trader.data.google_trends import (
    GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE,
    GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE,
    timeframe_base_label_to_date_ranges,
)


@pytest.mark.integration
def test_timeframe_base_label_to_date_ranges_one_month():
    google_trends_gprop_web_search = GOOGLE_TRENDS_GPROP_WEB_SEARCH.get_instance()
    output = timeframe_base_label_to_date_ranges(
        TIMEFRAME_ONE_MONTH.base_label, google_trends_gprop_web_search, datetime.now(timezone.utc), None
    )
    assert output == [(GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE, None)]
    google_trends_gprop_news_search = GOOGLE_TRENDS_GPROP_NEWS_SEARCH.get_instance()
    output = timeframe_base_label_to_date_ranges(
        TIMEFRAME_ONE_MONTH.base_label, google_trends_gprop_news_search, datetime.now(timezone.utc), None
    )
    assert output == [(GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE, None)]


@pytest.mark.integration
def test_timeframe_base_label_to_date_ranges_one_day():
    google_trends_gprop_web_search = GOOGLE_TRENDS_GPROP_WEB_SEARCH.get_instance()
    output = timeframe_base_label_to_date_ranges(
        TIMEFRAME_ONE_DAY.base_label,
        google_trends_gprop_web_search,
        datetime(2020, 12, 5, tzinfo=timezone.utc),
        datetime(2021, 2, 1, 1, tzinfo=timezone.utc),
    )
    assert output == [
        (datetime(2020, 12, 1, tzinfo=timezone.utc), datetime(2020, 12, 31, tzinfo=timezone.utc)),
        (datetime(2021, 1, 1, tzinfo=timezone.utc), datetime(2021, 1, 31, tzinfo=timezone.utc)),
        (datetime(2021, 2, 1, tzinfo=timezone.utc), datetime(2021, 2, 28, tzinfo=timezone.utc)),
    ]


@pytest.mark.integration
def test_timeframe_base_label_to_date_ranges_eight_minute():
    google_trends_gprop_web_search = GOOGLE_TRENDS_GPROP_WEB_SEARCH.get_instance()
    output = timeframe_base_label_to_date_ranges(
        TIMEFRAME_EIGHT_MINUTE.base_label,
        google_trends_gprop_web_search,
        datetime(2020, 12, 1, 1, tzinfo=timezone.utc),
        datetime(2020, 12, 3, 7, tzinfo=timezone.utc),
    )
    assert output == [
        (datetime(2020, 12, 1, tzinfo=timezone.utc), datetime(2020, 12, 2, tzinfo=timezone.utc)),
        (datetime(2020, 12, 2, tzinfo=timezone.utc), datetime(2020, 12, 3, tzinfo=timezone.utc)),
        (datetime(2020, 12, 3, tzinfo=timezone.utc), datetime(2020, 12, 4, tzinfo=timezone.utc)),
    ]


@pytest.mark.integration
def test_timeframe_base_label_to_date_ranges_one_minute():
    google_trends_gprop_web_search = GOOGLE_TRENDS_GPROP_WEB_SEARCH.get_instance()
    output = timeframe_base_label_to_date_ranges(
        TIMEFRAME_ONE_MINUTE.base_label,
        google_trends_gprop_web_search,
        datetime(2020, 12, 1, 1, tzinfo=timezone.utc),
        datetime(2020, 12, 1, 23, tzinfo=timezone.utc),
    )
    assert output == [
        (datetime(2020, 12, 1, 0, tzinfo=timezone.utc), datetime(2020, 12, 1, 4, tzinfo=timezone.utc)),
        (datetime(2020, 12, 1, 4, tzinfo=timezone.utc), datetime(2020, 12, 1, 8, tzinfo=timezone.utc)),
        (datetime(2020, 12, 1, 8, tzinfo=timezone.utc), datetime(2020, 12, 1, 12, tzinfo=timezone.utc)),
        (datetime(2020, 12, 1, 12, tzinfo=timezone.utc), datetime(2020, 12, 1, 16, tzinfo=timezone.utc)),
        (datetime(2020, 12, 1, 16, tzinfo=timezone.utc), datetime(2020, 12, 1, 20, tzinfo=timezone.utc)),
        (datetime(2020, 12, 1, 20, tzinfo=timezone.utc), datetime(2020, 12, 2, 0, tzinfo=timezone.utc)),
    ]
