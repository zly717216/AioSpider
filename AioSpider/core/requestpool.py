import copy
import os
import time
import json
import hashlib
from urllib import parse
from queue import Queue
from pathlib import Path

import pickle
from AioSpider.utils_pkg import aioredis
from redis import ConnectionPool, Redis

from AioSpider import tools, AioObject, GlobalConstant
from AioSpider.http import Request


class OrderQueue(Queue):

    def _init(self, maxsize=0):
        self.queue = set()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()

    def _qsize(self):
        return self.queue.__len__()

    def _remove(self, item):
        if item in self.queue:
            self.queue.remove(item)

    def _iter_q(self):
        return iter(self.queue)


class DictQueue(Queue):

    def _init(self, maxsize=0):
        self.queue = dict()

    def _put(self, item):
        self.queue[item] = self.queue.get(item, 0) + 1

    def _get(self):
        item = self.queue.popitem()
        return item[0] if item else None

    def _get_time(self, item):
        return self.queue.get(item, 0)

    def _qsize(self):
        return self.queue.__len__()

    def _remove(self, item):
        self.queue.pop(item)


class RequestBaseDB:

    failure_status = 'failure'
    success_status = 'success'

    def __init__(self):
        self._start_queue = OrderQueue()
        self._logger = GlobalConstant().logger

    def _get_request_hash(self, request, status):
        """计算request的hash值"""

        sts = GlobalConstant().settings
        url = request.url
        data = request.data or {}

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                data = {}

        if hasattr(sts, 'IGNORE_STAMP') and hasattr(sts, 'STAMP_NAMES'):
            for i in getattr(sts, 'STAMP_NAMES', []):
                if data and data.get(i):
                    data.pop(i)

        item = f'{url}{data}'.encode()
        req_hash = hashlib.md5(item).hexdigest()
        return f'{status}_{req_hash}'

    async def _set_status(self, request, status):
        pass

    async def _set_success(self, request):
        """存储成功的请求"""
        await self._set_status(request, self.success_status)

    async def _set_failure(self, request):
        """存储失败的请求"""
        await self._set_status(request, self.failure_status)

    async def _has_success_request(self, request):
        pass

    async def _has_failure_request(self, request):
        pass

    async def _has_request(self, request):

        if await self._has_success_request(request):
            return True

        if await self._has_failure_request(request):
            return True

        return False

    async def _remove_request(self, request, status):
        pass

    async def _remove_success(self, request):
        return await self._remove_request(request, self.success_status)

    async def _remove_failure(self, request):
        return await self._remove_request(request, self.failure_status)

    async def _close(self):
        pass


class RequestQueueDB(RequestBaseDB):

    def __init__(self, qsize=0):
        super(RequestQueueDB, self).__init__()
        self.queue = OrderQueue(qsize)

    async def _set_status(self, request, status):
        req_hash = self._get_request_hash(request, status)
        self.queue.put(req_hash)

    async def _has_success_request(self, request):

        req_hash = self._get_request_hash(request, self.success_status)

        if request.dnt_filter:
            return False

        return True if req_hash in self.queue.queue or req_hash in self._start_queue.queue else False

    async def _has_failure_request(self, request):

        req_hash = self._get_request_hash(request, self.failure_status)

        if not request.dnt_filter:
            return False

        return True if req_hash in self.queue.queue or req_hash in self._start_queue.queue else False

    async def _remove_request(self, request, status):
        req_hash = self._get_request_hash(request, status)
        self.queue._remove(req_hash)
        return request

    def _loads_request(self, path: Path = None, status='success'):
        """导入硬盘上的request"""

        if path is None or not path.exists():
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

        for request in txt.split():
            if status not in request:
                continue
            self._start_queue.put(request)

    async def _dumps_request(self, path: Path = None, expire=3600):
        """将队列中的request写入硬盘"""

        if path is None:
            return False

        expire = int(time.time()) + expire
        file_path = path / f'request_{expire}.pkl'
        txt = tools.join(self.queue.queue.union(self._start_queue.queue), on='\n')

        with file_path.open('wb') as f:
            pickle.dump(txt, f)

        return True

    async def qsize(self):
        return self.queue.qsize()


