from collections import namedtuple
from datetime import datetime
from typing import Union, Optional, Literal, Dict, Any, Tuple, Type, List

import aiofiles

from AioSpider import tools
from AioSpider import logger
from AioSpider import Connector
from AioSpider import GlobalConstant
from AioSpider import field
from AioSpider.constants import WriteMode
from AioSpider.db.sync_db import SyncMySQLAPI, SyncSQLiteAPI
from AioSpider.db.async_db import AsyncCSVFile
from AioSpider.db.sql import MysqlCreateTable, SqliteCreateTable


RType = Literal['model', 'list', 'dict', 'pd', 'iter']


class ModelConnector:

    databases: Optional[Dict[str, Any]] = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, engine: Optional[str] = None, db: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        self.engine = engine
        self.db = db
        self.config = config

    @property
    def connector(self) -> Any:

        if self.config is None:
            raise Exception('没加载到数据库相关配置')

        if self.databases is None:
            self.databases = self.init_database()

        return self.databases[self.engine][self.db]

    def init_database(self) -> Dict[str, Any]:

        conn_dict = dict()

        # SQLite
        if self.config.get('Sqlite') and self.config['Sqlite']['enabled']:
            conn_dict['sqlite'] = self.init_sqlite()

        # CSV
        if self.config.get('Csv') and self.config['Csv']['enabled']:
            conn_dict['csv'] = self.init_csv()

        # MySQL
        if self.config.get('Mysql') and self.config['Mysql']['enabled']:
            conn_dict['mysql'] = self.init_mysql()

        # MongoDB
        if self.config.get('Mongodb') and self.config['Mongodb']['enabled']:
            conn_dict['mongo'] = self.init_mongo()

        # File
        if self.config.get('File') and self.config['File']['enabled']:
            conn_dict['file'] = self.init_file()

        return conn_dict

    def init_sqlite(self):

        sq_conf = self.config['Sqlite']['CONNECT']
        sqlite_conn = Connector()

        for name, config in sq_conf.items():

            sq_path = config['SQLITE_PATH'] / config['SQLITE_DB']
            sq_timeout = config['SQLITE_TIMEOUT']

            if not sq_path.exists():
                tools.mkdir(sq_path)

            sqlite_conn[name] = SyncSQLiteAPI(path=sq_path, timeout=sq_timeout)

        return sqlite_conn

    def init_csv(self):
        csv_conf = self.config['Csv']['CONNECT']
        csv_conn = Connector()

        for name, config in csv_conf.items():

            csv_path = config['CSV_PATH']
            encoding = config['ENCODING']

            if not csv_path.exists():
                tools.mkdir(csv_path)

            csv_conn[name] = AsyncCSVFile(path=csv_path, encoding=encoding)

        return csv_conn

    def init_mysql(self):

        mysql_conf = self.config['Mysql']['CONNECT']
        mysql_conn = Connector()

        for name, config in mysql_conf.items():

            host = config['MYSQL_HOST']
            port = config['MYSQL_PORT']
            db = config['MYSQL_DB']
            user = config['MYSQL_USER_NAME']
            pwd = config['MYSQL_USER_PWD']
            charset = config['MYSQL_CHARSET']
            timeout = config['MYSQL_CONNECT_TIMEOUT']
            time_zone = config['MYSQL_TIME_ZONE']

            mysql_conn[name] = SyncMySQLAPI(
                host=host, port=port, db=db, user=user, password=pwd,
                connect_timeout=timeout, charset=charset, time_zone=time_zone
            )

        return mysql_conn

    def init_mongo(self):

        mongo_conf = self.config['Mongodb']['CONNECT']
        mongo_conn = Connector()

        for name, config in mongo_conf.items():

            mo_host = config['MONGO_HOST']
            mo_port = config['MONGO_PORT']
            mo_db = config['MONGO_DB']
            mo_user = config['MONGO_USER_NAME']
            mo_pwd = config['MONGO_USER_PWD']

            # mongo_conn[name] = AsyncCSVFile(path=csv_path, encoding=encoding, write_mode=write_mode)

        # conn_dict['mongo'] = mongo_conn
        # self.logger.info(f"MongoDB数据库已启动：\n{pformat(db_engine['MONGODB'])}")
        return mongo_conn

    def init_file(self):

        file_conf = self.config['File']['CONNECT']
        file_conn = Connector()

        for name, config in file_conf.items():

            file_path = config['FILE_PATH']

            if not file_path.exists():
                tools.mkdir(file_path)

            file_conn[name] = config

        return file_conn

    def get_config(self) -> Optional[Dict[str, Any]]:

        try:
            sts = __import__('settings')
        except Exception:
            return None

        if sts is not None and hasattr(sts, 'DataBaseConfig'):
            return {
                k: v for k, v in getattr(sts, 'DataBaseConfig').__dict__.items()
                if not k.startswith('__') or not k.endswith('__')
            }
        else:
            return None

    def __get__(self, instance: Any, owner: Type[Any]) -> Union[Any, 'ModelConnector']:

        if isinstance(self, owner):
            return self

        if owner.Meta.engine is None:
            return self

        ins = self.__class__(
            engine=owner.Meta.engine, db=owner.Meta.db,
            config=owner.Meta.config or self.get_config()
        )

        return ins.connector


