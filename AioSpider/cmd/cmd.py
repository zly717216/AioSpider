from abc import ABCMeta, abstractmethod
from typing import Callable
from pathlib import Path


class CommandName:
    """声明命令模式接口"""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class AioSpiderCommand(metaclass=ABCMeta):
    """声明命令模式接口"""
    
    def __init__(self):
        self.command_name = None
        self.args = []
        self.options = []

    @abstractmethod
    def execute(self):
        pass


class HelpCommand(AioSpiderCommand):

    def execute(self):
        print("""aioSpider帮助系统语法：aioSpider [action] [-argv] 
    aioSpider -h: 查看帮助
    aioSpider list: 查看项目路径下所有的爬虫
    aioSpider create -argv <name> [params]
        -argv:
            -p: 创建项目(project)
                exp: aioSpider create -p baiduSpiderProject
            -s: 创建爬虫(spider)
                exp: aioSpider create -s baiduSpider
                exp: aioSpider create -s baiduSpider https://wwww.baidu.com
    aioSpider make sth -argv
        sth:
            model : 将 sql 中的建表语句转换成 AioSpider 的 models
                exp: aioSpider make model -i D:\\create_table.txt
                exp: aioSpider make model -i D:\\create_table.txt -o D:\\model.py
            spider: 将 curl 脚本转换成 AioSpider 的 spider 
                exp: aioSpider make spider -i D:\\curl.txt
                exp: aioSpider make spider -i D:\\curl.txt -o D:\\spider.py
            bat: 将项目路径下所有爬虫脚本集中在 bat 中 
                exp: aioSpider make bat
                exp: aioSpider make spider -i -o D:\\run.bat
        -argv:
            -i: 输入路径(inputPath)
            -o: 输出路径(outputPath)
        """)

    def add_name(self, *args, **kwargs):
        pass

    def add_args(self, *args, **kwargs):
        pass


class VirsionCommand(AioSpiderCommand):

    def execute(self):
        print('AioSpider的当前版本为：' + (Path(__file__).parent.parent / '__version__').read_text(encoding='utf-8'))

    def add_name(self, *args, **kwargs):
        pass

    def add_args(self, *args, **kwargs):
        pass


class ListCommand(AioSpiderCommand):

    def execute(self):
        try:
            spiders = __import__('spider')
        except ModuleNotFoundError:
            print('没有找到spider目录，请检查是否切换到项目路径！')
            return

        if spiders:
            spiders = [getattr(spiders, i) for i in dir(spiders) if '__' not in i]
            spiders = [i.__name__ for i in spiders if isinstance(i, Callable)]
            print(spiders)
        else:
            print()

    def add_name(self, *args, **kwargs):
        pass

    def add_args(self, *args, **kwargs):
        pass
