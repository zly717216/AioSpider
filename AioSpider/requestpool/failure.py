__all__ = ['FailureRequest']

from collections import defaultdict
from typing import Dict

from AioSpider import logger
from AioSpider.http.base import BaseRequest
from AioSpider.requestpool.abc import RequestBaseABC


class FailureRequest(RequestBaseABC):

    def __init__(self, settings):
        self.name = 'failure'
        # {request: times} 记录失败的URL的次数
        self.failure: Dict[BaseRequest: int] = defaultdict(int)
        self.max_failure_times = settings.SpiderRequestConfig.MAX_RETRY_TIMES

    async def put_request(self, request: BaseRequest):
        """将请求添加到队列"""

        if self.failure.get(request, 0) >= self.max_failure_times:
            logger.warning(f'{request}失败次数超限，系统将其自动丢弃处理！')
            return False

        self.failure[request] = self.failure.get(request, 0) + 1
        return True

    async def remove_request(self, request: BaseRequest):
        """将请求移除队列"""
        self.failure.pop(request)

    async def get_requests(self, count):
        """从队列中获取一个请求"""
        
        count = count if count <= self.request_size() else self.request_size()
        if not self.failure:
            return

        for _ in range(count):
            yield self.failure.popitem()[0]

    async def has_request(self, request: BaseRequest):
        return True if request in self.failure else False

    def request_size(self):
        return self.failure.__len__()

    def get_failure_times(self, request: BaseRequest):
        return self.failure.get(request, 0)
