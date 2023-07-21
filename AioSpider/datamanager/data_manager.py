from typing import List, Dict, Type

from AioSpider import tools
from AioSpider.models.models import Model
from AioSpider.datamanager.create_table import CreateTable
from AioSpider.datamanager.data_loader import DataLoader
from AioSpider.datamanager.commit import SQLCommit, FileCommit, CSVCommit, Container


class DataManager:

    def __init__(self, settings, connector, models: List[Type[Model]]):

        self.settings = settings
        self.connector = connector
        self.models = models
        self._capacity = settings.DataFilterConfig.BLOOM_INIT_CAPACITY
        self._max_capacity = settings.DataFilterConfig.BLOOM_MAX_CAPACITY
        self._size = settings.DataFilterConfig.COMMIT_SIZE
        self._container: Dict[str, Container] = None
        self.dataloader: DataLoader = None

    @property
    def containers(self) -> Dict[str, 'Container']:
        """返回包含不同连接器对应容器类的容器字典"""

        if self._container is None:

            size = {m.Meta.tb_name: m.Meta.commit_size or self._size for m in self.models}
            db = {m.Meta.tb_name: m.Meta.db or self._size for m in self.models}

            container_classes = {
                'mysql': SQLCommit,
                'sqlite': SQLCommit,
                'csv': CSVCommit,
                'file': FileCommit,
            }

            self._container = {
                connector: container_class(
                    self.connector[connector], size=size, db=db, task_limit=self.settings.DataFilterConfig.TASK_LIMIT
                )
                for connector, container_class in container_classes.items()
                if connector in self.connector
            }

        return self._container

    async def open(self):
        """打开数据管理器，创建表并加载数据"""

        await self._create_table()
        self.dataloader = await self._load_data()

    async def _load_data(self) -> 'DataLoader':
        """加载数据，考虑数据过滤设置"""

        data_loader = DataLoader(
            connector=self.connector, capacity=self._capacity,
            max_capacity=self._max_capacity, models=self.models
        )

        if not self.settings.DataFilterConfig.DATA_FILTER_ENABLED:
            return data_loader

        data_loaders = {
            'mysql': data_loader.load_sql_data,
            'sqlite': data_loader.load_sql_data,
            'csv': data_loader.load_csv_data,
        }

        for connector in self.connector:
            data_loader_func = data_loaders.get(connector)
            if data_loader_func:
                await data_loader_func(connector)

        return data_loader

    async def _create_table(self):
        """创建表格"""

        table_manager = CreateTable(self.connector, models=self.models)

        table_creators = {
            'mysql': table_manager.create_sql_table,
            'sqlite': table_manager.create_sql_table,
            'csv': table_manager.create_csv_table,
        }

        for connector in self.connector:
            table_creator_func = table_creators.get(connector)
            if table_creator_func:
                await table_creator_func()

    async def add_hash(self, hash_str):
        await self.dataloader.add_hash(hash_str)

    async def hash_in_bloom(self, hash):
        return await self.dataloader.contains(hash)

    async def commit(self, model: Type[Model]):
        """提交数据到指定容器"""

        table = model.Meta.tb_name
        item = model.make_item()

        duplicate_field = [f for f in model.get_unique_field() if f in item]
        if duplicate_field:
            item_hash = tools.make_md5(
                tools.join([item.get(i) for i in duplicate_field], on='-')
            )
        else:
            field = [i for i in model.fields.keys() if i != 'id']
            item_hash = tools.make_md5(
                tools.join([item.get(i) for i in field], on='-')
            )

        if await self.hash_in_bloom(item_hash):
            return None

        await self.add_hash(item_hash)

        container = self.containers[model.Meta.engine]
        await container.add(table, item=item)

        if model.Meta.engine in ['mysql', 'sqlite']:
            await container.commit(table, auto_update=model.Meta.auto_update)
        elif model.Meta.engine == 'csv':
            await container.commit(table, encoding=model.Meta.encoding)
        elif model.Meta.engine == 'file':
            await container.commit(model)
        else:
            raise NotImplemented
