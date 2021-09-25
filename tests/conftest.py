import pytest
from trader.connections.database import DBSession
from trader.data.initial.google_trends_geo import GOOGLE_TRENDS_GEO_WORLDWIDE
from trader.data.initial.google_trends_gprop import GOOGLE_TRENDS_GPROP_NEWS_SEARCH, GOOGLE_TRENDS_GPROP_WEB_SEARCH
from trader.models.google_trends import GoogleTrendsGeo, GoogleTrendsGprop


@pytest.fixture
def google_trends_geo_worldwide() -> GoogleTrendsGeo:
    with DBSession() as session:
        return session.query(GoogleTrendsGeo).get(GOOGLE_TRENDS_GEO_WORLDWIDE.fetch_id())


@pytest.fixture
def google_trends_gprop_web_search() -> GoogleTrendsGprop:
    with DBSession() as session:
        return session.query(GoogleTrendsGprop).get(GOOGLE_TRENDS_GPROP_WEB_SEARCH.fetch_id())


@pytest.fixture
def google_trends_gprop_news_search() -> GoogleTrendsGprop:
    with DBSession() as session:
        return session.query(GoogleTrendsGprop).get(GOOGLE_TRENDS_GPROP_NEWS_SEARCH.fetch_id())
