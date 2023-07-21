from pathlib import Path

from AioSpider import tools
from AioSpider.utils_pkg import aiofiles
from AioSpider.db.async_db.async_abc import AbcDB


class AsyncFile(AbcDB):
    """file 增删改查API"""

    def __init__(self, path: Path, encoding: str = 'utf-8', write_mode: str = 'a'):
        self.path = path
        self.encoding = encoding
        self.write_mode = write_mode

    async def find_one(self):
        pass

    async def find_many(self):
        pass

    async def insert_one(self, table: str, item: dict, encoding=None):
        """
            插入一条数据
            @params:
                table: 表名
                item: 需要插入的数据，dict -> {'a': 1, 'b': 2}
        """

        if encoding is None:
            encoding = self.encoding

        dir_path = self.path / table
        tools.mkdir(dir_path)
        path = dir_path / (item[FileAttribute.NAME] + item[FileAttribute.EXTENSION])

        if isinstance(item[FileAttribute.CONTENT], bytes):
            async with aiofiles.open(path, mode=self.write_mode) as afp:
                await afp.write(item['content'])
        else:
            async with aiofiles.open(path, mode=self.write_mode, encoding=encoding) as afp:
                await afp.write(item['content'])

    async def insert_many(self, table: str, items: list, encoding=None):
        """
            插入多条数据
            @params:
                table: 表名
                items: 需要插入的数据列表，list -> [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
        """

        for item in items:
            await self.insert_one(table, item, encoding=encoding)

    def remove_one(self):
        ...

    def remove_many(self):
        ...

    def update_one(self):
        pass

    def update_many(self):
        pass

    async def close(self):
        pass