class RequestRedisDB(AioObject, RequestBaseDB):

    async def __init__(self, *, host, port=6379, user=None,  password=None, db=0):

        self.host = host
        self.port = port
        self.password = password
        self.username = user
        self._db = db

        self.db = await self.connect()
        await self.ping()

    async def ping(self):
        try:
            if await self.db.ping():
                return True
        except Exception as e:
            self._logger.error(e)

        self.db = self.connect()

    async def connect(self):

        redis = aioredis.from_url(
            f"redis://{self.host}:{self.port}", db=self._db, encoding="utf-8", decode_responses=True,
            username=self.username, password=self.password
        )

        return redis

    async def _set_status(self, request, status):
        await self.ping()
        item = self._get_request_hash(request, status).split('_')[-1]

        await self.db.zadd(status, {item: 1})

    async def _has_success_request(self, request):

        await self.ping()
        item = self._get_request_hash(request, self.success_status)

        async for i in self.db.zscan_iter(self.success_status):
            if i and isinstance(i, tuple) and item.split('_')[-1] == i[0]:
                return True
            else:
                continue

        return False

    async def _has_failure_request(self, request):

        await self.ping()
        item = self._get_request_hash(request, self.failure_status)

        async for i in self.db.zscan_iter(self.failure_status):
            if i and isinstance(i, tuple) and item.split('_')[-1] == i[0]:
                return True
            else:
                continue

        return False

    async def _remove_request(self, request, status):
        req_hash = self._get_request_hash(request, status)
        self.db.zrem(status, req_hash)
        return request

    async def qsize(self):
        return await self.db.zcard(self.success_status) + await self.db.zcard(self.failure_status)

    def _loads_request(self, cache_dir=None, status='success'):
        """导入硬盘上的request"""

        if cache_dir is None or not os.path.exists(cache_dir):
            return False

        file_list = os.listdir(cache_dir)
        expire_list = [eval(i.split('_')[-1].split('.')[0]) for i in file_list]
        expire_list = [i for i in expire_list if i > time.time()]
        expire_list.sort()

        if expire_list:
            file_path = os.path.join(cache_dir, f'request_{expire_list[-1]}.pkl')
            with open(file_path, 'rb') as f:
                txt = pickle.load(f)

            for i in txt.split():
                x, y = i.split('_')
                if x != status:
                    continue
                self.db.zadd(x, {y: 1})

    async def _dumps_request(self, path: Path = None, expire=3600):
        """将队列中的request写入硬盘"""

        if path is None:
            return False

        request_list = []
        async for i in self.db.zscan_iter(self.success_status):
            request_list.append(f'{self.success_status}_{i[0]}')
        async for i in self.db.zscan_iter(self.failure_status):
            request_list.append(f'{self.failure_status}_{i[0]}')

        expire = int(time.time()) + expire
        file_path = path / f'request_{expire}.pkl'
        txt = tools.join(request_list, on='\n')

        with file_path.open('wb') as f:
            pickle.dump(txt, f)

        await self.db.delete(self.success_status)
        await self.db.delete(self.failure_status)

        return True

    async def _close(self):
        await self.db.close()


