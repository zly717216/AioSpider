import re as _re
import json
import time
import copy
import hashlib
import webbrowser
from urllib import parse
from pathlib import Path
from typing import Union, Any, Iterable, Callable, NoReturn, Optional
from datetime import datetime, timedelta, date

import numpy as np
from pandas import to_datetime, Timestamp

from lxml import etree
from AioSpider.utils_pkg import pydash


def mkdir(path: Union[Path, str]):
    """ 创建目录 """

    if path.exists():
        return

    if path.suffix:
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        path.mkdir(parents=True, exist_ok=True)


def str2num(string: str, multi: int = 1, force: bool = False, _type: Callable = int) -> Union[int, float, str]:
    """
        数值转化
        @params:
            string: 待转化字符串
            multi：倍乘系数
            force：是否强制转化，指定为True时，若无法转化则返回0
    """

    if not isinstance(string, str):
        return _type() if force else string

    string = _re.findall(r'([\d十百千万亿\.,%十百千万亿-]+)', string)

    if not string:
        return _type() if force else string

    string = string[0]
    string = string.replace(',', '')
    has_percent = '%' in string
    neg = '-' in string

    has_unit = False
    for i in '十百千万亿':
        if i in string:
            has_unit = True
            break

    num = _re.findall(r'([\d\.]+)', string)
    if not num:
        return _type() if force else string
    num = num[0]

    if num.isdigit():
        num = int(num)

    elif '.' in num and num.split('.')[0].isdigit() and num.split('.')[-1].isdigit():
        num = float(num)
    else:
        return _type() if force else string

    if has_unit:
        unit = _re.findall(r'([十百千万亿]+)', string)

        if '十' in unit:
            num = num * 10
        if '百' in unit:
            num = num * 100
        if '千' in unit:
            num = num * 1000
        if '万' in unit:
            num = num * 10000
        if '亿' in unit:
            num = num * 10000 * 10000

    num = num / 100 if has_percent else num
    num = -num if neg else num
    num = num * multi

    return _type(num) if force else num


def aio_eval(string: str, default: Any = None) -> Any:
    if isinstance(string, str):
        try:
            s = eval(string)
        except:
            s = default
    else:
        s = string

    return s


def get_hash(item: Any) -> str:
    """计算hash值"""

    if isinstance(item, str):
        return hashlib.md5(item.encode()).hexdigest()

    return hashlib.md5(str(item).encode()).hexdigest()


def get_sha1(item: Any) -> str:
    """计算sha1值"""

    if isinstance(item, str):
        return hashlib.sha1(item.encode()).hexdigest()

    return hashlib.sha1(str(item).encode()).hexdigest()


def get_sha256(item: Any) -> str:
    """计算sha256值"""

    if isinstance(item, str):
        return hashlib.sha256(item.encode()).hexdigest()

    return hashlib.sha256(str(item).encode()).hexdigest()


def filter_type(string: str) -> str:
    if 'null' in string:
        string = string.replace('null', 'None')

    if 'false' in string:
        string = string.replace('false', 'False')

    if 'true' in string:
        string = string.replace('true', 'True')

    return string


def parse_json(json_data: dict, index: str, default: Any = None) -> Any:
    if not isinstance(json_data, dict):
        try:
            json_data = dict(json_data)
        except:
            return default

    if not isinstance(index, str):
        try:
            json_data = str(json_data)
        except:
            return default

    data = pydash.get(json_data, index, default)
    if not data:
        return default
    return data


def load_json(string: str, default: Any = None) -> Union[dict, list]:
    if default is None:
        default = {}

    if string:
        try:
            return json.loads(string)
        except:
            pass

    return default


def type_converter(data: Any, to: Callable = None, force: bool = False) -> Any:
    if to is None or type(data) == to:
        return data

    if to is int:
        if not isinstance(data, (float, str)):
            return data if not force else to()

        if not (isinstance(data, str) and (
                data.isdigit() or ('.' in data and data.split('.')[0].isdigit() and data.split('.')[1].isdigit())
        )):
            return data if not force else to()

    if to is float:
        if not isinstance(data, (int, str)):
            return data if not force else to()

        if not (isinstance(data, str) and (
                data.isdigit() or ('.' in data and data.split('.')[0].isdigit() and data.split('.')[1].isdigit())
        )):
            return data if not force else to()

    if not data:
        return data if not force else to()

    return to(data)


