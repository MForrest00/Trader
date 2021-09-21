import pytest
from trader.connections.database import DBSession
from trader.data.base import (
    GOOGLE_TRENDS_GEO_WORLDWIDE,
    GOOGLE_TRENDS_GPROP_NEWS_SEARCH,
    GOOGLE_TRENDS_GPROP_WEB_SEARCH,
)
from trader.models.google_trends import GoogleTrendsGeo, GoogleTrendsGprop
from trader.utilities.functions import fetch_base_data_id


@pytest.fixture
def google_trends_geo_worldwide() -> GoogleTrendsGeo:
    with DBSession() as session:
        return session.query(GoogleTrendsGeo).get(fetch_base_data_id(GOOGLE_TRENDS_GEO_WORLDWIDE))


@pytest.fixture
def google_trends_gprop_web_search() -> GoogleTrendsGprop:
    with DBSession() as session:
        return session.query(GoogleTrendsGprop).get(fetch_base_data_id(GOOGLE_TRENDS_GPROP_WEB_SEARCH))


@pytest.fixture
def google_trends_gprop_news_search() -> GoogleTrendsGprop:
    with DBSession() as session:
        return session.query(GoogleTrendsGprop).get(fetch_base_data_id(GOOGLE_TRENDS_GPROP_NEWS_SEARCH))
