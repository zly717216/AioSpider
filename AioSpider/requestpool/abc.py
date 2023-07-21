__all__ = ['RequestBaseABC']

from abc import abstractmethod
from AioSpider.http.base import BaseRequest


class RequestBaseABC:

    @abstractmethod
    async def put_request(self, request: BaseRequest):
        pass

    @abstractmethod
    async def get_requests(self):
        pass

    @abstractmethod
    async def has_request(self, request: BaseRequest):
        pass

    @abstractmethod
    async def remove_request(self, request: BaseRequest):
        pass

    @abstractmethod
    def request_size(self):
        pass