class QuerySet:

    def __init__(self, model=None):
        self.model = model
        self._field = None
        self._where = None
        self._count = None

    def __get__(self, instance, owner):
        return self.__class__(model=owner)

    @property
    def database(self):
        return self.model.database

    @property
    def table(self):
        return self.model.Meta.tb_name

    def table_exist(self):
        return self.database.table_exist(table=self.table)

    def create_table(self, *args, **kwargs):

        if issubclass(self.model, SQLiteModel):
            str(SqliteCreateTable(self.model))

        if issubclass(self.model, MySQLModel):
            sql = str(MysqlCreateTable(self.model))

        return self.database.create_table(sql=sql)

    def filter(self, **kwargs):

        if not kwargs:
            return self

        if self._where is None:
            self._where = kwargs
        else:
            self._where.update(kwargs)

        return self

    def only(self, *args):

        if not args:
            return self

        if self._field is None:
            self._field = list(set(args))
        else:
            self._field = list(set(self._field.extend(args)))

        return self

    def like(self, name, value):
        return self.filter(**{f'{name} like': value})

    def limit(self, n: int):
        self._count = n
        return self

    def exists(self):
        if self.get():
            return True
        return False

    def get(self, **kwargs):
        cls = self.filter(**kwargs)
        return cls.find_one(field=self._field, where=self._where)

    def all(self, flat=False, **kwargs):
        cls = self.filter(**kwargs)
        data = cls.find_many(field=self._field, where=self._where, limit=self._count)
        
        if flat:
            return [j for i in data for j in i.values()]
        return data

    def find_one(
            self, field: Union[list, tuple, str, None] = None, limit: Optional[int] = 1,
            offset: Optional[int] = 0, desc: bool = False, order: Union[list, tuple, str, None] = None,
            where: Optional[dict] = None, sql: Optional[str] = None, *args, **kwargs
    ):
        return self.database.find_one(
            table=self.table, field=field, offset=offset, desc=desc, order=order, limit=limit,
            where=where, sql=sql, *args, **kwargs
        )

    def find_many(
            self, field: Union[list, tuple, str, None] = None, limit: Optional[int] = None,
            offset: Optional[int] = None, desc: bool = False, order: Union[list, tuple, str, None] = None,
            where: Optional[dict] = None, sql: Optional[str] = None, *args, **kwargs
    ):
        return self.database.find_many(
            table=self.table, field=field, offset=offset, desc=desc, limit=limit,
            order=order, where=where, sql=sql, *args, **kwargs
        )

    def insert(self, items: Union[dict, List[dict]], sql: Optional[str] = None):
        
        if isinstance(items, dict):
            items = [items]

        return self.database.insert(table=self.table, items=items, sql=sql, auto_update=self.model.Meta.auto_update)

    def update(self, items: Union[dict, list], where: Union[str, list, tuple] = None):
        return self.database.update(table=self.table, items=items, where=where)

    def delete_one(self, where: dict, sql: str = None, *args, **kwargs) -> None:
        return self.database.delete_one(table=self.table, where=where, sql=sql, *args, **kwargs)

    def delete_many(self, where: dict, *args, **kwargs):
        return self.database.delete_many(table=self.table, where=where, *args, **kwargs)


