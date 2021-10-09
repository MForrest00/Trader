from abc import abstractmethod
import pandas as pd
from trader.strategies.base import Strategy


class EntryStrategy(Strategy):
    IS_ENTRY = True

    @abstractmethod
    def get_buy_signal_strength(self, dataframe: pd.DataFrame, row_index: int) -> float:
        ...
