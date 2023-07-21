import sqlite3
from pathlib import Path
from datetime import date, datetime
from typing import Union, Optional, List, Any, Literal, TypeVar, Iterator

import pandas as pd
from pymysql.converters import escape_string

from AioSpider import tools, logger
from AioSpider.db.sql import Select, SqliteInsert, SQLiteUpdate
from AioSpider.db.sync_db.sync_abc import AbcDB


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


class SyncSQLiteAPI(AbcDB):
    """sqlite 增删改查API"""

    def __init__(self, path: Union[str, Path], timeout: Optional[int] = None):
        
        if isinstance(path, Path):
            path = str(path)

        self.path = path

        self.conn = sqlite3.connect(database=path, timeout=timeout or 10)
        self.conn.row_factory = lambda cursor, row: {
            col[0]: row[index] for index, col in enumerate(cursor.description)
        }

    def _cursor(self):
        """创建游标"""
        return self.conn.cursor()

    def _escape_string(self, value):

        if isinstance(value, str):
            return '"' + escape_string(value) + '"'
        elif isinstance(value, Path):
            return '"' + escape_string(str(value)) + '"'
        elif isinstance(value, (datetime, date)):
            return '"' + str(value) + '"'
        else:
            return escape_string(str(value))

    def _make_update_sql(self, table: str, item: dict= None, where: dict = None):

        upsets = tools.join([f'`{k}`={self._escape_string(v)}' for k, v in item.items()], on=',')
        where_str = tools.join([f'`{k}`={self._escape_string(v)}' for k, v in where.items()], on=' and ')

        sql = f'UPDATE {table} SET {upsets} WHERE {where_str}'
        sql = sql.replace('None', 'NULL')

        return sql

    def _execute(self, sql: str, *args, **kwargs):
        """执行sql语句"""

        cur = self._cursor()
        try:
            cur.execute(sql, kwargs or args)
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if 'unique' in str(e).lower():
                print(f'unique重复值错误：{str(e).split(":")[-1]}有重复值')
            else:
                print(e)
        except Exception as e:
            self.conn.rollback()
            print(e)
        finally:
            cur.close()
            self.commit()

        return cur.lastrowid

    def _get(self, sql: str, *args, **kwargs) -> list:
        """查询一条数据"""

        cursor = self._cursor()
        # cur.description
        try:
            cursor.execute(sql, kwargs or args)
            return cursor.fetchall()
        except Exception as e:
            logger.error(e)
            return []
        finally:
            cursor.close()

    def _make_table_sql(self, sql):
        table = tools.re(regx=r'table(.*?)\(', text=sql) or tools.re(regx=r'TABLE(.*?)\(', text=sql)
        return table[0].strip() if table else None

    def table_exist(self, table: str):
        """判断表是否存在"""

        tables = self.find_many(field='name', table='sqlite_master', where={'type': 'table'})
        if table in [i['name'] for i in tables]:
            return True

        return False

    def create_table(self, table: Optional[str] = None, sql: Optional[str] = None):
        """
            创建表
            @params:
                table: 表名
                fields: 字段，如：fields={'name': 'TEXT'}
                 sql: 原始sql语句，当sql参数不为None时，table、fields无效
        """

        if table is None and sql is not None:
            table = self._make_table_sql(sql)
        else:
            logger.debug(f'参数错误')
            return

        if self.table_exist(table):
            logger.debug(f'{table} 表已存在')
            return

        sql = sql.replace(' ON UPDATE CURRENT_TIMESTAMP', '')
        sql = sql.replace('TINYINT', 'INTEGER').replace('SMALLINT', 'INTEGER').replace('MEDIUMINT', 'INTEGER').\
            replace('INT', 'INTEGER').replace('BIGINT', 'INTEGER')

        self._execute(sql)

    def desc(self, table):
        result = self._get(f'PRAGMA table_info({table})')
        return [
            DescField(
                i['name'], i['type'], i['notnull'], 'PRI' if i['pk'] else None,  i['dflt_value'], None
            ) for i in result
        ]

    async def index_list(self, table):
        sql = f'select * from sqlite_master where type="index" and tbl_name="{table}";'
        return [i['name'] for i in self._get(sql)]
    
    def add_field(
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

        self._execute(sql)

    def find_one(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None, limit: Optional[int] = 1,
            group: Union[list, tuple, list] = None, having: Optional[dict] = None,
            offset: Optional[int] = None, desc: bool = False, order: Union[list, tuple, str, None] = None,
            where: Optional[dict] = None, sql: Optional[str] = None
    ) -> dict:
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

        data = self._get(sql)
        return data[0] if data else {}

    def find_many(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None,
            limit: Optional[int] = None, offset: Optional[int] = None, desc: bool = False,
            group: Union[list, tuple, list] = None, having: Optional[dict] = None,
            order: Union[list, tuple, str, None] = None, where: Optional[dict] = None,
            sql: Optional[str] = None, rtype: DataType = 'list'
    ) -> Iterator:
        """
            查询多条数据
            @params:
                table: 表名
                field: 查询字段约束
                limit: 数量
                group: 分组
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

        data = self._get(sql)

        if rtype == 'list':
            return data
        elif rtype == 'dict':
            return data[0] if data else dict()
        elif rtype == 'pd':
            return pd.DataFrame(data)
        else:
            return iter(data)

    def insert(self, table: str, items: list, sql: Optional[str] = None, auto_update=True):
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

        return self._execute(sql)

    def remove_one(self): ...

    def remove_many(self): ...

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

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
