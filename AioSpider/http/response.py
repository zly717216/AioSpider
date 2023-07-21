import re
import json
from typing import Optional

import execjs
from AioSpider.parse import Parse
from AioSpider import tools

from .request import Request


class Response:
    """响应对象"""

    def __init__(
            self, url: str = '', status: int = 200, headers: Optional[dict] = None, content: bytes = b'', 
            text: str = '', request: Optional[Request] = None, **kwargs
    ):

        self.url = url
        self.status = status
        self.headers = headers or {}
        self.content = content
        self.text = text
        if request is None:
            self.request = Request('')
        else:
            self.request = request
        self._cached_selector = None
        self._cached_xpath = None
        self.__json = None
        self.__jsonp = None
        
        for k in kwargs:
            setattr(self, k, kwargs[k])

    # @property
    # def selector(self):
    #     from parsel import Selector
    #     if self._cached_selector is None:
    #         self._cached_selector = Selector(self.text)
    #     return self._cached_selector

    def xpath(self, query, **kwargs) -> Parse:
        return Parse(self.text).xpath(query, **kwargs)
    
    def css(self, query, **kwargs) -> Parse:
        return Parse(self.text).css(query, **kwargs)

    # def css(self, query):
    #     return self.selector.css(query)

    @property
    def json(self):
        if self.__json is None:
            try:
                self.__json = json.loads(self.text)
                times = 3
                while isinstance(self.__json, str) and times:
                    self.__json = json.loads(self.__json)
                    times -= 1
            except json.decoder.JSONDecodeError:
                try:
                    text = re.sub(r'\\u[\da-zA-Z]+', '', self.text)
                    self.__json = json.loads(text)
                    times = 3
                    while isinstance(self.__json, str) and times:
                        self.__json = json.loads(self.__json)
                        times -= 1
                except json.decoder.JSONDecodeError:
                    self.__json = {}
        return self.__json

    @property
    def jsonp(self):
        if self.__jsonp is None:
            text = re.findall(r'.*?\((.*)\)', self.text)
            try:
                return json.loads(text[0]) if text else {}
            except json.decoder.JSONDecodeError:
                return {}
        return self.__jsonp

    @property
    def _execjs(self):
        return execjs.compile(self.text)

    def eval_js(self, name):
        return self._execjs.eval(name)

    def call_js(self, name, *args):
        return self._execjs.call(name, *args)

    def re(self, regex, flags: int = 0) -> Parse:
        return Parse(self.text).re(regex, flags=flags)

    def __str__(self):

        if self.request.help:
            s = f'Response <{self.request.help} {self.status} {self.request.method} {tools.extract_url(self.url)}>'
        else:
            s = f'Response <{self.status} {self.request.method} {tools.extract_url(self.url)}>'

        return s
