from abc import abstractmethod
from dataclasses import dataclass
from trader.connections.cache import cache


@dataclass(frozen=True)
class BaseData:
    cache_key: str

    @abstractmethod
    def query_instance(self):
        ...

    def get_instance(self, raise_exception: bool = True):
        instance = self.query_instance()
        if raise_exception and not instance:
            raise Exception("Initial data does not exist")
        return instance

    @abstractmethod
    def create_instance(self):
        ...

    def fetch_id(self) -> int:
        cache_value = cache.get(self.cache_key)
        if not cache_value:
            instance = self.get_instance()
            instance_id = instance.id
            cache.set(self.cache_key, instance.id)
        else:
            instance_id = int(cache_value.decode())
        return instance_id
