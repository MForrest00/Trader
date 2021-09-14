from abc import abstractmethod
import pandas as pd
from trader.strategies.base import Strategy


class EntryStrategy(Strategy):
    IS_ENTRY = True

    @abstractmethod
    def should_open_position(self, dataframe: pd.DataFrame, row_index: int) -> bool:
        ...
