__all__ = ['PendingRequest']

import time
from typing import Tuple

from AioSpider.http.base import BaseRequest
from AioSpider.requestpool.abc import RequestBaseABC


class PendingRequest(RequestBaseABC):

    def __init__(self):
        # {(request, time.time()), (request, time.time())}
        self.name = 'pending'
        self.pending: Tuple[BaseRequest, int] = set()

    async def put_request(self, request: BaseRequest):
        """将请求添加到队列"""
        self.pending.add((request, time.time()))
        return request

    async def get_request(self):
        """从url池中取url"""
        return self.pending.pop()[0] if self.pending else None

    async def has_request(self, request: BaseRequest):
        """ 判断请求是否存在 """
        return True if request in [i[0] for i in self.pending] else False

    async def remove_request(self, request: BaseRequest):
        """把request移出队列"""

        for i in self.pending:
            if request not in i:
                continue
            self.pending.remove(i)
            break

    def request_size(self):
        return self.pending.__len__()
