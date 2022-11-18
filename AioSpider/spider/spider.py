from AioSpider.http import Request
from AioSpider.core import Engine
from AioSpider import GlobalConstant


class Spider:

    # 爬虫名字 默认AioSpider
    name = 'AioSpider'
    start_urls = []

    # 个性化配置文件
    settings = {
        # 'TASK_CONCURRENCY_COUNT': 100,
        # 'HEADERS': {},
        # 'REQUEST_TIMEOUT': 300,
        # 'REQUEST_PROXY': None,
    }
    logger = None
    _connector = None

    @property
    def connector(self):
        if self._connector is None:
            self._connector = GlobalConstant.database
        return self._connector

    def spider_open(self):
        self.logger.info(f'------------------- 爬虫：{self.name} 已启动 -------------------')

    def spider_close(self):
        self.logger.info(f'------------------- 爬虫：{self.name} 已关闭 -------------------')

    def start_requests(self):

        if not hasattr(self, 'start_urls'):
            self.logger.warning('没有start_urls')
            return

        for url in self.start_urls:
            yield Request(url, callback=self.parse)

    def start(self):
        """ 把爬虫传递到引擎中，初始化爬虫对象 """
        engine = Engine(self)
        engine.start()

    def parse(self, response):
        """
            解析回调函数
            @params: response: Response对象
            @return: Request | dict | None
        """
        pass

    def default_parse(self, response):
        pass
