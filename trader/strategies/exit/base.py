from abc import abstractmethod
import pandas as pd
from trader.models.asset_ohlcv_position import AssetOHLCVPosition
from trader.strategies.base import Strategy


class ExitStrategy(Strategy):
    IS_ENTRY = False

    @abstractmethod
    def should_close_position(self, position: AssetOHLCVPosition, dataframe: pd.DataFrame, row_index: int) -> bool:
        ...
