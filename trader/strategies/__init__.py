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
from trader.strategies.entry.asset_ohlcv.bollinger_bands import BollingerBandsAssetOHLCVEntryStrategy
from trader.strategies.exit.asset_ohlcv.trailing_stop_loss import TrailingStopLossAssetOHLCVExitStrategy
from trader.utilities.functions import fetch_base_data_id, get_hash_of_source, get_init_parameters


def parameter_space_to_arguments_dict(strategy: StrategyBase) -> List[Dict[str, Any]]:
    parameter_names: List[str] = []
    parameter_values: List[Sequence[Any]] = []
    for k, v in strategy.PARAMETER_SPACE.items():
        parameter_names.append(k)
        parameter_values.append(v)
    product_parameter_values = product(*parameter_values)
    return [dict(zip(parameter_names, p)) for p in product_parameter_values]


def initialize_strategy(session: Session, strategy: StrategyBase) -> None:
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
    strategy_version = (
        session.query(StrategyVersion).filter_by(strategy_id=strategy_object.id, version=strategy.VERSION).one_or_none()
    )
    if not strategy_version:
        strategy_version = StrategyVersion(
            strategy_id=strategy_object.id,
            base_data_feed_id=fetch_base_data_id(strategy.BASE_DATA_FEED),
            version=strategy.VERSION,
            source_code_md5_hash=get_hash_of_source(strategy),
        )
        session.add(strategy_version)
        session.flush()
        for data_feed in strategy.SUPPLEMENTAL_DATA_FEEDS:
            data_feed_id = fetch_base_data_id(data_feed)
            strategy_version_x_supplemental_data_feed = StrategyVersionXSupplementalDataFeed(
                strategy_version_id=strategy_version.id, data_feed_id=data_feed_id
            )
            session.add(strategy_version_x_supplemental_data_feed)
        for parameter in parameters:
            parameter = parameter.lower()
            strategy_version_parameter = (
                session.query(StrategyVersionParameter).filter_by(parameter=parameter).one_or_none()
            )
            if not strategy_version_parameter:
                strategy_version_parameter = StrategyVersionParameter(parameter=parameter)
                session.add(strategy_version_parameter)
                session.flush()
            strategy_version_x_strategy_version_parameter = StrategyVersionXStrategyVersionParameter(
                strategy_version_id=strategy_version.id, strategy_version_parameter_id=strategy_version_parameter.id
            )
            session.add(strategy_version_x_strategy_version_parameter)
        arguments_dict = parameter_space_to_arguments_dict(strategy)
        for item in arguments_dict:
            strategy_version_instance = StrategyVersionInstance(strategy_version_id=strategy_version.id, arguments=item)
            session.add(strategy_version_instance)
    elif strategy_version.source_code_md5_hash != get_hash_of_source(strategy):
        raise Exception("MD5 hash of source does not match persisted value for strategy {strategy.NAME}")


def initialize_strategies() -> None:
    with DBSession() as session:
        for item in (
            BollingerBandsAssetOHLCVEntryStrategy,
            TrailingStopLossAssetOHLCVExitStrategy,
        ):
            initialize_strategy(session, item)
        session.commit()
