__all__ = [
    'tools', 'logger', 'pretty_table', 'GlobalConstant'
]

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Union

from loguru import logger
from AioSpider.tools import tools
from AioSpider import settings as sts
from AioSpider.notice import Robot
from AioSpider.utils_pkg.prettytable import PrettyTable


def _get_work_path(path: Path = Path.cwd()):
    if str(path) == str(path.anchor):
        return None

    if {'spider', 'settings.py'} <= {i.name for i in path.iterdir()}:
        return path

    return _get_work_path(path.parent) or None


sys.path.append(str(_get_work_path()))
robot = Robot()


class Browser:

    def __init__(self, browser):
        self.browser = browser
        self._flag = False

    @property
    def flag(self):
        return self._flag

    @flag.setter
    def flag(self, k):
        self._flag = k


class Connector:

    def __init__(self):
        self._c = {}

    def __getitem__(self, name):
        return self._c[name]

    def __setitem__(self, name, conn):
        self._c[name] = conn

    def __contains__(self, item):
        return item in self._c

    def __iter__(self):
        return iter(self._c.keys())

    def __str__(self):
        return str(self._c)

    __repr__ = __str__


class GlobalConstant:

    start_time = None
    data_count = None

    _settings = None
    _download_middleware = None
    _spider_middleware = None
    _connector = None
    _spider = None
    _browser = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            setattr(cls, '_instance', super().__new__(cls))
        return cls._instance

    @property
    def spider(self):
        return self._spider

    @property
    def settings(self) -> sts:
        return self._settings or sts

    @property
    def download_middleware(self):
        return self._download_middleware

    @property
    def spider_middleware(self):
        return self._spider_middleware

    @property
    def connector(self):
        if self._connector is None:
            self._connector = Connector()
        return self._connector

    @property
    def browser(self):
        return self._browser

    @spider.setter
    def spider(self, k):
        self._spider = k

    @settings.setter
    def settings(self, k):
        self._settings = k

    @download_middleware.setter
    def download_middleware(self, k):
        self._download_middleware = k

    @spider_middleware.setter
    def spider_middleware(self, k):
        self._spider_middleware = k

    @connector.setter
    def connector(self, conn_dict: dict):
        for k, v in conn_dict.items():
            self.connector[k] = v

    @browser.setter
    def browser(self, k):
        self._browser = Browser(k)


def pretty_table(item: Union[dict, List[dict]]):

    if isinstance(item, dict):
        item = [item]

    return str(PrettyTable(item=item))


class TableView:

    def __init__(self, items, bold=True):
        self.items = items
        self.bold = bold
        self.colors = [
            'red', 'green', 'yellow', 'magenta', 'cyan',
            'white', 'orange3', 'purple3', 'turquoise4'
        ]

    def console(self):
        from rich.console import Console
        from rich.table import Table

        console = Console()

        # 创建表格
        table = Table(header_style="bold blue", border_style='#d2c1ad')

        for index, k in enumerate(self.items[0].keys()):
            style = 'bold ' + self.colors[index] if self.bold else self.colors[index]
            table.add_column(k, justify="left", style=style, no_wrap=True)
            # table.add_column("Age", justify="center", style="magenta")
            # table.add_column("City", justify="right", style="green")

        for v in self.items:
            table.add_row(*[str(i) for i in v.values()])

        # 输出表格
        console.print(table)
    

def welcom_print():
    words = """
*------------------------------------------------------------------------------------------------------------------------------------------------*
|             __        __   _                                      _                  _    _      ____        _     _                           |
|             \ \      / /__| | ___ ___  _ __ ___   ___          _ | |_ ___           / \  (_) ___/ ___| _ __ (_) __| | ___ _ __                 |
|              \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \        |_  __/ _ \          / _ \ | |/ _ \___ \| '_ \| |/ _` |/ _ \ '__|                |
|               \ V  V /  __/ | (_| (_) | | | | | |  __/          | || (_) |        / ___ \| | (_) |__) | |_) | | (_| |  __/ |                   |
|                \_/\_/ \___|_|\___\___/|_| |_| |_|\___|           \__\___/        /_/   \_\_|\___/____/| .__/|_|\__,_|\___|_|                   |
|                                                                                                       |_|                                      |
*------------------------------------------------------------------------------------------------------------------------------------------------*
    """
    print(words)
