from sqlalchemy.orm import Session
from trader.connections.database import DBSession
from trader.data.base import ASSET_TYPE_CRYPTOCURRENCY, ASSET_TYPE_STANDARD_CURRENCY
from trader.models.asset import Asset
from trader.models.enabled_quote_asset import EnabledQuoteAsset
from trader.utilities.constants import INITIAL_ENABLED_QUOTE_CRYPTOCURRENCIES, INITIAL_ENABLED_QUOTE_STANDARD_CURRENCIES
from trader.utilities.functions import fetch_base_data_id


def set_enabled_quote_asset(session: Session, asset_type_id: int, enabled_quote_asset: EnabledQuoteAsset) -> None:
    asset = session.query(Asset).filter_by(asset_type_id=asset_type_id, symbol=enabled_quote_asset.symbol).one_or_none()
    if asset:
        if not asset.enabled_quote_asset:
            enabled_quote_asset = EnabledQuoteAsset(asset_id=asset.id, priority=enabled_quote_asset.priority)
            session.add(enabled_quote_asset)


def set_initial_enabled_quote_assets() -> None:
    with DBSession() as session:
        for enabled_quote_cryptocurrency in INITIAL_ENABLED_QUOTE_CRYPTOCURRENCIES:
            asset_type_id = fetch_base_data_id(ASSET_TYPE_CRYPTOCURRENCY)
            set_enabled_quote_asset(session, asset_type_id, enabled_quote_cryptocurrency)
        for enabled_quote_standard_currency in INITIAL_ENABLED_QUOTE_STANDARD_CURRENCIES:
            asset_type_id = fetch_base_data_id(ASSET_TYPE_STANDARD_CURRENCY)
            set_enabled_quote_asset(session, asset_type_id, enabled_quote_standard_currency)
        session.commit()
