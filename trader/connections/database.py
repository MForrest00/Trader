from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from trader.utilities.environment import (
    POSTGRES_DATABASE,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


connection_string = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
)
database = create_engine(connection_string)
DBSession = sessionmaker(database)
session = DBSession()
