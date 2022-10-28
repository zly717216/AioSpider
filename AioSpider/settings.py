import os
import sys
from pathlib import Path

from .constants import LogLevel, Color, When, UserAgent, WriteMode

# ---------------------------------- 系统相关配置 ---------------------------------- #

# 切换工作路径为当前项目路径
AIOSPIDER_PATH = Path(__file__).parent

# url缓存方式，记录已爬取url的状态，默认 queue（队列引擎），redis（redis引擎）
BACKEND_CACHE_ENGINE = {
    'queue': {
        'enabled': True                     # 指定为队列引擎
    },
    'redis': {
        'enabled': False,                   # 指定为redis引擎
        'host': 'localhost',                # ip / 域名
        'port': 6379,                       # redis端口，默认一般都是6379
        'db': 0,                            # 数据库
        'user': '',                         # 用户名，一般没有；没有就指定为空或None
        'password': ''                      # 认证密码，一般没有；没有就指定为空或None
    }
}

# 日志配置
LOGGING = {
    'LOG_NAME': 'aioSpider',                        # 日志名称
    'LOG_PATH': AIOSPIDER_PATH / "log",             # 日志存储路径
    'LOG_CMD_FORMAT': '%(asctime)s - %(pathname)s - [line:%(lineno)d] - %(levelname)s: %(message)s',  # 控制台输出日志格式
    'LOG_FILE_FORMAT': '%(asctime)s - %(pathname)s - [line:%(lineno)d] - %(levelname)s: %(message)s',  # 文件输出日志格式
    'LOG_CMD_DATE_FORMAT': '%Y-%m-%d %H:%M:%S',     # 控制台输出日志时间格式
    'LOG_FILE_DATE_FORMAT': '%Y-%m-%d %H:%M:%S',    # 文件输出日志时间格式
    'LOG_CMD_LEVEL': LogLevel.DEBUG,                # 控制台输出日志等级
    'LOG_FILE_LEVEL': LogLevel.DEBUG,               # 文件输出日志等级
    'LOG_COLORFUL': True,                           # 是否带有颜色
    'LOG_IS_CONSOLE': True,                         # 是否打印到控制台
    'LOG_IS_FILE': False,                           # 是否写文件
    'LOG_MODE': "a",                                # 写文件的模式
    'LOG_LIMIT_BYTES': 10 * 1024 * 1024,            # 每个日志文件的默认最大字节数
    'LOG_BACKUP_COUNT': 10,                         # 日志文件保留数量
    'LOG_ENCODING': 'utf-8',                        # 日志文件编码
    'LOG_COLOR_DICT': {
        'debug': Color.GREEN, 'info': Color.WHITE, 'warning': Color.YELLOW,
        'error': Color.RED, 'critical': Color.PINK
    },                                              # 日志颜色
    'OTHERS_WHEN': When.DAYS,                       # 日志轮询间隔
    'OTHERS_LOG_LEVEL': LogLevel.ERROR,             # 第三方库的log等级
}

# -------------------------------------------------------------------------------- #

# ---------------------------------- 爬虫相关配置 ---------------------------------- #

REQUEST_CONCURRENCY_COUNT = 240     # 请求并发数
MAX_CONNECT_COUNT = 100             # 请求最大连接数
NO_REQUEST_SLEEP_TIME = 3           # 求情队列无请求时休眠时间
REQUEST_CONCURRENCY_SLEEP = 0       # 单位秒，每 REQUEST_CONCURRENCY_COUNT 个请求休眠1秒
PER_REQUEST_SLEEP = 0               # 单位秒，每并发1个请求时休眠1秒
REQUEST_TIMEOUT = 300               # 请求最大超时时间

# 请求失败是否要重试
RETRY_ENABLE = True
# 每个请求最大重试次数，RETRY_ENABLE指定为True时生效
MAX_RETRY_TIMES = 3
# 重试状态码，MAX_RETRY_TIMES大于0和RETRY_ENABLE指定为True时生效
RETRY_STATUS = [400, 403, 404, 500, 501, 502, 503]
# 优先级

# 默认请求头，优先级：spider headers > 默认headers > random headers
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,appl"
              "ication/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
}
RANDOM_HEADERS = True               # 随机UserAgent
RETRY_FAILED_REQUESTS = False       # 爬虫启动时，重新抓取失败的requests
# 字符串类型或可迭代对象，值为chrome, ie, opera, firefox, ff, safari，若指定RANDOM_HEADERS为True时则不生效
USER_AGENT_TYPE = UserAgent.CHROME

REQUEST_PROXY = None  # 代理 支持http和https，默认为NNone，不设置代理，需要设置则可以按照以下格式设置
# REQUEST_PROXY = 'http://127.0.0.1:7890'
# REQUEST_PROXY = '127.0.0.1:7890'

