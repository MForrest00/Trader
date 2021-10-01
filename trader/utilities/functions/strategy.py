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
        for data_feed in data_feeds:
            if data_feed not in data_feed_lookup:
                data_feed_lookup[data_feed] = data_feed.fetch_id()
        key = tuple(
            (
                data_feed_lookup[strategy.BASE_DATA_FEED],
                *sorted(data_feed_lookup[d] for d in strategy.SUPPLEMENTAL_DATA_FEEDS),
            )
        )
        output[key].append(int(cache.get(strategy.get_cache_key()).decode()))
    return output


data_feeds_to_entry_strategy_mapping = fetch_data_feeds_to_strategy_mapping(True)
data_feeds_to_exit_strategy_mapping = fetch_data_feeds_to_strategy_mapping(False)
strategy_data_feed_combinations = (
    data_feeds_to_entry_strategy_mapping.keys() | data_feeds_to_exit_strategy_mapping.keys()
)
