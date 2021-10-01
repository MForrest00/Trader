from ast import literal_eval
from collections import defaultdict
from time import sleep
from typing import DefaultDict, Dict, Set, Tuple
from trader.connections.cache import cache
from trader.utilities.constants import DATA_FEED_MESSAGE_DELIMITER, DATA_FEED_MONITOR_QUEUE_KEY
from trader.utilities.functions.strategy import strategy_data_feed_combinations


class DataFeedMonitor:
    IDLE_SLEEP_SECONDS = 0.5
    CACHE_STATE_KEY = "data_feed_monitor_state"

    def __init__(self):
        self.data_feed_to_combinations_mapping = self.generate_data_feed_to_combinations_mapping()
        self.data_feed_load_status = self.generate_data_feed_load_status()

    def generate_data_feed_to_combinations_mapping(self) -> DefaultDict[int, Set[Tuple[int, ...]]]:
        output: DefaultDict[int, Set[Tuple[int, ...]]] = defaultdict(set)
        for combination in strategy_data_feed_combinations:
            for data_feed_id in combination:
                output[data_feed_id].add(combination)
        return output

    def data_feed_load_combinations(self) -> Dict[Tuple[int, ...], Set[int]]:
        return {item: set(item) for item in strategy_data_feed_combinations}

    def generate_data_feed_load_status(self) -> Dict[int, Dict[int, Dict[Tuple[int, ...], Set[int]]]]:
        saved_state = cache.get(self.CACHE_STATE_KEY)
        if saved_state:
            return literal_eval(saved_state.decode())
        return {}

    def run(self) -> None:
        while True:
            record = cache.lpop(DATA_FEED_MONITOR_QUEUE_KEY)
            if not record:
                sleep(self.IDLE_SLEEP_SECONDS)
                continue
            timeframe_id, base_asset_id, data_feed_id = record.split(DATA_FEED_MESSAGE_DELIMITER)
            if timeframe_id not in self.data_feed_load_status:
                self.data_feed_load_status[timeframe_id] = {}
            if base_asset_id not in self.data_feed_load_status[timeframe_id]:
                self.data_feed_load_status[timeframe_id][base_asset_id] = self.data_feed_load_combinations()
            combinations = self.data_feed_load_status[timeframe_id][base_asset_id]
            targets = self.data_feed_to_combinations_mapping[data_feed_id]
            for target in targets:
                combinations[target].remove(data_feed_id)
                if len(combinations[target]) == 0:
                    combinations[target] = set(target)
            cache.set(DataFeedMonitor.CACHE_STATE_KEY, str(self.data_feed_load_status))
