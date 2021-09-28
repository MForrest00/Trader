from typing import Dict
from finta import TA
import pandas as pd
from trader.strategies.asset_ohlcv.base import AssetOHLCVStrategy
from trader.strategies.entry.base import EntryStrategy


class BollingerBandsAssetOHLCVEntryStrategy(AssetOHLCVStrategy, EntryStrategy):
    NAME = "Bollinger Bands"
    VERSION = "1.0.0"
    SUPPLEMENTAL_DATA_FEEDS = ()
    PARAMETER_SPACE = {"bollinger_bands_period": range(5, 45, 5)}

    def __init__(self, arguments: Dict[str, int]):
        super().__init__(arguments)
        self.bollinger_bands_period = self.arguments.get("bollinger_bands_period", 20)

    def enhance_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe.join(TA.BBANDS(dataframe, self.bollinger_bands_period))

    def should_open_position(self, dataframe: pd.DataFrame, row_index: int) -> bool:
        row = dataframe.iloc[row_index]
        if pd.isna(row["BB_LOWER"]):
            return False
        if row["close"] < row["BB_LOWER"]:
            return True
        return False