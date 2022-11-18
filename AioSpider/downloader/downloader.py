from AioSpider import GlobalConstant
from AioSpider.http import Request, Response


session = GlobalConstant().session


class DownloadHandler:

    def __init__(self, settings):
        self.settings = settings

    async def fetch(self, request):

        global session
        if session is None:
            session = GlobalConstant().session

        kwargs = {
            'headers': request.headers,
            'timeout': request.timeout or getattr(self.settings, "REQUEST_TIMEOUT", 10),
            'cookies': request.cookies,
            'proxy': request.proxy
        }

        url = request.url

        if request.method == "POST":
            response = await session.post(url, data=request.data, **kwargs)
            request.status = response.status
        else:
            try:
                response = await session.get(url, **kwargs)
                request.status = response.status
            except Exception as e:
                return e
        try:
            content = await response.read()
            res = Response(
                url=str(response.url), status=response.status, headers=response.headers,
                text=content, request=request
            )

            # 将request的属性绑定到response实例上
            for attr in request.kwargs:
                setattr(res, attr, request.kwargs[attr])

            return res
        except Exception as e:
            return e


class Downloader:

    def __init__(self, middleware, settings):
        self.handler = DownloadHandler(settings)
        self.middleware = middleware

    async def fetch(self, request):

        http_obj = await self._process_request(request)

        # 丢弃
        if http_obj is None:
            return None

        # 发起请求
        if isinstance(http_obj, Request):
            res_obj = await self.handler.fetch(http_obj)

            # 下载返回响应
            if isinstance(res_obj, Response):
                response = await self._process_response(res_obj)
                return response
            # 下载返回异常
            if isinstance(res_obj, Exception):
                request = await self._process_exception(request, res_obj)
                return request

        if isinstance(http_obj, Response):
            response = await self._process_response(http_obj)
            return response

    async def _process_request(self, request):

        if request is None:
            return None

        for m in self.middleware:
            if not hasattr(m, 'process_request'):
                continue
            ret = m.process_request(request)
            if ret is None:
                continue
            if ret is False:
                return None
            elif isinstance(ret, Request):
                return ret
            elif isinstance(ret, Response):
                return ret
            else:
                raise Exception('中间件的process_request方法返回值必须为 Request/Response/None/False 对象')
        else:
            return request

    async def _process_response(self, response):

        if response is None:
            return None

        for m in reversed(self.middleware):
            if not hasattr(m, 'process_response'):
                continue
            ret = m.process_response(response)
            if ret is None:
                continue
            if ret is False:
                return None
            elif isinstance(ret, Request):
                return ret
            elif isinstance(ret, Response):
                return ret
            else:
                raise Exception('中间件的process_response方法返回值必须为 Request/Response/None/False 对象')
        else:
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
            if ret is False:
                return None
            elif isinstance(ret, Request):
                return ret
            elif isinstance(ret, Response):
                return ret
            elif isinstance(ret, Exception):
                raise ret
            else:
                raise Exception('中间件的process_exception方法返回值必须为 Request/Response/None/False 对象')
        else:
            return request
