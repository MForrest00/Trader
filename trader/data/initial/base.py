from abc import abstractmethod
from dataclasses import dataclass
from sqlalchemy.orm import Session
from trader.connections.cache import cache
from trader.connections.database import DBSession


@dataclass(frozen=True)
class BaseData:
    cache_key: str

    @abstractmethod
    def query_instance(self, session: Session):
        ...

    @abstractmethod
    def create_instance(self):
        ...

    def fetch_id(self) -> int:
        cache_value = cache.get(self.cache_key)
        if not cache_value:
            with DBSession() as session:
                instance = self.query_instance(session)
                if instance:
                    instance_id = instance.id
                    cache.set(self.cache_key, instance.id)
                else:
                    raise Exception("Initial data does not exist")
        else:
            instance_id = int(cache_value.decode())
        return instance_id
