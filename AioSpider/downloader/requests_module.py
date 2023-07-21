import asyncio
import requests
from requests.adapters import HTTPAdapter

from AioSpider.http.base import BaseRequest
from AioSpider.downloader.abc import RequestMeta
from AioSpider.downloader.single import singleton


@singleton
class RequestsSession(RequestMeta):

    def __init__(self, *args, **kwargs):
        super(RequestsSession, self).__init__(*args, **kwargs)
        self._session = None
        self._closed = True

    @property
    def session(self):
        if self._session is None or self._closed:
            con_sts = self.settings.ConnectPoolConfig
            self._session = requests.Session()

            adapter = HTTPAdapter(
                pool_connections=con_sts.MAX_CONNECT_COUNT,
                pool_maxsize=con_sts.LIMIT_PER_HOST,
                pool_block=True
            )

            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)
            self._closed = False

        return self._session

    @RequestMeta.handle_request_except
    async def get(self, request: BaseRequest, **kwargs):
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, self.session.get, **kwargs)
        return self.process_response(request, resp)

    @RequestMeta.handle_request_except
    async def post(self, request: BaseRequest, **kwargs):
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, self.session.post, **kwargs)
        return self.process_response(request, resp)

    async def close_session(self):
        if self._session is None:
            return

        self.session.close()
        self._session = None
        self._closed = True


class RequestsNoSession(RequestMeta):

    @RequestMeta.handle_request_except
    async def get(self, request: BaseRequest, **kwargs):
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, requests.get, **kwargs)
        return self.process_response(request, resp)

    @RequestMeta.handle_request_except
    async def post(self, request: BaseRequest, **kwargs):
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, requests.post, **kwargs)
        return self.process_response(request, resp)