class TimeConverter:
    """
    时间转换器：时间字符串、时间戳、日期时间对象相互转换
        >>> print(TimeConverter.strtime_to_stamp('2022/02/15 10:12:40'))
        >>> print(TimeConverter.stamp_to_strtime(1658220419111))
        >>> print(TimeConverter.strtime_to_time('2022/02/15 10:12:40'))
        >>> print(TimeConverter.stamp_to_time(1658220419111.222))
    """

    @classmethod
    def strtime_to_stamp(cls, str_time: str, millisecond: bool = False) -> int:
        """
        时间字符串转时间戳
        :param str_time: 时间字符串
        :param millisecond: 默认为Flase，返回类型为秒级时间戳；若指定为True，则返回毫秒级时间戳
        :return: 时间戳，默认为秒级
        """

        str_time = _re.sub('[年月日]', '-', str_time)
        dt = to_datetime(str_time)
        return dt.value // pow(10, 6) - 8 * 60 * 60 * 1000 if millisecond else dt.value // pow(10, 9) - 8 * 60 * 60

    @classmethod
    def stamp_to_strtime(self, time_stamp: Union[int, float, str], format='%Y-%m-%d %H:%M:%S') -> Optional[str]:
        """
        时间戳转时间字符串，支持秒级（10位）和毫秒级（13位）时间戳自动判断
        :param time_stamp: 时间戳 ex: 秒级：1658220419、1658220419.111222 毫秒级：1658220419111、1658220419111。222
        :param format: 时间字符串格式
        :return: 时间字符串, ex: 2022-07-19 16:46:59   东八区时间
        """

        if isinstance(time_stamp, str) and time_stamp.isdigit():
            time_stamp = float(time_stamp)

        if len(str(time_stamp).split('.')[0]) <= len(str(int(time.time()))):
            dt = to_datetime(time_stamp, unit='s', origin=Timestamp('1970-01-01 08:00:00'))
            return dt.to_pydatetime().strftime(format)

        elif len(str(time_stamp).split('.')[0]) <= len(str(int(time.time() * 1000))):
            dt = to_datetime(time_stamp, unit='ms', origin=Timestamp('1970-01-01 08:00:00'))
            return dt.to_pydatetime().strftime(format)

        else:
            return None

    @classmethod
    def strtime_to_time(self, str_time: str) -> datetime:
        """
        时间字符串转时间戳
        :param str_time: 时间字符串
        :return: 时间戳，默认为秒级
        """

        str_time = _re.sub('[年月日]', '-', str_time)
        return to_datetime(str_time).to_pydatetime()

    @classmethod
    def stamp_to_time(self, time_stamp: Union[int, float, str]) -> Optional[datetime]:
        """
        时间戳转时间字符串，支持秒级（10位）和毫秒级（13位）时间戳自动判断
        :param time_stamp: 时间戳 ex: 秒级：1658220419、1658220419.111222 毫秒级：1658220419111、1658220419111。222
        :return: 时间字符串, ex: 2022-07-19 16:46:59   东八区时间
        """

        if len(str(time_stamp).split('.')[0]) <= len(str(int(time.time()))):
            dt = to_datetime(time_stamp, unit='s', origin=Timestamp('1970-01-01 08:00:00'))
            return dt.to_pydatetime()

        elif len(str(time_stamp).split('.')[0]) <= len(str(int(time.time() * 1000))):
            dt = to_datetime(time_stamp, unit='ms', origin=Timestamp('1970-01-01 08:00:00'))
            return dt.to_pydatetime()

        else:
            return None


def strtime_to_stamp(str_time: str, millisecond: bool = False) -> int:
    """
    时间字符串转时间戳
    :param str_time: 时间字符串
    :param millisecond: 默认为Flase，返回类型为秒级时间戳；若指定为True，则返回毫秒级时间戳
    :return: 时间戳，默认为秒级
    """
    return TimeConverter.strtime_to_stamp(str_time, millisecond=millisecond)


def stamp_to_strtime(time_stamp: Union[int, float, str], format='%Y-%m-%d %H:%M:%S') -> Optional[str]:
    """
    时间戳转时间字符串，支持秒级（10位）和毫秒级（13位）时间戳自动判断
    :param time_stamp: 时间戳 ex: 秒级：1658220419、1658220419.111222 毫秒级：1658220419111、1658220419111。222
    :param format: 时间字符串格式
    :return: 时间字符串, ex: 2022-07-19 16:46:59   东八区时间
    """
    return TimeConverter.stamp_to_strtime(time_stamp, format=format)


