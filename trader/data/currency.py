import xml.etree.ElementTree as ET
import requests
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.persistence.models.currency import Currency
from trader.persistence.base_data import ISO


def update_iso_currency_codes() -> None:
    response = requests.get(
        "https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/amendments/lists/"
        + "list_one.xml"
    )
    tree = ET.fromstring(response.text)
    iso_id = int(cache.get(ISO.cache_key).decode())
    with DBSession() as session:
        for currency in tree[0]:
            name = currency.find("CcyNm").text
            symbol = currency.find("Ccy").text
            currency = session.query(Currency).filter(Currency.name == name, Currency.symbol == symbol).first()
            if not currency:
                currency = Currency(source_id=iso_id, name=name, symbol=symbol, is_cryptocurrency=False)
                session.add(currency)
        session.commit()