class BaseModel(type):
    """
    基础模型元类
    """

    _MetaDefaults = namedtuple('MetaDefaults', [
        'abstract', 'encoding', 'write_mode', 'commit_size', 'engine', 'db', 'tb_name', 'config',
        'init_id', 'read_only', 'auto_update', 'union_index', 'union_unique_index'
    ])

    meta_defaults: _MetaDefaults = _MetaDefaults(
        abstract=True, encoding=None, write_mode=None, commit_size=1000, engine=None,  db='DEFAULT', tb_name=None,
        config=None, init_id=None, read_only=False, auto_update=True, union_index=None, union_unique_index=None
    )

    def __new__(cls, name: str, bases: Tuple, attrs: Dict[str, Any]) -> type:
        """
        创建新类
        """

        # 获取父类的所有字段
        fields = {k: v for base in bases for k, v in getattr(base, 'fields', {}).items()}
        fields = cls.overwrite_fields(fields, attrs)

        # 过滤掉新类中与父类重复的字段
        new_attrs = {
            k: v for k, v in attrs.items() if not (
                isinstance(v, field.Field) and fields.setdefault(k, v)
            )
        }

        # 排序字段，确保字段顺序
        if fields:
            fields = cls.order_field(new_attrs, fields)

        # 添加新类字段
        new_attrs["fields"] = fields
        new_attrs.update(fields)
        model_class = super().__new__(cls, name, bases, new_attrs)

        # 创建 Meta 类
        base_meta = getattr(bases[0], 'Meta', None) if bases else None
        model_meta = attrs.get('Meta', None)

        # 合并元类属性
        meta_attrs = {
            **cls.meta_defaults._asdict(),
            **getattr(base_meta, '__dict__', {}),
            **getattr(model_meta, '__dict__', {}),
            **{k: v for k, v in attrs.get('meta', {}).items() if k in cls.meta_defaults._fields}
        }

        # 设置 abstract 属性
        meta_attrs['abstract'] = False
        if getattr(model_meta, '__dict__', {}).get('abstract'):
            meta_attrs['abstract'] = True

        if attrs.get('meta', {}).get('abstract'):
            meta_attrs['abstract'] = True

        if meta_attrs['abstract']:
            meta_attrs['__abstractmethods__'] = frozenset(['__str__', '__repr__'])

        if not hasattr(model_meta, 'tb_name'):
            meta_attrs['tb_name'] = cls.get_name(name)

        # 创建 Meta 类并添加到新类中
        model_class.Meta = type('Meta', (base_meta or object,), meta_attrs)

        return model_class

    @classmethod
    def order_field(cls, attrs: Dict[str, Any], fields: Dict[str, field.Field]) -> Dict[str, field.Field]:

        if 'order' in attrs:
            order = ['id'] + attrs.pop('order', []) + ['source', 'create_time', 'update_time']
            ordered_fields = list(dict.fromkeys(order + list(fields.keys())))
        else:
            ordered_fields = list(fields.keys())

        for i in ordered_fields[:]:

            if i not in fields or not isinstance(fields[i], field.HashField):
                continue

            make_hash_field = fields[i].make_hash_field

            if make_hash_field is None:
                # 将没有指定哈希字段的字段移到最后
                ordered_fields.remove(i)
                ordered_fields.append(i)
            elif isinstance(make_hash_field, (str, field.Field)):
                # 处理哈希字段为字符串或字段对象的情况
                x = next((k for k, v in fields.items() if v is make_hash_field), '')
                if x and x in ordered_fields and ordered_fields.index(i) < ordered_fields.index(x):
                    # 将当前字段移到哈希字段之后
                    ordered_fields.remove(i)
                    ordered_fields.insert(ordered_fields.index(x) + 1, i)
            elif isinstance(make_hash_field, (tuple, list)):
                # 处理哈希字段为元组或列表的情况
                max_index = max(
                    ordered_fields.index(k) if isinstance(k, str) else ordered_fields.index(k) for x in make_hash_field
                    for k, v in fields.items() if v is x or k is x
                )
                if ordered_fields.index(i) < max_index:
                    # 将当前字段移到哈希字段集合中最后一个字段之后
                    ordered_fields.remove(i)
                    ordered_fields.insert(max_index + 1, i)

        return {k: fields[k] for k in ordered_fields if k in fields}

    @classmethod
    def overwrite_fields(cls, fields: Dict[str, Any], attrs: Dict[str, Any]) -> Dict:
        fields.update({k: v for k, v in attrs.items() if isinstance(v, field.Field) or k in fields})
        return {k: v for k, v in fields.items() if v is not None}

    @classmethod
    def get_name(cls, name) -> str:

        name_type = GlobalConstant().settings.DataFilterConfig.MODEL_NAME_TYPE

        if name_type == 'lower':
            return name.lower().replace('model', '')
        elif name_type == 'upper':
            name = cls.__name__
            return name.upper().replace('MODEL', '')
        else:
            name = name.replace('model', '').replace('Model', '')
            name = tools.re(regx='[A-Z][^A-Z]*', text=name)
            name = [i.lower() for i in name]
            return '_'.join(name)


