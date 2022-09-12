import csv

import aiofiles
from aiocsv import AsyncReader, AsyncDictReader, AsyncDictWriter


class CSVFile:
    """csv 增删改查API"""

    engine = 'csv'

    def __init__(self, path, encoding='utf-8', write_mode='a'):
        self.path = path
        self.encoding = encoding
        self.write_mode = write_mode

    async def find_one(self):

        # simple reading
        async with aiofiles.open("new_file.csv", mode="r", encoding="utf-8", newline="") as afp:
            async for row in AsyncReader(afp):
                print(row)  # row is a list

        # dict reading, tab-separated
        async with aiofiles.open("new_file2.csv", mode="r", encoding="utf-8", newline="") as afp:
            async for row in AsyncDictReader(afp, delimiter="\t"):
                print(row)  # row is a dict

    async def insert_one(self, table: str, item: dict, encoding=None):
        """
            插入一条数据
            @params:
                table: 表名
                item: 需要插入的数据，dict -> {'a': 1, 'b': 2}
        """

        if encoding is None:
            encoding = self.encoding

        async with aiofiles.open(
                self.path / table + '.csv', mode=self.write_mode, encoding=encoding, newline=""
        ) as afp:
            writer = AsyncDictWriter(afp, item.keys(), quoting=csv.QUOTE_ALL)
            await writer.writeheader()
            await writer.writerow(item)

    async def insert_many(self, table: str, items: list, encoding=None):
        """
            插入多条数据
            @params:
                table: 表名
                items: 需要插入的数据列表，list -> [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
        """

        if encoding is None:
            encoding = self.encoding

        if items:
            async with aiofiles.open(
                    self.path / (table + '.csv'), mode=self.write_mode, encoding=encoding, newline=""
            ) as afp:
                writer = AsyncDictWriter(afp, items[0].keys(), quoting=csv.QUOTE_NONNUMERIC)
                await writer.writeheader()
                await writer.writerows(items)

    def remove_one(self):
        ...

    def remove_many(self):
        ...

    async def modify_one_smart(self, table, items: dict, where):
        pass

    def modify_many(self):
        pass

    async def commit(self):
        pass

    def close(self):
        pass
