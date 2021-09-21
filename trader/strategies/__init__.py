from itertools import product
from typing import Any, Dict, List, Sequence
from sqlalchemy.orm import Session
from trader.connections.database import DBSession
from trader.models.strategy import (
    Strategy,
    StrategyVersion,
    StrategyVersionInstance,
    StrategyVersionParameter,
    StrategyVersionXStrategyVersionParameter,
    StrategyVersionXSupplementalDataFeed,
)
from trader.strategies.base import Strategy as StrategyBase
from trader.strategies.entry.currency_ohlcv.bollinger_bands import BollingerBandsCurrencyOHLCVEntryStrategy
from trader.strategies.exit.currency_ohlcv.trailing_stop_loss import TrailingStopLossCurrencyOHLCVExitStrategy
from trader.utilities.functions import fetch_base_data_id, get_hash_of_source, get_init_parameters


def parameter_space_to_arguments_dict(strategy: StrategyBase) -> List[Dict[str, Any]]:
    parameter_names: List[str] = []
    parameter_values: List[Sequence[Any]] = []
    for k, v in strategy.PARAMETER_SPACE.items():
        parameter_names.append(k)
        parameter_values.append(v)
    product_parameter_values = product(*parameter_values)
    return [dict(zip(parameter_names, p)) for p in product_parameter_values]


def initialize_ohlcv_strategy(session: Session, strategy: StrategyBase) -> None:
    parameters = get_init_parameters(strategy)
    if set(parameters) != strategy.PARAMETER_SPACE.keys():
        raise Exception(f"Init parameters and PARAMETER_SPACE keys do not match for strategy {strategy.NAME}")
    strategy_object = (
        session.query(Strategy)
        .filter_by(
            name=strategy.NAME,
            is_entry=strategy.IS_ENTRY,
        )
        .one_or_none()
    )
    if not strategy_object:
        strategy_object = Strategy(
            name=strategy.NAME,
            is_entry=strategy.IS_ENTRY,
        )
        session.add(strategy_object)
        session.flush()
    version = (
        session.query(StrategyVersion).filter_by(strategy_id=strategy_object.id, version=strategy.VERSION).one_or_none()
    )
    if not version:
        version = StrategyVersion(
            strategy_id=strategy_object.id,
            base_data_feed_id=fetch_base_data_id(strategy.BASE_DATA_FEED),
            version=strategy.VERSION,
            source_code_md5_hash=get_hash_of_source(strategy),
        )
        session.add(version)
        session.flush()
        for data_feed in strategy.SUPPLEMENTAL_DATA_FEEDS:
            data_feed_id = fetch_base_data_id(data_feed)
            link = StrategyVersionXSupplementalDataFeed(strategy_version_id=version.id, data_feed_id=data_feed_id)
            session.add(link)
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
        arguments_dict = parameter_space_to_arguments_dict(strategy)
        for item in arguments_dict:
            instance = StrategyVersionInstance(strategy_version_id=version.id, arguments=item)
            session.add(instance)
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
