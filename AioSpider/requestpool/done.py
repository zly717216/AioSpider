__all__ = ['RequestDB']

import time
import pickle
from pathlib import Path

from AioSpider import tools
from AioSpider.filter import BloomFilter
from AioSpider.http.base import BaseRequest


class RequestBaseDB:
    failure_status = 'failure'
    success_status = 'success'

    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.success_hash = set()
        self.failure_hash = set()

    async def set_success(self, request: BaseRequest, status):
        pass

    async def remove_failure(self, request: BaseRequest, status):
        pass

    async def request_size(self):
        pass

    async def has_request(self, request: BaseRequest, status):
        pass

    async def load_requests(self, path: Path = None, status='success'):
        pass

    async def dump_requests(self, path: Path, expire: int, strict=True):
        pass

    async def set_failure(self, request: BaseRequest):
        pass


class RequestQueueDB(RequestBaseDB):

    def __init__(self):
        super(RequestQueueDB, self).__init__()
        self._filter = None
        self.filter_max_count = 10000
        self.y = 0

    @property
    def filter(self):

        if self._filter is None:
            self._filter = [BloomFilter(capacity=self.filter_max_count)]

        if self.success_count // self.filter_max_count != self.y:
            self._filter.append(BloomFilter(capacity=self.filter_max_count))
            self.y += 1

        return self._filter[self.y]

    async def set_success(self, request: BaseRequest):
        self.success_hash.add(request.hash)
        self.filter.add(request.hash)
        self.success_count += 1

    async def set_failure(self, request: BaseRequest):
        self.failure_hash.add(request.hash)
        self.failure_count += 1

    async def clear_success(self):
        self._filter = None
        self.y = 0
        self.success_count = 0
        self.success_hash.clear()

    async def clear_failure(self):
        self.failure_count = 0
        self.failure_hash.clear()

    async def remove_failure(self, request: BaseRequest):
        if request.hash in self.failure_hash:
            self.failure_hash.discard(request.hash)
            self.failure_count -= 1

    async def has_request(self, request: BaseRequest):

        if request.dnt_filter:
            return False

        return request.hash in self.filter or request.hash in self.failure_hash

    async def request_size(self):
        return self.success_count + self.failure_count

    async def load_requests(self, path: Path = None, status='success'):

        if not path or not path.exists():
            return False

        file_list = path.iterdir()
        expire_list = [tools.type_converter(i.stem.split('_')[-1], to=int, force=True) for i in file_list]
        expire = tools.max(expire_list)

        if expire < time.time():
            return

        file_path = path / f'{expire}.aio'
        if not file_path.exists():
            return

        with file_path.open('rb') as f:
            txt = f.read().decode()

        for request in txt.split('\n'):
            self.success_hash.add(request)

    async def dump_requests(self, path: Path, expire: int, strict=True):

        if strict and len(self.success_hash) < self.filter_max_count:
            return False

        file_path = path / f'{expire}.aio'

        txt = '\n'.join(self.success_hash)
        await self.clear_success()

        with open(file_path, 'ab') as f:
            f.write(txt.encode())

        return True


class RequestRedisDB(RequestBaseDB):

    def __init__(self, connector):
        super().__init__()
        self.conn = connector['redis']['DEFAULT']

    async def set_success(self, request: BaseRequest):
        await self.conn.set.sadd(self.success_status, request.hash)
        self.success_hash.add(request.hash)
        self.success_count += 1

    async def set_failure(self, request: BaseRequest):
        await self.conn.set.sadd(self.failure_status, request.hash)
        self.failure_hash.add(request.hash)
        self.failure_count += 1

    async def clear_success(self):
        await self.conn.set.sadd(self.failure_status)
        self.success_hash.clear()

    async def remove_failure(self, request: BaseRequest):
        await self.conn.set.srem(self.failure_status, request.hash)
        self.failure_hash.discard(request.hash)

    async def has_request(self, request: BaseRequest):

        if request.hash in self.success_hash or request.hash in self.failure_hash:
            return True
        elif await self.conn.set.sismember(self.success_status, request.hash):
            return True
        elif await self.conn.set.sismember(self.failure_status, request.hash):
            return True
        else:
            return False

    async def request_size(self):
        return self.success_count + self.failure_count

    async def load_requests(self, path: Path = None, status='success'):

        if not path or not path.exists():
            return False

        file_list = path.iterdir()
        expire_list = [tools.type_converter(i.stem.split('_')[-1], to=int, force=True) for i in file_list]
        expire = tools.max(expire_list)

        if expire < time.time():
            return

        file_path = path / f'request_{expire}.pkl'
        with file_path.open('rb') as f:
            try:
                txt = pickle.load(f)
            except:
                return

        requests = [request for request in txt.split() if status in request]
        await self.conn.order_set.insert_many(status, requests)

    async def dump_requests(self, path: Path, expire: int, strict=True):
        return True
        if not path:
            return False

        request_list = []
        async for i in self.conn.zscan_iter(self.success_status):
            request_list.append(f'{self.success_status}_{i[0]}')
        async for i in self.conn.zscan_iter(self.failure_status):
            request_list.append(f'{self.failure_status}_{i[0]}')

        expire = int(time.time()) + expire
        file_path = path / f'request_{expire}.pkl'
        txt = '\n'.join(request_list)

        with file_path.open('wb') as f:
            pickle.dump(txt, f)

        await self.conn.order_set.delete(self.success_status)
        await self.conn.order_set.delete(self.failure_status)

        return True


class RequestDB:

    def __init__(self, spider, settings, connector):

        self.name = 'done'
        self.spider = spider
        self.settings = settings

        self._expire = None
        self._cache_path = None
        backend = settings.SystemConfig.BackendCacheEngine

        if backend == 'queue':
            self.done = RequestQueueDB()

        if backend == 'redis':
            self.done = RequestRedisDB(connector)

    @property
    def expire(self):

        if self._expire is None:

            cache_settings = self.settings.RequestFilterConfig

            if not cache_settings.Enabled:
                return self._expire

            if cache_settings.FilterForever:
                expire = 100 * 365 * 24 * 60 * 60
            else:
                expire = cache_settings.ExpireTime

            self._expire = int(time.time()) + expire

        return self._expire

    @property
    def cache_path(self):

        if self._cache_path is None:

            cache_settings = self.settings.RequestFilterConfig

            if not cache_settings.Enabled:
                return self._cache_path

            self._cache_path = Path(cache_settings.CachePath) / self.spider.name
            tools.mkdir(self._cache_path)

        return self._cache_path

    async def has_request(self, request):
        return await self.done.has_request(request=request)

    async def set_success(self, request):
        await self.dump_requests()
        await self.done.set_success(request)

    async def set_failure(self, request):
        await self.done.set_failure(request)

    async def remove_failure(self, request):
        return await self.done.remove_failure(request)

    async def request_size(self):
        return await self.done.request_size()

    async def load_requests(self):

        cache_settings = self.settings.RequestFilterConfig
        cache_dir = cache_settings.CachePath
        cache_dir = Path(cache_dir) if isinstance(cache_dir, str) else cache_dir

        if cache_settings.Enabled and cache_settings.LoadSuccess:
            cache_path = cache_dir / self.spider.name
            await self.done.load_requests(path=cache_path)

    async def dump_requests(self, strict=True):

        if self.expire is None or self.cache_path is None:
            return

        await self.done.dump_requests(path=self.cache_path, expire=self.expire, strict=strict)

    async def close(self):
        await self.done.clear_success()
        await self.done.clear_failure()
