import numbers
import os
import copy
import json
import math
import time
import uuid
import base64
import hashlib
import binascii
import re as _re
import webbrowser
import unicodedata
import subprocess
from urllib import parse
from pathlib import Path
from datetime import datetime, timedelta, date, time as dtime
from typing import Union, Any, Iterable, Callable, Optional, NoReturn, List

import rsa
import numpy as np
from pypinyin import lazy_pinyin
import pydash
import execjs
from lxml import etree
from lxml.html.clean import Cleaner
from Crypto.Cipher import AES
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

from AioSpider import constants
from AioSpider.tools.translate import BaiduTranslate


# ------------------ 文件目录处理 ------------------ #

def mkdir(path: Union[Path, str], auto: bool = True) -> NoReturn:
    """
    创建目录
    Args:
        path: 文件夹路径
        auto: 自动判断 path 参数是文件还是文件夹子，默认为 True。当 auto 为 True 时，会自动判断 path 路径参数是否有文件
            后缀（如：.txt、.csv等），如果有则创建父级文件夹，如果没有则创建当前路径文件夹；当 auto 为 False 时，
            会已当前路径作为文件夹创建
    Return:
        NoReturn
    """

    path = Path(path) if isinstance(path, str) else path

    if path.exists():
        return

    target_path = path.parent if auto and path.suffix else path
    target_path.mkdir(parents=True, exist_ok=True)


# ------------------ 文件目录处理 ------------------ #


# -------------------- 时间处理 -------------------- #

class TimeConverter:
    """
    时间转换器：时间字符串、时间戳、日期时间对象相互转换
        >>> print(TimeConverter.strtime_to_stamp('2022/02/15 10:12:40'))
        >>> print(TimeConverter.stamp_to_strtime(1658220419111))
        >>> print(TimeConverter.strtime_to_time('2022/02/15 10:12:40'))
        >>> print(TimeConverter.stamp_to_time(1658220419111.222))
    """

    DATE_FORMATS = [
        "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
        "%Y%m%d %H:%M:%S.%f", "%Y%m%d %H:%M:%S", "%Y%m%d %H:%M", "%Y%m%d",
        '%H:%M:%S.%f', '%H:%M:%S'
    ]

    @classmethod
    def _find_matching_format(cls, str_time: str) -> Optional[str]:
        for fmt in cls.DATE_FORMATS:
            try:
                datetime.strptime(str_time, fmt)
                return fmt
            except ValueError:
                continue
        return None

    @classmethod
    def _to_datetime(cls, str_time: str, format: str = None) -> Optional[datetime]:

        if not str_time or not isinstance(str_time, str):
            return None

        str_time = str_time.strip()

        if format is not None:
            return datetime.strptime(str_time, format)

        str_time = _re.sub('[年月/]', '-', str_time)
        str_time = _re.sub('[日]', '', str_time)

        matching_format = cls._find_matching_format(str_time)
        return datetime.strptime(str_time, matching_format) if matching_format else None

    @classmethod
    def strtime_to_stamp(cls, str_time: str, format: str = None, millisecond: bool = False) -> Optional[int]:
        """
        时间字符串转时间戳
        Args:
            str_time: 时间字符串
            format: 时间字符串格式
            millisecond: 默认为Flase，返回类型为秒级时间戳；若指定为True，则返回毫秒级时间戳
        Return:
            时间戳，默认为秒级
        """
        dt = cls._to_datetime(str_time, format)
        return int(dt.timestamp() * 1000) if dt and millisecond else int(dt.timestamp())

    @classmethod
    def stamp_to_strtime(cls, time_stamp: Union[int, float, str], format='%Y-%m-%d %H:%M:%S') -> Optional[str]:
        """
        时间戳转时间字符串，支持秒级（10位）和毫秒级（13位）时间戳自动判断
        Args:
            time_stamp: 时间戳 ex: 秒级：1658220419、1658220419.111222 毫秒级：1658220419111、1658220419111。222
            format: 时间字符串格式
        Return:
            时间字符串, ex: 2022-07-19 16:46:59   东八区时间
        """

        if time_stamp is None or not isinstance(str_time, (int, float, str)):
            return None

        if isinstance(time_stamp, str) and time_stamp.isdigit():
            time_stamp = float(time_stamp)

        if len(str(time_stamp).split('.')[0]) <= len(str(int(time.time()))):
            return time.strftime(format, time.localtime(time_stamp))
        elif len(str(time_stamp).split('.')[0]) <= len(str(int(time.time() * 1000))):
            return time.strftime(format, time.localtime(time_stamp / 1000))
        else:
            return None

    @classmethod
    def strtime_to_time(
            cls, str_time: str, format: str = None, is_date: bool = False, is_time: bool = False
    ) -> Union[datetime, date, dtime, None]:
        """
        时间字符串转日期时间类型
        Args:
            str_time: 时间字符串
            format: 时间格式化字符串
            is_date: 是否返回日期，默认返回日期时间
        Return:
            日期时间
        """
        dt = cls._to_datetime(str_time, format)
        if not dt:
            return dt
        elif is_date:
            return dt.date()
        elif is_time:
            return dt.time()
        else:
            return dt

    @classmethod
    def stamp_to_time(
            cls, time_stamp: Union[int, float, str], tz: str = None, is_date: bool = False, zone: str = '+8:00'
    ) -> Union[datetime, date, None]:
        """
        时间戳转时间字符串，支持秒级（10位）和毫秒级（13位）时间戳自动判断
        Args:
            time_stamp: 时间戳 ex: 秒级：1658220419、1658220419.111222 毫秒级：1658220419111、1658220419111。222
            tz: 时区，默认为中国标准时
            is_date: 是否返回日期，默认返回日期时间
            zone: 时区
        Return:
            日期时间对象
        """

        if time_stamp is None or not isinstance(time_stamp, (int, float, str)):
            return None

        if isinstance(time_stamp, str):
            time_stamp = float(time_stamp)

        if len(str(time_stamp).split('.')[0]) <= len(str(int(time.time()))):
            dt = datetime(1970, 1, 1) + timedelta(seconds=time_stamp)
        elif len(str(time_stamp).split('.')[0]) <= len(str(int(time.time() * 1000))):
            dt = datetime(1970, 1, 1) + timedelta(milliseconds=time_stamp)
        else:
            return None

        dt += timedelta(hours=int(zone.split(':')[0]))
        return dt.date() if is_date else dt

    @classmethod
    def time_to_stamp(cls, time: Union[datetime, date], millisecond: bool = False) -> int:
        """
        时间序列转时间戳，支持秒级和毫秒级时间戳自动判断
        Args:
            time: 时间序列
            millisecond: 是否返回毫秒级时间戳
        Return:
            时间戳
        """
        
        if not isinstance(time, (datetime, date)):
            return None

        if isinstance(time, date):
            time = datetime(time.year, time.month, time.day)

        return int(time.timestamp() * 1000) if millisecond else int(time.timestamp())


