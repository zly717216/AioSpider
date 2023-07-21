from AioSpider.http.base import BaseRequest


class Request(BaseRequest):

    def __init__(self, url: str, **kwargs):
        super(Request, self).__init__(url=url, method='GET', **kwargs)
