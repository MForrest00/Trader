from time import sleep
from typing import DefaultDict, Set, Tuple
from trader.connections.cache import cache
from trader.utilities.constants import DATA_FEED_MESSAGE_DELIMITER, DATA_FEED_MONITOR_KEY
from trader.utilities.functions.strategy import fetch_data_feeds_to_strategy_mapping


class DataFeedMonitor:
    IDLE_SLEEP_SECONDS = 0.5

    def __init__(self):
        self.data_feeds_to_entry_strategy_mapping = fetch_data_feeds_to_strategy_mapping(True)
        self.data_feeds_to_exit_strategy_mapping = fetch_data_feeds_to_strategy_mapping(False)
        self.data_feed_to_combination_mapping = self.generate_data_feed_to_combination_mapping()

    def generate_data_feed_to_combination_mapping(self) -> DefaultDict[int, Set[Tuple[int, ...]]]:
        output: DefaultDict[int, Set[Tuple[int, ...]]] = {}
        combinations = (
            self.data_feeds_to_entry_strategy_mapping.keys() | self.data_feeds_to_exit_strategy_mapping.keys()
        )
        for combination in combinations:
            for data_feed_id in combination:
                output[data_feed_id].add(combination)
        return output

    def run(self) -> None:
        while True:
            record = cache.lpop(DATA_FEED_MONITOR_KEY)
            if not record:
                sleep(self.IDLE_SLEEP_SECONDS)
                continue
            timeframe_id, base_asset_id = record.split(DATA_FEED_MESSAGE_DELIMITER)
