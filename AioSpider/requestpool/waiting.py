__all__ = ['WaitingRequest', 'WaitingRedisRequest']

import heapq
import random
import asyncio
from collections import defaultdict

from AioSpider import tools
from AioSpider.http.base import BaseRequest
from AioSpider.requestpool.abc import RequestBaseABC


class WaitingRequest(RequestBaseABC):

    def __init__(self):
        self.name = 'waiting'
        self.waiting = {}
        self.waiting_count = 0
        self.max_host_name = ''
        self.max_host_count = 0
        self.request_hashes = defaultdict(set)

    async def put_request(self, request: BaseRequest):
        host = request.domain
        if host not in self.waiting:
            self.waiting[host] = []
        heapq.heappush(self.waiting[host], (-request.priority, request.hash, request))
        self.waiting_count += 1
        self.request_hashes[host].add(request.hash)
        self._update_max_host(host)

    async def get_requests(self, count):

        requests_obtained = 0

        while requests_obtained < count and self.waiting_count > 0:
            max_requests_to_get = min(self.max_host_count, count - requests_obtained)

            for _ in range(max_requests_to_get):
                _, _, request = heapq.heappop(self.waiting[self.max_host_name])
                self.request_hashes[self.max_host_name].remove(request.hash)
                requests_obtained += 1
                self.waiting_count -= 1

                if not self.waiting[self.max_host_name]:
                    self.waiting.pop(self.max_host_name)

                yield request

            self._update_max_host()

    async def has_request(self, request: BaseRequest):
        host = request.domain
        return request.hash in self.request_hashes.get(host, set())

    async def request_size(self):
        return self.waiting_count

    def _update_max_host(self, new_host=None):
        if new_host and len(self.waiting[new_host]) > self.max_host_count:
            self.max_host_name = new_host
            self.max_host_count = len(self.waiting[new_host])
        else:
            if self.waiting:
                self.max_host_name, host_list = max(
                    self.waiting.items(), key=lambda x: len(x[1])
                )
                self.max_host_count = len(host_list)
            else:
                self.max_host_name, self.max_host_count = '', 0


class WaitingRedisRequest(RequestBaseABC):

    def __init__(self, connector):
        self.name = 'redis waiting'
        self.conn = connector['redis']['DEFAULT']
        self.request_info = {}

    async def put_request(self, request: BaseRequest):
        request_info = request.to_dict()
        help = str(request.help)
        await self.conn.order_set.zadd('url_' + help, {request.url: request.priority})
        if self.request_info.get(help) is None:
            await self.conn.hash.hmset('request_' + help, request_info)
            self.request_info[help] = request_info

    async def _get_url_keys_count(self):
        keys = {}
        for i in await self.conn.keys():
            if tools.re_match(i, '^url_.*'):
                count = await self.conn.order_set.zcard(i)
            else:
                continue
            if count > 0:
                keys[i] = count
        return keys

    async def _get_request_infos(self, name):
        if name in self.request_info:
            return self.request_info[name]

        key = f"request_{name}"
        if await self.conn.hash.hlen(key) > 0:
            info = await self.conn.hash.hgetall(key)
            info = {k: tools.load_json(v) for k, v in info.items()}
            return info

        return None

    async def _fetch_urls(self, key, count):
        new_urls = await self.conn.order_set.zrange(key, 0, count - 1)
        await self.conn.order_set.zrem(key, *new_urls)
        requests = []
        request_info = await self._get_request_infos(tools.re_text(key, '^url_(.*)'))
        for url in new_urls:
            request_info['url'] = '"' + url + '"'
            requests.append(BaseRequest.from_dict(request_info))
        return requests

    async def get_requests(self, count):
        keys = await self._get_url_keys_count()

        if not keys:
            return

        shuffled_keys = list(keys.keys())
        random.shuffle(shuffled_keys)

        tasks = []
        remaining_count = count

        for key in shuffled_keys:
            url_count = min(keys[key], remaining_count)
            tasks.append(self._fetch_urls(key, url_count))
            remaining_count -= url_count
            if remaining_count == 0:
                break

        for future in asyncio.as_completed(tasks):
            requests = await future
            for request in requests:
                yield request

    async def has_request(self, request: BaseRequest):
        return await self.conn.order_set.zscore(request.domain, request.url) is not None

    async def request_size(self):
        return sum((await self._get_url_keys_count()).values())
