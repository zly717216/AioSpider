import time
import asyncio
from typing import Optional, Iterable, Union

from AioSpider.aio_db.abc_db import ABCDB
from AioSpider.utils_pkg import aiomysql
from AioSpider import AioObject, GlobalConstant, tools


class MySQLAPI(ABCDB, AioObject):

    engine = 'mysql'

    async def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 3306, max_idle_time: int = 5 * 60 * 60, connect_timeout=5, time_zone: str = "+0:00",
            charset: str = "utf8mb4", sql_mode: str = "TRADITIONAL"
    ):

        self._logger = GlobalConstant().logger
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

        sql = f'INSERT IGNORE INTO {table} ({field_str}) VALUES({valve_str}) ON DUPLICATE KEY UPDATE'

        return sql

    def _from_sql_table(self, sql):
        table = tools.re(regx='table(.*?)\(', text=sql) or tools.re(regx='TABLE(.*?)\(', text=sql)
        return table[0].strip() if table else None

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
            sql += 'id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT)'

            for f in fields.items():
                sql += f'{f[0]} {f[1]}, '

            sql += ')'

        await self._execute(sql)

    async def table_exist(self, table: str):
        """判断表是否存在"""

        tables = await self.find_many(sql='show tables;')
        if table in [list(i.values())[0] for i in tables]:
            return True

        return False

    async def _ensure_connected(self):
        """默认情况下，如果连接空闲时间过长（默认情况下为7小时），重新连接数据库"""

        if self._pool is None or (time.time() - self._last_use_time > self.max_idle_time):
            await self.reconnect()

        self._last_use_time = time.time()

    async def _execute(self, sql: str, values=None) -> None:
        """执行sql语句"""

        await self._ensure_connected()
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(sql, values)
                except aiosqlite.IntegrityError as e:
                    if 'unique' in str(e).lower():
                        self._logger.error(f'unique重复值错误：{str(e).split(":")[-1]}有重复值')
                    else:
                        self._logger.error(e)
                except Exception as e:
                    self._logger.error(e)
                finally:
                    await conn.commit()

    async def _executemany(self, sql: str, values=None) -> None:
        """执行sql语句"""

        await self._ensure_connected()
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.executemany(sql, values)
                except aiomysql.IntegrityError as e:
                    if 'unique' in str(e).lower():
                        self._logger.error(f'unique重复值错误：{str(e).split(":")[-1]}有重复值')
                    else:
                        self._logger.error(e)
                except aiomysql.DataError as e:
                    self._logger.error(f'数据错误：{e}')
                except Exception as e:
                    self._logger.error(e)
                finally:
                    await conn.commit()

    async def _get(self, sql: str, values=None) -> dict:
        """查询一条数据"""

        await self._ensure_connected()
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(sql, values)
                except Exception as e:
                    self._logger.error(e)
                finally:
                    return await cur.fetchall()

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

        return await self._get(sql)

    async def find_many(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None,
            count: Optional[int] = None, offset: Optional[int] = None, desc: bool=False,
            order: Union[list, tuple, str, None] = None, where: Optional[dict] = None,
            sql: Optional[str] = None
    ) -> list:
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

        return await self._get(sql)

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
            values = iter(set((tuple(i.values()) for i in items)))
            sql = f'INSERT INTO {table} ({",".join([i for i in keys])}) VALUES (' + '%s,' * len(keys)
            sql = sql[:-1] + ')'

            await self._executemany(sql, values)
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

        if getattr(self, "_pool", None) is not None:
            # 连接池关闭
            self._pool.close()
            # 等待释放和关闭所有已获取连接的协同程序。应该在close（）之后调用，以等待实际的池关闭
            asyncio.create_task(self._pool.wait_closed())
