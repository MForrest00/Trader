from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.data.initial.asset_type import ASSET_TYPES
from trader.data.initial.data_feed import DATA_FEEDS
from trader.data.initial.google_trends_geo import GOOGLE_TRENDS_GEOS
from trader.data.initial.google_trends_gprop import GOOGLE_TRENDS_GPROPS
from trader.data.initial.source import SOURCES
from trader.data.initial.source_type import SOURCE_TYPES
from trader.data.initial.timeframe import TIMEFRAMES
from trader.data.initial.user import USERS


def initialize_data() -> None:
    with DBSession() as session:
        for data in (
            ASSET_TYPES,
            DATA_FEEDS,
            GOOGLE_TRENDS_GEOS,
            GOOGLE_TRENDS_GPROPS,
            SOURCE_TYPES,
            SOURCES,
            TIMEFRAMES,
            USERS,
        ):
            for item in data:
                instance = item.query_instance(session)
                if not instance:
                    instance = item.create_instance()
                    session.add(instance)
                    session.flush()
                cache.set(item.cache_key, instance.id)
        session.commit()
