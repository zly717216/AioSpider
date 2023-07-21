__all__ = ['LoadMiddleware']

from pprint import pformat
from importlib import import_module

from AioSpider import logger
from AioSpider.middleware import DownloadMiddleware, SpiderMiddleware, FirstMiddleware, LastMiddleware


class LoadMiddleware:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.init_download_middleware(), instance.init_spider_middleware()

    def __init__(self, spider, settings, request_pool):
        self.spider = spider
        self.settings = settings
        self.request_pool = request_pool

    def init_download_middleware(self):
        
        middleware = getattr(self.settings, 'DOWNLOAD_MIDDLEWARE', {})
        middleware = sorted(middleware, key=middleware.get)

        if middleware:
            logger.info(f'已加载到{len(middleware)}个下载中间件已启动：\n{pformat(middleware)}')
        else:
            return []

        instances = [self._create_middleware_instance(p, 'download') for p in middleware]
        instances = [instance for instance in instances if instance is not None]

        first_last = [
            (idx, instance) for idx, instance in enumerate(instances)
            if isinstance(instance, (FirstMiddleware, LastMiddleware))
        ]

        for idx, instance in reversed(first_last):
            instances.pop(idx)
            if isinstance(instance, FirstMiddleware):
                instances.insert(0, instance)
            else:
                instances.append(instance)

        return instances

    def init_spider_middleware(self):

        middleware = getattr(self.settings, 'SPIDER_MIDDLEWARE', {})

        self._process_concurrency_strategy(middleware)

        if middleware:
            logger.info(f'已加载到{len(middleware)}个爬虫中间件已启动：\n{pformat(middleware)}')
        else:
            return []

        instances = [self._create_middleware_instance(p, 'spider') for p in middleware]
        instances = [instance for instance in instances if instance is not None]

        return instances

    def _create_middleware_instance(self, p, type):

        x = __import__('middleware')
        y = import_module(f'AioSpider.middleware.{type}')

        *py, c = p.split('.')

        if hasattr(x, c):
            cls = getattr(x, c)
            if type == 'download' and not issubclass(cls, DownloadMiddleware):
                return None
            if type == 'spider' and not issubclass(cls, SpiderMiddleware):
                return None
        else:
            cls = getattr(y, c, None)

        if cls:
            return cls(self.spider, self.settings)

        return None

    def _remove_middleware_keys(self, middleware, keys_to_remove):
        for key in keys_to_remove:
            if key in middleware:
                middleware.pop(key)

    def _process_concurrency_strategy(self, middleware):

        conf = self.settings.ConcurrencyStrategyConfig
        self.spider.attrs['task_limit'] = 20

        if conf.random.get('enabled', False):
            keys_to_remove = [
                'AioSpider.middleware.spider.AutoConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.SpeedConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.TimeConcurrencyStrategyMiddleware'
            ]
        elif conf.speed.get('enabled', False):
            keys_to_remove = [
                'AioSpider.middleware.spider.AutoConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.RandomConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.TimeConcurrencyStrategyMiddleware'
            ]
        elif conf.time.get('enabled', False):
            keys_to_remove = [
                'AioSpider.middleware.spider.AutoConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.RandomConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.SpeedConcurrencyStrategyMiddleware'
            ]
        elif conf.fix.get('enabled', False):
            self.spider.attrs['task_limit'] = conf.fix.get('task_limit', 10)
            keys_to_remove = [
                'AioSpider.middleware.spider.AutoConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.SpeedConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.RandomConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.TimeConcurrencyStrategyMiddleware'
            ]
        else:
            keys_to_remove = [
                'AioSpider.middleware.spider.AutoConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.SpeedConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.RandomConcurrencyStrategyMiddleware',
                'AioSpider.middleware.spider.TimeConcurrencyStrategyMiddleware'
            ]

        self._remove_middleware_keys(middleware, keys_to_remove)
