import csv
from pathlib import Path
from typing import Optional, Union

import aiocsv
import aiofiles
import pandas as pd

from AioSpider import logger
from AioSpider.db.async_db.async_abc import AbcDB


class AsyncCSVFile(AbcDB):
    """csv 增删改查API"""

    def __init__(self, path: Path, encoding: str = 'utf-8'):
        self.path = path
        self.encoding = encoding

    def connect(self):
        return self

    async def table_exist(self, table: str) -> bool:
        return (self.path / (table + '.csv')).exists()

    async def clear_table(self, table: str) -> None:
        if not await self.table_exist(table):
            return None

        async with aiofiles.open(
                self.path / (table + '.csv'), newline="", encoding=self.encoding
        ) as afp:
            content = await afp.read()

        async with aiofiles.open(
                self.path / (table + '.csv'), mode='w+', newline="", encoding=self.encoding
        ) as afp:
            await afp.write(content.split('\n')[0])

    async def create_table(self, table: str, headers=None, encoding=None) -> None:
        if hasattr(self, table):
            return

        if headers is None:
            headers = []

        if encoding is None:
            encoding = self.encoding

        # 判断表是否存在
        if await self.table_exist(table):
            logger.debug(f'{table} 表已存在')
            return

        async with aiofiles.open(
                self.path / (table + '.csv'), mode='a', encoding=encoding, newline=""
        ) as afp:
            writer = aiocsv.AsyncDictWriter(
                afp, [i for i in headers if i != 'id'], restval="NULL", quoting=csv.QUOTE_ALL
            )
            await writer.writeheader()

        logger.info(f'{table} 表自动创建成功')

    async def find_one(
            self, table: str, encoding: Optional[str] = None,
            field: Union[list, tuple, str, None] = None, offset: Optional[int] = 0,
            where: Optional[dict] = None
    ) -> dict:
        """
            查询一条数据
            Args:
                table: 表名
                encoding: csv 读写编码
                field: 查询字段
                offset: 偏移量
                where: 查询条件
            Return:
                dict，返回第 index 条数据
        """

        if encoding is None:
            encoding = self.encoding

        if where is None:
            df = pd.read_csv(
                self.path / (table + '.csv'), encoding=encoding, usecols=field,
                skiprows=range(1, offset), nrows=1
            )
        else:
            df = pd.read_csv(
                self.path / (table + '.csv'), encoding=encoding, usecols=field,
                skiprows=range(1, offset)
            )
            for k, v in where.items():
                df = df[df[k] == v]

        data = list(df.T.to_dict().values())
        return data[-1] if data else {}

    async def find_many(
            self, table: str, encoding: Optional[str] = None, field: Union[list, tuple, str, None] = None,
            count: Optional[int] = None, offset: Optional[int] = 0, where: Optional[dict] = None
    ) -> list:
        """
            查询一条数据
            Args:
                table: 表名
                encoding: csv 读写编码
                field: 查询字段
                count: 返回数据条数
                offset: 偏移量
                where: 查询条件
            Return:
                dict，返回第 index 条数据
        """

        if encoding is None:
            encoding = self.encoding

        if where is None:
            df = pd.read_csv(
                self.path / (table + '.csv'), encoding=encoding, usecols=field,
                skiprows=range(1, offset), nrows=count, dtype=ftype
            )
            return list(df.T.to_dict().values())
        else:
            df = pd.read_csv(
                self.path / (table + '.csv'), encoding=encoding, usecols=field,
                skiprows=range(1, offset), dtype=ftype
            )
            for k, v in where.items():
                df = df[df[k] == v]

            data = list(df.T.to_dict().values())[:count]
            return data

    async def insert(self, table: str, items: Union[list, dict], encoding: str = None, auto_update=False) -> None:
        """
            插入多条数据
            @params:
                table: 表名
                items: 需要插入的数据列表，list -> [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
                encoding: 文件编码
        """

        if not items:
            return

        if isinstance(items, dict):
            items = [items]

        if encoding is None:
            encoding = self.encoding

        field = list(items[0].keys())

        async with aiofiles.open(
                self.path / (table + '.csv'), mode='a', encoding=encoding, newline=""
        ) as afp:
            writer = aiocsv.AsyncDictWriter(afp, field, restval="NULL", quoting=csv.QUOTE_ALL)
            await writer.writerows(items)

    def remove_one(self):
        ...

    def remove_many(self):
        ...

    async def modify_one_smart(self, table: str, items: dict, where: dict) -> None:
        pass

    def update(self):
        pass

    async def close(self) -> None:
        pass
