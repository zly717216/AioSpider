# AioSpider 开发文档

让爬虫更简单，让爬虫更高效，让爬虫更智能

## 一、基本概况

### AioSpider 简介

AioSpider 是基于 asyncio 和 aiohttp 设计的高性能协程异步爬虫框架，可用于高速、海量、大规模的数据抓取，框架由系统引擎、调度器、URL 池、
响应解析器、中间件、数据存储器等组件构成，具有高度自由配置、自动调度、随机 UA、自动代理、微信和邮箱自动报警、数据自动入库、海量数据去重、
断点续爬等功能。

### AioSpider 特性

- 语法简洁明了
- 速度快
- 性能高

### AioSpider 安装

## 二、系统架构

### AioSpider 架构设计

### AioSpider 运行流程

### URL 去重

### 数据去重

## 三、请求与响应

## 四、爬虫

### 请求 Resquest

### 响应 Response

## 五、响应解析

### Parse 对象

### ReParse 对象

### XpathParse 对象

## 六、中间件


## 七、数据自动入库

### 模型

### 管道

### 字段

## 八、配置文件

## 九、爬虫工具集

### 1. 文件目录处理

#### ① mkdir

创建目录，能创建深层次目录

##### 定义

```python
def mkdir(path: Union[Path, str]):
	...
```

##### 参数

| 参数 | 释义       | 类型             | 是否必选 |
| ---- | ---------- | ---------------- | -------- |
| path | 文件夹路径 | Union[Path, str] | 是       |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 无 | None |

##### 使用示例

```python
from AioSpider import tools


# 在D盘的a目录下创建b文件夹，若a文件夹不存在也会自动创建
tools.mkdir(r'D:\a\b')

# from pathlib import Path
# tools.mkdir(Path('D:\a\b'))
```

### 2. 时间处理

#### ① strtime_to_stamp

时间字符串转时间戳

##### 定义

```python
def strtime_to_stamp(str_time: str, millisecond: bool = False) -> int:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| str_time  | 时间字符串 |  str  | 是     |        |
| millisecond  | 是否返回毫秒级时间戳 |    bool   | 否  |    Flase    |

##### 使用示例

```python
from AioSpider import tools


# 将'2022/02/15 10:12:40'时间字符串转成时间戳
tools.strtime_to_stamp('2022/02/15 10:12:40')     # 1644891160
```

#### ② stamp_to_strtime

stamp_to_strtime: 时间戳转时间字符串

##### 定义

```python
def stamp_to_strtime(time_stamp: , format=) -> Union[str, None]:
    ...
```

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 时间字符串 | Union[str, None] |


##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| time_stamp  | 时间戳 |  Union[int, float, str]  | 是     |        |
| format  | 时间字符串格式 |    bool   | 否  |    '%Y-%m-%d %H:%M:%S'    |

##### 使用示例

```python
from AioSpider import tools


# 将 1644891160 时间戳转成时间字符串
tools.stamp_to_strtime(1644891160)    # '2022/02/15 10:12:40'
```

#### ③ strtime_to_time

时间字符串转时间戳

```python
def strtime_to_time(str_time: str) -> datetime:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 |
| ----- | ------------ | -------- | -------- |
| str_time  | 时间字符串 | str  | 是     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 时间对象 | datetime |

##### 使用示例

```python
from AioSpider import tools


# 将 '2022/02/15 10:12:40' 时间戳转成时间对象
tools.strtime_to_time('2022/02/15 10:12:40') # datetime.datetime(2022, 2, 15, 10, 12, 40)
```

#### ④ stamp_to_time

时间戳转时间字符串，支持秒级和毫秒级时间戳自动判断

##### 定义

```python
def stamp_to_time(time_stamp: Union[int, float]) -> Union[datetime, None]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 |
| ----- | ------------ | -------- | -------- |
| time_stamp  | 时间戳 |  Union[int, float, str]  | 是     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 时间对象 | Union[datetime, None] |

##### 使用示例

```python
from AioSpider import tools


# 将 1644891160 时间戳转成时间对象
tools.stamp_to_time(1644891160) # datetime.datetime(2022, 2, 15, 10, 12, 40)
```

### 3. 字符串处理

#### ① str2num

str2num: 数值类型转化，带有 ,、%、万、百万等格式化数字都能转换，一般用于字符串数字转整型或浮点型

##### 定义

```python
def str2num(string: str, multi: int = 1, force: bool = False, _type=int) -> Union[int, float, str]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | ------ |
| string  | 字符串       | str      | 是       |        |
| multi | 倍乘基数     | int      | 否       | 1      |
| force | 是否强制转换 | bool     | 否       | False  |
| _type | 输出类型     | Callable | 否       | int    |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 整型或浮点型数字 | Union[int, float, str]|

##### 使用示例

