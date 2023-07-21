import asyncio
from collections import defaultdict

from AioSpider import logger, pretty_table
from AioSpider.models.models import Model


class Container:

    def __init__(self, connector, size: dict, db: dict, task_limit: int = 10):
        self.connector = connector
        self._size = size
        self.db = db
        self._contain = defaultdict(list)
        self.item_count = defaultdict(int)
        self.task_list = []
        self.task_limit = task_limit

    def add_count(self, table: str, count: int):
        self.item_count[table] += count

    def count(self, table: str) -> int:
        return self.item_count[table]

    def all_count(self) -> int:
        return sum(self.item_count.values())

    async def add(self, table: str, item: dict):
        self._contain[table].append(item)

    def clear(self, table: str):
        self._contain[table].clear()

    def size(self, table: str) -> int:
        return self._contain[table].__len__()

    async def close(self):

        if self.task_list:
            await asyncio.wait(self.task_list)
            self.task_list.clear()

        for table, items in self._contain.items():
            if not items:
                continue
            self.add_count(table, len(items))
            await self.connector[self.db[table]].insert(table=table, items=items, auto_update=True)
            self.clear(table)
            logger.info(f'本次已向{table}表提交{len(items)}条记录，总共已提交{self.count(table)}条记录')

        if self.all_count():
            item = [
                {'表名': table, '总条数': v, "合计条数": self.all_count()}
                for table, v in self.item_count.items()
            ]
            logger.info(f'爬虫即将关闭：总共保存 {self.all_count()} 条数据，详情如下：\n{pretty_table(item)}')

        return self.all_count()


class SQLCommit(Container):

    async def commit(self, table: str, auto_update: bool = True):

        async def save(self, table, items):
            await self.connector[self.db[table]].insert(
                table=table, items=[i for i in items], auto_update=auto_update
            )
            logger.info(f'本次已向{table}表提交{len(items)}条记录，总共已提交{self.count(table)}条')

        if self.size(table) >= self._size[table]:

            items = self._contain[table]

            self.add_count(table, len(items))
            self.task_list.append(asyncio.create_task(save(self, table, items)))
            self.clear(table)

        if len(self.task_list) >= self.task_limit:
            await asyncio.wait(self.task_list)
            self.task_list.clear()


class CSVCommit(Container):

    async def commit(self, table: str, encoding: str = None):

        async def save(self, table, items):
            await self.connector[self.db[table]].insert(
                table=table, items=[i for i in items], encoding=encoding
            )
            logger.info(f'本次已向{table}表提交{len(items)}条记录，总共已提交{self.count(table)}条')

        if self.size(table) >= self._size[table]:

            items = self._contain[table]

            self.add_count(table, len(items))
            self.task_list.append(asyncio.create_task(save(self, table, items)))

            self.clear(table)

        if len(self.task_list) >= self.task_limit:
            await asyncio.wait(self.task_list)
            self.task_list.clear()


class FileCommit(Container):

    async def commit(self, sender: Model):

        table = sender.Meta.tb_name

        item = self._contain[table]
        await sender.save()

        self.add_count(table, len(item))
        self.clear(table)
        logger.info(
            str(sender.path / (sender.name + sender.extension)) + f'保存成功，总共已保存{self.count(table)}个文件'
        )
