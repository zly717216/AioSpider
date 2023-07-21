import re
from pathlib import Path

from AioSpider.cmd.cmd import AioSpiderCommand, CommandName
from AioSpider.cmd.args import AioSpiderArgs, ArgsI, ArgsO, ArgsH


class MakeCommand(AioSpiderCommand):

    def execute(self):

        if not self.command_name:
            raise Exception(f'AioSpider make error，AioSpider {ArgsH()} 查看帮助')
        elif self.command_name.name == 'model':
            self.make_model()
        elif self.command_name.name == 'bat':
            self.make_bat()
        else:
            raise Exception(f'AioSpider make error，AioSpider {ArgsH()} 查看帮助')

    def make_model(self):
        """sql转换成数据结构 aioSpider make model -i sqlFilePath -o <outPath>"""

        class Field:

            def __init__(
                    self, field, name, max_length=None, null=True, default=None,
                    unique=False
            ):
                self.field = field
                self.name = name
                self.max_length = max_length
                self.null = null
                self.default = default
                self.unique = unique

            def __str__(self):

                model_str = f'    {name} = models.{self.__class__.__name__}(name=\"{comment}\"'
                self.default = self.default if self.default != "null" else None

                if self.max_length:
                    model_str += f', max_length={self.max_length}'
                if not self.null:
                    model_str += f', null={self.null}'
                if self.default is not None:
                    if isinstance(self.default, str) and self.default.lower() == 'current_timestamp':
                        model_str += f', default="{self.default}"'
                    else:
                        model_str += f', default={self.default}'
                if self.unique:
                    model_str += f", unique={self.unique}, "

                return model_str + f")\n"

        class CharField(Field):
            pass

        class AutoIntField:

            def __init__(self, field, name):
                self.field = field
                self.name = name

            def __str__(self):
                return f"    {self.field} = models.AutoIntField(name=\"{self.name}\")\n"

        class IntField(Field):
            pass

        class TextField(Field):
            pass

        class FloatField(Field):
            pass

        class DateTimeField(Field):
            pass

        class DateField(Field):
            pass

        in_path = out_path = None
        for arv in self.args:
            if isinstance(arv, ArgsI):
                in_path = Path(arv.name)
            elif isinstance(arv, ArgsO):
                out_path = Path(arv.name)
            else:
                continue

        if in_path is None:
            raise Exception(f'AioSpider make error，no sql input. AioSpider {ArgsH()} 查看帮助')

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
            model_str = f'from AioSpider import models\n\n\nclass {table}Model(models.Model):\n    """{doc}数据结构"""\n\n'
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
            else:
                unique = False

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
                        field=name, name=comment, null=null, default=default
                    ))

            elif 'float' in f.lower() or 'double' in f.lower() or 'decimal' in f.lower():
                model_str += str(FloatField(
                    field=name, name=comment, null=null, default=default
                ))

            elif 'varchar' in f.lower() or 'char' in f.lower():
                max_length = re.findall(r'varchar\(([\d]+)\)', f.lower())
                max_length = max_length[0] if max_length else 255
                model_str += str(CharField(
                    field=name, name=comment, max_length=max_length, null=null, default=default,
                    unique=unique
                ))

            elif 'text' in f.lower():
                model_str += str(TextField(
                    field=name, name=comment, null=null, default=default, unique=unique,
                ))

            elif 'datetime' in f.lower():
                model_str += str(DateTimeField(
                    field=name, name=comment, null=null, default=default,
                    unique=unique
                ))

            elif 'date' in f.lower():
                model_str += str(DateField(
                    field=name, name=comment, null=null, default=default,
                    unique=unique
                ))

            else:
                pass

        out_path = out_path if out_path is not None else Path(f'{table}.py')
        out_path.write_text(model_str, encoding='utf-8')

    def make_bat(self, path: Path = None):
        """生成 bat 脚本：aioSpider make bat -o <outPath>"""
        spider_path = path or Path.cwd() / 'spider'
        for i in spider_path.iterdir():
            if i.name in ['__init__.py', '__pycache__']:
                continue
            if i.is_file():
                with open('run.bat', 'a') as f:
                    f.write(f'start cmd /k "python {i}\n')
            if i.is_dir():
                self.make_bat(i)

    def add_name(self, name: CommandName):
        self.command_name = name

    def add_args(self, args: AioSpiderArgs):
        self.args.append(args)
