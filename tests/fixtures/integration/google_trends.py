import pytest
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.data.base import NEWS_SEARCH, WEB_SEARCH, WORLDWIDE
from trader.models.google_trends import GoogleTrendsPullGeo, GoogleTrendsPullGprop


@pytest.fixture
def google_trends_geo_worldwide() -> GoogleTrendsPullGeo:
    worldwide_id = int(cache.get(WORLDWIDE.cache_key).decode())
    with DBSession() as session:
        return session.query(GoogleTrendsPullGeo).get(worldwide_id)


@pytest.fixture
def google_trends_gprop_web_search() -> GoogleTrendsPullGprop:
    web_search_id = int(cache.get(WEB_SEARCH.cache_key).decode())
    with DBSession() as session:
        return session.query(GoogleTrendsPullGprop).get(web_search_id)


@pytest.fixture
def google_trends_gprop_news_search() -> GoogleTrendsPullGprop:
    news_search_id = int(cache.get(NEWS_SEARCH.cache_key).decode())
    with DBSession() as session:
        return session.query(GoogleTrendsPullGprop).get(news_search_id)
