from trader.connections.database import DBSession
from trader.models.enabled_strategy_version_instance import EnabledStrategyVersionInstance
from trader.models.strategy import Strategy, StrategyVersion, StrategyVersionInstance
from trader.utilities.constants import (
    INITIAL_ENTRY_ENABLED_STRATEGY_VERSION_INSTANCES,
    INITIAL_EXIT_ENABLED_STRATEGY_VERSION_INSTANCES,
)
from trader.utilities.functions import fetch_base_data_id


def set_initial_enabled_strategy_version_instances() -> None:
    with DBSession() as session:
        timeframes = (
            INITIAL_ENTRY_ENABLED_STRATEGY_VERSION_INSTANCES.keys()
            | INITIAL_EXIT_ENABLED_STRATEGY_VERSION_INSTANCES.keys()
        )
        for timeframe in timeframes:
            enabled_strategy_version_instances = (
                *INITIAL_ENTRY_ENABLED_STRATEGY_VERSION_INSTANCES.get(timeframe, ()),
                *INITIAL_EXIT_ENABLED_STRATEGY_VERSION_INSTANCES.get(timeframe, ()),
            )
            for enabled_strategy_version_instance in enabled_strategy_version_instances:
                strategy_version_instance = (
                    session.query(StrategyVersionInstance)
                    .join(StrategyVersion)
                    .join(Strategy)
                    .filter(
                        Strategy.name == enabled_strategy_version_instance.strategy.NAME,
                        Strategy.is_entry.is_(enabled_strategy_version_instance.strategy.IS_ENTRY),
                        StrategyVersion.version == enabled_strategy_version_instance.strategy.VERSION,
                        StrategyVersionInstance.arguments == enabled_strategy_version_instance.arguments,
                    )
                    .one_or_none()
                )
                if strategy_version_instance:
                    enabled_strategy_version_instance = EnabledStrategyVersionInstance(
                        strategy_version_instance_id=strategy_version_instance.id,
                        timeframe_id=fetch_base_data_id(timeframe),
                        priority=enabled_strategy_version_instance.priority,
                    )
                    session.add(enabled_strategy_version_instance)
        session.commit()
