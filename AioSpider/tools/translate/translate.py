import re
from pathlib import Path

import requests
import pydash
from AioSpider.tools.translate.sign import get_sign


class BaiduTranslate:
    _token = None
    _sign = None
    _from_lan = None

    def __init__(self, query: str):
        session = requests.session()
        session.headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrom'
                          'e/110.0.0.0 Safari/537.36',
        }
        self.query = query
        self.session = session

    @property
    def token(self):
        if self._token is None:
            res = self.session.get("https://fanyi.baidu.com")
            token_match = re.search(r"token: '(.*?)',", res.text, re.S)
            self._token = token_match.group(1) if token_match else None
        return self._token

    @property
    def sign(self):
        if self._sign is None:
            self._sign = get_sign(self.query)
        return self._sign

    @property
    def lan_detect(self):
        if self._from_lan is None:
            url = "https://fanyi.baidu.com/langdetect"
            res = self.session.post(url, data={"query": self.query})
            self._from_lan = pydash.get(res.json(), 'lan', 'en')
        return self._from_lan

    def translate(self) -> str:
        from_lan = self.lan_detect
        to_lan = "zh" if from_lan != "zh" else "en"

        url = "https://fanyi.baidu.com/v2transapi"
        params = {"from": from_lan, "to": to_lan}
        data = {
            "from": from_lan, "to": to_lan, "query": self.query, "simple_means_flag": "3", "transtype": "realtime",
            "sign": self.sign, "token": self.token, "domain": "common"
        }

        attempts = 100
        while attempts:
            res = self.session.post(url, params=params, data=data)
            translation = pydash.get(res.json(), 'trans_result.data[0].dst', '')
            if translation:
                return translation
            else:
                attempts -= 1

        return ''
