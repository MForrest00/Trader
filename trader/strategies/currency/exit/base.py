from abc import abstractmethod
import pandas as pd
from trader.models.currency_position import CurrencyPosition
from trader.strategies.currency.base import CurrencyStrategy


class ExitCurrencyStrategy(CurrencyStrategy):
    @abstractmethod
    def should_close_position(position: CurrencyPosition, dataframe: pd.DataFrame, row_index: int) -> bool:
        ...
