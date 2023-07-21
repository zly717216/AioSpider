__all__ = [
    'Path', 'LogLevel', 'TimeFormater', 'Formater', 'UserAgent', 'WriteMode', 'Browser', 
    'PaddingMode', 'AESMode', 'ProxyPoolStrategy', 'RequestWay', 'ProxyType', 'ModelNameType', 
    'BackendEngine', 'ProxyVerifySource', 'RequestMethod', 'NoticeType'
]


from pathlib import Path
from Crypto.Cipher import AES


class BackendEngine:
    """数据缓存方式"""

    queue = 'queue'
    redis = 'redis'


class LogLevel:
    """日志等级常量"""

    DEBUG = 'DEBUG'
    INFO = 'INFO'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    CRITICAL = 'CRITICAL'


class TimeFormater:
    """
    支持自定义格式
        +------------------------+---------+----------------------------------------+
        |                        | Token   | Output                                 |
        +========================+=========+========================================+
        | Year                   | YYYY    | 2000, 2001, 2002 ... 2012, 2013        |
        |                        +---------+----------------------------------------+
        |                        | YY      | 00, 01, 02 ... 12, 13                  |
        +------------------------+---------+----------------------------------------+
        | Quarter                | Q       | 1 2 3 4                                |
        +------------------------+---------+----------------------------------------+
        | Month                  | MMMM    | January, February, March ...           |
        |                        +---------+----------------------------------------+
        |                        | MMM     | Jan, Feb, Mar ...                      |
        |                        +---------+----------------------------------------+
        |                        | MM      | 01, 02, 03 ... 11, 12                  |
        |                        +---------+----------------------------------------+
        |                        | M       | 1, 2, 3 ... 11, 12                     |
        +------------------------+---------+----------------------------------------+
        | Day of Year            | DDDD    | 001, 002, 003 ... 364, 365             |
        |                        +---------+----------------------------------------+
        |                        | DDD     | 1, 2, 3 ... 364, 365                   |
        +------------------------+---------+----------------------------------------+
        | Day of Month           | DD      | 01, 02, 03 ... 30, 31                  |
        |                        +---------+----------------------------------------+
        |                        | D       | 1, 2, 3 ... 30, 31                     |
        +------------------------+---------+----------------------------------------+
        | Day of Week            | dddd    | Monday, Tuesday, Wednesday ...         |
        |                        +---------+----------------------------------------+
        |                        | ddd     | Mon, Tue, Wed ...                      |
        |                        +---------+----------------------------------------+
        |                        | d       | 0, 1, 2 ... 6                          |
        +------------------------+---------+----------------------------------------+
        | Days of ISO Week       | E       | 1, 2, 3 ... 7                          |
        +------------------------+---------+----------------------------------------+
        | Hour                   | HH      | 00, 01, 02 ... 23, 24                  |
        |                        +---------+----------------------------------------+
        |                        | H       | 0, 1, 2 ... 23, 24                     |
        |                        +---------+----------------------------------------+
        |                        | hh      | 01, 02, 03 ... 11, 12                  |
        |                        +---------+----------------------------------------+
        |                        | h       | 1, 2, 3 ... 11, 12                     |
        +------------------------+---------+----------------------------------------+
        | Minute                 | mm      | 00, 01, 02 ... 58, 59                  |
        |                        +---------+----------------------------------------+
        |                        | m       | 0, 1, 2 ... 58, 59                     |
        +------------------------+---------+----------------------------------------+
        | Second                 | ss      | 00, 01, 02 ... 58, 59                  |
        |                        +---------+----------------------------------------+
        |                        | s       | 0, 1, 2 ... 58, 59                     |
        +------------------------+---------+----------------------------------------+
        | Fractional Second      | S       | 0 1 ... 8 9                            |
        |                        +---------+----------------------------------------+
        |                        | SS      | 00, 01, 02 ... 98, 99                  |
        |                        +---------+----------------------------------------+
        |                        | SSS     | 000 001 ... 998 999                    |
        |                        +---------+----------------------------------------+
        |                        | SSSS... | 000[0..] 001[0..] ... 998[0..] 999[0..]|
        |                        +---------+----------------------------------------+
        |                        | SSSSSS  | 000000 000001 ... 999998 999999        |
        +------------------------+---------+----------------------------------------+
        | AM / PM                | A       | AM, PM                                 |
        +------------------------+---------+----------------------------------------+
        | Timezone               | Z       | -07:00, -06:00 ... +06:00, +07:00      |
        |                        +---------+----------------------------------------+
        |                        | ZZ      | -0700, -0600 ... +0600, +0700          |
        |                        +---------+----------------------------------------+
        |                        | zz      | EST CST ... MST PST                    |
        +------------------------+---------+----------------------------------------+
        | Seconds timestamp      | X       | 1381685817, 1234567890.123             |
        +------------------------+---------+----------------------------------------+
        | Microseconds timestamp | x       | 1234567890123                          |
        +------------------------+---------+----------------------------------------+

    """

    A = 'YYYY-MM-DD HH:mm:ss.SSS'
    B = 'YYYY/MM/DD HH:mm:ss.SSS'

    C = 'YYYY-MM-DD HH:mm:ss'
    D = 'YYYY/MM/DD HH:mm:ss'


