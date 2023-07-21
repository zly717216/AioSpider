from AioSpider import constants
from AioSpider.downloader.aiohttp_module import AiohttpSession, AiohttpNoSession
from AioSpider.downloader.requests_module import RequestsSession, RequestsNoSession


class DownloaderFactory:

    @staticmethod
    def create_downloader(settings, request_type, use_session):
        handler_map = {
            (None, True): AiohttpSession,
            (None, False): AiohttpNoSession,
            (constants.RequestWay.aiohttp, True): AiohttpSession,
            (constants.RequestWay.aiohttp, False): AiohttpNoSession,
            (constants.RequestWay.requests, True): RequestsSession,
            (constants.RequestWay.requests, False): RequestsNoSession
        }

        handler = handler_map.get((request_type, use_session))
        if handler is None:
            raise ValueError('请求库配置不正确，请检查配置文件')
        return handler(settings)
