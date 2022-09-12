import json
import os
import hashlib
from typing import Union, Any

import pydash


def mkdir(path):
    """ 创建目录 """

    if os.path.isfile(path):
        path = os.path.split(path)[0]

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f'{path} 目录创建成功')


def str2num(char: str, multi: int = 1, force: bool = False, _type=int) -> Union[int, float, str]:
    """
        述职转化
        @params:
            char: 待转化字符串
            multi：倍乘系数
            force：是否强制转化，指定为True时，若无法转化则返回0
    """

    if not isinstance(char, str):
        return 0 if _type is int else 0.0 if force else char

    neg = False
    if char and char[0] == '-':
        neg = True
        char = char[1:]

    if char.isdigit():
        if _type is int:
            return -int(char) * multi if neg else int(char) * multi
        if _type is float:
            return -float(int(char)) * multi if neg else float(int(char)) * multi

    if '.' in char and char.split('.')[0].isdigit() and char.split('.')[-1].isdigit():
        if _type is int:
            return -int(float(char)) * multi if neg else int(float(char)) * multi
        if _type is float:
            return -float(char) * multi if neg else float(char) * multi

    return 0 if _type is int else 0.0 if force else char


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

    if to is None:
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
