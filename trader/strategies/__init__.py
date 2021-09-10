from sqlalchemy.orm import Session
from trader.connections.database import DBSession
from trader.models.currency_ohlcv_strategy import (
    CurrencyOHLCVStrategy,
    CurrencyOHLCVStrategyVersion,
    CurrencyOHLCVStrategyVersionParameter,
    CurrencyOHLCVStrategyVersionXCurrencyOHLCVStrategyVersionParameter,
)
from trader.strategies.currency.base import CurrencyStrategy
from trader.strategies.currency.entrance.currency_ohlcv.bollinger_bands import (
    BollingerBandsEntranceCurrencyOHLCVStrategy,
)
from trader.strategies.currency.exit.currency_ohlcv.trailing_stop_loss import TrailingStopLossExitCurrencyOHLCVStrategy
from trader.utilities.functions import get_hash_of_source, get_init_parameters


def initialize_ohlcv_strategy(session: Session, strategy: CurrencyStrategy) -> None:
    parameters = get_init_parameters(strategy)
    if set(parameters) != strategy.NORMAL_PARAMETER_SPACE.keys():
        raise Exception(f"Init parameters and NORMAL_PARAMETER_SPACE keys do not match for strategy {strategy.NAME}")
    strategy = (
        session.query(CurrencyOHLCVStrategy)
        .filter_by(
            name=strategy.NAME,
            is_entrance=strategy.IS_ENTRANCE,
        )
        .one_or_none()
    )
    if not strategy:
        strategy = CurrencyOHLCVStrategy(
            name=strategy.NAME,
            is_entrance=strategy.IS_ENTRANCE,
        )
        session.add(strategy)
        session.flush()
    version = (
        session.query(CurrencyOHLCVStrategyVersion)
        .filter_by(currency_ohlcv_strategy_id=strategy.id, version=strategy.VERSION)
        .one_or_none()
    )
    if not version:
        version = CurrencyOHLCVStrategyVersion(
            currency_ohlcv_strategy_id=strategy.id,
            version=strategy.VERSION,
            source_code_md5_hash=get_hash_of_source(strategy),
        )
        session.add(version)
        session.flush()
        for parameter in parameters:
            parameter = parameter.lower()
            version_parameter = (
                session.query(CurrencyOHLCVStrategyVersionParameter).filter_by(parameter=parameter).one_or_none()
            )
            if not version_parameter:
                version_parameter = CurrencyOHLCVStrategyVersionParameter(parameter=parameter)
                session.add(version_parameter)
                session.flush()
            link = CurrencyOHLCVStrategyVersionXCurrencyOHLCVStrategyVersionParameter(
                currency_strategy_version_id=version.id, currency_strategy_version_parameter_id=version_parameter.id
            )
            session.add(link)
    elif version.source_code_md5_hash != get_hash_of_source(strategy):
        raise Exception("MD5 hash of source does not match persisted value for strategy {strategy.NAME}")


def initialize_strategies() -> None:
    with DBSession() as session:
        for item in (
            BollingerBandsEntranceCurrencyOHLCVStrategy,
            TrailingStopLossExitCurrencyOHLCVStrategy,
        ):
            initialize_ohlcv_strategy(session, item)
        session.commit()
