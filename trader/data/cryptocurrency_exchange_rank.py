import json
from typing import Dict
from bs4 import BeautifulSoup
import requests
from trader.connections.database import DBSession
from trader.data.base import SOURCE_COIN_MARKET_CAP, SOURCE_TYPE_CRYPTOCURRENCY_EXCHANGE
from trader.models.asset import Asset
from trader.models.country import Country, CountryXCryptocurrencyExchange
from trader.models.cryptocurrency_exchange import (
    CryptocurrencyExchange,
    CryptocurrencyExchangeXStandardCurrency,
    CryptocurrencyExchangeType,
)
from trader.models.cryptocurrency_exchange_rank import CryptocurrencyExchangeRank, CryptocurrencyExchangeRankPull
from trader.models.standard_currency import StandardCurrency
from trader.models.source import Source
from trader.utilities.functions import fetch_base_data_id, iso_time_string_to_datetime


def update_cryptocurrency_exchange_ranks_from_coin_market_cap() -> None:
    coin_market_cap_id = fetch_base_data_id(SOURCE_COIN_MARKET_CAP)
    cryptocurrency_exchange_id = fetch_base_data_id(SOURCE_TYPE_CRYPTOCURRENCY_EXCHANGE)
    response = requests.get("https://coinmarketcap.com/rankings/exchanges/")
    soup = BeautifulSoup(response.text, "lxml")
    data = json.loads(soup.select("script#__NEXT_DATA__")[0].string)
    cryptocurrency_exchange_ranks = data["props"]["initialProps"]["pageProps"]["exchange"]
    with DBSession() as session:
        exchange_rank_pull = CryptocurrencyExchangeRankPull(source_id=coin_market_cap_id)
        session.add(exchange_rank_pull)
        session.flush()
        exchange_types_lookup: Dict[str, CryptocurrencyExchangeType] = {}
        standard_currencies_lookup: Dict[str, StandardCurrency] = {}
        countries_lookup: Dict[str, Country] = {}
        for record in cryptocurrency_exchange_ranks:
            name = record["name"]
            source_entity_id = record["id"]
            source_slug = record["slug"]
            source_date_launched = (
                iso_time_string_to_datetime(record["dateLaunched"]) if record["dateLaunched"] else None
            )
            source_date_last_updated = iso_time_string_to_datetime(record["lastUpdated"])
            exchange_type_description = record["type"].lower()
            standard_currency_symbols = record["fiats"]
            country_iso_alpha_2_codes = record["countries"]
            if exchange_type_description:
                if exchange_type_description not in exchange_types_lookup:
                    exchange_type = (
                        session.query(CryptocurrencyExchangeType)
                        .filter_by(description=exchange_type_description)
                        .one_or_none()
                    )
                    if not exchange_type:
                        exchange_type = CryptocurrencyExchangeType(
                            source_id=coin_market_cap_id,
                            description=exchange_type_description,
                        )
                        session.add(exchange_type)
                        session.flush()
                    exchange_types_lookup[exchange_type_description] = exchange_type
                else:
                    exchange_type = exchange_types_lookup[exchange_type_description]
                exchange_type_id = exchange_type.id
            else:
                exchange_type_id = None
            source = session.query(Source).filter_by(source_type_id=cryptocurrency_exchange_id, name=name).one_or_none()
            if not source:
                source = Source(source_id=coin_market_cap_id, source_type_id=cryptocurrency_exchange_id, name=name)
                session.add(source)
                session.flush()
            exchange = source.cryptocurrency_exchange
            if not exchange:
                exchange = CryptocurrencyExchange(
                    source_id=source.id,
                    cryptocurrency_exchange_type_id=exchange_type_id,
                    source_entity_id=source_entity_id,
                    source_slug=source_slug,
                    source_date_launched=source_date_launched,
                    source_date_last_updated=source_date_last_updated,
                )
                session.add(exchange)
                session.flush()
            elif exchange.source_date_last_updated < source_date_last_updated:
                exchange.source_id = source.id
                exchange.cryptocurrency_exchange_type_id = exchange_type_id
                exchange.source_entity_id = source_entity_id
                exchange.source_slug = source_slug
                exchange.source_date_launched = source_date_launched
                exchange.source_date_last_updated = source_date_last_updated
                for item in exchange.standard_currencies:
                    if item.standard_currency.currency.symbol not in standard_currency_symbols:
                        item.is_active = False
                for item in exchange.countries:
                    if item.country.iso_alpha_2_code not in country_iso_alpha_2_codes:
                        item.is_active = False
            for standard_currency_symbol in standard_currency_symbols:
                if standard_currency_symbol not in standard_currencies_lookup:
                    standard_currency = (
                        session.query(StandardCurrency)
                        .join(Asset)
                        .filter(Asset.symbol == standard_currency_symbol)
                        .one_or_none()
                    )
                    standard_currencies_lookup[standard_currency_symbol] = standard_currency
                else:
                    standard_currency = standard_currencies_lookup[standard_currency_symbol]
                if standard_currency:
                    cryptocurrency_exchange_x_standard_currency = (
                        session.query(CryptocurrencyExchangeXStandardCurrency)
                        .filter_by(
                            cryptocurrency_exchange_id=exchange.id,
                            standard_currency_id=standard_currency.id,
                        )
                        .one_or_none()
                    )
                    if not cryptocurrency_exchange_x_standard_currency:
                        cryptocurrency_exchange_x_standard_currency = CryptocurrencyExchangeXStandardCurrency(
                            source_id=coin_market_cap_id,
                            cryptocurrency_exchange_id=exchange.id,
                            standard_currency_id=standard_currency.id,
                        )
                        session.add(cryptocurrency_exchange_x_standard_currency)
                    elif not cryptocurrency_exchange_x_standard_currency.is_active:
                        cryptocurrency_exchange_x_standard_currency.is_active = True
            for country_iso_alpha_2_code in country_iso_alpha_2_codes:
                if country_iso_alpha_2_code not in countries_lookup:
                    country = session.query(Country).filter_by(iso_alpha_2_code=country_iso_alpha_2_code).one_or_none()
                    countries_lookup[country_iso_alpha_2_code] = country
                else:
                    country = countries_lookup[country_iso_alpha_2_code]
                if country:
                    country_x_cryptocurrency_exchange = (
                        session.query(CountryXCryptocurrencyExchange)
                        .filter_by(country_id=country.id, cryptocurrency_exchange_id=exchange.id)
                        .one_or_none()
                    )
                    if not country_x_cryptocurrency_exchange:
                        country_x_cryptocurrency_exchange = CountryXCryptocurrencyExchange(
                            source_id=coin_market_cap_id,
                            country_id=country.id,
                            cryptocurrency_exchange_id=exchange.id,
                        )
                        session.add(country_x_cryptocurrency_exchange)
                    elif not country_x_cryptocurrency_exchange.is_active:
                        country_x_cryptocurrency_exchange.is_active = True
            exchange_rank = CryptocurrencyExchangeRank(
                cryptocurrency_exchange_rank_pull_id=exchange_rank_pull.id,
                cryptocurrency_exchange_id=exchange.id,
                rank=record["rank"],
                spot_vol_24h=record.get("spotVol24h"),
                derivatives_vol_24h=record.get("derivativesVol24h"),
                derivatives_open_interests=record.get("derivativesOpenInterests"),
                weekly_web_visits=record["visits"],
                market_share_percentage=record.get("marketSharePct"),
                maker_fee=record["makerFee"],
                taker_fee=record["takerFee"],
                source_score=record["score"],
                source_liquidity_score=record["liquidity"],
            )
            session.add(exchange_rank)
        session.commit()
