import time
from typing import Optional
from AioSpider.utils_pkg import cchardet

import pymysql

from AioSpider import GlobalConstant


class MySQLAPI:

    engine = 'mysql'

    def __init__(
            self, *, host: str, database: str, user: Optional[str] = None, password: Optional[str] = None,
            port: int = 3306, max_idle_time: int = 5 * 60 * 60, connect_timeout=5, time_zone: str = "+0:00",
            charset: str = "utf8mb4", sql_mode: str = "TRADITIONAL"
    ):

        self.max_idle_time = float(max_idle_time)
        self._logger = GlobalConstant().logger

        args = dict(
            use_unicode=True, charset=charset, database=database,
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
            self._logger.error(f"Cannot connect to MySQL on {host}", exc_info=True)

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

    def _execute(self, sql: str, *args, **kwargs) -> None:
        """执行sql语句"""

        cursor = self._cursor()
        try:
            cursor.execute(sql, kwargs or args)
        except Exception as e:
            self._logger.error(e)
        finally:
            cursor.close()

    def _get(self, sql: str, *args, **kwargs) -> dict:
        """查询一条数据"""

        cursor = self._cursor()
        try:
            cursor.execute(sql, kwargs or args)
            return cursor.fetchone()
        finally:
            cursor.close()
            return {}

    def find_one(self, table: str, field: str, where: dict) -> dict:
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

    def find_many(self, sql: str, *args, **kwargs) -> list:
        """查询多条数据"""

        cursor = self._cursor()
        try:
            cursor.execute(sql, kwargs or args)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()
            return []

    def insert_one(self, table: str, item: dict) -> bool:
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
            self._logger.error(e)

    def insert_many(self, table: str, items: list) -> None:
        """
            插入多条数据
            @params:
                table: 表名
                items: 需要插入的数据列表，list -> [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
        """

        for item in items:
            self.insert_one(table, item)

    def update(self, table: str, item: dict, where: dict) -> None:
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
            self._db.close()
            self._db = None


if __name__ == '__main__':
    db = MysqlAPI(
        host='101.42.138.122', database='wenzz', user='root', password='717216'
    )