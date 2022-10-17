import os
import sys
import time
import json
import asyncio
from pathlib import Path
from pprint import pformat
from datetime import datetime
from importlib import import_module

import aiohttp

import AioSpider
from AioSpider.models import Model
from AioSpider import settings, init_logger
from AioSpider.downloader import Downloader
from AioSpider.http import Request, Response
from AioSpider.core.scheduler import Scheduler
from AioSpider.db import SQLiteAPI, MySQLAPI, MongoAPI
from AioSpider.aio_db import SQLiteAPI, CSVFile
from AioSpider.middleware import FirstMiddleware, LastMiddleware


class Engine:

    def __init__(self, spider):

        self.spider = spider                                  # 爬虫实例
        self.settings = self._read_settings()                 # 配置文件
        self.logger = self._init_log()

        self.pipeline = None
        self.scheduler = None
        self.middleware = None
        self.downloader = None

        self.loop = asyncio.get_event_loop()                  # 开始事件循环

    def _read_settings(self):

        pro_settings = import_module(str(Path().cwd().parent.name) + '.settings')
        # 项目settings
        for i in (i for i in dir(settings)):
            if getattr(pro_settings, i, None):
                setattr(settings, i, getattr(pro_settings, i, None))
            else:
                continue

        # 爬虫settings   优先级：爬虫settings > 项目settings > 系统settings
        for i in (i for i in dir(settings)):
            if self.spider.settings.get(i):
                setattr(settings, i, self.spider.settings.get(i))
            else:
                continue

        return settings

    def _init_log(self):

        if getattr(self.settings, 'LOGGING', None):
            sts = self.settings.LOGGING
        else:
            sts = settings.LOGGING

        if not sts['LOG_NAME']:
            warnings.warn("logger的'name'属性必须为非空str类型，日志名称设置无效，将使用默认名'aioSpider'作为日志名称")
            sts['LOG_NAME'] = self.spider.name

        logger = init_logger(sts)
        AioSpider.logger = logger
        self.spider.logger = logger

        return logger

    def _init_pipeline(self):

        pipelines = getattr(self.settings, 'ITEM_PIPELINES', [])
        if pipelines:
            self.logger.info(f'数据管道已启动：\n{pformat(pipelines)}')

        pp = []
        for p in pipelines:
            *py, c = p.split('.')
            x = import_module('.'.join(py))
            pp.append((eval(f'x.{c}'), pipelines[p]))

        return [p[0](self.spider) for p in sorted(pp, key=lambda k: k[1])]

    def _init_middleware(self):

        middleware = getattr(self.settings, 'DOWNLOAD_MIDDLEWARE', {})
        if middleware:
            self.logger.info(f'下载中间件已启动：\n{pformat(middleware)}')

        mm = []
        for p in middleware:
            *py, c = p.split('.')
            x = import_module('.'.join(py))
            mm.append((eval(f'x.{c}'), middleware[p]))

        # 中间件实例调序
        mm = [m[0](self.spider, self.settings, self.scheduler) for m in sorted(mm, key=lambda k: k[1])]
        for m in mm:

            if isinstance(m, FirstMiddleware):
                mm.remove(m)
                mm.insert(0, m)

            if isinstance(m, LastMiddleware):
                mm.remove(m)
                mm.append(m)

        return mm

    async def _init_database(self):

        db_engine = getattr(self.settings, 'DATABASE_ENGINE', None)

        if db_engine is None:
            return None

        elif db_engine['SQLITE']['ENABLE']:

            sq_path = db_engine['SQLITE']['SQLITE_PATH']
            if not sq_path.exists():
                sq_path.mkdir(parents=True, exist_ok=True)

            sq_db = db_engine['SQLITE']['SQLITE_DB']
            path = sq_path / sq_db
            sq_timeout = db_engine['SQLITE']['SQLITE_TIMEOUT']

            AioSpider.db = await SQLiteAPI(path, sq_timeout)
            self.logger.info(f"SQLite数据库已启动：\n{pformat(db_engine['SQLITE'])}")

        elif db_engine['CSVFile']['ENABLE']:

            csv_path = db_engine['CSVFile']['CSV_PATH']
            encoding = db_engine['CSVFile']['ENCODING']
            write_mode = db_engine['CSVFile']['WRITE_MODE']

            if not csv_path.exists():
                csv_path.mkdir(parents=True, exist_ok=True)

            AioSpider.db = CSVFile(path=csv_path, encoding=encoding, write_mode=write_mode)
            self.logger.info(f"CSVFile数据库已启动：\n{pformat(db_engine['CSVFile'])}")

        elif db_engine['MYSQL']['ENABLE']:

            my_host = db_engine['MYSQL']['MYSQL_HOST']
            my_port = db_engine['MYSQL']['MYSQL_PORT']
            my_db = db_engine['MYSQL']['MYSQL_DB']
            my_user = db_engine['MYSQL']['MYSQL_USER_NAME']
            my_pwd = db_engine['MYSQL']['MYSQL_USER_PWD']
            my_charset = db_engine['MYSQL']['MYSQL_CHARSET']
            my_timeout = db_engine['MYSQL']['MYSQL_CONNECT_TIMEOUT']
            my_time_zone = db_engine['MYSQL']['MYSQL_TIME_ZONE']

            AioSpider.db = MySQLAPI(
                host=my_host, port=my_port, database=my_db, user=my_user, password=my_pwd,
                connect_timeout=my_timeout, charset=my_charset, time_zone=my_time_zone
            )
            self.logger.info(f"MySql数据库已启动：\n{pformat(db_engine['MYSQL'])}")

        elif db_engine['MONGODB']['ENABLE']:

            mo_host = db_engine['MONGODB']['MONGO_HOST']
            mo_port = db_engine['MONGODB']['MONGO_HOST']
            mo_db = db_engine['MONGODB']['MONGO_DB']
            mo_user = db_engine['MONGODB']['MONGO_USER_NAME']
            mo_pwd = db_engine['MONGODB']['MONGO_USER_PWD']

            AioSpider.db = MongoAPI(
                host=mo_host, port=mo_port, db=mo_db, username=mo_user, password=mo_pwd
            )
            self.logger.info(f"MongoDB数据库已启动：\n{pformat(db_engine['MONGODB'])}")

        else:
            AioSpider.db = False

    async def _open(self):

        await self._init_database()
        self.pipeline = self._init_pipeline()
        self.scheduler = await Scheduler(self.settings)
        self.middleware = self._init_middleware()
        self.downloader = Downloader(self.middleware, self.settings)

        self.spider.spider_open()
        for p in self.pipeline:
            p.spider_open()

    async def _close(self):

        for p in self.pipeline:
            p.spider_close()

        await self.scheduler.close()

        while True:
            if len(asyncio.all_tasks(self.loop)) <= 1:
                break
            else:
                for i in asyncio.all_tasks(self.loop):
                    if i.get_name() == 'Task-1':
                        continue
                    await i

        if hasattr(AioSpider.db, 'close'):
            AioSpider.db.close()

        self.logger.info(f'爬取结束，总共成功发起{await self.scheduler.request_count()}个请求')
        self.spider.spider_close()

    def start(self):
        """启动引擎"""

        try:
            # 将协程注册到事件循环中
            self.loop.run_until_complete(self.execute())
        except Exception as e:
            raise e
            # self.logger.error(str(e))
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    async def execute(self):
        """ 执行初始化start_urls里面的请求 """

        # 开始采集
        self.logger.info(f'{">" * 25} {self.spider.name}: 开始采集 {"<" * 25}')
        # 爬虫开始的时间
        start_time = datetime.now()
        await self._open()

        connector = aiohttp.TCPConnector(
            limit=getattr(self.settings, 'MAX_CONNECT_COUNT', 100),
            use_dns_cache=getattr(self.settings, 'USE_DNS_CACHE', True)
        )

        async with aiohttp.ClientSession(connector=connector) as s:
            AioSpider.session = s
            for request in self.spider.start_requests():
                await self.scheduler.push_request(request)

            await self._next_request()
        await self._close()

        while True:
            if len(asyncio.all_tasks(self.loop)) <= 1:
                break
            else:
                for i in asyncio.all_tasks(self.loop):
                    if i.get_name() == 'Task-1':
                        continue
                    await i

        self.logger.info(f'{">" * 25} 采集结束 {"<" * 25}')
        self.logger.info(f'{">" * 25} 总共用时: {datetime.now() - start_time} {"<" * 25}')
        time.sleep(1)

    async def _next_request(self):
        """ 不断的获取下一个请求 """

        # 允许任务并发的数量
        task_limit = getattr(self.settings, 'REQUEST_CONCURRENCY_COUNT', 5)
        # 求情队列无请求时休眠时间
        sleep_time = getattr(self.settings, 'NO_REQUEST_SLEEP_TIME', 3)
        task_sleep = getattr(self.settings, 'REQUEST_CONCURRENCY_SLEEP', 1)
        per_task_sleep = getattr(self.settings, 'PER_REQUEST_SLEEP', 0)

        # 设置请求并发量
        semaphore = asyncio.Semaphore(value=task_limit)
        # 死循环 不断的循环 从调度器中的队列不断获取请求
        while True:

            # 从调度器队列中获取一个请求
            request = await self.scheduler.get_request()

            if per_task_sleep:
                time.sleep(per_task_sleep)

            if request is None:
                # 暂停
                await self.heart_beat(sleep_time)
                self.logger.warning(f"请求队列无请求，休眠{sleep_time}秒")

                # 如果队列中还是没有数据，则跳循环
                if self.scheduler.empty() and len(asyncio.all_tasks(self.loop)) <= 1:
                    break

                continue

            if semaphore._value == 0 and task_sleep:
                if task_sleep - 0.15 <= 0:
                    task_sleep = 0
                time.sleep(task_sleep - 0.15)

            # 如果取出来的不是请求 忽略
            if isinstance(request, Request):
                # 上锁 保证前面设置的并发量生效 每次上锁value值会减一
                # 但是value值是不能低于0的 value等于0就会造成阻塞 --> 从而可以实现并发的控制
                await semaphore.acquire()
                # 创建任务 注册到事件循环中
                self.loop.create_task(self._process_request(request, semaphore))

            continue

    @staticmethod
    async def heart_beat(sleep_time):
        """ 实现的心跳函数 求情队列无请求时休眠固定时间  """
        await asyncio.sleep(sleep_time)

    async def _process_request(self, request, semaphore):
        """ 从调度器中取出的请求交给下载器中处理 """

        # 调用下载器中的下载请求
        http_obj = await self.download(request)

        # 处理响应
        if isinstance(http_obj, Response):
            await self.scheduler.set_status(http_obj)
            await self.process_response(http_obj, request)
        elif isinstance(http_obj, Request):
            await semaphore.acquire()
            self.loop.create_task(self._process_request(http_obj, semaphore))
        else:
            pass

        # 释放锁资源 释放的时候 value的值会增加一 (+1)
        semaphore.release()

    async def download(self, request):
        """ 下载请求 """

        response = await self.downloader.fetch(request)
        response.request = request

        return response

    async def process_response(self, response, request):
        """ 处理响应 """

        callback = request.callback or self.spider.default_parse
        result = callback(response)

        if result is None:
            return

        if isinstance(result, dict) or isinstance(result, Model):
            await self.process_item(result)
            return

        if isinstance(result, Request):
            # 自动网请求头中添加Referer
            if result.auto_referer:
                if result.headers.get('Referer') or result.headers.get('referer'):
                    await self.scheduler.push_request(result)
                else:
                    result.headers['Referer'] = request.url
                    await self.scheduler.push_request(result)
            else:
                await self.scheduler.push_request(result)

            return

        if hasattr(result, '__iter__'):
            for item in result:

                if item is None:
                    continue

                if isinstance(item, Request):
                    if item.auto_referer:
                        if item.headers.get('Referer') or item.headers.get('referer'):
                            await self.scheduler.push_request(item)
                        else:
                            item.headers['Referer'] = request.url
                            await self.scheduler.push_request(item)
                    else:
                        await self.scheduler.push_request(item)
                    continue

                if isinstance(item, dict) or isinstance(item, Model):
                    await self.process_item(item)
                    continue

    async def process_item(self, item):
        for p in self.pipeline:
            if getattr(p, 'is_async', False):
                await p.process_item(item)
            else:
                p.process_item(item)
