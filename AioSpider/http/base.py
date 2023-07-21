import json
from urllib.parse import urlparse
from typing import Literal, Optional, Callable, Union

import requests
from w3lib.url import safe_url_string

from AioSpider import tools
from AioSpider import GlobalConstant


RequestMethod = Literal['GET', 'POST']


class BaseRequest(object):
    """ 实现请求方法 """

    __slots__ = (
        '_url', 'scheme', 'domain', 'website', 'path', 'method', 'headers', '_params', '_data', 'callback', 'cookies', 
        'timeout', 'proxy', 'encoding', 'priority', 'dnt_filter', 'help', 'auto_referer', 'meta', '_hash'
    )

    def __init__(
            self, url: str, method: RequestMethod = 'GET', callback: Optional[Callable] = None,
            params: Optional[dict] = None, headers: Optional[dict] = None, encoding: str = None,
            data: Union[dict, str] = None, cookies: Optional[dict] = None, timeout: Optional[int] = None,
            proxy: Optional[str] = None, priority: int = 1, dnt_filter: bool = False, help: Optional[str] = None,
            add_headers: Optional[dict] = None, target: str = None, auto_referer=True, **kwargs
    ):

        self._url = self._set_url(url, encoding)
        self.scheme = self._set_scheme(self.url)
        self.domain = self._set_domain(self.url)
        self.website = self._set_website(self.url)
        self.path = self._set_path(self.url)
        self.method = method.upper()
        self.headers = headers or {}
        self._params = params
        self._data = data or {}
        self.cookies = cookies or {}
        self.timeout = timeout
        self.proxy = proxy
        self.encoding = encoding
        self.callback = callback
        self.dnt_filter = dnt_filter
        self.priority = priority
        self.auto_referer = auto_referer
        self.help = help
        self.meta = {}
        self._hash = None

        if add_headers is not None:
            self.headers.update(add_headers)

        for k in kwargs:
            self.meta[k] = kwargs[k]
    
    @property
    def url(self):
        return self._url
    
    @url.setter
    def url(self, url):
        self._url = url
        self._hash = None

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self._params = params
        self._hash = None
        
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._hash = None

    def _set_url(self, url, encoding):
        """网址的修正以及判断"""

        # 如果不是字符类型肯定报错
        if not isinstance(url, str):
            raise TypeError(f'请求的网址必须是字符串类型, 您指定的是: {type(url).__name__}，请输入正确的网址。url ---> {url}')

        # 如果没有冒号 肯定不是完整的网址
        if ':' not in url:
            raise ValueError(f'网址协议不正确，请输入正确的网址，url ---> {url}')

        return safe_url_string(url, encoding or 'utf-8')

    def _set_scheme(self, url):
        return urlparse(url).scheme
        
    def _set_domain(self, url):
        return urlparse(url).netloc
    
    def _set_website(self, url):
        return self.scheme + '://' + self.domain
    
    def _set_path(self, url):
        return urlparse(url).path

    def fetch(self):
        proxies = {
            'http': self.proxy, 'https': self.proxy
        }
        if self.method.upper() == 'GET':
            return requests.get(
                self.url, headers=self.headers, params=self.params, proxies=proxies, cookies=self.cookies, 
                timeout=self.timeout
            )
        if self.method.upper() == 'POST':
            return requests.post(
                self.url, headers=self.headers, params=self.params, data=self.data, cookies=self.cookies, 
                proxies=proxies, timeout=self.timeout
            )

    def __str__(self):
        if self.help:
            return f"<{self.help} {self.method} {self.url}>"
        return f"<{self.method} {self.url}>"

    __repr__ = __str__

    def __getattr__(self, item):
        if item in self.__slots__:
            return self.__dict__[item]
        return self.meta.get(item, None)

    @property
    def hash(self):
        
        if self._hash is None:

            def remove_exclude_stamps(data_dict):
                if exclude_stamp:
                    return {k: v for k, v in data_dict.items() if k not in sts.ExcludeStamp}
                return data_dict
            
            sts = GlobalConstant().settings.RequestFilterConfig
            exclude_stamp = sts.IgnoreStamp and sts.ExcludeStamp

            url = self.url
            if self.params:
                params = remove_exclude_stamps(self.params)
                url = tools.quote_url(url, params)

            if isinstance(self.data, str):
                data = json.loads(self.data)
            else:
                data = self.data.copy()

            data = remove_exclude_stamps(data)

            self._hash = tools.make_md5(f'{url}-{self.method}-{tools.quote_params(data)}')

        return self._hash

    def to_dict(self):
        request_dict = {}
        for slot in self.__slots__:
            value = getattr(self, slot)
            if slot == 'callback' and callable(value):
                value = f'{value.__module__}.{value.__self__.__class__.__name__}.{value.__name__}'
            request_dict[slot] = tools.dump_json(value)
        return request_dict

    @classmethod
    def from_dict(cls, request_dict):

        request_dict = {k: tools.load_json(v) for k, v in request_dict.items()}
        request_dict['_hash'] = None

        if request_dict['callback'] and isinstance(request_dict['callback'], str):
            components = request_dict['callback'].split('.')
            module = __import__(components[0])
            for component in components[1:]:
                module = getattr(module, component)
            request_dict['callback'] = module

        return cls(
            url=request_dict['url'],
            method=request_dict['method'],
            callback=request_dict['callback'],
            params=request_dict['params'],
            headers=request_dict['headers'],
            encoding=request_dict['encoding'],
            data=request_dict['data'],
            cookies=request_dict['cookies'],
            timeout=request_dict['timeout'],
            proxy=request_dict['proxy'],
            priority=request_dict['priority'],
            dnt_filter=request_dict['dnt_filter'],
            help=request_dict['help'],
            auto_referer=request_dict['auto_referer'],
            **request_dict['meta']
        )
