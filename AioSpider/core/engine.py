import asyncio
import inspect
import itertools
import os
import time
from collections import deque
from datetime import datetime
from pprint import pformat
from typing import Callable, Union

from AioSpider import (
    GlobalConstant, logger, pretty_table, tools, welcom_print
)
from AioSpider.core.patch import apply
from AioSpider.datamanager import DataManager
from AioSpider.downloader import Downloader
from AioSpider.exceptions import *
from AioSpider.http import Response, BaseRequest
from AioSpider.loading import BootLoader
from AioSpider.middleware import AsyncMiddleware
from AioSpider.models import Model, TaskModel
from AioSpider.requestpool import RequestPool
from AioSpider.spider import BatchSpider, Spider


apply()


class Engine:

    def __init__(self):

        self.spider: Spider = None
        self.bootloader = BootLoader()
        self.settings = None
        self.models = None
        self.request_pool: RequestPool = None
        self.download_middleware = None
        self.spider_middleware = None
        self.downloader: Downloader = None
        self.connector = None
        self.datamanager: DataManager = None
        self.driver = None

        # 开始事件循环
        self.loop = asyncio.get_event_loop()
        self.req_tasks = None

        self.start_time = time.time()
        self.start_time1 = datetime.now()
        self.crawing_time = 0
        self.data_count = 0

    def add_spider(self, spider: Union[Spider, Callable], *args, **kwargs):

        if issubclass(spider, Spider):
            self.spider = spider(*args, **kwargs)
            return

        if isinstance(spider, Spider):
            self.spider = spider
            return

        raise Exception(f'{spider} 不是爬虫类！')

    def start(self):
        """启动引擎"""

        try:
            # 将协程注册到事件循环中
            self.loop.run_until_complete(self.execute())
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.close())
            logger.error('手动退出')
        except ValueError as e:
            logger.exception(e)
        except SystemConfigError as e:
            logger.error(e)
        # except BaseException as e:
        #     self.loop.run_until_complete(self.request_pool.close())
        #     logger.error(f'异常退出：原因：{e}')
        except Exception as e:
            raise e
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())

    async def execute(self):
        """ 执行初始化start_urls里面的请求 """

        await self.open()
        if isinstance(self.spider, BatchSpider):
            await self._scheduler_batch_spider()
        else:
            await self._scheduler_spider()
        await self.close()

    async def _init_request_pool(self) -> RequestPool:
        request_pool = RequestPool(self.spider, self.settings, self.connector)
        await request_pool.loads_cache()
        return request_pool

    async def _init_dataloader(self) -> DataManager:

        data_manager = DataManager(self.settings, self.connector, self.models)
        logger.info(f'数据管理器已启动，加载到 {len(data_manager.models)} 个模型，\n{pformat(data_manager.models)}')

        await data_manager.open()
        return data_manager

    def _init_downloader(self) -> Downloader:
        return Downloader(self.settings, self.download_middleware)

    def close_redis(self, port=6379):

        with os.popen(f"netstat -ano | findstr {port}") as r:
            pids = set([i.strip() for i in tools.re(r.read(), 'LISTENING(.*)')])

        for pid in pids:
            os.system(f"taskkill /PID {pid} /T /F")

    async def close_connect(self):
        """关闭数据库"""

        for name, connect in self.connector.items():

            # if name == 'redis':
            #     # 关闭本地redis终端
            #     self.close_redis()

            for k, v in connect.items():
                await v.close()
                logger.info(f'{name}-{k}数据库连接已关闭')

    async def open(self):

        welcom_print()
        logger.info(f'{">" * 25} {self.spider.name}: 开始采集 {"<" * 25}')

        GlobalConstant().spider = self.spider
        self.settings = self.bootloader.reload_settings(self.spider)
        self.bootloader.reload_logger(self.spider.name, self.settings)
        self.bootloader.reload_notice(self.spider.name, self.settings)
        self.connector = await self.bootloader.reload_connection(self.settings)
        self.models = self.bootloader.reload_models(self.spider, self.settings)
        self.request_pool = await self._init_request_pool()
        self.download_middleware, self.spider_middleware = self.bootloader.reload_middleware(
            self.spider, self.settings, self.request_pool
        )
        self.driver = self.bootloader.reload_driver(self.settings)
        self.downloader = self._init_downloader()
        self.datamanager = await self._init_dataloader()

    async def close(self):

        for k, v in self.datamanager.containers.items():
            self.data_count += await v.close()

        completed_count = await self.request_pool.done_size()
        failure_count = self.request_pool.failure_size()
        item = [{
            "完成数量": completed_count, "失败数量": failure_count, "运行时间": self.spider.attrs['running'],
            '并发速度': self.spider.attrs['avg_speed'], '完成进度': '100%'
        }]
        logger.info(f'爬取结束，总请求详情：\n{pretty_table(item)}')

        if self.driver is not None:
            self.driver.quit()
        if self.request_pool is not None:
            await self.request_pool.close()
        if self.downloader is not None:
            await self.downloader.close_session()

        await self.close_connect()

        logger.info(f'{">" * 25} {self.spider.name}: 采集结束 {"<" * 25}')
        logger.info(f'{">" * 25} 总共用时: {datetime.now() - self.start_time1} {"<" * 25}')

    def spider_open(self):

        for m in self.download_middleware:
            m.spider_open(self.spider)

        for m in self.spider_middleware:
            m.spider_open(self.spider)

        self.spider.spider_open()

    def spider_close(self):

        for m in self.download_middleware:
            m.spider_close(self.spider)

        for m in self.spider_middleware:
            m.spider_close(self.spider)

        self.spider.spider_close()

    async def process_spider_request(self, request: BaseRequest):

        if request is None:
            return False

        for m in self.spider_middleware:

            if not hasattr(m, 'process_request'):
                continue

            if isinstance(m, AsyncMiddleware):
                ret = await m.process_request(request)
            else:
                ret = m.process_request(request)

            if ret is None:
                continue
            elif isinstance(ret, (BaseRequest, Response)):
                return ret
            else:
                raise MiddlerwareError(flag=1)

        return None
    
    async def process_spider_response(self, response):
        
        if response is None:
            return False

        for m in self.spider_middleware:

            if not hasattr(m, 'process_response'):
                continue

            if isinstance(m, AsyncMiddleware):
                ret = await m.process_response(response)
            else:
                ret = m.process_response(response)

            if ret is None:
                continue
            elif isinstance(ret, BaseRequest):
                return ret
            else:
                raise MiddlerwareError(flag=1)

        return None

    async def _scheduler_spider(self):

        self.spider_open()

        # 将请求批量添加到waiting队列
        self.req_tasks = deque()
        self.start_requests_iterator = self.spider.start_requests()

        settings = self.settings.SpiderRequestConfig
        task_sleep = settings.REQUEST_CONCURRENCY_SLEEP

        # 如果start_requests_iterator已用完，则添加要跟踪的变量
        iterator_exhausted = False
        self.crawing_time = time.time()

        # 连续循环，从调度程序队列中获取请求
        while True:

            task_limit = self.spider.attrs['task_limit']

            if task_limit <= 0:
                raise ValueError('Task limit 必须大于0')

            # Add requests from start_requests generator to self.req_tasks
            if not iterator_exhausted:

                new_requests = list(itertools.islice(self.start_requests_iterator, task_limit))

                if new_requests:
                    self.req_tasks.extend(new_requests)
                else:
                    # 如果没有提取新的请求，则将迭代器标记为已用完
                    iterator_exhausted = True

            # 将请求添加到waiting队列
            if self.req_tasks:
                await self.request_pool.push_to_waiting(list(self.req_tasks))
                self.req_tasks.clear()

            tasks = []

            # 处理waiting队列中的请求
            async for request in self.request_pool.get_request(task_limit):
                obj = await self.process_spider_request(request)
                if obj is None:
                    tasks.append(asyncio.create_task(self.download(request)))
                elif isinstance(obj, BaseRequest):
                    await self.request_pool.pending.remove_request(request)
                    await self.request_pool.push_to_waiting(obj)
                elif isinstance(obj, Response):
                    await self.process_response(obj, request)
                else:
                    continue

            responses = await asyncio.gather(*tasks)

            # 使用asyncio.gather处理所有请求
            for response in responses:
                if response is None:
                    continue
                obj = await self.process_spider_response(response)
                if obj is None:
                    await self.process_response(response, response.request)
                elif isinstance(obj, BaseRequest):
                    await self.request_pool.pending.remove_request(response.request)
                    await self.request_pool.push_to_failure(obj)
                else:
                    continue

            # 暂停以遵循请求速率限制
            await asyncio.sleep(task_sleep)
            await self.fresh_progress()

            # 如果没有请求需要处理，则中断循环
            if iterator_exhausted and not self.req_tasks and await self.request_pool_empty():
                break

        self.spider_close()

    async def _scheduler_batch_spider(self):

        while True:

            if not self.spider.is_time_to_run():
                if self.spider.next_time < datetime.now():
                    self.spider.next_time = self.spider.get_next_time()
                    continue
                logger.debug(
                    f"爬虫({self.spider.name})还未到运行时间，{self.spider.name}将在{self.spider.next_time}启动，当前北京"
                    f"时间是{datetime.now()}，距离启动还有 {(self.spider.next_time - datetime.now()).total_seconds():,.5f} 秒"
                )
                time.sleep(0.9)
                continue

            self.spider.create_task()

            # 爬虫运行前回调
            if not self.spider.cust_call_before():
                break

            self.spider.next_time = self.spider.get_next_time()

            # 更新爬虫状态 --- 爬虫即将开始运行
            TaskModel.objects.update(
                items={'id': self.spider.task.id, 'status': 1},
                where='id',
            )

            # 执行登录逻辑
            self.spider.token = self.spider.cust_call_login(self.spider.username, self.spider.password)

            await self._scheduler_spider()

            # 更新爬虫状态 --- 爬虫运行结束
            TaskModel.objects.update(
                items={
                    'id': self.spider.task.id, 'status': 3, 'end_time': datetime.now(),
                    'data_count': self.data_count,
                    'running_time': self.spider.get_running_time()
                },
                where='id'
            )

            # 爬虫结束后回调
            if not self.spider.cust_call_end():
                break

            await self.request_pool.done.close()

    async def fresh_progress(self):

        running = round(time.time() - self.crawing_time, 3)
        waiting_count = await self.request_pool.waiting_size()
        completed_count = await self.request_pool.done_size()
        speed = round(completed_count / running, 3) if running else 0
        remaining = round(waiting_count / speed, 3) if waiting_count else 0

        progress = round(
            (
                completed_count / (waiting_count + completed_count)
            ) if (waiting_count + completed_count) else 0, 5
        )
        
        self.spider.attrs['running'] = running
        self.spider.attrs['remaining'] = remaining
        self.spider.attrs['avg_speed'] = speed
        self.spider.attrs['progress'] = progress

    async def request_pool_empty(self):
        return True if self.request_pool.pending_empty() and await self.request_pool.waiting_empty() and \
                       self.request_pool.failure_empty() else False

    async def download(self, request):
        """从调度器中取出的请求交给下载器中处理"""

        # 暂停以遵循请求速率限制
        if self.settings.SpiderRequestConfig.PER_REQUEST_SLEEP:
            await asyncio.sleep(self.settings.SpiderRequestConfig.PER_REQUEST_SLEEP)

        # 下载请求
        response = await self.downloader.fetch(request)
        await self.request_pool.pending.remove_request(request)

        if response is None:
            return None

        # 处理响应
        if isinstance(response, Response):
            await self.request_pool.set_status(response)
            return response
        elif isinstance(response, BaseRequest):
            await self.request_pool.pending.remove_request(response)
            await self.request_pool.push_to_failure(response)
        else:
            await self.request_pool.pending.remove_request(request)
            await self.request_pool.push_to_failure(request)

        return None

    async def process_response(self, response, request):
        """处理响应"""

        callback = request.callback or self.spider.parse or self.spider.default_parse

        args = []
        for k in inspect.signature(callback).parameters:
            if k == 'self':
                args.append(self.spider)
            elif k == 'response':
                args.append(response)
            else:
                args.append(None)

        result = callback(*args)

        await self._process_callback(result)

    async def _process_callback(self, result):
        """处理响应回调结果"""

        if result is None:
            return None

        if isinstance(result, Model):
            await self.datamanager.commit(result)
        elif isinstance(result, BaseRequest):
            self.req_tasks.append(result)
        elif hasattr(result, '__iter__'):
            for item in result:
                await self._process_callback(item)
        else:
            raise ValueError('回调必须返回Model对象或BaseRequest对象')

        return None
