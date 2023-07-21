import json
import random
import asyncio
from pathlib import Path
from abc import ABCMeta, abstractmethod
from asyncio import exceptions
from urllib.parse import urlparse
from urllib.request import getproxies
from typing import Union, Dict
from functools import reduce

import aiohttp
try:
    from cchardet import detect
except ModuleNotFoundError:
    from chardet import detect

from AioSpider import tools
from AioSpider import GlobalConstant, logger
from AioSpider.http import Response
from AioSpider.http.base import BaseRequest
from AioSpider.models import ProxyPoolModel
from AioSpider.constants import ProxyType, ProxyPoolStrategy, ProxyVerifySource


user_agent = json.load((Path(__file__).parent / "user-agent.json").open())


class DownloadMiddleware(metaclass=ABCMeta):
    """中间件基类"""

    is_async = False

    def __init__(self, spider, settings):
        self.spider = spider
        self.settings = settings
    
    @abstractmethod
    def process_request(self, request: BaseRequest):
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
    def process_response(self, response: Response):
        """
            处理响应
            @params:
                response: Response 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                Response: 交由引擎重新调度该Response对象
                None: 正常，继续往下执行 穿过下一个中间件
                False: 丢弃该Request或Response对象
        """

        return None

    def spider_open(self, spider):
        pass

    def spider_close(self, spider):
        pass


class AsyncMiddleware(metaclass=ABCMeta):
    """中间件基类"""

    is_async = True

    def __init__(self, spider, settings):
        self.spider = spider
        self.settings = settings

    @abstractmethod
    async def process_request(self, request: BaseRequest):
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
    async def process_response(self, response: Response):
        """
            处理请求
            @params:
                response: Response 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                Response: 交由引擎重新调度该Response对象
                None: 正常，继续往下执行 穿过下一个中间件
                False: 丢弃该Request或Response对象
        """

        return None

    def spider_open(self, spider):
        pass

    def spider_close(self, spider):
        pass

    
class ErrorMiddleware(metaclass=ABCMeta):
    """中间件基类"""

    def __init__(self, spider, settings):
        self.spider = spider
        self.settings = settings

    @abstractmethod
    def process_exception(self, request, exception):
        """
            处理异常
            @params:
                request: BaseRequest 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                Response: 交由引擎重新调度该Response对象
                None: 正常，继续往下执行 穿过下一个中间件
                False: 丢弃该Request或Response对象
                exception: 将会抛出该异常
        """

        return None

    def spider_open(self, spider):
        pass

    def spider_close(self, spider):
        pass


class FirstMiddleware(DownloadMiddleware):
    """最先执行的中间件"""

    def process_request(self, request: BaseRequest):
        return None

    def process_response(self, response: Response):
        return None


class HeadersMiddleware(DownloadMiddleware):
    """请求头处理的中间件"""

    def process_user_agent(self, request: BaseRequest):

        if request.headers.get('User-Agent') or request.headers.get('user-agent'):
            return None

        sts = self.settings.SpiderRequestConfig
        headers = sts.HEADERS

        if request.headers is None:
            request.headers = headers

        if request.headers.get('User-Agent') or request.headers.get('user-agent'):
            return None

        if sts.RANDOM_HEADERS:
            _r = str(random.randint(0, 984))
            _k = user_agent['randomize'][_r]
            headers['User-Agent'] = random.choice(user_agent['browsers'][_k])
        else:
            ua_type = sts.USER_AGENT_TYPE
            if ua_type:
                if isinstance(ua_type, str):
                    headers['User-Agent'] = random.choice(user_agent['browsers'][ua_type])

                if hasattr(self.settings, '__iter__'):
                    headers['User-Agent'] = random.choice(user_agent['browsers'][random.choice(ua_type)])

        request.headers['User-Agent'] = headers['User-Agent']

    def process_referer(self, request: BaseRequest):

        # 自动请求头中添加Referer
        if not (request.headers.get('Referer') or request.headers.get('referer')):
            request.headers['Referer'] = request.url

    def process_request(self, request: BaseRequest):

        self.process_user_agent(request)

        if request.auto_referer:
            self.process_referer(request)

        return None

    def process_response(self, response: Response):
        return None


class RetryMiddleware(DownloadMiddleware):
    """重试中间件"""

    def process_request(self, request: BaseRequest):
        return None

    def process_response(self, response: Response):

        if response.status == 200:
            return None
        
        if response.status == 407:
            logger.warning(f'{response.request} 请求代理验证失败')
        else:
            logger.warning(f'{response} 状态码异常')

        # 判断是否要重试
        if not self.settings.SpiderRequestConfig.RETRY_ENABLED:
            return False

        if response.status not in self.settings.SpiderRequestConfig.RETRY_STATUS:
            return False

        return response.request


