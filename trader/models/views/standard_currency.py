from textwrap import dedent
from trader.models.currency import Currency, CurrencyType
from trader.models.standard_currency import StandardCurrency


STANDARD_CURRENCY_SQL = dedent(
    """
    CREATE OR REPLACE VIEW public.standard_currency_view AS
    SELECT
        c.id AS currency_id
        ,c.name
        ,c.symbol
        ,sc.id AS standard_currency_id
        ,sc.iso_numeric_code
        ,sc.minor_unit
    FROM public.{currency_table} c
        INNER JOIN public.{currency_type_table} ct ON
            c.currency_type_id = ct.id
        INNER JOIN public.{standard_currency_table} sc ON
            c.id = sc.currency_id
    WHERE
        ct.description = 'Standard currency'
    """.format(
        currency_table=Currency.__tablename__,
        currency_type_table=CurrencyType.__tablename__,
        standard_currency_table=StandardCurrency.__tablename__,
    )
).strip()
