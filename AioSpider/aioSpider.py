import re
import sys
from pathlib import Path
from abc import ABCMeta, abstractmethod

from AioSpider.template import create_project as cpj
from AioSpider.template import gen_spider as gs
from AioSpider import tools


class AioSpiderOptions(metaclass=ABCMeta):
    """command options base class"""

    @abstractmethod
    def __init__(self):
        self.p = None

    def __str__(self):
        return self.p

    def __repr__(self):
        return self.p


class AioSpiderOptionsP(AioSpiderOptions):
    def __init__(self):
        self.p = '-p'


class AioSpiderOptionsS(AioSpiderOptions):
    def __init__(self):
        self.p = '-s'


class AioSpiderOptionsI(AioSpiderOptions):
    def __init__(self):
        self.p = '-i'


class AioSpiderOptionsO(AioSpiderOptions):
    def __init__(self):
        self.p = '-o'


class AioSpiderOptionsH(AioSpiderOptions):
    def __init__(self):
        self.p = '-h'


class AioSpiderCommandName:
    """声明命令模式接口"""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class AioSpiderCommand(metaclass=ABCMeta):
    """声明命令模式接口"""

    @abstractmethod
    def execute(self):
        pass


class HelpCommand(AioSpiderCommand):

    def execute(self):
        print("""
        aioSpider帮助系统语法：aioSpider [action] [-argv] 

        aioSpider -h: 查看帮助
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
            -argv:
                -i: 输入路径(inputPath)
                -o: 输出路径(outputPath)
        """)

    def add_name(self, *args, **kwargs):
        pass

    def add_option(self, *args, **kwargs):
        pass


class CreateCommand(AioSpiderCommand):

    def __init__(self):
        self.names = []
        self.options = None

    def execute(self):
        if isinstance(self.options, AioSpiderOptionsP):
            self.create_project()
        elif isinstance(self.options, AioSpiderOptionsS):
            self.create_spider()
        else:
            raise Exception(f'options error, AioSpider create 没有该参数，AioSpider {AioSpiderOptionsH()} 查看帮助')

    def create_project(self):
        """创建项目: aioSpider create -p <name>"""

        if not self.names:
            raise Exception(
                f'aioSpider create -p <name>, Do you forget inout project name? AioSpider {AioSpiderOptionsH()} 查看帮助'
            )

        items = cpj(self.names[0])

        for item in items:
            if item['type'] == 'dir' and not item['path'].exists():
                item['path'].mkdir(parents=True, exist_ok=True)

        for item in items:
            if item['type'] == 'file' and not item['path'].exists():
                item['path'].write_text(item['text'], encoding='utf-8')

    def create_spider(self):
        """创建爬虫 aioSpider create -s <name> <start_url>"""

        if not self.names:
            raise Exception(
                f'aioSpider create -p <name>, Do you forget inout project name? AioSpider {AioSpiderOptionsH()} 查看帮助'
            )

        if len(self.names) >= 2:
            name, *start_url = self.names
        else:
            name, start_url = self.names[0], None

        spider_text = gs(name, start_url)
        path = Path().cwd() / f'spider/{name}.py'
        if not path.exists():
            path.write_text(spider_text, encoding='utf-8')

    def add_name(self, name: AioSpiderCommandName):
        self.names.append(name)

    def add_option(self, option: AioSpiderOptions):
        if self.options is None:
            self.options = option


