from urllib import parse
from AioSpider.utils_pkg.w3lib.url import safe_url_string


class Request(object):
    """ 实现请求方法 """

    def __init__(
            self, url, method='GET', callback=None, params=None, headers=None, encoding='utf-8',
            data=None, cookies=None, timeout=0, proxy=None, priority=1, dnt_filter=False,
            help=None, *args, **kwargs
        ):

        self.encoding = encoding
        self.url = self._set_url(url)
        self.method = method.upper()
        self.url = self._quote_params(params) or {}
        self.params = params or {}
        self.cookies = cookies or {}
        self.callback = callback
        self.dnt_filter = dnt_filter
        self.help = help

        self.headers = headers or {}
        if kwargs.get('add_headers'):
            self.headers.update(kwargs.get('add_headers', {}))
            kwargs.pop('add_headers')

        self.auto_referer = True
        if kwargs.get('auto_referer'):
            self.auto_referer = True if kwargs.get('auto_referer') else False

        if kwargs.get('auto_referer') is not None:
            kwargs.pop('auto_referer')

        self.data = data or {}
        self.timeout = timeout
        self.proxy = proxy
        self.args = args
        self.kwargs = kwargs
        self.status = None

    def _set_url(self, url):
        """网址的修正以及判断"""

        # 如果不是字符类型肯定报错
        if not isinstance(url, str):
            raise TypeError(f'请求的网址必须是字符串类型, 您指定的是: {type(url).__name__}，请输入正确的网址。url ---> {url}')

        # 如果没有冒号 肯定不是完整的网址
        if ':' not in url:
            raise ValueError(f'网址协议不正确，请输入正确的网址，url ---> {url}')

        return safe_url_string(url, self.encoding)

    def _quote_params(self, params):

        if params is None:
            return self.url

        params_str = parse.urlencode(params, encoding=self.encoding)
        return f'{self.url}&{params_str}' if '?' in self.url else f'{self.url}?{params_str}'

    def __str__(self):
        if self.help:
            return f"<{self.help} {self.method} {self.url}>"
        return f"<{self.method} {self.url}>"
