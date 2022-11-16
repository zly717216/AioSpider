import re
from pprint import pformat

from AioSpider.parse import Parse
from AioSpider.utils_pkg import execjs
from .request import Request


class Response(object):
    """响应对象"""

    def __init__(self, url='', status=200, headers=None, text='', request=None):

        self.url = url
        self.status = status
        self.headers = headers or {}
        self.text = text
        if request is None:
            self.request = Request('')
        else:
            self.request = request
        self._cached_selector = None
        self.meta = request.meta

    @property
    def selector(self):
        from parsel import Selector
        if self._cached_selector is None:
            self._cached_selector = Selector(self.text)
        return self._cached_selector

    def xpath(self, query, **kwargs):
        return self.selector.xpath(query, **kwargs)

    def css(self, query):
        return self.selector.css(query)

    @property
    def _execjs(self):
        return execjs.compile(self.text)

    def eval_js(self, name):
        return self._execjs.eval(name)

    def call_js(self, name, *args):
        return self._execjs.call(name, *args)

    def re(self, regex):
        arr = re.findall(regex, self.text)
        return Parse(arr)

    def __str__(self):
        s = f'Response <{self.status} {self.request.method} {self.url}>'

        if self.request.headers:
            s += '\n' + f'headers: {pformat(self.request.headers)}'

        if self.request.params:
            s += '\n' + f'params: {pformat(self.request.params)}'

        if self.request.data:
            s += '\n' + f'data: {pformat(self.request.data)}'

        if self.request.proxy:
            s += '\n' + f'proxy: {pformat(self.request.proxy)}'

        return s