def strtime_to_time(str_time: str) -> datetime:
    """
    时间字符串转时间戳
    :param str_time: 时间字符串
    :return: 时间戳，默认为秒级
    """
    return TimeConverter.strtime_to_time(str_time)


def stamp_to_time(time_stamp: Union[int, float, str]) -> Optional[datetime]:
    """
    时间戳转时间字符串，支持秒级（10位）和毫秒级（13位）时间戳自动判断
    :param time_stamp: 时间戳 ex: 秒级：1658220419、1658220419.111222 毫秒级：1658220419111、1658220419111。222
    :return: 时间字符串, ex: 2022-07-19 16:46:59   东八区时间
    """
    return TimeConverter.stamp_to_time(time_stamp)


def join(data: Iterable, on: str = '') -> str:
    """
    拼接字符串
    :param data: 可迭代对象，若data中的元素有非字符串类型的，会被强转
    :param on: 连接符
    :return: 拼接后的字符串
    """
    for i in data:
        if isinstance(i, str):
            continue
        i = str(i)
    return on.join(data)


def max(arry: Iterable, default: Union[int, float] = 0) -> Union[int, float]:
    """
    求最大值
    :param arry: 数组，如果传入可迭代对象，会强转成数组
    :param default: 默认值
    :return: np.max
    """

    try:
        arry = list(arry)
    except:
        return default

    if not arry:
        return default

    return np.array(arry).max()


def min(arry: Iterable, default: Union[int, float] = 0) -> Union[int, float]:
    """
    求最小值
    :param arry: 数组，如果传入可迭代对象，会强转成数组
    :param default: 默认值
    :return: np.min
    """

    try:
        arry = list(arry)
    except:
        return default

    if not arry:
        return default

    return np.array(arry).min()


def xpath(node: Union[str, etree._Element], q: str, default: Any = None) -> Union[list, etree._Element, str]:
    """
    xpath 提取数据
    :param node: 原始 html 文本数据
    :param q: xpath 解析式
    :param default: 默认值
    :return: default or Union[list, etree._Element, str]
    """

    try:
        if isinstance(node, str):
            return etree.HTML(node).xpath(q)
        elif isinstance(node, etree._Element):
            return node.xpath(q)
        else:
            return default
    except:
        return default


def xpath_text(node: Union[str, etree._Element], q: str, on: str = None, default: str = None) -> str:
    """
    xpath 提取文本数据
    :param node: 原始 html 文本数据
    :param q: xpath 解析式
    :param on: 连接符
    :param default: 默认值
    :return: str
    """

    if on is None:
        on = ''

    if default is None:
        default = ''

    text_list = xpath(node=node, q=q, default=default)

    if isinstance(text_list, list):
        return join(text_list, on) if text_list else default

    if isinstance(text_list, str):
        return text_list

    return default


def re(text: str, regx: str, default: Any = None) -> list:
    """
    正则 提取数据
    :param text: 原始文本数据
    :param regx: 正则表达式
    :param default: 默认值
    :return: default or list
    """

    if default is None:
        default = []

    t = _re.findall(regx, text)
    return t if t else default


def re_text(text: str, regx: str, default: Any = None) -> list:
    """
    正则 提取文本数据
    :param text: 原始文本数据
    :param regx: 正则表达式
    :param default: 默认值
    :return: default or list
    """

    if default is None:
        default = ''

    t = re(text=text, regx=regx, default=default)
    return t[0] if t else default


def extract_params(url: str) -> dict:
    """从 url 中提取参数"""

    params_query = parse.urlparse(url).query
    return {i[0]: i[-1] for i in parse.parse_qsl(params_query)}


def extract_url(url: str) -> str:
    """从url中提取接口"""

    url_parse = parse.urlparse(url)
    return f'{url_parse.scheme}://{url_parse.netloc}{url_parse.path}'


def open_html(url: str) -> NoReturn:
    webbrowser.open(url)


def deepcopy(item: Any) -> Any:
    return copy.deepcopy(item)


def before_day(
        now: Optional[datetime] = None, before: int = 0, is_date=False
) -> Union[datetime, date]:

    if now is None:
        now = datetime.now()

    if is_date:
        return (now - timedelta(days=before)).date()

    return now - timedelta(days=before)
