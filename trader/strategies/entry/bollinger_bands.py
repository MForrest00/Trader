from typing import Dict
from finta import TA
import pandas as pd
from trader.data.initial.data_feed import DATA_FEED_ASSET_OHLCV
from trader.strategies.entry.base import EntryStrategy


class BollingerBandsEntryStrategy(EntryStrategy):
    NAME = "Bollinger Bands"
    VERSION = "1.0.0"
    DATA_FEEDS = (DATA_FEED_ASSET_OHLCV,)
    PARAMETER_SPACE = {"bollinger_bands_period": range(5, 45, 5)}

    @property
    def bollinger_bands_period(self) -> int:
        return self.arguments.get("bollinger_bands_period", 20)

    def enhance_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe.join(TA.BBANDS(dataframe, self.bollinger_bands_period))

    def should_open_position(self, dataframe: pd.DataFrame, row_index: int) -> bool:
        row = dataframe.iloc[row_index]
        if pd.isna(row["BB_LOWER"]):
            return False
        if row["close"] < row["BB_LOWER"]:
            return True
        return False
