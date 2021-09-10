from typing import List
import pandas as pd
from trader.connections.database import DBSession
from trader.implementations.currency.base import CurrencyImplementation
from trader.models.currency_ohlcv_implementation import (
    CurrencyOHLCVImplementation as CurrencyOHLCVImplementationModel,
    CurrencyOHLCVImplementationVersion,
)
from trader.models.currency_ohlcv_position import CurrencyOHLCVPosition
from trader.models.currency_ohlcv_strategy import CurrencyOHLCVStrategy, CurrencyOHLCVStrategyVersion
from trader.strategies.currency.base import CurrencyStrategy
from trader.utilities.functions import get_hash_of_source
from trader.utilities.functions.currency_ohlcv import fetch_currency_ohlcv_as_dataframe


class CurrencyOHLCVImplementation(CurrencyImplementation):
    def fetch_implementation_version_id(self) -> int:
        with DBSession() as session:
            implementation = (
                session.query(CurrencyOHLCVImplementationVersion)
                .join(CurrencyOHLCVImplementationModel)
                .filter(
                    CurrencyOHLCVImplementationModel.name == self.NAME,
                    CurrencyOHLCVImplementationVersion.version == self.VERSION,
                )
                .one()
            )
        return implementation.id

    def fetch_open_positions(self) -> List[CurrencyOHLCVPosition]:
        ...

    def fetch_closed_positions(self) -> List[CurrencyOHLCVPosition]:
        pass

    @staticmethod
    def fetch_strategy_version_id(strategy: CurrencyStrategy, is_entrance: bool) -> int:
        with DBSession() as session:
            strategy_version = (
                session.query(CurrencyOHLCVStrategyVersion)
                .join(CurrencyOHLCVStrategy)
                .filter(
                    CurrencyOHLCVStrategy.name == strategy.NAME,
                    CurrencyOHLCVStrategy.is_entrance.is_(is_entrance),
                    CurrencyOHLCVStrategyVersion.version == strategy.VERSION,
                )
                .one()
            )
        if strategy_version.source_code_md5_hash != get_hash_of_source(strategy):
            raise Exception("MD5 hash of source does not match persisted value for strategy {strategy.NAME}")
        return strategy_version.id

    def generate_dataframe(self) -> pd.DataFrame:
        return fetch_currency_ohlcv_as_dataframe(
            self.source, self.base_currency, self.quote_currency, self.timeframe, self.from_inclusive
        )
