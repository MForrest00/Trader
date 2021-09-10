from abc import abstractmethod
import pandas as pd
from trader.models.currency_ohlcv_position import CurrencyOHLCVPosition
from trader.strategies.currency.base import CurrencyStrategy


class ExitCurrencyStrategy(CurrencyStrategy):
    @abstractmethod
    def should_close_position(self, position: CurrencyOHLCVPosition, dataframe: pd.DataFrame, row_index: int) -> bool:
        ...
