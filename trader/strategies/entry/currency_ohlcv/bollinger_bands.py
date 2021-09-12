from finta import TA
import pandas as pd
from trader.strategies.entry.base import EntryStrategy


class BollingerBandsCurrencyOHLCVEntryStrategy(EntryStrategy):
    NAME = "Bollinger Bands"
    VERSION = "1.0.0"
    IS_ENTRY = True
    NORMAL_PARAMETER_SPACE = {"bollinger_bands_period": range(5, 45, 5)}

    def __init__(self, bollinger_bands_period: int = 20):
        self.bollinger_bands_period = bollinger_bands_period

    def refine_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe.join(TA.BBANDS(dataframe, self.bollinger_bands_period))

    def should_open_position(self, dataframe: pd.DataFrame, row_index: int) -> bool:
        row = dataframe.iloc[row_index]
        if pd.isna(row["BB_LOWER"]):
            return False
        if row["close"] < row["BB_LOWER"]:
            return True
        return False
