from typing import Union, Callable, NewType

from AioSpider import logger, robot
from AioSpider.models import SpiderModel
from AioSpider.http import Response, BaseRequest
from AioSpider.exceptions import *


username = NewType('username', str)
password = NewType('password', str)
token = NewType('token', str)


class Spider:

    name: str = None
    source: str = None
    target: str = None
    description: str = None
    version: str = None
    start_urls: list = []

    attrs = {
        'task_limit': 0,
        'avg_speed': 0,
        'running': 0,
        'remaining': 0,
        'progress': 0
    }

    middleware = None

    class SpiderRequestConfig:
        pass

    class ConcurrencyStrategyConfig:
        pass

    class ConnectPoolConfig:
        pass

    class DataFilterConfig:
        pass

    class RequestFilterConfig:
        pass

    class RequestProxyConfig:
        pass

    class BrowserConfig:
        pass

    def __init__(
            self,
            *,
            username: str = None,
            password: str = None,
            cookies: dict = None, token: str = None,
            level: int = None,
            call_before: Callable[[], bool] = None,
            call_end: Callable[[], bool] = None,
            call_login: Callable[[str, str], str] = None,
    ):

        self.id: Optional[int] = None
        self.status: int = 0
        self.count: int = 0
        self.start_time: datetime = None
        self.interval: Optional[int] = None
        self.level: int = None
        self.username: Optional[str] = username
        self.password: Optional[str] = password
        self.cookies: Optional[dict] = cookies
        self.token: Optional[str] = token
        self.cust_call_before: Callable[[], bool] = call_before or (lambda: True)
        self.cust_call_end: Callable[[], bool] = call_end or (lambda: True)
        self.cust_call_login: Callable[[str, str], str] = call_login or (lambda username, password: '')

    def set_name(self):
        if self.name is None:
            self.name = self.__class__.__name__

    def get_running_time(self):

        running = int(self.attrs['running'])
        hour, remainder = divmod(running, 3600)
        minute, second = divmod(remainder, 60)
        
        return f"{hour:02d}:{minute:02d}:{second:02d}"

    def get_remaining_time(self):

        remaining = int(self.attrs['remaining'])
        hour, remainder = divmod(remaining, 3600)
        minute, second = divmod(remainder, 60)

        return f"{hour:02d}:{minute:02d}:{second:02d}"

    def spider_open(self):
        self.set_name()
        logger.info(f'------------------- 爬虫：{self.name} 已启动 -------------------')
        robot.info(f'{self.name} 爬虫已启动')

    def spider_close(self):
        logger.info(f'------------------- 爬虫：{self.name} 已关闭 -------------------')
        robot.info(f'{self.name} 爬虫已关闭')

    def start_requests(self):

        if not hasattr(self, 'start_urls'):
            logger.warning('没有start_urls')
            return

        for url in self.start_urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        """
            解析回调函数
            @params: response: Response对象
            @return: Request | dict | None
        """
        pass

    def default_parse(self, response: Response):
        pass