class MakeCommand(AioSpiderCommand):

    def __init__(self):
        self.names = []
        self.options = []

    def execute(self):

        if not self.names:
            raise Exception(f'AioSpider make error，AioSpider {AioSpiderOptionsH()} 查看帮助')
        elif self.names[0].name == 'model':
            self.names = self.names[1:]
            self.make_model()
        elif self.names[0].name == 'spider':
            self.names = self.names[1:]
            self.make_spider()
        else:
            raise Exception(f'AioSpider make error，AioSpider {AioSpiderOptionsH()} 查看帮助')

    def make_model(self):
        """sql转换成模型 aioSpider make model -i sqlFilePath -o <outPath>"""

        class Field:

            __name__ = ''

            def __init__(
                    self, field, name, max_length=None, blank=True, null=True, default=None,
                    unique=False, dnt_filter=False
            ):
                self.field = field
                self.name = name
                self.max_length = max_length
                self.blank = blank
                self.null = null
                self.default = default
                self.unique = unique
                self.dnt_filter = dnt_filter

            def __str__(self):

                model_str = f'    {name} = models.{self.__name__}(name=\"{comment}\"'
                self.default = self.default if self.default != "null" else None

                if self.max_length:
                    model_str += f', max_length={self.max_length}'
                if not self.blank:
                    model_str += f', blank={self.null}'
                if not self.null:
                    model_str += f', null={self.null}'
                if self.default is not None:
                    model_str += f', default={self.default}'
                if self.unique:
                    model_str += f", unique={self.unique}, "
                if self.dnt_filter:
                    model_str += f"dnt_filter={self.dnt_filter}"

                return model_str + f")\n"

        class CharField(Field):
            __name__ = 'CharField'

        class AutoIntField:

            def __init__(self, field, name):
                self.field = field
                self.name = name

            def __str__(self):
                return f"    {self.field} = models.AutoIntField(name=\"{self.name}\", auto_field='AUTO_INCREMENT')\n"

        class IntField(Field):
            __name__ = 'IntField'

        class TextField(Field):
            __name__ = 'TextField'

        class FloatField(Field):
            __name__ = 'FloatField'

        class DateTimeField(Field):
            __name__ = 'DateTimeField'

        class DateField(Field):
            __name__ = 'DateField'

        class StampField(Field):
            __name__ = 'StampField'

        in_path = out_path = None
        order = []

        for i, o in enumerate(self.options):
            if isinstance(o, AioSpiderOptionsI):
                in_path = Path(self.names[i].name)
            elif isinstance(o, AioSpiderOptionsO):
                out_path = Path(self.names[i].name)
            else:
                continue

        if in_path is None:
            raise Exception(f'AioSpider make error，no sql input. AioSpider {AioSpiderOptionsH()} 查看帮助')

        sql = in_path.read_text(encoding='utf-8')

        if 'create' not in sql and 'CREATE' not in sql:
            raise Exception('请输入正确的sql语句，ex: CREATE TABLE xxx ...')

        table = re.findall(r'TABLE(.*?)\(', sql) or re.findall(r'table(.*?)\(', sql)
        if table:
            table = table[0].strip().replace('`', '').replace('\'', '').replace('\"', '')
            if '_' in table:
                table = ''.join([i.title() for i in table.split('_')])
        else:
            raise Exception('没有匹配到table，输入的sql有误')

        field_str = re.findall(r'\((.*)\)', sql, re.S)
        if field_str:
            field_str = field_str[0].strip()
        else:
            raise Exception('没有匹配到创建的字段，输入的sql有误')

        if 'comment' in sql.split('\n')[-1].lower():
            doc = re.findall("COMMENT='(.*?)'", sql.split('\n')[-1])
            doc = doc[0] if doc else None
        else:
            doc = None

        if doc is None:
            model_str = f'from AioSpider import models\n\n\nclass {table}Model(models.Model):\n\n'
        else:
            model_str = f'from AioSpider import models\n\n\nclass {table}Model(models.Model):\n    """{doc}模型"""\n\n'
        for f in field_str.split('\n'):
            x = f.strip().split()
            name = x[0].replace('`', '').replace('\'', '').replace('\"', '')

            if 'comment' in f.lower():
                comment = re.findall('comment(.*),', f.lower())
                comment = comment[0] if comment else name
                comment = comment.strip().replace('`', '').replace('\'', '').replace('\"', '')
            else:
                comment = name

            if name in ['PRIMARY', 'UNIQUE', 'KEY', 'primary', 'unique', 'id', ')']:
                continue

            if 'not null' in f.lower():
                null = False
            else:
                null = True

            if 'unique' in f.lower():
                unique = True
                dnt_filter = True
            else:
                unique = False
                dnt_filter = False

            if 'default' in f.lower():
                default = re.findall('default (.*?) ', f.lower())
                default = default[0] if default else None
            else:
                default = None

            if 'int' in f.lower():
                if 'auto_increment' in f.lower() or 'autoincrement' in f.lower():
                    model_str += str(AutoIntField(field=name, name=comment))
                else:
                    model_str += str(IntField(
                        field=name, name=comment, blank=null, null=null, default=default, dnt_filter=dnt_filter
                    ))

            if 'float' in f.lower() or 'double' in f.lower() or 'decimal' in f.lower():
                model_str += str(FloatField(
                    field=name, name=comment, blank=null, null=null, default=default, dnt_filter=dnt_filter
                ))

            if 'varchar' in f.lower() or 'char' in f.lower():
                max_length = re.findall(r'varchar\(([\d]+)\)', f.lower())
                max_length = max_length[0] if max_length else 255
                model_str += str(CharField(
                    field=name, name=comment, max_length=max_length, blank=null, null=null, default=default,
                    unique=unique, dnt_filter=dnt_filter
                ))

            if 'text' in f.lower():
                model_str += str(TextField(
                    field=name, name=comment, blank=null, null=null, default=default, unique=unique,
                    dnt_filter=dnt_filter
                ))

            if ' datetime ' in f.lower():
                model_str += str(DateTimeField(
                    field=name, name=comment, blank=null, null=null, default=default,
                    unique=unique, dnt_filter=dnt_filter
                ))

            if ' date ' in f.lower():
                model_str += str(DateField(
                    field=name, name=comment, blank=null, null=null, default=default,
                    unique=unique, dnt_filter=dnt_filter
                ))

            if ' timestamp ' in f.lower():
                model_str += str(StampField(
                    field=name, name=comment, blank=null, null=null, default=default,
                    unique=unique, dnt_filter=dnt_filter
                ))

            order.append(name)

        model_str += f'\n    order = {str(order)}\n'

        out_path = out_path if out_path is not None else Path(f'{table}.py')
        out_path.write_text(model_str, encoding='utf-8')

    def make_spider(self):
        """curl 转换成 spider：aioSpider make spider -i <inputPath> -o <outPath>"""

        in_path = out_path = None
        for i, o in enumerate(self.options):
            if isinstance(o, AioSpiderOptionsI):
                in_path = Path(self.names[i].name)
            elif isinstance(o, AioSpiderOptionsO):
                out_path = Path(self.names[i].name)
            else:
                continue

        if in_path is None:
            raise Exception(f'AioSpider make error，no curl input. AioSpider {AioSpiderOptionsH()} 查看帮助')

        curl = in_path.read_text(encoding='utf-8')

        url = re.findall('curl \'(.*?)\'', curl)
        if url:
            url = url[0]
        else:
            raise Exception('没有匹配到url')

        params = tools.extract_params(url)
        url = tools.extract_url(url)

        try:
            headers = {
                i.split(': ')[0].strip().replace('\n', '').replace('\r', '').replace('  ', ''):
                    i.split(': ')[-1].strip().replace('\n', '').replace('\r', '').replace('  ', '')
                for i in re.findall('-H \'(.*?)\'', curl, re.S)}
        except:
            headers = None

        body = re.findall('--data-binary \'(.*?)\'', curl, re.S)
        if body:
            body = body[0]
        else:
            body = None

        tmp = 'from AioSpider import tools\nfrom AioSpider.http import Request, FormRequest\nfrom AioSpider.spider im' \
              f'port Spider\n\n\nclass DemoSpider(Spider):\n\n    name = "demoSpider"\n    start_urls = [\n{" " * 8}"' \
              f'{url}"\n{" " * 4}]\n\n    def start_request(self):\n{" " * 8}for url in self.start_urls:\n{" " * 12}y' \
              f'ield {"FormRequest" if body else "Request"}(\n{" " * 16}url=url, \n{" " * 16}callback=self.parse'

        if headers:
            tmp += f",\n{' ' * 16}headers={headers}"

        if params:
            tmp += f",\n{' ' * 16}params={params}"

        if body:
            tmp += f",\n{' ' * 16}body={body}"

        tmp += f'\n{" " * 12})\n\n{" " * 4}def parse(self, response):\n{" " * 8}self.logger(response)\n\n\nif __name_' \
               f'_ == "__main__":\n{" " * 4}spider = DemoSpider()\n{" " * 4}spider.start()'

        out_path = out_path if out_path is not None else Path('demoSpider.py')
        out_path.write_text(tmp, encoding='utf-8')

    def add_name(self, name: AioSpiderCommandName):
        self.names.append(name)

    def add_option(self, option: AioSpiderOptions):
        self.options.append(option)


