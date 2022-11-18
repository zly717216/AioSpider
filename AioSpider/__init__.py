import sys
from pathlib import Path

from AioSpider.utils import tools
from AioSpider.log import logger as lgr
from AioSpider import settings as sts


sys.path.append(str(Path().cwd().parent.parent))


class GlobalConstant:

    _settings = None
    _datamanager = None
    _database = None
    _session = None
    _pipelines = None
    _spider_name = None
    _logger = None
    _models = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            setattr(cls, '_instance', super().__new__(cls))
        return cls._instance

    @property
    def spider_name(self):
        return self._spider_name

    @property
    def logger(self):
        if self._logger is None:
            self._logger = init_logger()
        return self._logger

    @property
    def settings(self):
        return self._settings

    @property
    def datamanager(self):
        return self._datamanager

    @property
    def database(self):
        return self._database
    
    @property
    def session(self):
        return self._session

    @property
    def pipelines(self):
        return self._pipelines

    @property
    def models(self):
        return self._models

    @spider_name.setter
    def spider_name(self, k):
        self._spider_name = k

    @logger.setter
    def logger(self, k):
        self._logger = k

    @settings.setter
    def settings(self, k):
        self._settings = k

    @datamanager.setter
    def datamanager(self, k):
        self._datamanager = k

    @database.setter
    def database(self, k):
        self._database = k

    @session.setter
    def session(self, k):
        self._session = k

    @pipelines.setter
    def pipelines(self, k):
        self._pipelines = k

    @models.setter
    def models(self, k):
        self._models = k


class AioObject:

    async def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        await instance.__init__(*args, **kwargs)
        return instance


def init_logger(settings=sts.LOGGING):

    log_name = settings.get('LOG_NAME')
    file_path = settings['LOG_PATH'] / ((log_name or GlobalConstant().spider_name) + '.log')
    cmd_fmt = settings['LOG_CMD_FORMAT']
    file_fmt = settings['LOG_FILE_FORMAT']

    if cmd_fmt and not file_fmt:
        file_fmt = cmd_fmt

    if not cmd_fmt and file_fmt:
        cmd_fmt = file_fmt

    cmd_level = settings['LOG_CMD_LEVEL']
    file_level = settings['LOG_FILE_LEVEL']

    if cmd_level and not file_level:
        file_level = cmd_level

    if not cmd_level and file_level:
        cmd_level = file_level

    cmd_date_fmt = settings['LOG_CMD_DATE_FORMAT']
    file_date_fmt = settings['LOG_FILE_DATE_FORMAT']

    if cmd_date_fmt and not file_date_fmt:
        file_date_fmt = cmd_date_fmt

    if not cmd_date_fmt and file_date_fmt:
        cmd_date_fmt = file_date_fmt

    colorful = settings['LOG_COLORFUL']
    backup_count = settings['LOG_BACKUP_COUNT']
    limit = settings['LOG_LIMIT_BYTES']
    cmd_log = settings['LOG_IS_CONSOLE']
    file_log = settings['LOG_IS_FILE']
    file_mode = settings['LOG_MODE']
    encoding = settings['LOG_ENCODING']
    color_dict = settings['LOG_COLOR_DICT']
    others_level = settings['OTHERS_LOG_LEVEL']
    when = settings['OTHERS_WHEN']

    kwargs = {
        'name': log_name, 'file_path': file_path, 'cmd_level': cmd_level, 'file_level': file_level,
        'cmd_fmt': cmd_fmt, 'file_fmt': file_fmt, 'cmd_date_fmt': cmd_date_fmt, 'file_date_fmt': file_date_fmt,
        'colorful': colorful, 'backup_count': backup_count, 'limit': limit, 'cmd_log': cmd_log,
        'file_log': file_log, 'file_mode': file_mode, 'encoding': encoding, 'cmd_color_dict': color_dict,
        'others_level': others_level, 'when': when
    }

    return lgr(**kwargs)
