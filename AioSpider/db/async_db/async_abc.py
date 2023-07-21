from abc import ABCMeta, abstractmethod


class AbcDB(metaclass=ABCMeta):

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.connect()

    @abstractmethod
    async def find_one(self, table: str, encoding=None):
        pass

    @abstractmethod
    async def find_many(self, table: str, encoding=None):
        pass

    @abstractmethod
    async def insert(self, table: str, items: list, auto_update: bool = False):
        pass

    @abstractmethod
    def remove_one(self):
        pass

    @abstractmethod
    def remove_many(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def close(self):
        pass
