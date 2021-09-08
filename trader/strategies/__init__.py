from inspect import signature
from typing import List
from sqlalchemy.orm import Session
from trader.connections.database import DBSession
from trader.data.base import CURRENCY_OHLCV
from trader.models.currency_strategy import (
    CurrencyStrategy,
    CurrencyStrategyVersion,
    CurrencyStrategyVersionParameter,
    CurrencyStrategyVersionXCurrencyStrategyVersionParameter,
)
from trader.strategies.currency.entrance.currency_ohlcv.bollinger_bands import (
    BollingerBandsCurrencyOHLCVEntranceCurrencyStrategy,
)
from trader.strategies.currency.exit.currency_ohlcv.trailing_stop_loss import (
    TrailingStopLossCurrencyOHLCVExitCurrencyStrategy,
)
from trader.utilities.functions import fetch_base_data_id


def get_parameters(function) -> List[str]:
    parameters = signature(function.__init__).parameters.keys()
    return sorted(list(parameters - set(["self"])))


def initialize_strategy(
    session: Session,
    currency_strategy_implementation_type_id: int,
    name: str,
    is_entrance: bool,
    version: str,
    parameters: List[str],
) -> None:
    strategy = (
        session.query(CurrencyStrategy)
        .filter_by(
            currency_strategy_implementation_type_id=currency_strategy_implementation_type_id,
            name=name,
            is_entrance=is_entrance,
        )
        .one_or_none()
    )
    if not strategy:
        strategy = CurrencyStrategy(
            currency_strategy_implementation_type_id=currency_strategy_implementation_type_id,
            name=name,
            is_entrance=is_entrance,
        )
        session.add(strategy)
        session.flush()
    version = (
        session.query(CurrencyStrategyVersion)
        .filter_by(currency_ohlcv_strategy_id=strategy.id, version=version)
        .one_or_none()
    )
    if not version:
        version = CurrencyStrategyVersion(currency_ohlcv_strategy_id=strategy.id, version=version)
        session.add(version)
        session.flush()
        for parameter in parameters:
            parameter = parameter.lower()
            version_parameter = (
                session.query(CurrencyStrategyVersionParameter).filter_by(parameter=parameter).one_or_none()
            )
            if not version_parameter:
                version_parameter = CurrencyStrategyVersionParameter(parameter=parameter)
                session.add(version_parameter)
                session.flush()
            link = CurrencyStrategyVersionXCurrencyStrategyVersionParameter(
                currency_strategy_version_id=version.id, currency_strategy_version_parameter_id=version_parameter.id
            )
            session.add(link)


def initialize_strategies() -> None:
    currency_ohlcv_id = fetch_base_data_id(CURRENCY_OHLCV)
    with DBSession() as session:
        for item in (BollingerBandsCurrencyOHLCVEntranceCurrencyStrategy,):
            initialize_strategy(session, currency_ohlcv_id, item.NAME, True, item.VERSION, get_parameters(item))
        for item in (TrailingStopLossCurrencyOHLCVExitCurrencyStrategy,):
            initialize_strategy(session, currency_ohlcv_id, item.NAME, False, item.VERSION, get_parameters(item))
        session.commit()
