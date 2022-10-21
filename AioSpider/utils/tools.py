import os
import re
import json
import time
import hashlib
from pathlib import Path
from typing import Union, Any, Iterable
from datetime import datetime

import pydash
import numpy as np
from pandas import to_datetime, Timestamp


def mkdir(path: Union[Path, str]):
    """ 创建目录 """

    if path.exists():
        return

    if path.suffix:
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        path.mkdir(parents=True, exist_ok=True)

def str2num(char: str, multi: int = 1, force: bool = False, _type=int) -> Union[int, float, str]:
    """
        数值转化
        @params:
            char: 待转化字符串
            multi：倍乘系数
            force：是否强制转化，指定为True时，若无法转化则返回0
    """

    if not isinstance(char, str):
        return _type() if force else char

    char = re.findall('([\d十百千万亿\.,%十百千万亿-]+)', char)
    
    if not char:
        return _type() if force else char
    
    char = char[0]
    char = char.replace(',', '')
    has_percent = '%' in char
    neg = '-' in char

    has_unit = False
    for i in '十百千万亿':
        if i in char:
            has_unit = True
            break

    num = re.findall('([\d\.]+)', char)
    if not num:
        return _type() if force else char
    num = num[0]
    
    if num.isdigit():
        num = int(num)

    elif '.' in num and num.split('.')[0].isdigit() and num.split('.')[-1].isdigit():
        num = float(num)
    else:
        return _type() if force else char
    
    if has_unit:
        unit = re.findall('([十百千万亿]+)', char)
        for i in unit:
            if '十' in char:
                num = num * 10
            if '百' in char:
                num = num * 100
            if '千' in char:
                num = num * 1000
            if '万' in char:
                num = num * 10000
            if '亿' in char:
                num = num * 10000 * 10000
                
    num = num / 100 if has_percent else num
    num = -num if neg else num
    num = num * multi

    return _type(num) if force else num


def aio_eval(string: str,  default: Any = None, force: bool = False) -> Any:

    if isinstance(string, str):
        try:
            s = eval(string)
        except:
            s = default
    else:
        s = string

    if force:
        return s if s else default

    return s


def get_hash(item: Any) -> str:
    """计算hash值"""

    if isinstance(item, str):
        return hashlib.md5(item.encode()).hexdigest()

    return hashlib.md5(str(item).encode()).hexdigest()


def filter_type(string: str) -> str:

    if 'null' in string:
        string = string.replace('null', 'None')

    if 'false' in string:
        string = string.replace('false', 'False')

    if 'true' in string:
        string = string.replace('true', 'True')

    return string


def parse_json(json_data: dict, index: str, default=None) -> str:

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

    return pydash.get(json_data, index, default)


def load_json(data: str, default=None) -> Union[dict, list]:

    if default is None:
        default = {}

    if data:
        return json.loads(data)

    return default


def type_converter(data, to=None, force=False):

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

        str_time = re.sub('[年月日]', '-', str_time)
        dt = to_datetime(str_time)
        return dt.value // pow(10, 6) - 8 * 60 * 60 * 1000 if millisecond else dt.value // pow(10, 9) - 8 * 60 * 60

    @classmethod
    def stamp_to_strtime(self, time_stamp: Union[int, float, str], format='%Y-%m-%d %H:%M:%S') -> Union[str, None]:
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
    def strtime_to_time(self, str_time: str) -> str:
        """
        时间字符串转时间戳
        :param str_time: 时间字符串
        :return: 时间戳，默认为秒级
        """

        str_time = re.sub('[年月日]', '-', str_time)
        return to_datetime(str_time).to_pydatetime()

    @classmethod
    def stamp_to_time(self, time_stamp: Union[int, float]) -> Union[datetime, None]:
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


def max(arry: Iterable, default=0):
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


def min(arry: Iterable, default=0):
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
