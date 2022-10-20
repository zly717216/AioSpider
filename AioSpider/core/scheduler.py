import time

from AioSpider import AioObject
from AioSpider.core.requestpool import RequestPool


class Scheduler(AioObject):

    async def __init__(self):
        self._request_pool = await RequestPool()

    @property
    def failure_pool(self):
        return self._request_pool.failure

    async def push_request(self, request):
        """ 将请求添加到队列 """
        await self._request_pool._push_to_waiting(request)

    async def get_request(self):
        """ 取出请求 """
        return await self._request_pool._get_request()

    async def set_status(self, response):
        """ 设置请求队列 """
        await self._request_pool._set_status(response)

    def get_waiting_size(self):
        """ 获取待下载请求队列长度 """

        return self._request_pool._waiting_qsize()

    def pending_empty(self):
        """ 判断pending队列中是否有请求 """

        return self._request_pool._pending_empty()

    def waiting_empty(self):
        """ 判断waiting队列中是否有请求 """

        return self._request_pool._waiting_empty()

    def failure_empty(self):
        """ 判断failure队列中是否有请求 """

        return self._request_pool._failure_empty()

    def empty(self):

        if self.pending_empty() and self.waiting_empty() and self.failure_empty():
            return True

        return False

    async def request_count(self):
        return await self._request_pool._url_db_qsize()

    async def close(self):
        await self._request_pool.close()