def strtime_to_stamp(str_time: str, format: str = None, millisecond: bool = False) -> Optional[int]:
    """
    时间字符串转时间戳
    Args:
        str_time: 时间字符串
        format: 时间字符串格式
        millisecond: 默认为Flase，返回类型为秒级时间戳；若指定为True，则返回毫秒级时间戳
    Return:
        时间戳，默认为秒级
    """
    return TimeConverter.strtime_to_stamp(str_time, format=format, millisecond=millisecond)


def stamp_to_strtime(time_stamp: Union[int, float, str], format='%Y-%m-%d %H:%M:%S') -> Optional[str]:
    """
    时间戳转时间字符串，支持秒级（10位）和毫秒级（13位）时间戳自动判断
    Args:
        time_stamp: 时间戳 ex: 秒级：1658220419、1658220419.111222 毫秒级：1658220419111、1658220419111。222
        format: 时间字符串格式
    Return:
        时间戳，时间字符串, ex: 2022-07-19 16:46:59   东八区时间
    """
    return TimeConverter.stamp_to_strtime(time_stamp, format=format)


def strtime_to_time(
        str_time: str, format: str = None, is_date: bool = False, is_time: bool = False
) -> Union[datetime, date, dtime, None]:
    """
    时间字符串转日期时间类型
    Args:
        str_time: 时间字符串
        format: 时间格式化字符串
        is_date: 是否返回日期类型，默认为 False
    Return:
        日期时间
    """
    return TimeConverter.strtime_to_time(str_time, format=format, is_date=is_date, is_time=is_time)


def stamp_to_time(
        time_stamp: Union[int, float, str], is_date: bool = False, zone: str = '+8:00'
) -> Union[datetime, date, None]:
    """
    时间戳转时间字符串，支持秒级（10位）和毫秒级（13位）时间戳自动判断
    Args:
        time_stamp: 时间戳 ex: 秒级：1658220419、1658220419.111222 毫秒级：1658220419111、1658220419111。222
        is_date: 是否返回日期类型，默认为 False
        zone: 时区
    Return:
        日期时间对象, ex: 2022-07-19 16:46:59
    """
    return TimeConverter.stamp_to_time(time_stamp, is_date=is_date)


def time_to_stamp(time: Union[datetime, date], millisecond: bool = False) -> int:
    """
    时间序列转时间戳，支持秒级和毫秒级时间戳自动判断
    Args:
        time: 时间序列
        millisecond: 是否返回毫秒级时间戳
    Return:
        时间戳
    """

    return TimeConverter.time_to_stamp(time, millisecond=millisecond)


