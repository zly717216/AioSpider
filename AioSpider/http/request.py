from w3lib.url import safe_url_string


class Request(object):
    """ 实现请求方法 """

    def __init__(
            self, url, method='GET', callback=None, params=None, headers=None, encoding='utf-8',
            data=None, timeout=0, proxy=None, priority=1, meta=None, *args, **kwargs
        ):

        self.encoding = encoding
        self.url = self._set_url(url)
        self.method = method.upper()
        self.params = params or {}
        self.callback = callback

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
        self.meta = meta or {}
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
        # safe_url_string 返回一个安全的网址
        self.url = safe_url_string(url, self.encoding)

        return self.url

    def __str__(self):
        return f"<{self.method} {self.url}>"