class Client:

    def __init__(self, argv: list):
        """装配者"""

        if not isinstance(argv, list):
            raise Exception(f'aioSpider command error, aioSpider {AioSpiderOptionsH()} 查看帮助')

        if len(argv) <= 1:
            raise Exception(f'aioSpider command error, aioSpider {AioSpiderOptionsH()} 查看帮助')

        if argv[0].rstrip('.py') != 'aioSpider':
            raise Exception(f'aioSpider command error, aioSpider {AioSpiderOptionsH()} 查看帮助')

        if argv[1] == 'create':
            argv = argv[2:]
            cmd = CreateCommand()
        elif argv[1] == 'make':
            argv = argv[2:]
            cmd = MakeCommand()
        elif argv[1] == '-h':
            argv = argv[2:]
            cmd = HelpCommand()
        else:
            raise Exception(f'aioSpider command error, aioSpider {AioSpiderOptionsH()} 查看帮助')

        for i in argv:
            if '-' in i:
                if i == '-p':
                    cmd.add_option(AioSpiderOptionsP())
                elif i == '-s':
                    cmd.add_option(AioSpiderOptionsS())
                elif i == '-i':
                    cmd.add_option(AioSpiderOptionsI())
                elif i == '-o':
                    cmd.add_option(AioSpiderOptionsO())
            else:
                cmd.add_name(AioSpiderCommandName(i))

        cmd.execute()
