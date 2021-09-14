from abc import abstractmethod
import pandas as pd
from trader.models.currency_ohlcv_position import CurrencyOHLCVPosition
from trader.strategies.base import Strategy


class ExitStrategy(Strategy):
    IS_ENTRY = False

    @abstractmethod
    def should_close_position(self, position: CurrencyOHLCVPosition, dataframe: pd.DataFrame, row_index: int) -> bool:
        ...