class RequestDB(AioObject):

    async def __init__(self):

        backend = getattr(GlobalConstant().settings, 'BACKEND_CACHE_ENGINE', {})

        if backend.get('queue', {}).get('enabled'):
            if backend.get('queue', {}).get('qsize') is None:
                self.url_db = self._init_queue()
            else:
                self.url_db = self._init_queue(backend.get('queue', {}).get('qsize'))

        elif backend.get('redis', {}).get('enabled'):
            _redis = backend.get('redis', {})
            self.url_db = await self._init_redis(
                _redis.get('host'), _redis.get('port'), _redis.get('db'),
                _redis.get('user'), _redis.get('password')
            )
        else:
            raise Exception('settings中为配置BACKEND_CACHE_ENGINE(url缓存方式)')

        self._loads_request()

    def _init_queue(self, qsize=0):
        """创建队列"""

        if isinstance(qsize, int):
            return RequestQueueDB(qsize=qsize)

        if isinstance(qsize, str):
            if qsize.isdigit():
                return RequestQueueDB(qsize=int(qsize))

        return RequestQueueDB()

    async def _init_redis(self, host, port, db, user=None, password=None):
        """创建redis数据库连接"""

        if not host or not isinstance(host, str):
            raise ValueError('队列引擎的host值配置不正确')

        if not isinstance(port, int):
            raise ValueError('队列引擎的port值配置不正确')

        if not isinstance(db, int):
            raise ValueError('队列引擎的db值配置不正确')

        return await RequestRedisDB(host=host, port=port, db=db, user=user, password=password)

    async def _has_request(self, request):
        return await self.url_db._has_request(request=request)

    async def _set_success(self, request):
        await self.url_db._set_success(request)

    async def _set_failure(self, request):
        await self.url_db._set_failure(request)

    async def _remove_success(self, request):
        return await self.url_db._remove_success(request)

    async def _remove_failure(self, request):
        return await self.url_db._remove_failure(request)

    async def request_size(self, loc=True):
        return await self.url_db.qsize()

    def _loads_request(self):
        cache_settings = getattr(GlobalConstant().settings, 'CACHED_REQUEST', {})

        if cache_settings and cache_settings.get('LOAD_SUCCESS', False):
            cache_path = Path(cache_settings.get('CACHE_PATH', '')) / GlobalConstant().spider_name
            self.url_db._loads_request(path=cache_path, status='success')

        if cache_settings and cache_settings.get('LOAD_FAILURE', False):
            cache_path = Path(cache_settings.get('CACHE_PATH', '')) / GlobalConstant().spider_name
            self.url_db._loads_request(path=cache_path, status='failure')

    async def _dumps_request(self):
        cache_settings = getattr(GlobalConstant().settings, 'CACHED_REQUEST', {})
        if cache_settings and cache_settings.get('CACHED'):
            if cache_settings.get('FILTER_FOREVER', False):
                expire = 100 * 365 * 24 * 60 * 60
            else:
                expire = cache_settings.get('CACHED_EXPIRE_TIME', 3600)
            cache_path = Path(cache_settings.get('CACHE_PATH', '')) / GlobalConstant().spider_name
            tools.mkdir(cache_path)
            await self.url_db._dumps_request(path=cache_path, expire=expire)

    async def _close(self):
        await self.url_db._close()


class WaitingRequest:

    def __init__(self):

        # {host: queue([request1, request2...])}
        self.waiting = {}
        self.waiting_count = 0

        # 目前pool中url最多的host和url数量
        self.max_host_name = ''
        self.max_host_count = 0
        self._logger = GlobalConstant().logger

    async def has_request(self, request):

        host = parse.urlparse(request.url).netloc
        q = self.waiting.get(host)

        if q:
            return True if request in q.queue else False
        else:
            return False

    async def put_request(self, request):
        """将请求添加到队列"""

        host = parse.urlparse(request.url).netloc

        if not host or '.' not in host:
            self._logger.warning(f'该url可能存在问题：{request}')
            return False

        if host in self.waiting:

            if not isinstance(self.waiting[host], OrderQueue):
                self._logger.warning('待下载请求队列的host值必须为Queue类型')
                q = OrderQueue()
                self.waiting[host] = q

            self.waiting[host].put(request)
            qsize = self.waiting[host].qsize()
            if qsize > self.max_host_count:
                self.max_host_name, self.max_host_count = host, qsize

        else:
            q = OrderQueue()
            q.put(request)
            self.waiting[host] = q

        self.waiting_count += 1
        return True

    async def _host_refresh(self):
        """刷新最多的域名下的url数量"""

        for k, q in self.waiting.items():
            qsize = q.qsize()
            if qsize > self.max_host_count:
                self.max_host_name = k
                self.max_host_count = qsize
            else:
                continue

    async def get_request(self, count=1):
        """从url池中取url"""

        request_list = []

        while True:

            if self.max_host_count <= 0:
                await self._host_refresh()

            host, qsize = self.max_host_name, self.max_host_count
            q = self.waiting[host]

            for i in range(qsize):
                request_list.append(q.get())
                self.max_host_count -= 1
                self.waiting_count -= 1

                if len(request_list) >= count:
                    break

                if self.max_host_count <= 0:
                    break

            if len(request_list) >= count:
                break

        if count == 1:
            return request_list[0]
        else:
            return request_list

    def _qsize(self):

        size = 0
        for i in self.waiting.values():
            size += i.qsize()

        return size

    def request_size(self, loc=True):
        return self.waiting_count if loc else self._qsize()

    def _load_request(self):
        """导入硬盘上的request"""

        if os.path.exists('waiting_url.pkl'):
            with open('waiting_url.pkl', 'rb') as f:
                self.waiting = pickle.load(f)

        for k in self.waiting:
            q = OrderQueue(1 * 10000 * 10000 * 10000)
            self.waiting[k] = [q.put(i) for i in self.waiting if isinstance(i, Request)]

    # def __del__(self):
        """将队列中的request写入硬盘"""

        # for k in self.waiting:
        #     self.waiting[k] = [i for i in self.waiting[k].queue]
        #
        # with open('waiting_url.pkl', 'wb') as f:
        #     pickle.dump(self.waiting, f)
        # pass


