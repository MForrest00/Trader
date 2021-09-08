from abc import abstractmethod
import pandas as pd
from trader.strategies.currency.base import CurrencyStrategy


class EntranceCurrencyStrategy(CurrencyStrategy):
    @abstractmethod
    def should_open_position(dataframe: pd.DataFrame, row_index: int) -> bool:
        ...
