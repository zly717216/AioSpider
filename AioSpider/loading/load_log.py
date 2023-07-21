__all__ = ['LoadLogger']

import sys
from datetime import datetime

from AioSpider import logger
from AioSpider import tools


class LoadLogger:

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.init_log(*args, **kwargs)

    def load_console(self, config):

        format = config['format']
        date_format = config['time_format']
        level = config['level']

        fmt = ' <red>|</red> '.join([self.format_item(item, date_format) for item in format])

        kwargs = {
            'level': level, 'format': fmt, 'colorize': True
        }

        if kwargs is not None:
            logger.remove()

        logger.add(sys.stdout, **kwargs)

    def format_item(self, item, date_format):
        if item == 'time':
            return '<green><b>{time:' + date_format + '}</b></green>'
        elif item == 'module':
            return '<yellow><b>{module}</b></yellow>'
        elif item == 'function':
            return '<yellow><b>{function}</b></yellow>'
        elif item == 'line':
            return '<yellow><b>{line}</b></yellow>'
        elif item == 'level':
            return '<magenta><b>{level}</b></magenta>'
        elif item == 'message':
            return '<level><b>{message}</b></level>'
        else:
            return '{' + item + '}'

    def load_file(self, name, config):

        file_dir = config['path'] / name / datetime.now().strftime('%Y%m%d')
        tools.mkdir(file_dir)
        file_path = file_dir / (name + ".{time}.log")

        format = config['format']
        level = config['level']
        time_format = config['time_format']
        mode = config['mode']
        size = config['size']
        encoding = config['encoding']
        retention = config['retention']
        kwargs = {}
        fmt = ''

        if config['compression']:
            kwargs['compression'] = 'zip'

        # Formatting file log output
        if isinstance(size, (int, float)):
            size = str(int(size)) + 'B'

        if 'module' in format and 'function' in format and 'line' in format:
            x = '{module}:{function}:{line}'
            format.remove('module')
            format.remove('function')
            format.remove('line')

            msg_index = format.index('message')
            format.insert(msg_index, x) if msg_index > 0 else format.append(x)

        for i in format:
            if i == 'time':
                fmt += '{' + i + ':' + time_format + '} | '
            elif i == '{module}:{function}:{line}':
                fmt += i + ' | '
            else:
                fmt += '{' + i + '} | '

            kwargs = {
                'sink': file_path, 'level': level, 'format': fmt[:-3], 'mode': mode, 'encoding': encoding,
                'rotation': size, 'retention': retention, 'backtrace': True, 'diagnose': True
            }

        logger.add(**kwargs)

    def init_log(self, spider_name, config):

        if not hasattr(config, 'Console') or not hasattr(config, 'File'):
            raise TypeError('日志类型配置错误')

        if hasattr(config, 'Console') and config.Console['engine']:
            self.load_console(config.Console)

        if hasattr(config, 'File') and config.File['engine']:
            self.load_file(spider_name, config.File)
