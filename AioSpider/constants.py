class LogLevel:
    """日志等级常量"""

    DEBUG = 'DEBUG'
    INFO = 'INFO'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    CRITICAL = 'CRITICAL'


class Color:
    """CMD日志输出颜色常量"""

    GREEN = 'green'
    YELLOW = 'yellow'
    RED = 'red'
    PINK = 'pink'
    WHITE = 'white'


class When:
    """日志轮询间隔常量"""

    SECONDS = 'S'
    MINUTES = 'M'
    HOURS = 'H'
    DAYS = 'D'
    WEEK = 'W'
    MIDNIGHT = 'midnight'


class UserAgent:
    """日志轮询间隔常量"""

    CHROME = 'chrome'
    IE = 'ie'
    OPERA = 'opera'
    FIREFOX = 'firefox'
    FF = 'ff'
    SAFARI = 'safari'


class WriteMode:
    A = 'a'     # 追加模式
    W = 'w'     # 覆盖模式


CACHE_DIR_NAME = 'AioSpider'
