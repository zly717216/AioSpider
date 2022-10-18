import time
import asyncio
from typing import Optional

import aiomysql
import AioSpider
from AioSpider import AioObject


class MySQLAPI(AioObject):

    engine = 'mysql'

    async def __init__(
            self, *, host: str, db: str, user: str | None = None, password: str | None = None,
            port: int = 3306, max_idle_time: int = 5 * 60 * 60, connect_timeout=5, time_zone: str = "+0:00",
            charset: str = "utf8mb4", sql_mode: str = "TRADITIONAL"
    ):

        self.max_idle_time = float(max_idle_time)

        args = dict(
            use_unicode=True, charset=charset, db=db,
            init_command=f'SET time_zone = "{time_zone}"', sql_mode=sql_mode,
            cursorclass=aiomysql.cursors.DictCursor, connect_timeout=connect_timeout
        )

        if user is not None:
            args["user"] = user

        if password is not None:
            args["password"] = password

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

        args['loop'] = asyncio.get_event_loop()
        args['autocommit'] = True

        self._pool = None
        self._pool_args = args
        self._last_use_time = time.time()

        try:
            await self.reconnect()
        except:
            raise Exception(f"Cannot connect to MySQL on {host}")

    async def reconnect(self):
        """重新连接数据库"""

        self.close()
        self._pool = await aiomysql.create_pool(**self._pool_args)

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

        sql = f'INSERT INTO {table} ({field_str}) VALUES({valve_str})'

        return sql

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

        if await self.table_exist(table):
            return

        if sql is None:
            sql = f'CREATE TABLE {table} ('
            sql += 'id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT)'

            for f in fields.items():
                sql += f'{f[0]} {f[1]}, '

            sql += ')'

        await self._execute(sql)

    async def table_exist(self, table: str):
        """判断表是否存在"""

        tables = await self.find_many(field='name', table='show tables;')
        if table in [list(i.values())[0] for i in tables]:
            return True

        return False

    async def _ensure_connected(self):
        """默认情况下，如果连接空闲时间过长（默认情况下为7小时），重新连接数据库"""

        if self._pool is None or (time.time() - self._last_use_time > self.max_idle_time):
            await self.reconnect()

        self._last_use_time = time.time()

    async def _cursor(self):
        """创建游标"""
        self._ensure_connected()
        return self._db.cursor()

    async def _execute(self, sql: str, values) -> None:
        """执行sql语句"""

        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.executemany(sql, values)or(e)
                except aiosqlite.IntegrityError as e:
                    if 'unique' in str(e).lower():
                        AioSpider.logger.error(f'unique重复值错误：{str(e).split(":")[-1]}有重复值')
                    else:
                        AioSpider.logger.error(e)
                except Exception as e:
                    AioSpider.logger.error(e)
                finally:
                    await conn.commit()

    async def _get(self, sql: str, *args, **kwargs) -> dict:
        """查询一条数据"""

        cursor = self._cursor()
        try:
            cursor.execute(sql, kwargs or args)
            return cursor.fetchone()
        finally:
            cursor.close()
            return {}

    async def find_one(self, table: str, field: str, where: dict) -> dict:
        """
            查询一条数据
            @params:
                table: 表名
                field: 查询字段
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
            @return: dict or None
        """

        where_str = ' and '.join([f'{k}="{v}"' for k, v in where.items()])
        sql = f'SELECT {field} FROM {table} WHERE {field}="{where_str}"'

        return self._get(sql)

    async def find_many(
            self, table: Optional[str] = None, field: Optional[Iterable] = None,
            where: Optional[dict] = None, sql: Optional[str] = None
    ) -> list:
        """
            查询多条数据
            @params:
                table: 表名
                field: 查询字段
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
                sql: 原始sql语句，当sql参数不为None时，table、field、where无效
        """

        if sql is None:
            sql = self._make_select_sql(table, field=field, where=where)

        await self._execute(sql)
        result = await cur.fetchall()

        return self._serialize_to_dict(cur, result)

    async def insert_one(self, table: str, item: dict) -> bool:
        """
            插入一条数据
            @params:
                table: 表名
                item: 需要插入的数据，dict -> {'a': 1, 'b': 2}
        """

        values = list(item.values())

        field_str = ','.join([k for k in item.keys()])
        valve_str = ','.join(['%s'] * len(item))

        sql = f'INSERT INTO {table} ({field_str}) VALUES({valve_str})'
        try:
            return self._execute(sql, *values)
        except Exception as e:
            AioSpider.logger.error(e)

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
            values = set((tuple(i.values()) for i in items))
            sql = f'INSERT INTO {table} ({",".join([i for i in keys])}) VALUES (' + '%s,' * len(keys)
            sql = sql[:-1] + ')'

            await self._execute(sql, values)
        else:
            await self._execute(sql)

    async def update(self, table: str, item: dict, where: dict) -> None:
        """
            更新数据
            @params:
                table: 表名
                item: 需要插入的数据，dict -> {'a': 1, 'b': 2}
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
        """

        upsets = ','.join([f'{k}=%s' for k in item.keys()])
        values = [v for v in item.values()]
        where_str = ' and '.join([f'{k}="{v}"' for k, v in where])

        sql = f'UPDATE {table} SET {upsets} WHERE {where_str}'

        self._execute(sql, *values)

    def close(self):
        """关闭数据库连接"""

        if getattr(self, "_db", None) is not None:
            # 连接池关闭
            self._pool.close()
            # 等待释放和关闭所有已获取连接的协同程序。应该在close（）之后调用，以等待实际的池关闭
            asyncio.create_task(self._pool.wait_closed())


