from bisect import insort_left
from collections import defaultdict
from typing import DefaultDict, Dict, List, Tuple
from trader.connections.cache import cache
from trader.data.initial.data_feed import DataFeedData
from trader.strategies.entry import ENTRY_STRATEGIES
from trader.strategies.exit import EXIT_STRATEGIES


def fetch_data_feeds_to_strategy_mapping(is_entry: bool) -> DefaultDict[Tuple[int, ...], List[int]]:
    strategies = ENTRY_STRATEGIES if is_entry else EXIT_STRATEGIES
    output: DefaultDict[Tuple[int, ...], List[int]] = defaultdict(list)
    data_feed_lookup: Dict[DataFeedData, int] = {}
    for strategy in strategies:
        data_feeds = (strategy.BASE_DATA_FEED, *strategy.SUPPLEMENTAL_DATA_FEEDS)
        data_feed_list: List[int] = []
        for data_feed in data_feeds:
            if data_feed not in data_feed_lookup:
                data_feed_lookup[data_feed] = data_feed.fetch_id()
            insort_left(data_feed_list, data_feed_lookup[data_feed])
        output[tuple(data_feed_list)].append(int(cache.get(strategy.cache_key).decode()))
    return output
