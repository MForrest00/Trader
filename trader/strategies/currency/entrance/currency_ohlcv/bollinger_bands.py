from finta import TA
import pandas as pd
from trader.strategies.currency.entrance.base import EntranceCurrencyStrategy


class BollingerBandsCurrencyOHLCVEntranceCurrencyStrategy(EntranceCurrencyStrategy):
    NAME = "Bollinger Bands"
    VERSION = "1.0.0"

    @staticmethod
    def refine_dataframe(dataframe: pd.DataFrame, bollinger_bands_period: int) -> pd.DataFrame:
        return dataframe.join(TA.BBANDS(dataframe, bollinger_bands_period))

    @staticmethod
    def should_open_position(dataframe: pd.DataFrame, row_index: int) -> bool:
        row = dataframe.iloc[row_index]
        if pd.isna(row["BB_LOWER"]):
            return False
        if row["close"] < row["BB_LOWER"]:
            return True
        return False