def before_day(
        now: Optional[datetime] = None, before: int = 0, is_date: bool = False, is_str: bool = False
) -> Union[datetime, date, str]:
    """
    获取时间间隔
    Args:
        now: 时间，默认为 None，表示当前时间
        before: 时间，默认为 None，表示今天，-1 为昨天，1 为明天
        is_date: 是否返回日期对象
    Return:
        时间对象
    """

    if now is None:
        now = datetime.now()
    
    dt = now - timedelta(days=before)
    
    if is_date:
        dt = dt.date()
    
    if is_str:
        dt = str(dt)
    
    return dt


def make_timestamp(millisecond: bool = True, to_string: bool = False) -> Union[int, str]:
    """
    获取时间戳
    Args:
        millisecond: 是否获取毫秒时间戳
        to_string: 结果是否返回字符串类型
    Return:
        时间戳，返回类型和输入参数有关系
    """

    if to_string:
        return str(int(time.time() * 1000) if millisecond else int(time.time()))

    return int(time.time() * 1000) if millisecond else int(time.time())


def get_quarter_end_dates(start_year: int, end_year: int) -> List[str]:
    """
    获取区间内每个季度的最后一天
    Args:
        start_year: 开始年份
        end_year: 结束年份
    Rerutn:
        返回季度最后一天日期列表
    """
    
    return [
        str(date(year, month, day))
        for year in range(start_year, end_year + 1)
        for quarter, (month, day) in {
            1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)
        }.items()
    ]


def get_next_month_same_day(current_date: Union[str, datetime], is_date=False) -> Union[date, datetime]:

    if isinstance(current_date, str):
        current_date = strtime_to_time(current_date)

    year = current_date.year
    month = current_date.month
    day = current_date.day
    time = current_date.time()

    if month == 12:
        next_month = 1
        year += 1
    else:
        next_month = month + 1

    days_in_next_month = 31 if next_month in [1, 3, 5, 7, 8, 10, 12] else (
        30 if next_month != 2 else 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
    )

    day = min([day, days_in_next_month])

    return date(year, next_month, day) if is_date else datetime(
        year, next_month, day, time.hour, time.minute, time.second
    )


# -------------------- 时间处理 -------------------- #


# ------------------- 字符串处理 ------------------- #

