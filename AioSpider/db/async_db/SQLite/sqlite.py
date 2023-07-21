from pathlib import Path
from typing import Optional, Union, List, Any, Literal, TypeVar, Iterator

import aiosqlite
import pandas as pd

from AioSpider import tools, logger
from AioSpider.db.sql import Select, SqliteInsert, SQLiteUpdate
from AioSpider.db.async_db.async_abc import AbcDB

DataType = Literal['list', 'dict', 'pd', 'iter']
RType = TypeVar('RType', list, dict, pd.DataFrame, Iterator)


class DescField:
    field: str = None
    type: str = None
    null: bool = None
    key: str = None
    length: Optional[int] = None
    default: Any = None
    extra: str = None

    def __init__(self, Field, Type, Null, Key, Default, Extra):

        self.field = Field

        x = Type.split('(')
        if len(x) == 1:
            self.type = x[0].upper()
        elif len(x) == 2:
            self.type = x[0].upper()
            try:
                self.length = int(x[-1][:-1])
            except:
                self.length = None
        else:
            pass

        self.null = (Null == 'YES')
        self.key = Key
        self.default = Default
        self.extra = Extra

        if self.field in ['ID', 'Id']:
            self.field = 'id'

    @property
    def to_dict(self):
        return {
            'field': self.field, 'type': self.type, 'null': self.null, 'key': self.key,
            'length': self.length, 'default': self.default, 'extra': self.extra
        }

    def __str__(self):
        return str(self.to_dict)

    def __repr__(self):
        return str(self)


