from sqlalchemy.orm import Session
from trader.connections.database import DBSession
from trader.models.strategy import (
    Strategy,
    StrategyVersion,
    StrategyVersionParameter,
    StrategyVersionXStrategyVersionParameter,
)
from trader.strategies.base import Strategy as StrategyBase
from trader.strategies.entry.currency_ohlcv.bollinger_bands import BollingerBandsCurrencyOHLCVEntryStrategy
from trader.strategies.exit.currency_ohlcv.trailing_stop_loss import TrailingStopLossCurrencyOHLCVExitStrategy
from trader.utilities.functions import get_hash_of_source, get_init_parameters


def initialize_ohlcv_strategy(session: Session, strategy: StrategyBase) -> None:
    parameters = get_init_parameters(strategy)
    if set(parameters) != strategy.NORMAL_PARAMETER_SPACE.keys():
        raise Exception(f"Init parameters and NORMAL_PARAMETER_SPACE keys do not match for strategy {strategy.NAME}")
    strategy = (
        session.query(Strategy)
        .filter_by(
            name=strategy.NAME,
            is_entry=strategy.IS_ENTRY,
        )
        .one_or_none()
    )
    if not strategy:
        strategy = Strategy(
            name=strategy.NAME,
            is_entry=strategy.IS_ENTRY,
        )
        session.add(strategy)
        session.flush()
    version = session.query(StrategyVersion).filter_by(strategy_id=strategy.id, version=strategy.VERSION).one_or_none()
    if not version:
        version = StrategyVersion(
            strategy_id=strategy.id, version=strategy.VERSION, source_code_md5_hash=get_hash_of_source(strategy)
        )
        session.add(version)
        session.flush()
        for parameter in parameters:
            parameter = parameter.lower()
            version_parameter = session.query(StrategyVersionParameter).filter_by(parameter=parameter).one_or_none()
            if not version_parameter:
                version_parameter = StrategyVersionParameter(parameter=parameter)
                session.add(version_parameter)
                session.flush()
            link = StrategyVersionXStrategyVersionParameter(
                strategy_version_id=version.id, strategy_version_parameter_id=version_parameter.id
            )
            session.add(link)
    elif version.source_code_md5_hash != get_hash_of_source(strategy):
        raise Exception("MD5 hash of source does not match persisted value for strategy {strategy.NAME}")


def initialize_strategies() -> None:
    with DBSession() as session:
        for item in (
            BollingerBandsCurrencyOHLCVEntryStrategy,
            TrailingStopLossCurrencyOHLCVExitStrategy,
        ):
            initialize_ohlcv_strategy(session, item)
        session.commit()
