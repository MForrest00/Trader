from finta import TA
import pandas as pd
from trader.strategies.currency.entrance.base import EntranceCurrencyStrategy


class BollingerBandsCurrencyOHLCVEntranceCurrencyStrategy(EntranceCurrencyStrategy):
    NAME = "Bollinger Bands"
    VERSION = "1.0.0"

    def __init__(self, bollinger_bands_period: int):
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
