from bs4 import BeautifulSoup
import requests
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.data.base import ISO
from trader.models.currency import Currency
from trader.models.standard_currency import StandardCurrency


def update_currency_data_from_iso() -> None:
    response = requests.get("https://en.wikipedia.org/wiki/ISO_4217")
    soup = BeautifulSoup(response.text, "lxml")
    table_h2 = soup.select("span#Active_codes")[0]
    table_body_rows = table_h2.parent.next_sibling.next_sibling.next_sibling.next_sibling.find_all("tr")[1:]
    iso_id = int(cache.get(ISO.cache_key).decode())
    with DBSession() as session:
        for table_body_row in table_body_rows:
            table_data = table_body_row.find_all("td")
            name = table_data[3].find_all(text=True)[0]
            symbol = table_data[0].text
            iso_numeric_code = table_data[1].text
            minor_unit = table_data[2].text if table_data[2].text.isnumeric() else None
            currency = session.query(Currency).filter(Currency.name == name, Currency.symbol == symbol).first()
            if not currency:
                currency = Currency(source_id=iso_id, name=name, symbol=symbol)
                session.add(currency)
                session.flush()
                standard_currency = StandardCurrency(
                    currency_id=currency.id, iso_numeric_code=iso_numeric_code, minor_unit=minor_unit
                )
                session.add(standard_currency)
            else:
                standard_currency = currency.standard_currency
                if not standard_currency:
                    standard_currency = StandardCurrency(
                        currency_id=currency.id, iso_numeric_code=iso_numeric_code, minor_unit=minor_unit
                    )
                    session.add(standard_currency)
                else:
                    standard_currency.update(
                        {
                            "iso_numeric_code": iso_numeric_code,
                            "minor_unit": minor_unit,
                        }
                    )
        session.commit()