# 下载中间件
DOWNLOAD_MIDDLEWARE = {
    "AioSpider.middleware.download.FirstMiddleware": 100,
    "AioSpider.middleware.download.HeadersMiddleware": 101,
    "AioSpider.middleware.download.LastMiddleware": 102,
    "AioSpider.middleware.download.RetryMiddleware": 103,
    "AioSpider.middleware.download.ProxyMiddleware": 104,
}

# 数据管道
ITEM_PIPELINES = {}

# 数据去重
DATA_FILTER_ENABLE = True                   # 是否启用数据去重
CACHED_ORIGIN_DATA = False                  # 是否启用缓存原始数据 数据量大的时候建议设置为True，每次启动将会自动去重
CAPACITY = 5000 * 10000                     # 去重的数据容量 数据器中可以容纳100亿条数据
MODEL_NAME_TYPE = 'smart'                   # lower / upper / smart，处理表明的方式

# URL去重
CACHED_REQUEST = {
    'CACHED': True,                         # 是否缓存爬过的请求 将爬过的请求缓存到本地
    'LOAD_SUCCESS': True,                   # 将CACHED_REQUEST缓存中成功的请求加载到队列
    'LOAD_FAILURE': False,                  # 将CACHED_REQUEST缓存中失败的请求加载到队列
    'CACHED_EXPIRE_TIME': 60 * 60 * 24 * 30,    # 缓存时间 秒
    'CACHE_PATH': AIOSPIDER_PATH / "cache",     # 数据和资源缓存路径
    'FILTER_FOREVER': True                  # 是否永久去重，配置此项 CACHED_EXPIRE_TIME 无效
}

IGNORE_STAMP = True                         # 去重忽略时间戳
STAMP_NAMES = []                            # 时间戳字段名，一般指请求中params、data中的参数

USE_DNS_CACHE = True                        # 使用内部DNS映射缓存，用来查询DNS，使建立连接速度更快

# -------------------------------------------------------------------------------- #

# --------------------------------- 数据库相关配置 --------------------------------- #
DATABASE_ENGINE = {
    'CSVFile': {
        'ENABLE': True,
        'CSV_PATH': Path(AIOSPIDER_PATH) / 'data',
        'ENCODING': 'utf-8',
        'WRITE_MODE': WriteMode.W
    },
    'SQLITE': {
        'ENABLE': False,
        'SQLITE_PATH': Path(AIOSPIDER_PATH) / 'data',
        'SQLITE_DB': "aioSpider",
        'SQLITE_TIMEOUT': 10
    },
    'MYSQL': {
        'ENABLE': False,
        'MYSQL_HOST': "127.0.0.1",
        'MYSQL_PORT': 3306,
        'MYSQL_DB': "",
        'MYSQL_USER_NAME': "",
        'MYSQL_USER_PWD': "",
        'MYSQL_CHARSET': "utf8",
        'MYSQL_CONNECT_TIMEOUT': 10,
        'MYSQL_TIME_ZONE': '+0:00',
    },
    'MONGODB': {
        'ENABLE': False,
        'MONGO_HOST': "127.0.0.1",
        'MONGO_PORT': 27017,
        'MONGO_DB': "",
        'MONGO_USER_NAME': "",
        'MONGO_USER_PWD': ""
    },
}

# -------------------------------------------------------------------------------- #

# ---------------------------------- 消息通知配置 ---------------------------------- #

# 钉钉报警
DINGDING_WEB_TOKEN = ""             # 钉钉机器人api
DINGDING_WARNING_PHONE = ""         # 报警人 支持列表，可指定多个
DINGDING_WARNING_ALL = False        # 是否提示所有人， 默认为False
# 邮件报警
EMAIL_SENDER = ""                   # 发件人
EMAIL_PASSWORD = ""                 # 授权码
EMAIL_RECEIVER = ""                 # 收件人 支持列表，可指定多个
EMAIL_SMTPSERVER = "smtp.qq.com"    # 邮件服务器 默认为qq邮箱
# 企业微信报警
WECHAT_WARNING_URL = ""             # 企业微信机器人api
WECHAT_WARNING_PHONE = ""           # 报警人 将会在群内@此人, 支持列表，可指定多人
WECHAT_WARNING_ALL = False          # 是否提示所有人， 默认为False
# 时间间隔
WARNING_INTERVAL = 3600             # 相同报警的报警时间间隔，防止刷屏; 0表示不去重
WARNING_LEVEL = "DEBUG"             # 报警级别， DEBUG / ERROR
WARNING_FAILED_COUNT = 1000         # 任务失败数 超过WARNING_FAILED_COUNT则报警

# -------------------------------------------------------------------------------- #
