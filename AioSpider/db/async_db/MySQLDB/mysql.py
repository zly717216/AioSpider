import time
import asyncio
from typing import Optional, Union, Any, List, Literal, TypeVar, Iterator

import pandas as pd
import aiomysql

from AioSpider import tools, logger
from AioSpider import exceptions
from AioSpider.db.sql import Select, MysqlInsert, MysqlUpdate
from AioSpider.db.async_db.async_abc import AbcDB


RType = Literal['list', 'dict', 'pd', 'iter']
DataType = TypeVar('RType', list, dict, pd.DataFrame, Iterator)


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


class AsyncMySQLAPI(AbcDB):

    def __init__(
            self, *, host: str, db: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 3306, min_size: int = 10, max_size: int = 20, max_idle_time: int = 5 * 60 * 60,
            connect_timeout=5, time_zone: str = "+0:00", charset: str = "utf8mb4", sql_mode: str = "TRADITIONAL",
            max_retry: int = 3
    ):

        self.max_idle_time = float(max_idle_time)
        self.max_retry = max_retry
        args = dict(
            use_unicode=True, charset=charset, db=db, minsize=min_size, maxsize=max_size,
            init_command=f'SET time_zone = "{time_zone}"', sql_mode=sql_mode, 
            cursorclass=aiomysql.cursors.DictCursor, connect_timeout=connect_timeout
        )
        self._lock = asyncio.Lock()

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
        self.args = args
        self._last_use_time = time.time()

    async def connect(self):
        """重新连接数据库"""
        try:
            self._pool = await aiomysql.create_pool(**self.args)
        except:
            raise Exception(f"Cannot connect to MySQL on {self.args['host']}")
        return self

    async def _ensure_connected(self):
        """默认情况下，如果连接空闲时间过长（默认情况下为7小时），重新连接数据库"""

        async with self._lock:
            if self._pool is None or (time.time() - self._last_use_time > self.max_idle_time):
                await self.connect()

            self._last_use_time = time.time()

    def _is_deadlock_error(self, exception):
        """判断是否是死锁错误"""
        if isinstance(exception, aiomysql.OperationalError):
            error_code = exception.args[0]
            # MySQL的死锁错误代码
            if error_code == 1213:
                return True
        return False

    async def _log_and_handle_error(self, e: Exception, sql: str, values=None):
        """处理并记录错误"""

        if isinstance(e, aiomysql.IntegrityError):
            logger.error(f'Integrity error: {e}, SQL: {sql}, values: {values}')
        elif isinstance(e, aiomysql.DataError):
            logger.error(f'Data error: {e}, SQL: {sql}, values: {values}')
        elif isinstance(e, aiomysql.OperationalError):
            if e.args[0] == 1071:
                raise exceptions.SqlError(f'指定的索引太长；最大最大长度为767字节, SQL: {sql}')
            else:
                logger.error(f'Operational error: {e}, SQL: {sql}, values: {values}')
        elif isinstance(e, aiomysql.InternalError):
            logger.error(f'Internal error: {e}, SQL: {sql}, values: {values}')
        elif isinstance(e, aiomysql.ProgrammingError):
            logger.error(f'Programming error: {e}, SQL: {sql}, values: {values}')
        elif isinstance(e, aiomysql.NotSupportedError):
            logger.error(f'Not supported error: {e}, SQL: {sql}, values: {values}')
        else:
            logger.error(f'Unknown error: {e}, SQL: {sql}, values: {values}')

    async def _execute(self, sql: str, values=None) -> int:
        """执行sql语句"""

        await self._ensure_connected()
        retry_count = 0

        while retry_count < self.max_retry:
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cur:
                    try:
                        await cur.execute(sql, values)
                    except Exception as e:
                        if self._is_deadlock_error(e):
                            retry_count += 1
                            await asyncio.sleep(0.1)
                        else:
                            await conn.rollback()
                            await self._log_and_handle_error(e, sql, values)
                    else:
                        await conn.commit()
                    return cur.lastrowid

    async def _get(self, sql: str, values=None) -> list:

        await self._ensure_connected()
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(sql, values)
                    return await cur.fetchall()
                except Exception as e:
                    await self._log_and_handle_error(e, sql, values)
                    return []

    async def table_exist(self, table: str):
        """判断表是否存在"""

        tables = await self.find_many(sql='show tables;')
        if table in [list(i.values())[0] for i in tables]:
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

        await self._execute(sql)

    async def desc(self, table: str) -> List[DescField]:

        result = await self._get(f'desc {table}')
        return [DescField(**i) for i in result]

    async def find_one(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None, limit: Optional[int] = 1,
            group: Union[list, tuple, list] = None, having: Optional[dict] = None,
            offset: Optional[int] = 1, desc: bool = False, order: Union[list, tuple, str, None] = None,
            where: Optional[dict] = None, join: Optional[list] = None,
            subquery: Optional[str] = None, union: Optional[str] = None, union_all: Optional[str] = None,
            distinct: bool = False, sql: Optional[str] = None
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
                where=where, group=group, having=having, join=join, subquery=subquery, union=union,
                union_all=union_all, distinct=distinct
            ))

        data = await self._get(sql)
        return data[0] if data else {}

    async def find_many(
            self, table: Optional[str] = None, field: Union[list, tuple, str, None] = None,
            limit: Optional[int] = None, offset: Optional[int] = None, desc: bool = False,
            group: Union[list, tuple, list] = None, having: Optional[dict] = None,
            order: Union[list, tuple, str, None] = None, where: Optional[dict] = None,
            join: Optional[list] = None,
            subquery: Optional[str] = None, union: Optional[str] = None, union_all: Optional[str] = None,
            distinct: bool = False,
            sql: Optional[str] = None, rtype: RType = 'list'
    ) -> DataType:
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
                where=where, group=group, having=having, join=join, subquery=subquery, union=union,
                union_all=union_all, distinct=distinct
            ))

        data = await self._get(sql)

        if rtype == 'list':
            return data if data else []
        elif rtype == 'dict':
            return data[0] if data else dict()
        elif rtype == 'pd':
            return pd.DataFrame(data)
        else:
            return iter(data)

    async def insert(self, table: str, items: list, sql: Optional[str] = None, auto_update: bool = False):
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

        sql = str(MysqlUpdate(table, items, where))

        self._execute(sql)

    def remove_one(self):
        pass

    def remove_many(self):
        pass

    async def close(self):
        """关闭数据库连接"""

        if getattr(self, "_pool", None) is not None:
            # 连接池关闭
            self._pool.close()
            # 等待释放和关闭所有已获取连接的协同程序。应该在close（）之后调用，以等待实际的池关闭
            await self._pool.wait_closed()
