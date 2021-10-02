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
        data_feed_list: List[DataFeedData] = []
        for data_feed in strategy.DATA_FEEDS:
            if data_feed not in data_feed_lookup:
                data_feed_lookup[data_feed] = data_feed.fetch_id()
            insort_left(data_feed_list, data_feed_lookup[data_feed])
        if data_feed_list:
            output[tuple(data_feed_list)].append(int(cache.get(strategy.get_cache_key()).decode()))
    return output


data_feeds_to_entry_strategy_mapping = fetch_data_feeds_to_strategy_mapping(True)
data_feeds_to_exit_strategy_mapping = fetch_data_feeds_to_strategy_mapping(False)
strategy_data_feed_combinations = (
    data_feeds_to_entry_strategy_mapping.keys() | data_feeds_to_exit_strategy_mapping.keys()
)
