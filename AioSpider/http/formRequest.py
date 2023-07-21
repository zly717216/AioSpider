import json
from typing import Union

from AioSpider.http.base import BaseRequest


class FormRequest(BaseRequest):

    def __init__(self, url: str, body: Union[dict, str] = None, data: Union[dict, str] = None, **kwargs):

        if isinstance(body, dict):
            data = json.dumps(body) if isinstance(body, dict) else body

        super(FormRequest, self).__init__(url=url, method='POST', data=data,  **kwargs)
