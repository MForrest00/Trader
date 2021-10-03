from typing import Dict
from trader.connections.database import session
from trader.data.initial.asset_type import AssetTypeData
from trader.models.asset import Asset
from trader.models.enabled_quote_asset import EnabledQuoteAsset
from trader.utilities.initial_enabled_data import INITIAL_ENABLED_QUOTE_ASSETS


def set_initial_enabled_quote_assets() -> None:
    asset_type_lookup: Dict[AssetTypeData, int] = {}
    for item in INITIAL_ENABLED_QUOTE_ASSETS:
        if item.asset_type not in asset_type_lookup:
            asset_type_lookup[item.asset_type] = item.asset_type.fetch_id()
        asset = (
            session.query(Asset)
            .filter_by(asset_type_id=asset_type_lookup[item.asset_type], symbol=item.symbol)
            .one_or_none()
        )
        if asset:
            if not asset.enabled_quote_asset:
                enabled_quote_asset = EnabledQuoteAsset(asset_id=asset.id, priority=item.priority)
                session.add(enabled_quote_asset)
    session.commit()
