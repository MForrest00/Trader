from sqlalchemy.orm import Session
from trader.connections.database import DBSession
from trader.data.base import CURRENCY_OHLCV
from trader.models.currency_strategy import (
    CurrencyStrategy,
    CurrencyStrategyVersion,
    CurrencyStrategyVersionParameter,
    CurrencyStrategyVersionXCurrencyStrategyVersionParameter,
)
from trader.strategies.currency.base import CurrencyStrategy as CurrencyStrategyObject
from trader.strategies.currency.entrance.currency_ohlcv.bollinger_bands import (
    BollingerBandsCurrencyOHLCVEntranceCurrencyStrategy,
)
from trader.strategies.currency.exit.currency_ohlcv.trailing_stop_loss import (
    TrailingStopLossCurrencyOHLCVExitCurrencyStrategy,
)
from trader.utilities.functions import fetch_base_data_id, get_hash_of_source, get_init_parameters


def initialize_strategy(
    session: Session,
    currency_strategy_implementation_type_id: int,
    strategy: CurrencyStrategyObject,
) -> None:
    strategy = (
        session.query(CurrencyStrategy)
        .filter_by(
            currency_strategy_implementation_type_id=currency_strategy_implementation_type_id,
            name=strategy.NAME,
            is_entrance=strategy.IS_ENTRANCE,
        )
        .one_or_none()
    )
    if not strategy:
        strategy = CurrencyStrategy(
            currency_strategy_implementation_type_id=currency_strategy_implementation_type_id,
            name=strategy.NAME,
            is_entrance=strategy.IS_ENTRANCE,
        )
        session.add(strategy)
        session.flush()
    version = (
        session.query(CurrencyStrategyVersion)
        .filter_by(currency_ohlcv_strategy_id=strategy.id, version=strategy.VERSION)
        .one_or_none()
    )
    if not version:
        version = CurrencyStrategyVersion(
            currency_ohlcv_strategy_id=strategy.id,
            version=strategy.VERSION,
            source_code_md5_hash=get_hash_of_source(strategy),
        )
        session.add(version)
        session.flush()
        for parameter in get_init_parameters(strategy):
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
        for item in (
            BollingerBandsCurrencyOHLCVEntranceCurrencyStrategy,
            TrailingStopLossCurrencyOHLCVExitCurrencyStrategy,
        ):
            initialize_strategy(session, currency_ohlcv_id, item)
        session.commit()
