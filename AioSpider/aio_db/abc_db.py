from abc import ABCMeta, abstractmethod


class ABCDB(metaclass=ABCMeta):

    engine = None

    @abstractmethod
    async def find_one(self):
        pass

    @abstractmethod
    async def insert_one(self, table: str, item: dict, encoding=None):
        pass

    @abstractmethod
    async def insert_many(self, table: str, items: list, encoding=None):
        pass

    @abstractmethod
    def remove_one(self):
        pass

    @abstractmethod
    def remove_many(self):
        pass

    @abstractmethod
    def close(self):
        pass
