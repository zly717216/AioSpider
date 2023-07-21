import time
import math
import random
from abc import ABCMeta, abstractmethod


class SpiderMiddleware(metaclass=ABCMeta):
    """中间件基类"""

    is_async = False

    def __init__(self, spider, settings):
        self.spider = spider
        self.settings = settings

    @abstractmethod
    def process_request(self, request):
        """
            处理请求
            @params:
                request: BaseRequest 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                Response: 交由引擎重新调度该Response对象
                None: 正常，继续往下执行 穿过下一个中间件
                False: 丢弃该Request或Response对象
        """

        return None

    @abstractmethod
    def process_response(self, response):
        """
            处理请求
            @params:
                response: Response 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                None: 正常，继续往下执行 穿过下一个中间件
                False: 丢弃该Request或Response对象
        """

        return None

    def spider_open(self, spider):
        pass

    def spider_close(self, spider):
        pass


class AutoConcurrencyStrategyMiddleware(SpiderMiddleware):
    """自动并发策略"""

    def __init__(self, spider, settings, min_concurrency_speed: int = 20):
        super().__init__(spider=spider, settings=settings)
        self.min_concurrency_speed = min_concurrency_speed

    def process_request(self, request):

        avg_speed = self.spider.attrs['avg_speed']
        running = self.spider.attrs['running']

        if avg_speed == 0:
            return None

        # 周期，单位为秒
        period = 60
        # 当前时间，取模周期得到0到周期之间的值
        t = running % period

        task_limit = self.min_concurrency_speed + (
                avg_speed - self.min_concurrency_speed) * math.sin(2 * math.pi * t / period)

        self.spider.attrs['task_limit'] = int(task_limit)

        return None

    def process_response(self, response):
        return None


class RandomConcurrencyStrategyMiddleware(SpiderMiddleware):
    """随机并发策略"""

    def __init__(self, spider, settings, min_speed: int = 10, max_speed: int = 30):
        super().__init__(spider=spider, settings=settings)
        self.min_speed = min_speed
        self.max_speed = max_speed

    def process_request(self, request):

        task_limit = self.spider.attrs['task_limit'] or random.randint(self.min_speed, self.max_speed)
        avg_speed = self.spider.attrs['avg_speed']

        # 调整任务限制值
        if task_limit > avg_speed:
            # 计算缩小比例
            scale = min(self.max_speed / task_limit, 1)
            task_limit = int(task_limit * scale)
        else:
            # 计算放大比例
            scale = min(task_limit / self.min_speed, 1)
            task_limit = int(task_limit / scale)

        self.spider.attrs['task_limit'] = task_limit
        return None

    def process_response(self, response):
        return None


class SpeedConcurrencyStrategyMiddleware(SpiderMiddleware):
    """
    速度并发策略，根据设定并发速度系统自动调整
    """

    def __init__(self, spider, settings, avg_concurrency_speed: int = 20, b: int = 10, k: float = 0.5):
        super().__init__(spider=spider, settings=settings)
        self.avg_concurrency_speed = avg_concurrency_speed or 1
        self.b = b
        self.k = k
        self.start_time = time.time()

    def process_request(self, request):

        avg_speed = self.spider.attrs['avg_speed']
        current_time = time.time()

        if current_time - self.start_time <= 60:
            self.spider.attrs['task_limit'] = int(self.k * (current_time - self.start_time) + self.b)
        else:
            self.spider.attrs['task_limit'] = self.avg_concurrency_speed

        if avg_speed != self.avg_concurrency_speed:
            self.spider.attrs['task_limit'] = int(
                self.spider.attrs['task_limit'] * (avg_speed / self.avg_concurrency_speed)
            )

        return None

    def process_response(self, response):
        return None


class TimeConcurrencyStrategyMiddleware(SpiderMiddleware):
    """
    时间并发策略，根据设定并发时间系统自动完成爬取任务
    """

    def __init__(self, spider, settings, second: int = 10 * 60):
        super().__init__(spider=spider, settings=settings)
        self.second = second

    def process_request(self, request):

        remaining = self.spider.attrs['remaining']
        running = self.spider.attrs['running']
        logical_remaining = self.second - running

        if remaining == 0:
            return None

        if logical_remaining <= 0:
            self.spider.attrs['task_limit'] = 1
            return None

        task_limit = int(remaining / logical_remaining)
        self.spider.attrs['task_limit'] = task_limit

        return None

    def process_response(self, response):
        return None