class Model(metaclass=BaseModel):

    database = ModelConnector()
    objects = QuerySet()

    def __init__(self, *args, **kwargs):

        item = args[0] if args and isinstance(args[0], dict) else kwargs

        self.create_time = datetime.now()
        self.update_time = datetime.now()
        self.source = GlobalConstant().spider.source

        item = self.clean(item)

        for k in self.fields:
            if k not in item:
                continue
            setattr(self, k, item[k])

    @classmethod
    def get_unique_field(cls, include_id=False):
        unique_fields = [field for field, props in cls.fields.items() if props.unique]
        if not include_id and 'id' in unique_fields:
            unique_fields.remove('id')
        unique_fields = sorted(unique_fields, key=lambda field: list(cls.fields.keys()).index(field))
        return unique_fields

    def make_item(self):

        item = {}

        item = {f: getattr(self, f) for f, field in self.fields.items() if field.is_save}

        if 'id' in item:
            item.pop('id')

        return item

    def clean(self, item):
        return item

    def save(self):
        self.id = self.objects.insert(items=self.make_item())
        data = self.objects.get(id=self.id)
        for field in self.fields:
            if field not in data:
                continue
            setattr(self, field, data[field])

    def delete(self):
        item = self.make_item()
        return self.objects.delete_one()

    def update(self):
        item = {k: v for k, v in self.make_item().items() if v}
        self.objects.update(items=item, where='id')

    def __str__(self):
        return f'{self.__class__.__name__} {self.id}'

    __repr__ = __str__


class ABCModel(Model):
    
    class Meta:
        abstract = True

    id = field.AutoIntField(name='主键', primary=True)
    source = field.CharField(name='数据源', max_length=50)
    create_time = field.DateTimeField(name='创建时间', auto_add=True)
    update_time = field.DateTimeField(name='更新时间', auto_add=True, auto_update=True)


class SQLiteModel(ABCModel):

    class Meta:
        engine = 'sqlite'


class MySQLModel(ABCModel):

    class Meta:
        engine = 'mysql'


