from typing import List, Union

from AioSpider import logger
from AioSpider import constants
from AioSpider.exceptions import SystemConfigError
from AioSpider.http.base import BaseRequest
from AioSpider.requestpool.done import RequestDB
from AioSpider.requestpool.pending import PendingRequest
from AioSpider.requestpool.failure import FailureRequest
from AioSpider.requestpool.waiting import WaitingRequest, WaitingRedisRequest
from AioSpider import pretty_table


class RequestPool:

    def __init__(self, spider, settings, connector):

        self.spider = spider
        self.settings = settings
        self.waiting = self._init_waiting(connector)
        self.pending = PendingRequest()
        self.failure = FailureRequest(settings)
        self.done = RequestDB(spider, settings, connector)
        self._last_percent = 0

    def _init_waiting(self, connector):

        backend = self.settings.SystemConfig.BackendCacheEngine

        if backend == constants.BackendEngine.queue:
            return WaitingRequest()

        if backend == constants.BackendEngine.redis:
            return WaitingRedisRequest(connector)

        raise SystemConfigError(flag=2)

    async def close(self):
        # 缓存
        await self._dumps_cache()
        # 清空waiting队列
        self.waiting = None
        # 清空pending队列
        self.pending = None
        # 清空failure队列
        self.failure = None
        # 清空done队列
        await self.done.close()

    async def loads_cache(self):
        await self.done.load_requests()

    async def _dumps_cache(self):
        await self.done.dump_requests(strict=False)

    async def set_status(self, response):

        request = response.request

        # 从pending队列中删除
        if await self.pending.has_request(request):
            await self.pending.remove_request(request)

        await self.update_status(response, request)
        await self.update_progress(request, response)

        return

    async def update_status(self, response, request):
        """更新状态"""

        if response.status == 200:
            await self.done.set_success(request)
            if await self.failure.has_request(request):
                await self.failure.remove_request(request)
            if await self.done.has_request(request):
                await self.done.remove_failure(request)
        else:
            r = await self.failure.put_request(request)
            if not r:
                await self.done.set_failure(request)

    async def update_progress(self, request, response):
        """更新进度"""

        if not await self.should_log_progress():
            return

        waiting_count = await self.waiting_size()
        completed_count = await self.done_size()

        item = [{
            '响应名称': request.help, '响应状态': response.status, "进行数量": self.pending_size(),
            "完成数量": completed_count, "剩余数量": waiting_count, "运行时间": self.spider.get_running_time(),
            "剩余时间": self.spider.get_remaining_time(), '并发速度': self.spider.attrs['avg_speed'],
            '完成进度': str(self.spider.attrs['progress'] * 100)[:6] + '%'
        }]

        logger.debug(f'已成功完成 {await self.done_size()} 个请求，任务进度表：\n{pretty_table(item)}')

    async def should_log_progress(self):

        completed_count = await self.done_size()
        progress = self.spider.attrs['progress']
        running = self.spider.attrs['running']

        if running % 30 == 0:
            return True
        elif completed_count % 100 == 0:
            return True
        elif progress - 0.01 > self._last_percent:
            self._last_percent = progress
            return True
        else:
            return False

    async def push_to_waiting(self, request: Union[BaseRequest, List[BaseRequest]]):
        """将request添加到waiting队列"""

        count = await self._push_requests_to_waiting(request)
        item = [{
            '请求名称': request[-1].help if isinstance(request, list) else request.help,
            '添加数量': count, "待发数量": await self.waiting_size(), "进行数量": self.pending_size(),
            "失败数量": self.failure_size(), '成功数量': await self.done_size()
        }]
        logger.debug(f'{count} 个请求添加到 waiting 队列，请求池详情表：\n{pretty_table(item)}')

    async def _push_requests_to_waiting(self, request: Union[BaseRequest, List[BaseRequest]]):
        """将多个request添加到waiting队列"""

        if not isinstance(request, list):
            request = [request]

        count = 0
        for req in request:
            if await self._is_request_valid_and_unique(req):
                await self.waiting.put_request(req)
                count += 1

        return count

    async def _is_request_valid_and_unique(self, request: BaseRequest):
        """判断请求是否有效且唯一"""

        queue = await self._request_exists_queue(request)
        if queue:
            logger.debug(f'request 已存在{queue}队列中 ---> {request}')
            return False

        if not request.domain or '.' not in request.domain or 'http' not in request.website:
            logger.debug(f'该request可能存在问题，已自动丢弃 ---> {request}')
            return False

        return True

    async def _request_exists_queue(self, request: BaseRequest):
        for queue in [self.waiting, self.pending, self.failure, self.done]:
            if await queue.has_request(request):
                return queue.name
        return None

    async def push_to_failure(self, request: BaseRequest):

        if await self.done.has_request(request):
            return None
        if await self.pending.has_request(request) or await self.waiting.has_request(request):
            await self.failure.put_request(request)
            return None

    async def get_request(self, count: int):
        """从请求池中获取request"""

        async def _get_valid_request():
            while True:
                if not await self.waiting_empty():
                    requests = self.waiting.get_requests(count)
                elif not self.failure_empty():
                    requests = self.failure.get_requests(count)
                else:
                    return

                async for request in requests:
                    if not (await self.pending.has_request(request) or await self.done.has_request(request)):
                        yield request

        async for request in _get_valid_request():
            if request is not None:
                yield await self.pending.put_request(request)

    async def waiting_size(self):
        return await self.waiting.request_size()

    def pending_size(self):
        return self.pending.request_size()

    def failure_size(self):
        return self.failure.request_size()

    async def done_size(self):
        return await self.done.request_size()

    async def waiting_empty(self):
        return await self.waiting_size() == 0

    def pending_empty(self):
        return self.pending_size() == 0

    def failure_empty(self):
        return self.failure_size() == 0
