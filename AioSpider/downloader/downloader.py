from AioSpider.exceptions import *
from AioSpider.http import Response
from AioSpider.http.base import BaseRequest
from AioSpider.downloader.downloader_factory import DownloaderFactory


class RequestHandler:

    def __init__(self, settings):
        use_session = settings.SpiderRequestConfig.REQUEST_USE_SESSION
        _type = settings.SpiderRequestConfig.REQUEST_USE_METHOD
        self._handle = DownloaderFactory.create_downloader(settings, _type, use_session)

    async def __call__(self, request, *args, **kwargs):
        res = await self._handle(request)

        if isinstance(res, Response):
            return self.set_attr(res)

        return res

    @staticmethod
    def set_attr(response):
        """将request的属性绑定到response实例上"""

        for attr in response.request.meta:
            setattr(response, attr, response.request.meta[attr])

        return response

    async def fetch(self, request):
        return await self(request)

    async def close_session(self):
        await self._handle.close_session()


class Downloader:

    def __init__(self, settings, middleware):
        self.handler = RequestHandler(settings)
        self.middleware = middleware

    async def fetch(self, request):

        http_obj = await self._process_request(request)
        if http_obj is None:
            return None

        if isinstance(http_obj, BaseRequest):
            res_obj = await self.handler.fetch(http_obj)

            if isinstance(res_obj, Response):
                response = await self._process_response(res_obj)
                if response is None:
                    return None
                response.request = http_obj
                return response

            if isinstance(res_obj, Exception):
                return await self._process_exception(request, res_obj)

        if isinstance(http_obj, Response):
            return await self._process_response(http_obj)

    async def _process_request(self, request):

        if request is None:
            return False

        for m in self.middleware:
            if not hasattr(m, 'process_request'):
                continue

            ret = await m.process_request(request) if m.is_async else m.process_request(request)

            if ret is None:
                continue
            elif ret is False:
                return None
            elif isinstance(ret, (BaseRequest, Response)):
                return ret
            else:
                raise MiddlerwareError()

        return request

    async def _process_response(self, response):

        if response is None:
            return False

        for m in reversed(self.middleware):
            if not hasattr(m, 'process_response'):
                continue

            ret = await m.process_response(response) if m.is_async else m.process_response(response)

            if ret is None:
                continue
            elif ret is False:
                return None
            elif isinstance(ret, (BaseRequest, Response)):
                return ret
            else:
                raise MiddlerwareError(flag=1)

        return response

    async def _process_exception(self, request, exception):

        if exception is None:
            return None

        for m in self.middleware:
            if not hasattr(m, 'process_exception'):
                continue

            ret = m.process_exception(request, exception)

            if ret is None:
                continue
            elif ret is False:
                return None
            elif isinstance(ret, Exception):
                raise ret
            elif isinstance(ret, (BaseRequest, Response)):
                return ret
            else:
                raise MiddlerwareError(flag=2)
            
        raise exception

    async def close_session(self):
        await self.handler.close_session()