```python
from AioSpider import tools


tools.str2num(string='100')   # 100
tools.str2num(string='100', multi=10)   # 1000
# force 指定为True的情况下才会强转
tools.str2num(string='100', multi=10, _type=float, force=False)# 1000.0
tools.str2num(string='100', multi=10, _type=float, force=True) # 1000.0
tools.str2num(string='100.0', multi=10, _type=float)           # 1000.0
```

#### ② aio_eval

执行字符串

##### 定义

```python
def aio_eval(string: str, default: Any = None) -> Any:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | ------ |
| string  | 字符串       | str      | 是       |        |
| default | 默认值     | Any      | 否       |       |

##### 返回值

##### 使用示例

```python
from AioSpider import tools


tools.aio_eval('print("hello world")')    # hello world
tools.aio_eval('{"a": 1111}')             # {"a": 1111}
tools.aio_eval('1/0', default=100)        # 100 
```

#### ③ get_hash

计算 md5 hash 值

##### 定义

```python
def get_hash(item: Any) -> str:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 |
| ----- | ------------ | -------- | -------- |
| item  | hash 待计算值       | Any      | 是       |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 哈希值 | str |

##### 使用示例

```python
from AioSpider import tools


tools.get_hash('hello world')    # '5eb63bbbe01eeed093cb22bb8f5acdc3'
```

#### ④ filter_type

将 js 中的 null、false、true 过滤并转换成 python 对应的数据类型，常用于 json.loads 前

##### 定义

```python
def filter_type(string: str) -> str:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 |
| ----- | ------------ | -------- | -------- |
| string  | 代转字符串 |  str     | 是     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 过滤后新的字符串 | str |

##### 使用示例

```python
from AioSpider import tools


tools.filter_type('{"a": "null", "b": "false"}')    # '{"a": "None", "b": "False"}'
```

#### ⑤ join

拼接字符串，若 data 参数中的元素有非字符串类型的元素，会被强转


##### 定义

```python
def join(data: Iterable, on: str = '') -> str:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | ------ |
| data  | 待转可迭代对象 |  Iterable  | 是     |        |
| on  | 拼接字符 |  str  | 是     |        | ''     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 拼接后新的字符串 | str |

##### 使用示例

```python
from AioSpider import tools


tools.join(['a', 'b', 'c', 'd'])             # 'abcd'
tools.join(('a', 'b', 'c', 'd'))             # 'abcd'
tools.join({'a', 'b', 'c', 'd'})             # 'abcd'
tools.join(['a', 'b', 'c', 'd'], on=',')     # 'a,b,c,d'
```

### 4. 数值处理

#### ① max

求最大值

##### 定义

```python
def max(arry: Iterable, default: Union[int, float] = 0) -> Uniun[int, float]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| arry  | 数组 |  Iterable  | 是     |        |
| default  | 默认值 |  Union[int, float]  | 否     |   0     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 数组中的最大值 | Uniun[int, float] |

##### 使用示例

```python
from AioSpider import tools


tools.max([1, 5, 3, 10, 2])    # 10
```

#### ② min

求最小值


##### 定义

```python
def min(arry: Iterable, default: Union[int, float] = 0) -> Uniun[int, float]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| arry  | 数组 |  Iterable  | 是     |        |
| default  | 默认值 |  Union[int, float]  | 否     |   0     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 数组中的最小值 | Uniun[int, float] |

##### 使用示例

```python
from AioSpider import tools


tools.min([1, 5, 3, 10, 2])    # 1
```

### 5. 爬虫常用工具

#### ① parse_json

字典取值


##### 定义

```python
def parse_json(json_data: dict, index: str, default=None) -> Any:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| json_data  | 原始数据 |  dict     | 是     |        |
| index  | 取值索引 |  str     | 是  |        |
| default  | 默认值 |  Any     | 否     |    None    |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 从 json_data 中取到的值 | Any |

##### 使用示例

```python
from AioSpider import tools


data = {
    "a": "null", "b": "false", "f": {
        "h": [
            {"g": "hello"}
        ]
    }
    "c": [{"d": 1}]
}

# 取 false
tools.parse_json(json_data=data, index='b') 
# 取 hello
tools.parse_json(json_data=data, index='f.h[0].g')
tools.parse_json(json_data=data, index='f.h[0].x', default='world')  # world   index索引表达式错误会返回默认值
# 取 {"d": 1}
tools.parse_json(json_data=data, index='c[0]', default={})
```


#### ② load_json

load_json: 将 json 字符串转化为字典

##### 定义

```python
def load_json(string: str, default=None) -> Union[dict, list]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| string  | json 字符串 |  dict     | 是     |        |
| default  | 默认值 |    Any   | 否  |    None    |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 提取出的字典 | Union[dict, list] |

##### 使用示例

