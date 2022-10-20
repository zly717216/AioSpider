import json

from w3lib.url import safe_url_string
from .request import Request


class FormRequest(Request):
    """ 实现请求方法 """

    def __init__(
            self, url, callback=None, params=None, headers=None, encoding='utf-8',
            data=None, body=None, cookies=None, timeout=0, proxy=None, priority=1,
            dnt_filter=False, *args, **kwargs
        ):

        if body:
            data = json.dumps(body) if isinstance(body, dict) else body

        super(FormRequest, self).__init__(
            url=url, method='POST', callback=callback, params=params, headers=headers,
            encoding=encoding, data=data, cookies=cookies, timeout=timeout, proxy=proxy,
            priority=priority, dnt_filter=dnt_filter, *args, **kwargs
        )
