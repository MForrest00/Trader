from typing import Dict
from bs4 import BeautifulSoup
import requests
from trader.connections.database import DBSession
from trader.data.base import CURRENCY_TYPE_STANDARD_CURRENCY, CURRENCY_TYPE_UNKNOWN_CURRENCY, SOURCE_ISO
from trader.models.country import Country, CountryXStandardCurrency
from trader.models.currency import Currency
from trader.models.standard_currency import StandardCurrency
from trader.utilities.functions import fetch_base_data_id


def update_standard_currencies_from_iso() -> None:
    iso_id = fetch_base_data_id(SOURCE_ISO)
    standard_currency_id = fetch_base_data_id(CURRENCY_TYPE_STANDARD_CURRENCY)
    unknown_currency_id = fetch_base_data_id(CURRENCY_TYPE_UNKNOWN_CURRENCY)
    response = requests.get("https://en.wikipedia.org/wiki/ISO_4217")
    soup = BeautifulSoup(response.text, "lxml")
    table_h2 = soup.select("span#Active_codes")[0]
    table_body_rows = table_h2.parent.next_sibling.next_sibling.next_sibling.next_sibling.find_all("tr")[1:]
    with DBSession() as session:
        countries: Dict[str, Country] = {}
        for table_body_row in table_body_rows:
            table_data = table_body_row.find_all("td")
            name = table_data[3].find_all(text=True)[0]
            symbol = table_data[0].find_all(text=True)[0]
            iso_numeric_code = table_data[1].text
            minor_unit = table_data[2].text if table_data[2].text.isnumeric() else None
            country_names = {country_anchor.text for country_anchor in table_data[4].find_all("a")}
            currency = (
                session.query(Currency)
                .filter(
                    Currency.currency_type_id.in_([standard_currency_id, unknown_currency_id]),
                    Currency.symbol == symbol,
                )
                .one_or_none()
            )
            if not currency:
                currency = Currency(source_id=iso_id, currency_type_id=standard_currency_id, name=name, symbol=symbol)
                session.add(currency)
                session.flush()
            elif currency.currency_type_id == unknown_currency_id:
                currency.source_id = iso_id
                currency.currency_type_id = standard_currency_id
                currency.name = name
            else:
                for item in currency.countries:
                    if item.country.name not in country_names:
                        item.is_active = False
            standard_currency = currency.standard_currency
            if not standard_currency:
                standard_currency = StandardCurrency(
                    currency_id=currency.id, iso_numeric_code=iso_numeric_code, minor_unit=minor_unit
                )
                session.add(standard_currency)
            else:
                standard_currency.iso_numeric_code = iso_numeric_code
                standard_currency.minor_unit = minor_unit
            for country_name in country_names:
                if country_name not in countries:
                    country = session.query(Country).filter_by(name=country_name).all()
                    countries[country_name] = country
                else:
                    country = countries[country_name]
                if len(country) != 1:
                    continue
                country_currency = (
                    session.query(CountryXStandardCurrency)
                    .filter_by(country_id=country[0].id, standard_currency_id=standard_currency.id)
                    .one_or_none()
                )
                if not country_currency:
                    country_currency = CountryXStandardCurrency(
                        source_id=iso_id,
                        country_id=country[0].id,
                        standard_currency_id=standard_currency.id,
                    )
                    session.add(country_currency)
                elif not country_currency.is_active:
                    country_currency.is_active = True
        session.commit()
