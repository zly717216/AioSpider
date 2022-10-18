import re
import json
from typing import Any, Optional, TypeVar

from lxml.etree import _Element, _ElementUnicodeResult, _ElementStringResult


_Parse = TypeVar("Parse")


class Parse:
    
    def __init__(self, arr, default=None):
        self.arr = arr
        self.default = default

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.arr})>'

    def __str__(self):
        return f'<{self.__class__.__name__}({self.arr})>'

    def __getitem__(self, index):
        return Parse(self.arr[index], self.default)
    
    @property
    def text(self) -> str:
        return self.extract_first(text=True)

    @property
    def json(self) -> dict:
        return json.loads(self.text)
    
    def strip_text(self, strip: Optional[str] = None) -> str:
        if strip is None:
            return self.text.strip()
        return self.text.strip(strip)
    
    def _check_text(self, default):
        if self.arr:
            return str(self.arr[0])
        elif default != '':
            return default
        elif self.default is not None:
            return self.default
        else:
            return default
    
    def extract_first(self, default: Any = '', text: bool = False) -> _Parse:
        
        if text:
            return self._check_text(default=default)
        elif self.arr:
            return Parse(self.arr[0], self.default)
        elif default != '':
            return Parse(default, self.default)
        elif self.default is not None:
            return Parse(self.default, self.default)
        else:
            return Parse(default, self.default)
        
    def extract_last(self, default: Any = '', text: bool = False) -> _Parse:
        
        if text:
            return self._check_text(default=default)
        elif self.arr:
            return Parse(self.arr[-1], self.default)
        elif default != '':
            return Parse(default, self.default)
        elif self.default is not None:
            return Parse(self.default, self.default)
        else:
            return Parse(default, self.default)

    def extract(self) -> Any:
        return self.arr

    def re(self, query: str, **kwargs: dict) -> _Parse:
        
        if isinstance(self.arr, (list, tuple)) and self.arr and isinstance(self.arr[0], str):
            return self.extract_first().re(query, **kwargs)
        elif isinstance(self.arr, (_ElementUnicodeResult, _ElementStringResult, str)):
            self.arr = str(self.arr)
            return Parse(re.findall(query, self.arr, **kwargs), self.default)
        else:
            raise TypeError(
                f'对象类型错误，链式调用re的 Parse 的 arr 属性必须为 str、_ElementUnicodeResult、_ElementStringResult 或 '
                f'列表嵌套 str 类型，当前类型为 {type(self.arr).__name__} 类型，Parse.arr ---> {self.arr}'
            )
    
    def xpath(self, query: str, **kwargs: dict) -> _Parse:
        
        if isinstance(self.arr, (list, tuple)) and self.arr and isinstance(self.arr[0], _Element):
            return self.extract_first().xpath(query, **kwargs)
        elif isinstance(self.arr, _Element):
            return Parse(self.arr.xpath(query, **kwargs), self.default)
        else:
            raise TypeError(
                f'对象类型错误，链式调用xpath的 Parse 的 arr 属性必须为xpath节点（_Element 类型或列表嵌套 _Element 类型），'
                f'当前类型为 {type(self.arr).__name__} 类型，Parse.arr ---> {self.arr}'
            )

    @property
    def empty(self):
        
        if isinstance(self.arr, list) and not self.arr:
            return True
        
        if isinstance(self.arr, str) and not self.arr:
            return True
        
        return False


class ReParse:

    def __init__(self, arr, default=None):
        self.arr = Parse(arr, default)

    def extract_first(self, default: Any = '', text: bool = False) -> Parse:
        return self.arr.extract_first(default=default, text=text)

    def extract_last(self, default: Any = '', text: bool = False) -> Parse:
        return self.arr.extract_last(default=default, text=text)

    def extract(self) -> Any:
        return self.arr.extract()
    
    def xpath(self, query: str, **kwargs: dict) -> Parse:
        return self.arr.xpath(query, **kwargs)

    def re(self, query: str, **kwargs: dict) -> Parse:
        return self.arr.re(query=query, kwargs=kwargs)
    
    @property
    def text(self) -> str:
        return self.arr.text

    @property
    def json(self) -> dict:
        return self.arr.json

    @property
    def empty(self):
        return self.arr.empty
    
    def strip_text(self, strip: Optional[str] = None) -> str:
        return self.arr.strip_text(strip)
    
    
class XpathParse:

    def __init__(self, arr, default=None):
        self.arr = Parse(arr, default)
        
    def __getitem__(self, index):
        return self.arr[index]

    def extract_first(self, default: Any = '', text: bool = False) -> Parse:
        return self.arr.extract_first(default=default, text=text)

    def extract_last(self, default: Any = '', text: bool = False) -> Parse:
        return self.arr.extract_last(default=default, text=text)

    def extract(self) -> Any:
        return self.arr.extract()
    
    def xpath(self, query: str, **kwargs: dict) -> Parse:
        return self.arr.xpath(query, **kwargs)
    
    def re(self, query: str, **kwargs: dict) -> Parse:
        return self.arr.re(query, **kwargs)
    
    @property
    def text(self) -> str:
        return self.arr.text

    @property
    def json(self) -> dict:
        return self.arr.json

    @property
    def empty(self):
        return self.arr.empty
    
    def strip_text(self, strip: Optional[str] = None) -> str:
        return self.arr.strip_text(strip)
