import re
import json
from typing import Optional, TypeVar, Union, Callable

from lxml import etree
from lxml.etree import _Element, _ElementUnicodeResult, _ElementStringResult
from bs4 import BeautifulSoup, ResultSet


_Parse = TypeVar("Parse")


class Parse:

    strip_list = []
    replace_dic = {'&quot;': '"'}

    def __init__(self, text: str = None, engine=None):
        if isinstance(text, (_ElementUnicodeResult, _ElementStringResult)):
            text = str()

        self._text = text
        self.engine = engine

    def __str__(self):
        return f'<{self.__class__.__name__}({self._text})>'

    def __getitem__(self, index):
        return self.__class__(self._text[index])

    def __len__(self):
        return len(self._text)

    __repr__ = __str__

    @property
    def text(self) -> str:
        if isinstance(self._text, list) and self._text:
            if isinstance(self._text[0], str):
                text = self._text[0]
            elif isinstance(self._text, ResultSet):
                text = self._text[0].contents[0]
            else:
                return ''
            for k, v in self.replace_dic.items():
                text = text.replace(k, v)
            return text
        elif isinstance(self._text, str):
            return self._text
        else:
            return ''

    @property
    def json(self) -> dict:
        try:
            return json.loads(self.strip_text())
        except json.decoder.JSONDecodeError:
            return {}

    def strip_text(self, strip: Optional[str] = None, callback: Callable[[str], str] = None) -> str:
        if strip is None:
            text = self.text.strip()
            for i in self.strip_list:
                text = text.strip(i)
            return callback(text) if callback is not None else text
        else:
            return self.text.strip(strip)

    def extract_first(self) -> Union[str, _Element]:
        if self.engine == 're':
            return self._text[0] if isinstance(self._text, list) else self._text
        elif self.engine == 'xpath':
            return (
                self._text[0] if self._text else None
            ) if isinstance(self._text, list) else (
                self._text[0] if isinstance(self._text, _Element) else _Element()
            )
        elif self.engine == 'css':
            return self._text[0] if isinstance(self._text, list) else _Element()
        else:
            return '' if self.engine is not None else _Element()

    def extract_last(self) -> Union[str, _Element]:
        if self.engine == 're':
            return self._text[-1] if isinstance(self._text, list) else self._text
        elif self.engine == 'xpath':
            return self._text[-1] if isinstance(self._text, list) else (
                self._text[-1] if isinstance(self._text, _Element) else _Element()
            )
        elif self.engine == 'css':
            return self._text[-1] if isinstance(self._text, list) else _Element()
        else:
            return '' if self.engine is not None else _Element()

    def extract(self) -> Union[str, list, _Element]:
        return self._text

    def re(self, query: str, flags: int = 0) -> _Parse:
        if not self._text:
            return self.__class__(engine='re')

        if isinstance(self._text, str):
            return self.__class__(re.findall(query, self._text, flags=flags), engine='re')

        if isinstance(self._text, list):
            arr = [re.findall(query, i, flags=flags) for i in self._text if isinstance(i, str)]
            return self.__class__([j for i in arr for j in i], engine='re')

        return self.__class__(self._text, engine='re')

    def xpath(self, query: str, **kwargs: dict) -> _Parse:
        if self._text is None:
            return self.__class__(engine='xpath')

        if isinstance(self._text, str):
            return self.__class__(etree.HTML(self._text).xpath(query, **kwargs), engine='xpath')

        if isinstance(self._text, _Element):
            return self.__class__(self._text.xpath(query, **kwargs), engine='xpath')

        if isinstance(self._text, list):
            x = [i.xpath(query, **kwargs) for i in self._text if isinstance(i, _Element)]
            return self.__class__([j for i in x for j in i], engine='xpath')

        return self.__class__(self._text, engine='xpath')

    def css(self, query: str, **kwargs: dict) -> _Parse:
        if self._text is None:
            return self.__class__(engine='css')

        if isinstance(self._text, str):
            return self.__class__(BeautifulSoup(self._text, 'html.parser').select(query), engine='css')

    @property
    def empty(self):
        return not bool(self._text)

    def remove_tags(self, tags: Union[str, list]):

        if isinstance(tags, str):
            tags = [tags]

        if isinstance(self._text, _Element):
            for tag in tags:
                element = self._text.xpath(f"//{tag}")
                for e in element:
                    parent = e.getparent()
                    if parent is not None:
                        parent.remove(e)

        if isinstance(self._text, list):
            for i in self._text:
                if not isinstance(i, _Element):
                    continue
                for tag in tags:
                    element = i.xpath(f"//{tag}")
                    for e in element:
                        parent = e.getparent()
                        if parent is not None:
                            parent.remove(e)

        return self

    def to_string(self, encoding='unicode', delete: Union[str, list] = '\n'):
        if self.engine == 'xpath':
            ele = self.extract_first()
            if ele is None:
                return ''
            txt = etree.tostring(ele, encoding=encoding)
            if isinstance(delete, str):
                delete = [delete]
            for i in delete:
                txt = txt.replace(i, '')
            return txt
        else:
            return ''
