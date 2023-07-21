import re
import time
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Union, Any, List, Literal, TypeVar, Iterator

import pymysql
import pandas as pd
from pymysql.converters import escape_string

from AioSpider import logger, tools
from AioSpider.db.sql import Select, MysqlUpdate, MysqlInsert
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

        length = tools.re_text(Type, r'\d+')
        self.length = self._convert_to_int(length)

        self.type = tools.re_sub(Type, r'\(\d+\)', '').upper()
        self.null = (Null == 'YES')
        self.key = Key
        self.default = Default
        self.extra = Extra

        if self.field in ['ID', 'Id']:
            self.field = 'id'

    @staticmethod
    def _convert_to_int(value):
        try:
            return int(value)
        except ValueError:
            return None

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


class SyncMySQLAPI(AbcDB):

    def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 3306, max_idle_time: int = 5 * 60 * 60, connect_timeout=5, time_zone: str = "+0:00",
            charset: str = "utf8mb4", sql_mode: str = "TRADITIONAL"
    ):

        self.max_idle_time = float(max_idle_time)

        args = dict(
            use_unicode=True, charset=charset, database=db,
            init_command=f'SET time_zone = "{time_zone}"', sql_mode=sql_mode,
            cursorclass=pymysql.cursors.DictCursor, connect_timeout=connect_timeout
        )

        if user is not None:
            args["user"] = user

        if password is not None:
            args["passwd"] = password

        # 接受MySQL套接字文件的路径或 主机:端口 字符串
        if "/" in host:
            args["unix_socket"] = host
        else:
            self.socket = None
            pair = host.split(":")
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = port

        if port:
            args['port'] = port

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except:
            logger.exception(f"Cannot connect to MySQL on {host}", exc_info=True)

    def __del__(self):
        """实例销毁后确保数据库连接关闭"""
        self.close()

    def reconnect(self):
        """重新连接数据库"""

        self.close()
        self._db = pymysql.connect(**self._db_args)
        self._db.autocommit(True)

    def _ensure_connected(self):
        """默认情况下，如果连接空闲时间过长（默认情况下为7小时），重新连接数据库"""

        if self._db is None or (time.time() - self._last_use_time > self.max_idle_time):
            self.reconnect()

        self._last_use_time = time.time()

    def _cursor(self):
        """创建游标"""
        self._ensure_connected()
        return self._db.cursor()

    def _escape_string(self, value):

        if isinstance(value, str):
            return '"' + escape_string(value) + '"'
        elif isinstance(value, Path):
            return '"' + escape_string(str(value)) + '"'
        elif isinstance(value, (datetime, date)):
            return '"' + str(value) + '"'
        else:
            return escape_string(str(value))

    def _make_delete_sql(self, table: str, where: dict = None):

        where_str = tools.join([f'`{k}`={self._escape_string(v)}' for k, v in where.items()], on=' and ')

        sql = f'DELETE FROM {table} WHERE {where_str}'
        sql = sql.replace('None', 'NULL')

        return sql

    def _make_table_sql(self, sql):
        table = tools.re(regx=r'table(.*?)\(', text=sql) or tools.re(regx=r'TABLE(.*?)\(', text=sql)
        return table[0].strip() if table else None

    def _execute(self, sql: str) -> None:
        """执行sql语句"""

        self._ensure_connected()
        cursor = self._cursor()
        try:
            cursor.execute(sql)
        except Exception as e:
            self._db.rollback()
            logger.error(e)
        else:
            cursor.commit()
        finally:
            cursor.close()
            return cursor.lastrowid

    def _execute_many(self, sql: str, values=None) -> None:
        """执行sql语句"""

        self._ensure_connected()
        cursor = self._cursor()
        try:
            cursor.executemany(sql, values)
        except pymysql.IntegrityError as e:
            self._db.rollback()
            if 'unique' in str(e).lower():
                logger.error(f'unique重复值错误：{str(e).split(":")[-1]}有重复值')
            else:
                logger.error(e)
        except pymysql.DataError as e:
            self._db.rollback()
            logger.error(f'数据错误：{e}')
        except Exception as e:
            self._db.rollback()
            logger.error(e)
        finally:
            cursor.close()

    def _get(self, sql: str, *args, **kwargs) -> list:
        """查询一条数据"""

        cursor = self._cursor()
        try:
            cursor.execute(sql, kwargs or args)
            return cursor.fetchall()
        except Exception as e:
            logger.error(e)
            return []
        finally:
            cursor.close()

    def table_exist(self, table: str):
        """判断表是否存在"""

        tables = self.find_many(sql='show tables;')
        if table in [list(i.values())[0] for i in tables]:
            return True

        return False
    
    def create_table(
            self, table: Optional[str] = None, fields: Optional[dict] = None, sql: Optional[str] = None
    ):
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

        sql = sql.replace('AUTOINCREMENT', 'AUTO_INCREMENT')

        self._execute(sql)
        logger.info(f'{table} 表自动创建成功')

    def desc(self, table: str) -> List[DescField]:

        result = self._get(f'desc {table}')
        return [DescField(**i) for i in result]

    def find_one(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None, limit: Optional[int] = 1,
            group: Union[list, tuple, list] = None, having: Optional[dict] = None,
            offset: Optional[int] = 0, desc: bool = False, order: Union[list, tuple, str, None] = None,
            where: Optional[dict] = None, sql: Optional[str] = None
    ) -> RType:
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
    ) -> RType:
        """
            查询多条数据
            @params:
                table: 表名
                field: 查询字段约束
                limit: 数量
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

        if rtype == 'list':
            return data if data else []
        elif rtype == 'dict':
            return data[0] if data else dict()
        elif rtype == 'pd':
            return pd.DataFrame(data)
        else:
            return iter(data)

    def insert(self, table: str, items: list, sql: Optional[str] = None, auto_update: bool = False):
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
            sql = str(MysqlInsert(table, field, values, auto_update=auto_update))

        self._execute(sql)

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

        sql = str(MysqlUpdate(table, items, where))

        self._execute(sql)

    def remove_one(self) -> None:
        pass

    def remove_many(self):
        pass

    def delete_one(self, table: str, where: dict, sql: str = None) -> None:
        """
            更新一条数据
            @params:
                table: 表名
                item: 需要修改的数据，dict -> {'a': 1, 'b': 2}
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
                sql: 原始sql语句，当sql参数不为None时，table、item、where无效
        """

        if sql is None:
            sql = self._make_delete_sql(table=table, where=where)

        self._execute(sql)

    def delete_many(self):
        pass
            
    def close(self):
        """关闭数据库连接"""

        if self._db is not None:
            self._db.close()
            self._db = None
            
    def __del__(self):
        """关闭数据库连接"""

        if self._db is not None:
            self._db.close()
            self._db = None