class FileModel(ABCModel):

    class Meta:
        encoding = 'utf-8'             # 文件编码格式
        mode = 'wb'                    # 文件打开模式
        engine = 'file'

    _base = None

    name = field.CharField(name='文件名', max_length=255)
    path = field.PathField(name='文件夹路径', max_length=255)
    extension = field.ExtensionNameField(name='拓展名')
    content = field.BytesContentField(name='内容')

    order = [
        'name', 'path', 'extension', 'content', 'source', 'create_time', 'update_time'
    ]

    def __init__(self, name=None, path=None, extension=None, content=None, *args, **kwargs):
        super(FileModel, self).__init__(
            name=name, path=path, extension=extension, content=content, *args, **kwargs
        )

    @property
    def base_path(self):
        if self._base is None:
            sts = GlobalConstant().settings.DataBaseConfig
            if hasattr(sts, 'File'):
                self._base = sts.File['CONNECT'][self.Meta.db]['FILE_PATH']
            else:
                self._base = ''
        return self._base

    async def save(self):

        if self.Meta.mode in ['w', 'w+', 'a', 'a+'] and isinstance(self.content, bytes):
            content = self.content.decode(self.Meta.encoding)
        elif self.Meta.mode in ['wb', 'wb+', 'ab', 'ab+'] and isinstance(self.content, str):
            content = self.content.encode(self.Meta.encoding)
        else:
            content = self.content

        path = self.base_path / str(self.path)

        if not path.exists():
            tools.mkdir(path)

        if self.Meta.mode in ['wb', 'wb+', 'ab', 'ab+']:
            fopen = aiofiles.open(
                str(path / (self.name + self.extension)), self.Meta.mode
            )
        else:
            fopen = aiofiles.open(
                str(path / (self.name + self.extension)), self.Meta.mode, encoding=self.Meta.encoding
            )

        try:
            async with fopen as fp:
                await fp.write(self.content)
        except OSError:
            logger.error(f'{str(self.path / (self.name + self.extension))}：文件路径中有特殊字符，请手动处理')


class CSVModel(ABCModel):

    class Meta:
        engine = 'csv'
        encoding = 'utf-8'
        write_mode = WriteMode.A


class ImageModel(FileModel):
    extension = field.ExtensionNameField(name='拓展名', default='png')


class AiospiderModel(ABCModel):
    """AioSpider总表数据结构"""

    name = field.CharField(name='表名')
    db = field.DateTimeField(name='库名')
    status = field.BoolField(name='表状态。0：废弃，1：正常', default=True)

    order = [
        'id', 'name', 'db', 'status', 'source', 'create_time', 'update_time'
    ]


class SpiderModel(ABCModel):
    """爬虫数据结构"""

    SPIDER_STATUS_TYPE = (
        ('未开始', 0), ('进行中', 1), ('成功', 2), ('异常', 3),
    )
    DEV_STATUS_TYPE = (
        ('开发中', 0), ('测试中', 1), ('已上线', 2), ('维护中', 3), ('已废弃', 4)
    )
    RUN_LEVEL_TYPE = (
        ('秒级', 0), ('分级', 1), ('时级', 2), ('日级', 3), ('周级', 4), ('月级', 5),
        ('季级', 6), ('年级', 7)
    )

    # site = models.ForeignKey(
    #     SiteModel, on_delete=models.SET_NULL, verbose_name='所属站点', db_column='site',
    #     null=True, blank=True, related_name='spider'
    # )
    name = field.CharField(name='爬虫名称', max_length=20, null=False, unique=True)
    target = field.CharField(name='目标页面', max_length=255,  null=False)
    description = field.TextField(name='描述', null=True)
    status = field.TinyIntField(name='运行状态', choices=SPIDER_STATUS_TYPE, default=0)
    dev_status = field.TinyIntField(name='开发状态', choices=DEV_STATUS_TYPE, default=0)
    start_time = field.TimeField(name='启动时间', default=None)
    last_run_time = field.DateTimeField(name='最近运行时间', default=None, null=True)
    level = field.TinyIntField(name='运行级别', choices=RUN_LEVEL_TYPE, default=0)
    count = field.IntField(name='运行次数', default=0)
    interval = field.MediumIntField(name='时间间隔')
    version = field.CharField(name='版本号', max_length=120, default='1.0')

    order = [
        'id', 'name', 'target', 'description', 'status', 'dev_status', 'start_time', 'last_run_time',
        'level', 'count', 'interval', 'version', 'source', 'create_time', 'update_time'
    ]


