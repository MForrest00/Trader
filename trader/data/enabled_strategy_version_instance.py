from trader.connections.database import session
from trader.data.initial.user import USER_ADMIN
from trader.models.enabled_strategy_version_instance import (
    EnabledStrategyVersionInstance,
    EnabledStrategyVersionInstanceHistory,
)
from trader.models.strategy import Strategy, StrategyVersion, StrategyVersionInstance
from trader.utilities.initial_enabled_data import (
    INITIAL_ENTRY_ENABLED_STRATEGY_VERSION_INSTANCES,
    INITIAL_EXIT_ENABLED_STRATEGY_VERSION_INSTANCES,
)


def set_initial_enabled_strategy_version_instances() -> None:
    admin_id = USER_ADMIN.fetch_id()
    timeframes = (
        INITIAL_ENTRY_ENABLED_STRATEGY_VERSION_INSTANCES.keys() | INITIAL_EXIT_ENABLED_STRATEGY_VERSION_INSTANCES.keys()
    )
    for timeframe in timeframes:
        timeframe_id = timeframe.fetch_id()
        enabled_strategy_version_instances = (
            *INITIAL_ENTRY_ENABLED_STRATEGY_VERSION_INSTANCES.get(timeframe, ()),
            *INITIAL_EXIT_ENABLED_STRATEGY_VERSION_INSTANCES.get(timeframe, ()),
        )
        for item in enabled_strategy_version_instances:
            strategy_version_instance = (
                session.query(StrategyVersionInstance)
                .join(StrategyVersion)
                .join(Strategy)
                .filter(
                    Strategy.name == item.strategy.NAME,
                    Strategy.is_entry.is_(item.strategy.IS_ENTRY),
                    StrategyVersion.version == item.strategy.VERSION,
                    StrategyVersionInstance.arguments == item.arguments,
                )
                .one_or_none()
            )
            if not strategy_version_instance:
                strategy_version = item.strategy.get_strategy_version()
                strategy_version_instance = StrategyVersionInstance(
                    strategy_version_id=strategy_version.id,
                    arguments=item.arguments,
                )
                session.add(strategy_version_instance)
                session.flush()
            if not strategy_version_instance.enabled_strategy_version_instance:
                enabled_strategy_version_instance = EnabledStrategyVersionInstance(
                    strategy_version_instance_id=strategy_version_instance.id,
                    timeframe_id=timeframe_id,
                )
                session.add(enabled_strategy_version_instance)
                session.flush()
                enabled_strategy_version_instance_history = EnabledStrategyVersionInstanceHistory(
                    enabled_strategy_version_instance_id=enabled_strategy_version_instance.id,
                    user_id=admin_id,
                    priority=item.priority,
                )
                session.add(enabled_strategy_version_instance_history)
    session.commit()