```python
from AioSpider import tools


tools.load_json('{"a": "None", "b": "False"}')    # {'a': 'None', 'b': 'False'}
```

#### ③ type_converter

类型转换


##### 定义

```python
def type_converter(data, to=None, force=False) -> Any:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| data  | 待转数据 |  Any  | 是     |        |
| to  | 转换类型 |    Callable   | 否  |    None    |
| force  | 是否强制转换 |    bool   | 否  |    None    |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 转换值 | Any |

##### 使用示例

```python
from AioSpider import tools


tools.type_converter(100.0, to=int)    # 100
```

#### ④ xpath

xpath 提取数据

##### 定义

```python
def xpath(node: Union[str, etree._Element], q: str, default: Any = None) -> Union[list, etree._Element, str]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| node  | 元素节点或 html 字符串 |  Union[str, etree._Element]  | 是     |        |
| q  | xpath 表达式 |  str  | 是     |        |
| default  | 默认值 |  Any  | 否     |   None   |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| xpath 元素节点列表 | Union[list, etree._Element, str] |

##### 使用示例

```python
from AioSpider import tools


html = '<p><span>hellor world</span></p>'
tools.xpath(node=html, q='//span/text()')     # ['hellor world']
# html 若是一个xpath元素节点
tools.xpath(node=html, q='//span/text()')     # ['hellor wo
tools.xpath(node=html, q='//span')            # 返回节点列表
```

#### ⑤ xpath_text

xpath 提取文本数据

##### 定义

```python
def xpath_text(node: Union[str, etree._Element], q: str, on: str = None, default: str = None) -> str:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| node  | 元素节点或 html 字符串 |  Union[str, etree._Element]  | 是     |        |
| q  | xpath 表达式 |  str  | 是     |   0     |
| on  | 拼接字符串 |  str  | 否     |   ''     |
| default  | 默认值 |  str  | 否     |   ''     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| xpath 提取的字符串 | str |

##### 使用示例

```python
from AioSpider import tools


html = '<p><span>hellor world</span></p>'
tools.xpath_text(node=html, q='//span/text()')     # 'hellor world'
# html 若是一个xpath元素节点
tools.xpath(node=html, q='//span/text()')     # 'hellor world"
```


#### ⑥ re

正则提取数据

##### 定义

```python
def re(text: str, regx: str, default: Any = None) -> list:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| text  | 原始文本字符串 |  str  | 是     |        |
| regx  | 正则表达式 |  str  | 是     |   0     |
| default  | 默认值 |  Any  | 否     |   None     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 正则表达式匹配到的元素列表 | list |


##### 使用示例

```python
from AioSpider import tools


text = '<a href="https://www.baidu.com"></a>'
tools.re(text=text, regx='href="(.*?)"')    # ['https://www.baidu.com']
```

#### ⑦ re_text

正则提取文本数据

##### 定义

```python
def re_text(text: str, regx: str, on: str = None, default: str = None) -> str:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| text  | 原始文本字符串 |  str | 是     |        |
| regx  | 正则表达式 |  str  | 是     |   0     |
| on  | 拼接字符串 |  str  | 否     |   ''     |
| default  | 默认值 |  str  | 否     |   ''     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 正则表达式匹配到的第一个元素 | str |

##### 使用示例

```python
from AioSpider import tools


text = '<a href="https://www.baidu.com"></a>'
tools.re_text(text=text, regx='href="(.*?)"') # 'https://www.baidu.com'
```

#### ⑧ extract_params

从 url 中提取参数

##### 定义

```python
def extract_params(url: str) -> dict:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 |
| ----- | ------------ | -------- | -------- |
| url  | url |  str  | 是     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 从 url 中提取的 query 参数 | dict |

##### 使用示例

```python
from AioSpider import tools


url = 'http://127.0.0.1:5025/ip?a=1&b=2'
tools.extract_params(url)    # {"a": "1", "b": "2"}
```

#### ⑨ extract_url

从url中提取接口

##### 定义

```python
def extract_url(url: str) -> str:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 |
| ----- | ------------ | -------- | -------- |
| url  | url |  str  | 是     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 截断 query 后的 url | str |

##### 使用示例

```python
from AioSpider import tools


url = 'http://127.0.0.1:5025/ip?a=1&b=2'
tools.extract_url(url)    # 'http://127.0.0.1:5025/ip'
```

#### ⑩ open_html

用默认浏览器打开网址或 html 文件

##### 定义

```python
def open_html(url: str):
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 |
| ----- | ------------ | -------- | -------- |
| url  | url 或 html 文件路径 |  str  | 是     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 无 | None |

##### 使用示例

```python
from AioSpider import tools


tools.open_html('https://www.baidu.com')    # 将会用默认浏览器打开
tools.open_html('D:\\a\\b.html')            # 将会用默认浏览器打开
```