class PendingRequest:

    def __init__(self):
        # queue([(request, time.time()), (request, time.time())])
        self.pending = OrderQueue()
        self.pending_count = 0

    async def has_request(self, request):
        """ 判断请求是否存在 """
        return True if request in [i[0] for i in self.pending.queue] else False

    async def put_request(self, request):
        """将请求添加到队列"""

        self.pending.put((request, time.time()))
        self.pending_count += 1

    async def get_request(self):
        """从url池中取url"""

        request = self.pending.get()
        self.pending_count -= 1

        return request[0] if request else None

    async def remove_request(self, request):
        """把request移出队列"""
        self.pending._remove(request)
        self.pending_count -= 1

    async def _qsize(self):
        return self.pending.qsize()

    def _waiting_count(self):
        return self.pending_count

    def request_size(self, loc=True):
        return self._waiting_count() if loc else self._qsize()

    def _load_request(self):
        """导入硬盘上的request"""

        if os.path.exists('pending_url.pkl'):
            with open('pending_url.pkl', 'rb') as f:
                request_list = pickle.load(f)

            for request in request_list:
                self.pending.put(request)


class FailureRequest:

    def __init__(self):
        # {request: times} 记录失败的URL的次数
        self.failure = DictQueue()
        self.failure_count = 0

    async def has_request(self, request):

        if self.failure.queue.get(request):
            return True
        else:
            return False

    async def put_request(self, request):
        """将请求添加到队列"""

        self.failure.put(request)
        self.failure_count += 1

    async def remove_request(self, request):
        """将请求添加到队列"""

        self.failure._remove(request)
        self.failure_count -= 1

    def get_failure_times(self, request):
        return self.failure._get_time(request)

    async def get_request(self):

        request = self.failure.get()
        self.failure_count -= 1

        return request

    def request_size(self, loc=True):
        return self.failure_count if loc else self.failure.qsize()

    def _load_request(self):
        """导入硬盘上的request"""

        if os.path.exists('failure_url.pkl'):
            with open('failure_url.pkl', 'rb') as f:
                request_list = pickle.load(f)
            for request in request_list:
                self.failure.put(request)

    # def __del__(self):
    #     """将队列中的request写入硬盘"""

        # request_list = [i for i in self.failure.queue]
        # with open('failure_url.pkl', 'wb') as f:
        #     pickle.dump(request_list, f)
        # pass


