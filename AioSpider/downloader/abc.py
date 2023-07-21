import numbers
from abc import ABC, abstractmethod

import aiohttp
from AioSpider import constants
from AioSpider.exceptions import RequestError
from AioSpider.http.base import BaseRequest
from AioSpider.http.response import Response


class BaseDownloader(ABC):

    @abstractmethod
    async def get(self, request: BaseRequest, **kwargs):
        pass

    @abstractmethod
    async def post(self, request: BaseRequest, **kwargs):
        pass

    @classmethod
    async def close_session(cls):
        pass


class RequestBaseMeta(BaseDownloader):

    def __init__(self, settings, *args, **kwargs):
        self.settings = settings

    async def __call__(self, request: BaseRequest, *args, **kwargs):
        return await self.request(request)

    async def get(self, request: BaseRequest, **kwargs):
        pass

    async def post(self, request: BaseRequest, **kwargs):
        pass

    async def close_session(cls):
        pass

    async def request(self, request: BaseRequest):

        self.validate_request(request)
        attrs = self.query_attrs(request)

        if request.method.upper() == 'GET':
            return await self.get(request, **attrs)

        if request.method.upper() == 'POST':
            return await self.post(request, **attrs)

        raise RequestError()

    def query_attrs(self, request: BaseRequest):
        if not request:
            return None

        attrs = {
            'headers': request.headers,
            'timeout': request.timeout or self.settings.SpiderRequestConfig.REQUEST_TIMEOUT,
            'cookies': request.cookies,
            'params': request.params,
            'data': request.data,
            'proxy': request.proxy
        }

        url = request.url
        if '?' not in url:
            attrs['params'] = request.params
        attrs['url'] = url

        return attrs

    def validate_request(self, request: BaseRequest):

        # 判断请求方法是否合法
        if request.method.upper() not in constants.RequestMethod:
            raise ValueError(f"无效的请求方法: {request.method}")

        # 检查url是否合法
        if not request.scheme or not request.domain:
            raise ValueError(f"无效的 URL: {request.url}")

        return True


class RequestMeta(RequestBaseMeta):

    async def request(self, request: BaseRequest):
        attrs = self.query_attrs(request)
        attrs = self.handle_proxy(attrs)

        if request.method.upper() == 'GET':
            return await self.get(request, **attrs)

        if request.method.upper() == 'POST':
            return await self.post(request, **attrs)

        raise RequestError()

    @staticmethod
    def handle_proxy(attrs):
        proxy = attrs.pop('proxy', None)

        if not proxy:
            attrs['proxies'] = None
            return attrs

        if isinstance(proxy, dict):
            attrs['proxies'] = proxy
            return attrs

        if 'http' not in proxy:
            attrs['proxies'] = {
                'http': 'http://' + proxy, 'https': 'http://' + proxy
            }
        else:
            attrs['proxies'] = {'http': proxy, 'https': proxy}

        return attrs

    @staticmethod
    def handle_request_except(func):

        async def ware(self, request, **kwargs):
            try:
                return await func(self, request, **kwargs)
            except aiohttp.ClientConnectorCertificateError as e:
                await self.close_session()
                raise e
            except aiohttp.ClientConnectorError as e:
                return e
            except RuntimeError as e:
                if 'Session is closed' in str(e):
                    self._closed = True
                    return await func(self, request, **kwargs)
                else:
                    return e
            except Exception as e:
                return e

        return ware

    @staticmethod
    def handle_response_except(func):

        async def ware(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                return e

        return ware
    
    def process_response(self, req: BaseRequest, resp) -> Response:
        return Response(
            url=resp.url, status=resp.status_code, headers=dict(resp.headers),
            content=resp.content, request=req
        )


class AiohttpMeta(RequestBaseMeta):

    def __init__(self, settings):
        super().__init__(settings)
        self._connector = None
        self._session = None
        self._closed = True

    def query_attrs(self, request: BaseRequest):
        attrs = super().query_attrs(request=request)

        if attrs.get('timeout') and isinstance(attrs['timeout'], numbers.Number):
            attrs['timeout'] = aiohttp.ClientTimeout(total=int(attrs['timeout']))

        return attrs

    @staticmethod
    def handle_request_except(func):

        async def ware(self, request, **kwargs):
            try:
                return await func(self, request, **kwargs)
            except aiohttp.ClientConnectorCertificateError as e:
                # await self.close_session()
                return e
            except aiohttp.ClientConnectorError as e:
                return e
            except RuntimeError as e:
                if 'Session is closed' in str(e):
                    self._closed = True
                    return await func(self, request, **kwargs)
                else:
                    return e
            except Exception as e:
                return e

        return ware

    @staticmethod
    def handle_response_except(func):

        async def ware(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                return e

        return ware
    
    async def process_response(self, req: BaseRequest, resp) -> Response:
        return Response(
            url=str(resp.url), status=resp.status, headers=dict(resp.headers),
            content=await resp.read(), request=req
        )
