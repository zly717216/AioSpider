import sys
from pathlib import Path

from AioSpider.utils import tools
from AioSpider.log import logger as lgr
from AioSpider import settings as sts


sys.path.append(str(Path().cwd().parent.parent))


class GlobalConstant:

    _settings = None
    _dataloader = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            setattr(cls, '_instance', super().__new__(cls))
        return cls._instance

    @property
    def settings(self):
        return self._settings

    @property
    def dataloader(self):
        return self._dataloader

    @settings.getter
    def settings(self):
        return self._settings

    @dataloader.getter
    def dataloader(self):
        return self._dataloader

    @settings.setter
    def settings(self, sts):
        self._settings = sts

    @dataloader.setter
    def dataloader(self):
        return self._dataloader


class AioObject:

    async def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        await instance.__init__(*args, **kwargs)
        return instance


def init_logger(settings=sts.LOGGING):

    log_name = settings['LOG_NAME']

    if not log_name:
        warnings.warn("logger的'name'属性必须为非空str类型，日志名称设置无效，将使用默认名'aioSpider'作为日志名称")

    file_path = settings['LOG_PATH']
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


logger = None

session = None
db = None
