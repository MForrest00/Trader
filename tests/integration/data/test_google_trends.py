from datetime import datetime, timezone
import pytest
from tests.fixtures.integration.google_trends import google_trends_gprop_news_search, google_trends_gprop_web_search
from trader.data.base import ONE_MONTH
from trader.data.google_trends import timeframe_base_label_to_date_ranges
from trader.utilities.constants import GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE, GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE


@pytest.mark.integration
def test_timeframe_base_label_to_date_ranges_one_month(google_trends_gprop_news_search, google_trends_gprop_web_search):
    output = timeframe_base_label_to_date_ranges(
        ONE_MONTH.base_label, google_trends_gprop_web_search, datetime.now(timezone.utc), None
    )
    assert output == [(GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE, None)]
    output = timeframe_base_label_to_date_ranges(
        ONE_MONTH.base_label, google_trends_gprop_news_search, datetime.now(timezone.utc), None
    )
    assert output == [(GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE, None)]