class TaskModel(ABCModel):
    """批次爬虫任务数据结构"""

    TASK_STATUS_TYPE = (
        ('未开始', 0), ('进行中', 1), ('成功', 2), ('异常', 3),
    )

    spider = field.CharField(name='爬虫名称', max_length=150)
    start_time = field.DateTimeField(name='启动时间')
    end_time = field.DateTimeField(name='结束时间')
    status = field.TinyIntField(name='任务状态', choices=TASK_STATUS_TYPE, default=0)
    data_count = field.IntField(name='数据条数', default=0)
    running_time = field.IntField(name='运行时间(s)', default=0)
    success_request_count = field.IntField(name='成功请求数量', default=0)
    failure_request_count = field.IntField(name='失败请求数量', default=0)

    order = [
        'id', 'spider', 'start_time', 'end_time', 'status', 'data_count', 'running_time',
        'success_request_count', 'failure_request_count', 'source', 'create_time', 'update_time'
    ]


class UserAcount(ABCModel):

    username = field.CharField(name='登录账号')
    password = field.CharField(name='登录密码')
    cookies = field.TextField(name='cookies')
    token = field.CharField(name='token')

    order = [
        'id', 'username', 'password', 'cookies', 'token',
        'source', 'create_time', 'update_time'
    ]


class ProxyPoolModel(ABCModel):
    """IP代理池数据结构"""

    brand = field.CharField(name="代理服务商名称", max_length=50)
    ip = field.CharField(name="ip地址", max_length=20, null=False)
    port = field.SmallIntField(name="端口", null=False)
    protocol = field.CharField(name="ip协议", max_length=20, null=False)
    username = field.CharField(name="用户名", max_length=50)
    password = field.CharField(name="密码", max_length=50)
    status = field.BoolField(name="ip是否可用", default=True)
    address = field.CharField(name="ip城市地址", max_length=20)
    operator = field.CharField(name="运营商", max_length=20)
    weight = field.FloatField(name="分配权重", null=False, default=0.1)
    use_count = field.IntField(name="使用次数", null=False, default=0)
    weekday = field.IntField(name="周一 ~ 周日，0开始，周一：0；周日：6", null=False, default=0)
    running = field.BoolField(name="是否正在使用，1：正在使用，1：未使用", default=False)
    due_date = field.DateField(name="截止日期")
    remark1 = field.CharField(name="备注1", max_length=255)
    remark2 = field.CharField(name="备注2", max_length=255)
    remark3 = field.CharField(name="备注3", max_length=255)

    order = [
        'brand', 'ip', 'port', 'protocol', 'username', 'password', 'status', 'address', 'operator', 
        'weight', 'use_count', 'weekday', 'running', 'due_date', 'remark1' 'remark2', 'remark3', 
        'source', 'create_time', 'update_time'
    ]


class NoticeModel(BaseModel):

    LEVEL_CHOICES = (
        ('调试', 'DEBUG'), ('信息', 'INFO'), ('警告', 'WARNING'), ('异常', 'DEBUG'), ('崩溃', 'DANGEROUS')
    )
    TYPE_CHOICES = (
        ('通知', 'NOTICE'), ('预警', 'WARNING')
    )
    PLATFORM_CHOICES = (
        ('企业微信', 'WECHAT'), ('钉钉', 'DINGDING'), ('邮件', 'EMAIL')
    )

    # spider = field.ForeignKey(
    #     'spider.SpiderModel', on_delete=models.CASCADE, verbose_name='所属爬虫', related_name='notice',
    #     null=True, blank=True
    # )
    level = field.CharField('等级', max_length=20, choices=LEVEL_CHOICES, default='INFO')
    type = field.CharField('类型', max_length=20,  choices=TYPE_CHOICES, default='INFO')
    platform = field.CharField('平台', max_length=20, choices=PLATFORM_CHOICES, default='WECHAT')
    message = field.CharField('消息', max_length=20, )

    # class Meta:
    #     db_table = 'notice'
    #     verbose_name = '消息预警'
    #     verbose_name_plural = '预警类型'
