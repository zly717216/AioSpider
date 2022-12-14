import asyncio
from typing import Optional, Iterable, Union

import aiosqlite
from AioSpider.aio_db.abc_db import ABCDB
from AioSpider import AioObject, GlobalConstant, tools


class SQLiteAPI(ABCDB, AioObject):
    """sqlite 增删改查API"""

    engine = 'sqlite'

    async def __init__(self, path: str, timeout: Optional[int] = None):
        self.conn = await aiosqlite.connect(database=path, iter_chunk_size=64, timeout=timeout)
        self._logger = GlobalConstant().logger

    async def _execute(self, sql: str, *args, **kwargs):
        """执行sql语句"""

        async with self.conn.cursor() as cur:
            try:
                await cur.execute(sql, kwargs or args)
            except aiosqlite.IntegrityError as e:
                if 'unique' in str(e).lower():
                    self._logger.error(f'unique重复值错误：{str(e).split(":")[-1]}有重复值')
                else:
                    self._logger.error(e)
            except Exception as e:
                self._logger.error(e)
            finally:
                await self.commit()

    def _make_select_sql(
            self, table: str, field: Union[list, tuple, str, None] = None, count: Optional[int] = None,
            offset: Optional[int] = None, desc: bool = False, order: Union[list, tuple, list] = None,
            where: Optional[dict] = None
    ) -> str:
        """
            生成查询语句
            @params:
                table: 表名
                field: 查询字段约束
                count: 数量
                offset: 偏移量
                desc: 是否倒序
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
        """

        def _func(sql):

            if order is None:
                pass
            elif isinstance(order, str):
                sql += f' ORDER BY {order}'
            elif isinstance(order, (list, tuple)):
                sql += f' ORDER BY {",".join(order)}'
            else:
                raise TypeError(f'order 参数类型错误，当前类型为：{type(field)}')

            if desc and order is not None:
                sql += ' DESC'

            if count is not None:
                sql += f' LIMIT {count}'

            if offset is not None:
                sql += f' OFFSET {offset}'

            return sql

        if field is None:
            sql = f'SELECT * FROM {table}'
        elif isinstance(field, str):
            sql = f'SELECT {field} FROM {table}'
        elif isinstance(field, (list, tuple)):
            sql = f'SELECT {",".join(field)} FROM {table}'
        else:
            raise TypeError(f'field 参数类型错误，当前类型为：{type(field)}')

        if where is None:
            return _func(sql)

        where_list = []
        for k, v in where.items():
            if isinstance(v, str):
                where_list.append(f'{k}="{v}"')
            else:
                where_list.append(f'{k}={v}')

        sql += ' WHERE '
        sql += ' and '.join(where_list)

        return _func(sql)

    def _make_insert_sql(self, table: str, item: dict):
        """
            插入一条数据
            @params:
                table: 表名
                item: 需要插入的数据，dict -> {'a': 1, 'b': 2}
        """

        field_str = valve_str = ''
        for k in item:
            field_str += k + ','
            if isinstance(item[k], str):
                valve_str += f'"{item[k]}",'
            else:
                valve_str += f'{item[k]},'

        field_str = field_str[:-1]
        valve_str = valve_str[:-1]

        sql = f'INSERT IGNORE INTO {table} ({field_str}) VALUES({valve_str}) ON DUPLICATE KEY UPDATE'

        return sql

    def _serialize_to_dict(self, cur, data: Iterable) -> list:
        """
            将查询到的数据序列化成字典
            @params:
                cur: cursor 数据库游标对象
                data： 嵌套可迭代对象
        """

        f = [i[0] for i in cur.description]

        if data:
            return [dict(zip(f, i)) for i in data]
        else:
            return []

    def _from_sql_table(self, sql):
        table = tools.re(regx='table(.*?)\(', text=sql) or tools.re(regx='TABLE(.*?)\(', text=sql)
        return table[0].strip() if table else None

    async def table_exist(self, table: str):
        """判断表是否存在"""

        tables = await self.find_many(field='name', table='sqlite_master', where={'type': 'table'})
        if table in [list(i.values())[0] for i in tables]:
            return True

        return False

    async def create_table(
            self, table: Optional[str] = None, fields: Optional[dict] = None,
            sql: Optional[str] = None
    ):
        """
            创建表
            @params:
                table: 表名
                fields: 字段，如：fields={'name': 'TEXT'}
                 sql: 原始sql语句，当sql参数不为None时，table、fields无效
        """

        if table is None:
            table = self._from_sql_table(sql)

        if await self.table_exist(table):
            return

        if sql is None:
            sql = f'CREATE TABLE {table} ('
            sql += 'id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT)'

            for f in fields.items():
                sql += f'{f[0]} {f[1]}, '

            sql += ')'

        await self._execute(sql)

    async def find_one(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None,
            offset: Optional[int] = None, desc: bool=False, order: Union[list, tuple, str, None] = None, 
            where: Optional[dict] = None, sql: Optional[str] = None
    ) -> list:
        """
            查询一条数据
            @params:
                table: 表名
                field: 查询字段约束
                offset: 偏移量
                order: 排序约束
                desc: 是否倒序
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
                sql: 原始sql语句，当sql参数不为None时，table、field、where无效
        """

        if sql is None:
            sql = self._make_select_sql(
                table, field=field, count=count, offset=offset, desc=desc, order=order, where=where
            )

        async with self.conn.cursor() as cur:
            await cur.execute(sql)
            result = await cur.fetchone()
            return self._serialize_to_dict(cur, result)

    async def find_many(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None,
            count: Optional[int] = None, offset: Optional[int] = None, desc: bool = False,
            order: Union[list, tuple, str, None] = None, where: Optional[dict] = None,
            sql: Optional[str] = None
    ):
        """
            查询多条数据
            @params:
                table: 表名
                field: 查询字段约束
                count: 数量
                offset: 偏移量
                order: 排序约束
                desc: 是否倒序
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
                sql: 原始sql语句，当sql参数不为None时，table、field、where无效
        """

        if sql is None:
            sql = self._make_select_sql(
                table, field=field, count=count, offset=offset, order=order, desc=desc, where=where
            )

        async with self.conn.cursor() as cur:
            await cur.execute(sql)
            result = await cur.fetchall()

            return self._serialize_to_dict(cur, result)

    async def insert_one(self, table: str, item: dict, sql: Optional[str] = None):
        """
            插入一条数据
            @params:
                table: 表名
                item: 需要插入的数据，dict -> {'a': 1, 'b': 2}
                sql: 原始sql语句，当sql参数不为None时，table、item无效
        """

        if sql is None:
            sql = self._make_insert_sql(table, item)

        await self._execute(sql)

    async def insert_many(self, table: str, items: list, sql: Optional[str] = None):
        """
            插入多条数据
            @params:
                table: 表名
                items: 需要插入的数据列表，list -> [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
                sql: 原始sql语句，当sql参数不为None时，table、items无效
        """

        if sql is None:
            if not items:
                return

            keys = items[0].keys()
            values = iter(set(tuple(i.values()) for i in items))
            sql = f'INSERT INTO {table} ({",".join([i for i in keys])}) VALUES (' + '?,' * len(keys)
            sql = sql[:-1] + ')'

            async with self.conn.cursor() as cur:
                try:
                    await cur.executemany(sql, values)
                except aiosqlite.IntegrityError as e:
                    if 'unique' in str(e).lower():
                        self._logger.error(f'unique重复值错误：{str(e).split(":")[-1]}有重复值')
                    else:
                        self._logger.error(e)
                except Exception as e:
                    self._logger.error(e)
                finally:
                    await self.commit()
        else:
            await self._execute(sql)

    def remove_one(self): ...

    def remove_many(self): ...

    async def modify_one_smart(self, table, items: dict, where):

        sql = f"UPDATE {table} SET "

        for key in items.keys():
            sql += f'{key}="{items[key]}",' if isinstance(items[key], str) else f'{key}={items[key]},'

        sql = sql[:-1] + f" where {where}={items[where]}"

        await self._execute(sql)

    def modify_many(self): ...

    async def commit(self):
        await self.conn.commit()

    def close(self):
        asyncio.create_task(self.conn.close())