import asyncio
from typing import Optional, Iterable

import aiosqlite
import AioSpider
from AioSpider import AioObject


class SQLiteAPI(AioObject):
    """sqlite 增删改查API"""

    engine = 'sqlite'

    async def __init__(self, path, timeout=None):
        self.conn = await aiosqlite.connect(database=path, iter_chunk_size=64, timeout=timeout)

    async def _execute(self, sql: str, *args, **kwargs):
        """执行sql语句"""

        async with self.conn.cursor() as cur:
            try:
                await cur.execute(sql, kwargs or args)
            except aiosqlite.IntegrityError as e:
                if 'unique' in str(e).lower():
                    AioSpider.logger.error(f'unique重复值错误：{str(e).split(":")[-1]}有重复值')
                else:
                    AioSpider.logger.error(e)
            except Exception as e:
                AioSpider.logger.error(e)
            finally:
                await self.commit()

    def _make_select_sql(self, table: str, field: Optional[Iterable] = None, where: Optional[dict] = None) -> str:
        """
            生成查询语句
            @params:
                table: 表名
                field: 查询字段
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
        """

        if field is None:
            sql = f'SELECT * FROM {table}'
        elif isinstance(field, str):
            sql = f'SELECT {field} FROM {table}'
        elif isinstance(field, list):
            sql = f'SELECT {",".join(field)} FROM {table}'
        else:
            raise TypeError(f'field 参数类型错误，当前类型为：{type(field)}')

        if where is None:
            return sql

        where_list = []
        for k, v in where.items():
            if isinstance(v, str):
                where_list.append(f'{k}="{v}"')
            else:
                where_list.append(f'{k}={v}')

        sql += ' WHERE '
        sql += ' and '.join(where_list)

        return sql

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

        sql = f'INSERT INTO {table} ({field_str}) VALUES({valve_str})'

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

    async def table_exist(self, table: str):
        """判断表是否存在"""

        tables = await self.find_many(field='name', table='sqlite_master', where={'type': 'table'})
        if table in [list(i.values())[0] for i in tables]:
            return True

        return False

    async def find_one(
            self, table: Optional[str] = None, field: Optional[Iterable] = None,
            where: Optional[dict] = None, sql: Optional[str] = None
    ) -> list:
        """
            查询一条数据
            @params:
                table: 表名
                field: 查询字段
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
                sql: 原始sql语句，当sql参数不为None时，table、field、where无效
        """

        if sql is None:
            sql = self._make_select_sql(table, field=field, where=where)

        async with self.conn.cursor() as cur:
            await cur.execute(sql)
            result = await cur.fetchone()
            return self._serialize_to_dict(cur, result)

    async def find_many(
            self, table: Optional[str] = None, field: Optional[Iterable] = None,
            where: Optional[dict] = None, sql: Optional[str] = None
    ) -> list:
        """
            查询多条数据
            @params:
                table: 表名
                field: 查询字段
                where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
                sql: 原始sql语句，当sql参数不为None时，table、field、where无效
        """

        if sql is None:
            sql = self._make_select_sql(table, field=field, where=where)

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
                        AioSpider.logger.error(f'unique重复值错误：{str(e).split(":")[-1]}有重复值')
                    else:
                        AioSpider.logger.error(e)
                except Exception as e:
                    AioSpider.logger.error(e)
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


if __name__ == '__main__':
    db = MySQLAPI(
        host='101.42.138.122', database='wenzz', user='root', password='717216'
    )