class LastMiddleware(DownloadMiddleware):
    """最后执行的中间件"""

    def __init__(self, *args, **kwargs):
        super(LastMiddleware, self).__init__(*args, **kwargs)
        self.encoding_map = {}

    def process_request(self, request: BaseRequest):
        return None

    def process_response(self, response: Response):

        host = urlparse(response.url).netloc
        content = response.content

        if not content:
            return None

        if self.encoding_map.get(host) is None:
            if hasattr(response.request, 'encoding') and response.request.encoding:
                self.encoding_map[host] = response.request.encoding
            else:
                encoding = detect(content)["encoding"]
                encoding = encoding if encoding else response.request.encoding
                encoding = "GB18030" if encoding.upper() in ("GBK", "GB2312") else encoding
                self.encoding_map[host] = encoding

        try:
            text = content.decode(self.encoding_map[host], "replace")
        except MemoryError:
            text = content.decode(self.encoding_map[host], "ignore")

        response.content = content
        response.text = text

        return None
    

class ProxyPoolMiddleware(AsyncMiddleware, LastMiddleware):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._proxy = None
        self.proxy = []
        self._proxy_count = None
        self._verify_site = {}
        self._weights = None
        self._expanded_proxies = None
        self._proxy_event = asyncio.Event()
        self.fetch_flag = False

    @property
    def weights(self):
        if self._weights is None:
            weights = [i["weight"] for i in ProxyPoolModel.objects.only('weight').filter(status=1).all()]
            weights = self.calculate_weights(weights)
            self._weights = {proxy: weight for proxy, weight in zip(self.proxy, weights)}
        return self._weights

    @property
    def proxy_count(self):
        if self._proxy_count is None:
            self._proxy_count = {k: 0 for k in self.proxy}
        return self._proxy_count

    @property
    def expanded_proxies(self):
        if self._expanded_proxies is None:
            self._expanded_proxies = [proxy for proxy in self.proxy for _ in range(self.weights[proxy])]
        return self._expanded_proxies

    @staticmethod
    def calculate_weights(weights):
        gcd = lambda a, b: a if b == 0 else gcd(b, a % b)
        sim_ratio = lambda x: [i // reduce(gcd, x) for i in x]
        weights = sim_ratio([int((weight / sum(weights)) * 100) for weight in weights])
        return weights

    async def get_proxy(self, request):
        conf = self.settings.RequestProxyConfig
        if conf.proxy_type is ProxyType.none:
            return None
        elif conf.proxy_type == ProxyType.system:
            return self.distribute_system()
        elif conf.proxy_type == ProxyType.appoint:
            address = tools.parse_json(conf.config, f"{ProxyType.appoint}.address", None)
            return address if address is None else self.distribute_appoint(address)
        elif conf.proxy_type == ProxyType.pool:
            return await self.distribute_pool(request)
        else:
            return None

    def distribute_appoint(self, proxy: Union[None, str, list, tuple]):
        if proxy is None:
            return None
        if isinstance(proxy, (list, tuple)):
            random.shuffle(proxy)
            proxy = random.choice(proxy)
        if isinstance(proxy, str):
            return proxy if 'http' in proxy else ('http://' + proxy)
        else:
            return None

    def distribute_system(self):
        return getproxies().get('http') or getproxies().get('https')

    async def distribute_pool(self, request):

        if self._proxy is None and not self.fetch_flag:
            self.fetch_flag = True
            proxies = ProxyPoolModel.objects.filter(status=1).all()
            self._proxy = await self.first_verify(proxies)
            # 设置事件，通知等待的任务可以继续执行
            self._proxy_event.set()

        await self._wait_for_proxy()

        if not self.proxy:
            self.proxy = self._proxy

        strategy = tools.parse_json(
            self.settings.RequestProxyConfig.config, f'{ProxyType.pool}.strategy', ProxyPoolStrategy.balance
        )
        if strategy == ProxyPoolStrategy.weight:
            return await self.distribute_weighted(request)
        elif strategy == ProxyPoolStrategy.balance:
            return await self.distribute_balanced(request)
        elif strategy == ProxyPoolStrategy.random:
            return await self.distribute_random(request)
        else:
            return await self.distribute_balanced(request)

    async def distribute_balanced(self, request):
        while self.proxy_count:
            proxy = min(self.proxy_count, key=self.proxy_count.get)
            if proxy not in self.proxy:
                self.proxy_count.pop(proxy)
                continue
            if request.website not in self._verify_site.get(proxy, []) and not await self.verify_proxy(proxy, request):
                continue
            self.proxy_count[proxy] += 1
            return proxy
        return False

    async def distribute_weighted(self, request):
        if not self.expanded_proxies:
            self.reset_expanded_proxies()

        while self.expanded_proxies:
            proxy = random.choice(self.expanded_proxies)
            self.expanded_proxies.remove(proxy)

            if request.website in self._verify_site.get(proxy, []) or await self.verify_proxy(proxy, request):
                return proxy

        return False

    async def distribute_random(self, request):
        while self.proxy:
            proxy = random.choice(self.proxy)
            if request.website not in self._verify_site.get(proxy, []) and not await self.verify_proxy(proxy, request):
                continue
            return proxy
        return False

    def reset_expanded_proxies(self):
        self._expanded_proxies = None

    def reset_weights(self):
        self._weights = None

    async def is_proxy_valid(self, proxy, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=1, proxy=proxy) as response:
                    if response.status == 200:
                        return True
                    return False
        except Exception as e:
            return False

    async def first_verify(self, proxies):
        proxy_list = []
        for i in proxies:
            proxy = f'{i["protocol"]}://{i["username"]}:{i["password"]}@{i["ip"]}:{i["port"]}'
            verify_site = tools.parse_json(
                self.settings.RequestProxyConfig.config,
                f'{ProxyType.pool}.firstVerifySite',
                ProxyVerifySource.baidu
            )
            self._verify_site.setdefault(proxy, []).append(verify_site)
            if await self.is_proxy_valid(proxy, url=verify_site):
                logger.info(f'代理首次验证成功：{proxy}({i["address"]}-{i["operator"]})，验证源: {verify_site}')
                proxy_list.append(proxy)
            else:
                logger.info(f'代理首次验证失败：{proxy}({i["address"]}-{i["operator"]})，验证源: {verify_site}')
                ProxyPoolModel.objects.update(items={'id': i["id"], 'status': 0}, where='id')
        return proxy_list

    async def verify_proxy(self, proxy, request):

        self._verify_site.setdefault(proxy, []).append(request.website)
        if await self.is_proxy_valid(proxy, request.website):
            if proxy is not None:
                logger.info(f'代理验证成功：{proxy}，验证源: {request.website}')
            return True
        else:
            if proxy is not None:
                logger.info(f'代理验证失败：{proxy}，验证源: {request.website}')

            self.proxy.remove(proxy)
            return False

    async def _wait_for_proxy(self):
        if self._proxy is None:
            # 等待事件被设置，即获取到代理
            await self._proxy_event.wait()
            # 清除事件状态，以便下次等待
            self._proxy_event.clear()

    async def process_request(self, request):
        
        if request.proxy:
            proxy = request.proxy
        elif self.settings.RequestProxyConfig:
            proxy = await self.get_proxy(request)
        else:
            proxy = None
            
        if proxy is not False:
            request.proxy = proxy
        
        return None

    async def process_response(self, response):
        return None
    

class ExceptionMiddleware(ErrorMiddleware):
    """异常中间件"""

    def process_exception(self, request, exception):

        if isinstance(exception, aiohttp.ClientPayloadError):
            logger.error(f'ClientPayloadError：{str(exception)}')
            return request
        if isinstance(exception, aiohttp.ServerDisconnectedError):
            logger.error(f'ServerDisconnectedError：{str(exception)}')
            return request
        if isinstance(exception, aiohttp.ClientOSError):
            logger.error(f'ClientOSError：{str(exception)}')
            return request
        if isinstance(exception, aiohttp.ClientHttpProxyError):
            logger.error(f'ClientHttpProxyError：{str(exception)}')
            return request
        if isinstance(exception, aiohttp.ClientConnectorCertificateError):
            logger.error(f'ClientConnectorCertificateError：{str(exception)}')
            return request
        if isinstance(exception, exceptions.TimeoutError):
            logger.error(
                f'网络连接超时：{request}, TIMEOUT: {request.timeout or self.settings.SpiderRequestConfig.REQUEST_TIMEOUT}'
            )
            return request

        return exception


class BrowserMiddleware(DownloadMiddleware):
    """浏览器渲染中间件"""

    _browser = None
    _driver = None

    @property
    def browser(self):
        if self._browser is None:
            self._browser = GlobalConstant().browser
        return self._browser

    @property
    def driver(self):
        if self._driver is None:
            self._driver = self.browser.browser
        return self._driver

    def goto(self, url):
        self.driver.get(url)
        GlobalConstant().browser.flag = True

    def refresh(self):
        self.driver.execute_script("location.reload()")
        
    def execut_js(self, js):
        return self.driver.execute_script(js)

    def get_cookies(self) -> dict:
        return {i['name']: i['value'] for i in self.driver.get_cookies()}

    def process_request(self, request: BaseRequest):
        return None

    def process_response(self, response: Response):
        return None
    
    def __del__(self):
        if self._driver is None:
            return 
        self.driver.quit()