class AsyncSQLiteAPI(AbcDB):
    """sqlite 增删改查API"""

    def __init__(self, path: Union[str, Path], chunk_size: int = 1024 * 4, timeout: int = 10):

        if isinstance(path, Path):
            path = str(path)

        self.args = {
            'database': path, 'iter_chunk_size': chunk_size, 'timeout': timeout
        }
        self.path = path
        self.chunk_size = chunk_size
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(**self.args)
        self.conn.row_factory = lambda cursor, row: {
            col[0]: row[index] for index, col in enumerate(cursor.description)
        }
        return self

    async def _execute(self, sql: str, *args, **kwargs):
        """执行sql语句"""

        async with self.conn.cursor() as cur:
            try:
                await cur.execute(sql, kwargs or args)
            except aiosqlite.IntegrityError as e:
                await self.conn.rollback()
                if 'unique' in str(e).lower():
                    logger.error(f'unique重复值错误：{str(e).split(":")[-1]}有重复值')
                else:
                    logger.error(e)
            except Exception as e:
                await self.conn.rollback()
                logger.error(e)
            finally:
                await self.commit()

    async def _get(self, sql: str, *args, **kwargs) -> list:
        """查询一条数据"""

        async with self.conn.cursor() as cur:
            try:
                await cur.execute(sql, kwargs or args)
                return await cur.fetchall()
            except Exception as e:
                logger.error(e)
                return []

    async def table_exist(self, table: str):
        """判断表是否存在"""

        tables = await self.find_many(field='name', table='sqlite_master', where={'type': 'table'})
        if table in [i['name'] for i in tables]:
            return True

        return False

    async def create_table(self, sql: Optional[str] = None):
        """
            创建表
            @params:
                sql: 原始sql语句，当sql参数不为None时，table、fields无效
        """

        table = tools.re_text(regx=r'TABLE(.*?)\(', text=sql.upper()).strip()

        if await self.table_exist(table):
            logger.debug(f'{table} 表已存在')
            return

        for i in sql.split(';'):
            await self._execute(i.strip())

    async def drop_table(self, table):
        """删除表"""
        await self._execute(f'DROP TABLE IF EXISTS {table};')

    async def desc(self, table):

        result1 = await self._get(f'PRAGMA table_info({table})')
        result2 = await self._get(f'PRAGMA index_list({table})')

        unique_indexes = [
            await self._get(f'PRAGMA index_info({index_row["name"]})') for index_row in result2
            if index_row['unique'] == 1
        ]
        unique_indexes = [j['name'] for i in unique_indexes for j in i]

        desc_fields = []
        for row in result1:
            key = 'PRI' if bool(row['pk']) else ('UNI' if row['name'] in unique_indexes else 'MUL')
            desc_fields.append(DescField(row['name'], row['type'], bool(row['notnull']), key, row['dflt_value'], None))

        return desc_fields

    async def index_list(self, table):
        sql = f'select * from sqlite_master where type="index" and tbl_name="{table}";'
        return [i['name'] for i in await self._get(sql)]

    async def add_field(
            self, *, table: str, field: str, field_type: str, length: Union[int, str] = None, default: Any = None,
            primary: bool = False, unique: bool = False, auto_inr: bool = False
    ):

        sql = f'ALTER TABLE {table} ADD COLUMN {field} {field_type}'

        if length is not None:
            sql += f'({length})'

        if primary:
            if auto_inr:
                sql += f' primary key auto_increment'
            else:
                sql += f' primary key'
        elif unique:
            sql += f' unique key'
        else:
            if field_type not in ['TEXT', 'LOB', 'GEOMETRY', 'JSON'] and default is not None:
                if field_type in ['VARCHAR']:
                    sql += f' DEFAULT "{default}"'
                else:
                    sql += f' DEFAULT {default}'
            else:
                sql += f' DEFAULT NULL'

        sql += ';'

        await self._execute(sql)

    async def find_one(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None, limit: int = 1,
            group: Union[list, tuple, list] = None, having: Optional[dict] = None,
            offset: Optional[int] = None, desc: bool = False, order: Union[list, tuple, str, None] = None,
            where: Optional[dict] = None, sql: Optional[str] = None
    ) -> list:
        """
            查询一条数据
            @params:
                table: 表名
                field: 查询字段约束
                group: 分组
                having: 筛选分组后的各组数据
                limit: 数量
                offset: 偏移量
                order: 排序约束
                desc: 是否倒序
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
                sql: 原始sql语句，当sql参数不为None时，table、field、where无效
        """

        if sql is None:
            sql = str(Select(
                table=table, field=field, limit=limit, offset=offset, desc=desc, order=order,
                where=where, group=group, having=having
            ))

        data = await self._get(sql)
        return data[0] if data else {}

    async def find_many(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None,
            limit: Optional[int] = None, offset: Optional[int] = None, desc: bool = False,
            group: Union[list, tuple, list] = None, having: Optional[dict] = None,
            order: Union[list, tuple, str, None] = None, where: Optional[dict] = None,
            sql: Optional[str] = None, rtype: DataType = 'list'
    ):
        """
            查询多条数据
            @params:
                table: 表名
                field: 查询字段约束
                limit: 数量
                group: 分组
                having: 筛选分组后的各组数据
                offset: 偏移量
                order: 排序约束
                desc: 是否倒序
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
                sql: 原始sql语句，当sql参数不为None时，table、field、where无效
        """

        if sql is None:
            sql = str(Select(
                table=table, field=field, limit=limit, offset=offset, desc=desc, order=order,
                where=where, group=group, having=having
            ))

        data = await self._get(sql)

        if rtype == 'list':
            return data
        elif rtype == 'dict':
            return data[0] if data else dict()
        elif rtype == 'pd':
            return pd.DataFrame(data)
        else:
            return iter(data)

    async def insert(self, table: str, items: list, sql: Optional[str] = None, auto_update=True):
        """
            插入或更新多条数据
            @params:
                table: 表名
                items: 需要插入的数据列表，list -> [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
                sql: 原始sql语句，当sql参数不为None时，table、items无效
        """

        if sql is None:

            if not items:
                return

            if isinstance(items, dict):
                items = [items]

            field = list(items[0].keys())
            values = [list(i.values()) for i in items]

            sql = str(SqliteInsert(table, field, values, auto_update=auto_update))

        await self._execute(sql)

    def update(self, table: str, items: Union[List[dict], dict], where: Union[str, list, tuple] = None):
        """
            更新多条数据
            @params:
                table: 表名
                items: 需要插入的数据，dict -> [{'a': 1, 'b': 2}, ...]
                wheres: 更新条件
        """

        if not items:
            return

        if where is None:
            where = []

        if isinstance(items, dict):
            items = [items]

        if isinstance(where, str):
            where = [where]

        sql = str(SQLiteUpdate(table, items, where))

        self._execute(sql)

    def remove_one(self):
        ...

    def remove_many(self):
        ...

    async def commit(self):
        await self.conn.commit()

    async def close(self):
        await self.conn.close()
