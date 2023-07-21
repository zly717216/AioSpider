import aiohttp

from AioSpider.http.base import BaseRequest
from AioSpider.downloader.abc import AiohttpMeta
from AioSpider.downloader.single import singleton


@singleton
class AiohttpSession(AiohttpMeta):

    @property
    def connector(self):
        if self._connector is None or self._closed:
            con_sts = self.settings.ConnectPoolConfig
            self._connector = aiohttp.TCPConnector(
                limit=con_sts.MAX_CONNECT_COUNT,
                use_dns_cache=con_sts.USE_DNS_CACHE,
                force_close=con_sts.FORCE_CLOSE,
                ttl_dns_cache=con_sts.TTL_DNS_CACHE,
                limit_per_host=con_sts.LIMIT_PER_HOST,
                verify_ssl=con_sts.VERIFY_SSL
            )
            self._closed = False

        return self._connector

    @property
    def session(self):
        if self._session is None or self._closed:
            self._session = aiohttp.ClientSession(connector=self.connector)
        return self._session

    @AiohttpMeta.handle_request_except
    async def get(self, request: BaseRequest, **kwargs):
        async with self.session.get(**kwargs) as resp:
            return await self.process_response(request, resp)

    @AiohttpMeta.handle_request_except
    async def post(self, request: BaseRequest, **kwargs):
        async with self.session.post(**kwargs) as resp:
            return await self.process_response(request, resp)

    async def close_session(self):
        if self._session is None:
            return

        await self.session.close()
        self._session = None
        self._closed = True


class AiohttpNoSession(AiohttpMeta):

    @AiohttpMeta.handle_request_except
    async def get(self, request: BaseRequest, **kwargs):
        async with aiohttp.request('GET', **kwargs) as resp:
            return await self.process_response(request, resp)

    @AiohttpMeta.handle_request_except
    async def post(self, request: BaseRequest, **kwargs):
        async with aiohttp.request('POST', **kwargs) as resp:
            return await self.process_response(request, resp)
