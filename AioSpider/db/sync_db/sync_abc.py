from abc import ABCMeta, abstractmethod


class AbcDB(metaclass=ABCMeta):

    @abstractmethod
    async def find_one(self):
        pass

    @abstractmethod
    async def find_many(self):
        pass

    @abstractmethod
    async def insert(self, table: str, item: dict):
        pass
    
    @abstractmethod
    async def update(self, table: str, item: dict):
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