class Formater:

    class Attribute:

        time = 'time'
        name = 'name'
        file = 'file'
        module = 'module'
        function = 'function'
        level = 'level'
        line = 'line'
        message = 'message'
        process = 'process'
        thread = 'thread'
        extra = 'extra'
        exception = 'exception'
        elapsed = 'elapsed'

    A = [
        Attribute.time, Attribute.level, Attribute.module, Attribute.function,
        Attribute.line, Attribute.message
    ]
    B = [
        Attribute.process, Attribute.thread, Attribute.time, Attribute.level,
        Attribute.module, Attribute.function, Attribute.line, Attribute.message
    ]
    C = [Attribute.time, Attribute.level, Attribute.file, Attribute.line, Attribute.message]


class UserAgent:
    """日志轮询间隔常量"""

    CHROME = 'chrome'
    IE = 'ie'
    OPERA = 'opera'
    FIREFOX = 'firefox'
    FF = 'ff'
    SAFARI = 'safari'


class WriteMode:
    A = 'a'         # 追加模式
    W = 'w'         # 覆盖模式
    WB = 'wb'       # 二进制写模式


class RobotApi:

    DINGDING = 'https://oapi.dingtalk.com/robot/send?access_token='    # 钉钉机器人api


class Browser:

    CHROMIUM_DRIVER_PATH = Path(__file__).parent / r'tools/Chromium/chromedriver.exe'
    CHROMIUM_BINARY_PATH = Path(__file__).parent / r'tools/Chromium/chrome.exe'
    FIREFOX_DRIVER_PATH = Path(__file__).parent / r'tools\Firefox\geckodriver.exe'
    FIREFOX_BINARY_PATH = Path(__file__).parent / r'tools\Firefox\firefox.exe'


class PaddingMode:
    NoPadding = 0
    ZeroPadding = 1
    PKCS7Padding = 2


class AESMode:
    ECB = AES.MODE_ECB
    CBC = AES.MODE_CBC


class RequestWay:

    aiohttp = 'aiohttp'
    requests = 'requests'
    

RequestMethod = ['GET', 'POST']


class ProxyType:

    none = None                 # 不使用代理
    system = 'system'           # 使用系统代理
    pool = 'pool'               # 使用AioSpider内置代理池
    appoint = 'appoint'         # 手动指定proxy_pool
    
    
class ProxyPoolStrategy:

    random = 'random'           # 随机模式
    balance = 'balance'         # 均衡负载模式
    weight = 'weight'           # 按权分配模式


class ProxyVerifySource:

    baidu = 'https://www.baidu.com'             # 百度
    google = 'https://www.google.com.hk'        # 谷歌
    bing = 'https://cn.bing.com/'               # 必应


class ModelNameType:

    lower = 'lower'
    upper = 'upper'
    smart = 'smart'


class DataBaseType:

    mysql = 'mysql'
    sqlite = 'sqlite'
    csv = 'csv'
    file = 'file'


class NoticeType:

    dingding = 'dingding'
    wechat = 'wechat'
    email = 'email'