def str2num(string: str, multi: int = 1, force: bool = False, _type: Callable = int) -> Union[int, float, str]:
    """
    数值转化
    Args:
        string: 待转化字符串
        multi: 倍乘系数
        force: 是否强制转化，指定为True时，若无法转化则返回0
        _type: 转换类型
    Return:
        转换后的数字类型，int | float | str
    """

    if string is None or not isinstance(string, (int, float, str, numbers.Number)):
        return (_type() * multi) if force else string

    if isinstance(string, (int, float, numbers.Number)):
        return _type(string * multi)

    string = _re.findall(r'([\d十百千万亿\.,%十百千万亿-]+)', string)

    if not string:
        return (_type() * multi) if force else string

    string = string[0].replace(',', '')
    has_percent = '%' in string
    neg = '-' in string

    units = {'十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}

    num = _re.findall(r'([\d\.]+)', string)
    if not num:
        return (_type() * multi) if force else string

    num = num[0]

    if num.isdigit():
        num = int(num)
    elif '.' in num and num.split('.')[0].isdigit() and num.split('.')[-1].isdigit():
        num = float(num)
    else:
        return (_type() * multi) if force else string

    for unit, multiplier in units.items():
        if unit in string:
            num *= multiplier

    num = num / 100 if has_percent else num
    num = -num if neg else num
    num = num * multi

    return _type(num) if force else num


def aio_eval(string: str, default: Any = None) -> Any:
    """
    执行字符串
    Args:
        string: 字符串
        default: 默认值
    Return:
        字符串执行结果 Any
    """
    if not isinstance(string, str):
        return string

    try:
        return eval(string)
    except Exception:
        return default


def make_md5(item: Any) -> str:
    """
    计算md5值
    Args:
        item: md5 待计算值
    Return:
        哈希值 Any
    """

    if isinstance(item, str):
        return hashlib.md5(item.encode('utf-8', 'ignore')).hexdigest()
    
    if isinstance(item, bytes):
        return hashlib.md5(item).hexdigest()

    return hashlib.md5(str(item).encode()).hexdigest()


def make_sha1(item: Any) -> str:
    """
    计算sha1值
    Args:
        item: hash 待计算值
    Return:
        sha1值 Any
    """

    if isinstance(item, str):
        return hashlib.sha1(item.encode()).hexdigest()
    
    if isinstance(item, bytes):
        return hashlib.sha1(item).hexdigest()

    return hashlib.sha1(str(item).encode()).hexdigest()


def make_sha256(item: Any) -> str:
    """
    计算sha256值
    Args:
        item: hash 待计算值
    Return:
        sha256值 Any
    """

    if isinstance(item, str):
        return hashlib.sha256(item.encode()).hexdigest()
    
    if isinstance(item, bytes):
        return hashlib.sha256(item).hexdigest()

    return hashlib.sha256(str(item).encode()).hexdigest()


def filter_type(string: str) -> str:
    """
    将 js 中的 null、false、true、对象和数组过滤并转换成 python 对应的数据类型
    Args:
        string: 代转字符串
    Return:
        过滤后新的字符串
    """

    if 'null' in string:
        string = string.replace('null', 'None')

    if 'false' in string:
        string = string.replace('false', 'False')

    if 'true' in string:
        string = string.replace('true', 'True')

    # 将 JavaScript 对象转换为 Python 字典
    string = re.sub(r'\{(.+?)\}', r'dict(\1)', string)

    # 将 JavaScript 数组转换为 Python 列表
    string = re.sub(r'\[(.+?)\]', r'list(\1)', string)

    return string


def join(data: Iterable, on: str = '') -> str:
    """
    拼接字符串
    Args:
        data: 可迭代对象，若data中的元素有非字符串类型的，会被强转
        on: 连接符
    Return:
        拼接后的字符串
    """

    if not isinstance(data, list):
        data = list(data)

    for index, value in enumerate(data):
        if isinstance(value, str):
            continue
        data[index] = str(value)

    return on.join(data)


def execute_js(path: Union[str, Path], func: str, encoding: str = 'utf-8') -> Any:
    """
    执行 js 文件
    Args:
        path: js 文件路径
        func: 需要调用的js方法
        encoding: 文件编码
    Return:
        执行结果 Any
    """

    if isinstance(path, str):
        path = Path(path)

    if not path.exists():
        return None

    if not path.is_file():
        return None

    ctx = execjs.compile(path.read_text(encoding=encoding))
    return ctx.call(func)


def translate(query):
    """翻译"""
    return BaiduTranslate(query).translate()


def is_chinese(string: str) -> bool:
    """判断字符串是否是中文"""

    if not isinstance(string, str):
        return False

    return bool(re.search(r'[\u4e00-\u9fff]+', string))


# ------------------- 字符串处理 ------------------- #


# -------------------- 数值处理 -------------------- #

def max(arry: Iterable, default: Union[int, float] = 0) -> Union[int, float]:
    """
    求最大值
    Args:
        arry: 数组，如果传入可迭代对象，会强转成数组
        default: 默认值
    Return:
        序列的最大值
    """

    if not isinstance(arry, Iterable):
        return default

    try:
        arry = list(arry)
    except TypeError:
        return default

    if not arry:
        return default

    return np.max(arry)


def min(arry: Iterable, default: Union[int, float] = 0) -> Union[int, float]:
    """
    求最小值
    Args:
        arry: 数组，如果传入可迭代对象，会强转成数组
        default: 默认值
    Return:
        序列的最小值
    """

    if not isinstance(arry, Iterable):
        return default

    try:
        arry = list(arry)
    except:
        return default

    if not arry:
        return default

    return np.min(arry)


def round_up(item: Union[float, int, str]) -> Union[int, float]:
    """
    向上取整
    Args:
        item: 待取整数据
    Return:
        取整数据后的数据
    """

    if isinstance(item, str):
        item = type_converter(item, to=float, force=True)

    return math.ceil(item)

# -------------------- 数值处理 -------------------- #


# -------------------- HTML 网页结构处理 -------------------- #

def clean_html(html: str, remove_tags: Iterable = None, safe_attrs: Iterable = None) -> str:
    """
    清晰 html 文本
    Args:
        html: html 文本
        remove_tags: 移除 html 中不需要的标签，如：['a', 'p', 'img']
        safe_attrs: 保留相关属性，如：['src', 'href']
    Return:
        清晰后的html文本
    """

    if not html:
        return ''

    # 保存新闻的时候，很多属性不需要保存，不然会占用硬盘资源，所以只保留图片标签的src属性就行
    if remove_tags is None:
        remove_tags = []

    if safe_attrs is None:
        safe_attrs = []

    remove_tags = frozenset(remove_tags)
    safe_attrs = frozenset(safe_attrs)

    cleaner = Cleaner(safe_attrs=safe_attrs, remove_tags=remove_tags)
    return cleaner.clean_html(html)


def xpath(node: Union[str, etree._Element], query: str, default: Any = None) -> Union[list, etree._Element, str]:
    """
    xpath 提取数据
    Args:
        node: 原始 html 文本数据
        query: xpath 解析式
        default: 默认值
    Return:
        default or Union[list, etree._Element, str]
    """

    if not isinstance(node, (str, etree._Element)) or not isinstance(query, str):
        return default

    try:
        if isinstance(node, str):
            parsed_node = etree.HTML(node)
        else:
            parsed_node = node
        return parsed_node.xpath(query)
    except:
        return default


def xpath_text(node: Union[str, etree._Element], query: str, on: str = None, default: str = None) -> str:
    """
    xpath 提取文本数据
    Args:
        node: 原始 html 文本数据
        query: xpath 解析式
        on: 连接符
        default: 默认值
    Return:
        xpath 提取出来的文本
    """

    if on is None:
        on = ''

    if default is None:
        default = ''

    text_list = xpath(node=node, query=query, default=default)

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


def re_match(text: str, regx: str) -> bool:
    """
    正则匹配
    Args:
        text: 原始文本数据
        regx: 正则表达式
    Return: 
        bool
    """

    return bool(_re.match(regx, text))


def re_text(text: str, regx: str, default: Any = None) -> str:
    """
    正则 提取文本数据
    Args:
        text: 原始文本数据
        regx: 正则表达式
        default: 默认值
    Return:
        default or list
    """

    if default is None:
        default = ''

    t = re(text=text, regx=regx, default=default)
    return t[0] if t else default


def re_sub(text: str, regx: str, replace: str) -> str:
    """
    正则 提取文本数据
    Args:
        text: 原始文本数据
        regx: 正则表达式
        replace: 替换值
    Return:
        返回被替换后的字符串
    """
    return _re.sub(regx, replace, text)

# -------------------- HTML 网页结构处理 -------------------- #


# ------------------ 加解密工具集 ------------------ #

class AESCryptor:
    """
    AES 加密
    Args:
        key: 秘钥
        明文	需要加密的参数; 数据类型为bytes
        mode: 加密模式，可选值有两个：ECB、CBC
        padding: 填充方式，可选值有三个：NoPadding、ZeroPadding、PKCS7Padding
        encoding: 编码格式，默认为 utf-8

    使用示例：
    >>> aes = AESCryptor(
    >>>     key='yg5qV3fSqSuDzzSd', mode=AES.MODE_ECB, padding=constants.PaddingMode.PKCS7Padding
    >>> )
    >>> enc_str = '{"x":114.7,"y":5}'
    >>> rData = aes.encrypt(enc_str)
    >>> print("密文：", rData.to_base64())
    >>> dec_data = aes.decrypt(rData)
    >>> print("明文：", dec_data)
    """

    class MetaData:

        def __init__(self, data: bytes = None, encoding: str = 'utf-8'):
            if data is None:
                data = bytes()

            self.data = data
            self.encoding = encoding

        def to_string(self):
            return self.data.decode(self.encoding)

        def to_base64(self):
            return base64.b64encode(self.data).decode()

        def to_hex(self):
            return binascii.b2a_hex(self.data).decode()

        def __str__(self):
            return self.to_string()

    def __init__(
            self, key: str, mode: int, iv: str = None, padding: int = 0,
            encoding: str = "utf-8"
    ):

        key = key.encode() if isinstance(key, str) else key
        iv = iv.encode() if isinstance(iv, str) else iv

        if mode in (AES.MODE_CBC, AES.MODE_ECB):
            if iv is not None:
                self.aes = AES.new(key, mode, iv)
            else:
                self.aes = AES.new(key, mode)
        else:
            raise ValueError(f"不支持这种模式: {mode}")

        self.encoding = encoding
        self.padding = padding

    @staticmethod
    def set_zero_padding(data):
        data += b'\x00'
        while len(data) % 16 != 0:
            data += b'\x00'
        return data

    @staticmethod
    def set_pkcs7_padding(data):
        size = 16 - len(data) % 16
        if size == 0:
            size = 16
        return data + size.to_bytes(1, 'little') * size

    @staticmethod
    def strip_zero_padding(data):
        data = data[:-1]
        while len(data) % 16 != 0:
            data = data.rstrip(b'\x00')
            if data[-1] != b"\x00":
                break
        return data

    @staticmethod
    def strip_pkcs7_padding(data):
        size = data[-1]
        return data.rstrip(size.to_bytes(1, 'little'))

    def set_padding(self, data):
        if self.padding == constants.PaddingMode.NoPadding:
            if len(data) % 16 == 0:
                return data
            else:
                return self.set_zero_padding(data)
        elif self.padding == constants.PaddingMode.ZeroPadding:
            return self.set_zero_padding(data)
        elif self.padding == constants.PaddingMode.PKCS7Padding:
            return self.set_pkcs7_padding(data)
        else:
            raise Exception("不支持Padding")

    def strip_padding(self, data):
        if self.padding == constants.PaddingMode.NoPadding:
            return self.strip_zero_padding(data)
        elif self.padding == constants.PaddingMode.ZeroPadding:
            return self.strip_zero_padding(data)
        elif self.padding == constants.PaddingMode.PKCS7Padding:
            return self.strip_pkcs7_padding(data)
        else:
            raise Exception("不支持Padding")

    def encrypt(self, data: Union[str, bytes, dict]) -> MetaData:

        if isinstance(data, dict):
            data = json.dumps(data, separators=(',', ':'))

        if isinstance(data, str):
            data = data.encode(self.encoding)

        enc_data = self.aes.encrypt(self.set_padding(data))
        return self.MetaData(enc_data)

    def decrypt(self, data: Union[MetaData, bytes]) -> str:

        if isinstance(data, self.MetaData):
            data = data.data

        decrypt_data = self.strip_padding(self.aes.decrypt(data))
        return decrypt_data.decode(self.encoding)


class RSACryptor:
    """
    RSA 加密
    Args:
        public_key: 公钥
        mode: 模长

    使用示例：
    >>> rsa = RSACryptor(
    >>>     public_key = 'd3bcef1f00424f3261c89323fa8cdfa12bbac400d9fe8bb627e8d27a44bd5d59dce559135d678a8143beb5b8d‘
    >>>                  ’7056c4e1f89c4e1f152470625b7b41944a97f02da6f605a49a93ec6eb9cbaf2e7ac2b26a354ce69eb265953d2‘
    >>>                  ’c29e395d6d8c1cdb688978551aa0f7521f290035fad381178da0bea8f9e6adce39020f513133fb‘, 
    >>>     mode=AES.MODE_ECB
    >>> )
    >>> enc_str = rsa.to_hen('123456')       # 返回16进制密文
    >>> enc_str = rsa.to_base64('123456')    # 返回base64密文
    """
    
    def __init__(self, public_key: str, mode: str):
        self.public_key = public_key
        self.mode = mode

    def encrypt(self, msg: Union[str, bytes]) -> bytes:
        key = rsa.PublicKey(int(self.public_key, 16), int(self.mode, 16))
        return rsa.encrypt(msg.encode(), key)
    
    def to_hen(self, msg: Union[str, bytes]) -> str:
        enc_text = self.encrypt(msg)
        return enc_text.hex()
    
    def to_base64(self, msg: Union[str, bytes]) -> str:
        enc_text = self.encrypt(msg)
        return base64.b64encode(enc_text).decode()


def aes_encrypt(
        *, enc_str: Union[str, bytes, dict], key: str, mode: int = constants.AES.MODE_ECB, iv: str = None,
        padding: int = constants.PaddingMode.PKCS7Padding, encoding: str = "utf-8"
) -> str:
    """
    AES 加密
    Args:
        enc_str: 待加密字符串
        key: 秘钥
        mode: 加密模式，可选值有两个：ECB、CBC
        iv: 偏移量
        padding: 填充方式，可选值有三个：NoPadding、ZeroPadding、PKCS7Padding
        encoding: 编码格式，默认为 utf-8
    Return:
        AES 加密后的base64密文
    """

    aes = AESCryptor(key=key, mode=mode, iv=iv, padding=padding, encoding=encoding)
    meta_data = aes.encrypt(enc_str)

    return meta_data.to_base64()


def rsa_encrypt_hen(*, public_key: str, mode: str, msg: Union[str, bytes]) -> str:
    """
    AES 加密
    Args:
        public_key: 公钥
        mode: 模长
    Return:
        RSA 加密后的16进制密文
    """

    rsa = RSACryptor(public_key=public_key, mode=mode)
    return rsa.to_hen('123456')
    
    
def rsa_encrypt_base64(*, public_key: str, key: str, mode: str, msg: Union[str, bytes]) -> str:
    """
    AES 加密
    Args:
        public_key: 公钥
        mode: 模长
    Return:
        RSA 加密后的base64密文
    """

    rsa = RSACryptor(public_key=public_key, mode=mode)
    return rsa.to_base64('123456')


def make_uuid(string: str = None, mode: int = 1, namespace: uuid.UUID = uuid.NAMESPACE_DNS) -> str:
    """
    生成 UUID 字符串
    Args:
        string: 字符串
        mode: 模式
            1: 根据当前的时间戳和 MAC 地址生成
            2: 根据 MD5 生成
            3: 根据随机数生成
            4. 根据 SHA1 生成
        namespace: 命名空间，有四个可选值：NAMESPACE_DNS、NAMESPACE_URL、NAMESPACE_OID、NAMESPACE_X500
    Return:
        uuid 字符串
    """

    if mode == 1:
        uid = uuid.uuid1()
    elif mode == 2:
        uid = uuid.uuid3(namespace, str(string))
    elif mode == 2:
        uid = uuid.uuid4()
    elif mode == 2:
        uid = uuid.uuid5(namespace, str(string))
    else:
        uid = uuid.uuid1()

    return str(uid).replace('-', '')

# ------------------ 加解密工具集 ------------------ #


# -------------------- 网络协议 -------------------- #

def extract_params(url: str) -> dict:
    """
    从 url 中提取参数
    Args:
        url: url
    Return:
        从 url 中提取的参数
    """

    params_query = parse.urlparse(url).query
    return {i[0]: i[-1] for i in parse.parse_qsl(params_query)}


def extract_url(url: str) -> str:
    """
    从url中提取接口
    Args:
        url: url
    Return:
        接口
    """

    url_parse = parse.urlparse(url)
    return f'{url_parse.scheme}://{url_parse.netloc}{url_parse.path}'


def format_cookies(cookies: str) -> dict:
    """
    格式化cookies
    Args:
        cookies: cookies文本字符串，可以是浏览器请求头中复制出来的
    Return:
        返回格式化的cookies
    """

    return {
        i.split('=')[0].strip(): i.split('=')[-1].strip()
        for i in cookies.split(';') if i.split('=')[0].strip() and i.split('=')[-1].strip()
    }


def quote_params(params: dict) -> str:
    """
    转换并压缩 params 参数
    Args:
        params: 待转换数据
    Return:
        转换后可拼接到 url 的字符串
    """
    return parse.urlencode({i: params[i] for i in sorted(params.keys())})


def quote_url(url: str, params: dict) -> str:
    """
    拼接 params 参数到 url
    Args:
        url: url
        params: 待转换数据
    Return:
        拼接的 url
    """
    return url + '?' + quote_params(params)

# -------------------- 网络协议 -------------------- #


# ------------------ 爬虫常用工具 ------------------ #

def parse_json(
        json_data: dict, index: Union[str, Callable], default: Any = None,
        callback: Union[Callable, List[Callable]] = None
) -> Any:
    """
    字典取值
    Args:
        json_data: 原始数据
        index: 取值索引
        default: 默认值
    Return:
        从 json_data 中取到的值
    """
    if not isinstance(json_data, dict):
        return default

    data = pydash.get(json_data, index(json_data) if callable(index) else index, default)

    if not data or not callback:
        return data

    if isinstance(callback, Callable):
        return callback(data)

    if isinstance(callback, list):
        for clk in callback:
            data = clk(data)

    return data


def load_json(string: str, default: Any = None) -> Union[dict, list]:
    """
    将 json 字符串转化为字典
    Args:
        string: json 字符串
        default: 默认值
    Return:
        提取出的字典
    """

    if not string:
        return default or {}

    try:
        return json.loads(string)
    except json.JSONDecodeError:
        return default or {}


def dump_json(data: Union[dict, list], separators: tuple = None, *args, **kwargs) -> str:
    """
    将字典转化为 json 字符串
    Args:
        data: 原始数据
        separators: 分隔符，为了获得最紧凑的JSON表示，指定为 （'，'，'：'） 以消除空白。
                    如果指定，应指定为（item_separator，key_separator）元组
    Return:
        json 字符串
    """
    return json.dumps(data, separators=separators, *args, **kwargs)


from typing import Any, Callable

def type_converter(data: Any, to: Callable = None, force: bool = False) -> Any:
    """
    类型转换
    Args:
        data: 待转数据
        to: 转换类型
        force: 是否强制转换
    Return:
        转换值
    """

    def is_valid_number(data):
        if isinstance(data, str) and (
            data.isdigit() or ('.' in data and data.split('.')[0].isdigit() and data.split('.')[1].isdigit())
        ):
            return True
        return False

    if to is None or type(data) == to:
        return data

    if to in (int, float):
        if not isinstance(data, (int, float, str)) or (isinstance(data, str) and not is_valid_number(data)):
            return data if not force else to()

    return to(data)


def open_html(url: str) -> NoReturn:
    """
    用默认浏览器打开网址或文件
    Args:
        url: url
    Return:
        NoReturn
    """

    webbrowser.open(url)

# ------------------ 爬虫常用工具 ------------------ #


def deepcopy(item: Any) -> Any:
    """
    深拷贝
    Args:
        item: 待拷贝数据
    Return:
        深拷贝数据
    """

    return copy.deepcopy(item)


def get_ipv4():

    r = os.popen("ipconfig")
    text = r.read()

    ipv4 = _re.findall(r'以太网适配器 以太网:(.*?)默认网关', text, _re.S)[0]
    ipv4 = _re.findall(r'IPv4 地址 . . . . . . . . . . . . :(.*?)子网掩码', ipv4, _re.S)[0].replace(" ", "")

    return ipv4.strip()


def redis_running(port=6379):

    with os.popen(f"netstat -ano | findstr {port}") as r:
        pids = set([i.strip() for i in _re.findall('LISTENING(.*)', r.read())])

    return True if pids else False


def firefox_instance(
    executable_path: Union[str, Path] = None,
    binary_path: Union[str, Path] = None,
    headless: bool = False,
    proxy: str = None,
    options: dict = None,
    extension_path: Union[str, Path] = None,
    user_agent: str = None,
    download_path: Union[str, Path] = None,
    profile_path: Union[Path, str] = None,
    disable_images: bool = False,
):

    def to_str(path: Union[str, Path]) -> str:
        return str(path) if path is not None else None

    executable_path = to_str(executable_path)
    binary_path = to_str(binary_path)
    download_path = to_str(download_path)
    extension_path = to_str(extension_path)
    profile_path = to_str(profile_path)

    if options is None:
        options = {}

    if profile_path is None:
        profile_path = str(Path(fr'{os.getenv("AppData")}') / r'Mozilla/Firefox/Profiles/8qrydh7k.default-release-1')
        mkdir(profile_path, auto=False)

    if binary_path is None:
        binary_path = str(constants.Browser.FIREFOX_BINARY_PATH)

    firefox_options = FirefoxOptions()

    firefox_options.binary_location = binary_path
    profile = webdriver.FirefoxProfile(profile_path)

    if headless:
        firefox_options.add_argument("--headless")
    if user_agent is not None:
        firefox_options.add_argument(f'--user-agent={user_agent}')
    if extension_path is not None:
        firefox_options.add_extension(extension_path)
    if disable_images:
        profile.set_preference("permissions.default.image", 2)
    if download_path is not None:
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.dir", download_path)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "binary/octet-stream")

    if proxy is not None:
        parser = parse.urlparse(proxy)
        proxy_type = parser.scheme.lower()
        proxy_host, proxy_port = parser.netloc.split(':')
        proxy_port = int(proxy_port)

        if proxy_type in ("http", "https", "socks4", "socks5", "socks5h"):
            profile.set_preference('network.proxy.type', 1)
            proxy_preferences = {
                "http": ("network.proxy.http", "network.proxy.http_port", "network.proxy.ssl", "network.proxy.ssl_port"),
                "https": ("network.proxy.https", "network.proxy.https_port", "network.proxy.ssl", "network.proxy.ssl_port"),
                "socks4": ("network.proxy.socks", "network.proxy.socks_port"),
                "socks5": ("network.proxy.socks", "network.proxy.socks_port", "network.proxy.socks_version"),
                "socks5h": ("network.proxy.socks", "network.proxy.socks_port", "network.proxy.socks_version"),
            }
            for pref in proxy_preferences[proxy_type]:
                profile.set_preference(pref, proxy_host if pref.endswith("ssl") or pref.endswith("socks") else proxy_port)
            if proxy_type.startswith("socks"):
                profile.set_preference('network.proxy.socks_remote_dns', True)

    for k in options:
        profile.set_preference(k, options[k])

    profile.set_preference("network.http.use-cache", True)
    profile.set_preference("browser.cache.memory.enable", True)
    profile.set_preference("browser.cache.disk.enable", True)

    driver = webdriver.Firefox(
        executable_path=executable_path, firefox_profile=profile, options=firefox_options
    )

    return driver


def chromium_instance(
        executable_path: Union[str, Path] = None, binary_path: Union[str, Path] = None, headless: bool = False,
        proxy: str = None, options: list = None, extension_path: Union[str, Path] = None, user_agent: str = None,
        download_path: Union[str, Path] = None, profile_path: Union[Path, str] = None, disable_images: bool = False,
        disable_javascript: bool = False, log_level: int = 3
):

    if options is None:
        options = []

    if profile_path is None:
        profile_path = str(Path(os.getenv("AppData")).parent / r'Local\Google\Chrome\User Data\Default')
        mkdir(profile_path, auto=False)

    chrome_options = ChromeOptions()

    chrome_options.binary_location = str(binary_path or constants.Browser.CHROMIUM_BINARY_PATH)
    download_path = str(download_path or '')

    prefs = {
        'download.default_directory': download_path,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': False,
        'safebrowsing.disable_download_protection': True,
        'profile.default_content_setting_values': {}
    }

    if headless:
        chrome_options.add_argument("--headless")
    if proxy is not None:
        chrome_options.add_argument("--proxy-server={}".format(proxy))
    if user_agent is not None:
        chrome_options.add_argument(f'--user-agent={user_agent}')
    if extension_path is not None:
        chrome_options.add_extension(str(extension_path))
    if disable_javascript:
        prefs['profile.default_content_setting_values']['javascript'] = 2
    if disable_images:
        prefs['profile.default_content_setting_values']['images'] = 2

    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])

    chrome_options.add_argument(f"log-level={log_level}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-data-dir={profile_path}")

    for o in options:
        chrome_options.add_argument(o)

    driver = webdriver.Chrome(options=chrome_options, executable_path=str(executable_path or constants.Browser.CHROMIUM_DRIVER_PATH))

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_path}}
    driver.execute("send_command", params)

    return driver


def start_cmd(command, close=True):
    if close:
        process = subprocess.Popen(f'start cmd /c {command}', shell=True)
    else:
        process = subprocess.Popen(f'start cmd /k {command}', shell=True)
    return process.pid


def start_python_in_background(path, close=True):
    return start_cmd(command=f'python {path}', close=close)


def close_program_by_port(port):
    
    with os.popen(f"netstat -ano | findstr {port}") as r:
        pids = set([i.strip() for i in re(r.read(), 'LISTENING(.*)')])

    for pid in pids:
        os.system(f"taskkill /PID {pid} /T /F")


def get_pinyin(x, initial=False):

    if initial:
        return join([i[0] for i in lazy_pinyin('平安银行') if i])
    else:
        return join([i for i in lazy_pinyin('平安银行')])