class RequestPool(AioObject):

    async def __init__(self, pool_name='AioSpider'):

        self.name = pool_name
        self.waiting = WaitingRequest()
        self.pending = PendingRequest()
        self.failure = FailureRequest()
        self.url_db = await RequestDB()
        self._logger = GlobalConstant().logger

    async def close(self):
        await self._dumps_cache()
        await self.url_db._close()

    def _loads_cache(self):
        self.url_db._loads_request()

    async def _dumps_cache(self):
        await self.url_db._dumps_request()

    async def _set_status(self, response):

        request = response.request

        # 1.从pending队列中删除
        if await self.pending.has_request(request):
            await self.pending.remove_request(request)

        if await self.failure.has_request(request):
            await self.failure.remove_request(request)

        # 2.如果状态码200
        if response.status == 200:
            await self.url_db._set_success(request)
        else:
            await self.url_db._set_failure(request)
            await self.failure.put_request(request)

        self._logger.debug(f'总共完成{await self._url_db_qsize()}个请求 --> {response}')
        return

    async def _push_to_waiting(self, request):
        """将request添加到waiting队列"""

        # 1.如果在waiting队列中
        if await self.waiting.has_request(request):
            self._logger.debug(f'request 已在 waiting 队列中 ---> {request}')
            return False

        # 2.如果在pending队列中
        if await self.pending.has_request(request):
            self._logger.debug(f'request 已在 pending 队列中 ---> {request}')
            return False

        # 3.如果在failure队列中
        if await self.failure.has_request(request):
            self._logger.debug(f'request 已在 failure 队列中 ---> {request}')
            return False

        # 4.如果在url_db缓存中
        if await self.url_db._has_request(request):
            self._logger.debug(f'request 已在 url 缓存队列中 ---> {request}')
            return False

        # 添加
        parse_result = parse.urlparse(request.url)
        host = parse_result.netloc
        if not host or '.' not in host or 'http' not in parse_result.scheme:
            self._logger.debug(f'该request可能存在问题 ---> {request}')
            return False

        await self.waiting.put_request(request)
        self._logger.debug(f'1个request添加进 waiting 队列，总共{self._waiting_qsize()}个request等待发起请求 --> {request}')

        return True

    async def _push_many_to_waiting(self, requests):
        """将多个request添加到waiting队列"""

        for request in requests:
            await self._push_to_waiting(request)

    async def _get_request(self):
        """从请求池中获取request"""

        if not self._waiting_empty():
            # 1.从 waiting 队列获取一个 request
            request = await self.waiting.get_request()
            if request is None:
                return None

            # 2.判断是否在 pending 缓存中
            if await self.pending.has_request(request):
                return self.get_request()

            # 3.判断是否在 url_db 缓存中
            if await self.url_db._has_request(request):
                return self._get_request()

            # 4.判断是否在 failure 队列中
            if await self.failure.has_request(request):
                request = await self.failure.get_request()
                return request

            # 5.添加到 pending队列中
            await self.pending.put_request(request)
            return request

        if not self._failure_empty():

            # 1.从 failure 队列获取一个 request
            request = await self.failure.get_request()
            if request is None:
                return None

            # 2.判断是否在 pending 缓存中
            if await self.pending.has_request(request):
                return await self.pending.get_request()

            # 3.判断是否在 url_db 缓存中
            if await self.url_db._has_request(request):
                return await self.url_db._remove_failure(request)

            # 4.添加到 pending队列中
            await self.pending.put_request(request)
            self._logger.debug(
                f'从 failure 队列中取出1个request，正在发起{self._pending_qsize()}个请求，'
                f'剩余{self._failure_qsize()}个request等待发起请求 --> {request}'
            )

            return request

        return None

    def _waiting_qsize(self, loc=True):
        return self.waiting.request_size(loc=loc)

    def _pending_qsize(self, loc=True):
        return self.pending.request_size(loc=loc)

    def _failure_qsize(self, loc=True):
        return self.failure.request_size(loc=loc)

    async def _url_db_qsize(self, loc=True):
        return await self.url_db.request_size(loc=False)

    def _waiting_empty(self, loc=True):
        return self._waiting_qsize(loc=loc) == 0

    def _pending_empty(self, loc=True):
        return self._failure_qsize(loc=loc) == 0

    def _failure_empty(self, loc=True):
        return self._failure_qsize(loc=loc) == 0
