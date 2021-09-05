from finta import TA
import pandas as pd


class BollingerBandsTrailingStopLossStrategy:
    def __init__(self, ohlcv_df: pd.DataFrame, bollinger_bands_period: int, trailing_stop_loss_percentage: float):
        self.ohlcv_df = ohlcv_df.join(TA.BBANDS(ohlcv_df, bollinger_bands_period))
        self.trailing_stop_loss_percentage = trailing_stop_loss_percentage
        self.buy_signal_indexes: List[int] = []
        self.sell_signal_indexes: List[int] = []
        self.current_max = None

    def reset_indicators(self) -> None:
        self.current_max = None

    def run_strategy(self):
        for i, row in self.ohlcv_df.iterrows():
            if pd.isna(row["BB_MIDDLE"]):
                continue
            if row["close"] <= (self.current_max * trailing_stop_loss_percentage):
                self.should_sell = True
