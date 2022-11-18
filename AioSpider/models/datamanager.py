from pathlib import Path
from typing import Optional
from importlib import import_module
from abc import ABCMeta, abstractmethod

from AioSpider import tools, GlobalConstant
from AioSpider.filter import BloomFilter

from .field import Field


class DataManager:

    def __init__(self, capacity: int):

        self._logger = GlobalConstant().logger
        self._db = GlobalConstant.database
        self._pipelines = GlobalConstant().pipelines
        self._models = None
        self._capacity = capacity
        self._size = getattr(GlobalConstant().settings, 'COMMIT_SIZE', 1000)
        self._container = None
        self._dataloader = None

    @property
    def models(self):
        """遍历模型"""

        if self._models is None:
            models = import_module(Path().cwd().name + '.models')
            GlobalConstant().models = models
            self._models = [getattr(models, p.model, None) for p in self._pipelines]
            self._models = [i for i in self._models if i]
        return self._models

    async def open(self):
        """加载数据管理器"""

        await self._create_table()
        self._dataloader = await self._load_data()
        self._set_container()

    async def _load_data(self):
        """加载数据"""

        data_loader = DataLoader(capacity=self._capacity, models=self.models)

        # 数据去重
        if not getattr(GlobalConstant().settings, 'DATA_FILTER_ENABLE', False):
            return data_loader

        if self._db.engine == 'mysql' or self._db.engine == 'sqlite':
            await data_loader._load_sql_data()
        elif self._db.engine == 'mongo':
            pass
        elif self._db.engine == 'csv':
            pass
        else:
            raise Exception('数据库引擎错误')

        return data_loader

    async def _create_table(self):
        """建表"""

        table_manager = CreateTable(models=self.models)

        if self._db.engine == 'mysql' or self._db.engine == 'sqlite':
            await table_manager._create_sql_table()
        elif self._db.engine == 'mongo':
            pass
        elif self._db.engine == 'csv':
            pass
        else:
            raise Exception('数据库引擎错误')

    def _set_container(self):
        """绑定数据容器"""

        if self._db.engine == 'mysql' or self._db.engine == 'sqlite':
            self._container = SQLContainer(
                manager=self,
                size={m().__name__: m.commit_size or self._size for m in self.models}
            )
        elif self._db.engine == 'mongo':
            pass
        elif self._db.engine == 'csv':
            self._container = CSVContainer(
                manager=self,
                encoding={m().__name__: m.encoding for m in self.models},
                size={m().__name__: m.commit_size or self._size for m in self.models}
            )

        else:
            raise Exception('数据库引擎错误')

    async def commit(self, model: object):
        if self._container is None:
            return
        await self._container.commit(model)

    async def close(self):
        """结束保存剩余数据"""
        await self._container.close()


class DataLoader:

    def __init__(self, capacity: int, models: list):

        self._capacity = capacity
        self._data_contain = dict()
        self._logger = GlobalConstant().logger
        self._db = GlobalConstant.database
        self._models = models

    async def _load_sql_data(self):
        for m in self._models:
            field = self._get_field(m)
            table = self._handler_name(m.__name__)

            data = await self._db[m.db].find_many(sql=f'SELECT {field} FROM {table}')
            bloom = BloomFilter(capacity=self._capacity)
            bloom.add_many(data, is_hash=True)
            self._data_contain[table] = bloom
            self._logger.info(f'已加载到 {table} 表 {len(data)} 条数据')

    def _handler_name(self, name: str):

        name_type = getattr(GlobalConstant().settings, 'MODEL_NAME_TYPE', None)
        if name_type == 'lower':
            name = name.replace('model', '').replace('Model', '')
            return name.lower()
        elif name_type == 'upper':
            name = name.replace('model', '').replace('Model', '')
            return name.upper()
        else:
            name = name.replace('model', '').replace('Model', '')
            name = tools.re(regx='[A-Z][^A-Z]*', text=name)
            name = [i.lower() for i in name]
            return '_'.join(name)

    def __contains__(self, item: str, table: str):
        if self._data_contain.get(table) is None:
            return False
        return item in self._data_contain[table]

    def _get_field(self, model: object):

        field = [i for i in dir(model) if isinstance(getattr(model, i), Field) and not getattr(model, i).dnt_filter]
        order = model.order

        if order is None:
            return tools.join(field, ',')

        if len(order) == len(field):
            return tools.join(order, ',')

        for i in field:
            if i in order:
                continue
            order.append(i)

        return tools.join(order, ',')


class CreateTable:

    def __init__(self, models: list):

        self._logger = GlobalConstant().logger
        self._db = GlobalConstant.database
        self._models = models

    async def _create_sql_table(self):
        for m in self._models:
            table = self._handler_name(m.__name__)
            sql = f'CREATE TABLE {table} (\n'
            for f in self._get_field(m):
                sql += getattr(m, f)._table_sql(cols=f) + ',\n'
            sql = f'{sql[:-2]}\n) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT="{m.__doc__}"'
            await self._db[m.db].create_table(sql=sql)
            self._logger.info(f'{table} 创建表成功')

    def _create_mongo_doc(self):
        pass

    def _create_csv_table(self):
        pass

    def _handler_name(self, name):

        name_type = getattr(GlobalConstant().settings, 'MODEL_NAME_TYPE', None)
        if name_type == 'lower':
            name = name.replace('model', '').replace('Model', '')
            return name.lower()
        elif name_type == 'upper':
            name = name.replace('model', '').replace('Model', '')
            return name.upper()
        else:
            name = name.replace('model', '').replace('Model', '')
            name = tools.re(regx='[A-Z][^A-Z]*', text=name)
            name = [i.lower() for i in name]
            return '_'.join(name)

    def _get_field(self, model):
        """获取模型字段"""

        attr = [i for i in dir(model) if isinstance(getattr(model, i), Field)]
        order = self._order(model)

        if order and hasattr(order, '__iter__'):
            for i in attr:
                if i not in order:
                    order.append(i)
            attr = order

        if 'id' in attr:
            attr.remove('id')
            attr.insert(0, 'id')

        return attr

    def _order(self, model):
        if model.order is None:
            return [i for i in dir(model) if isinstance(getattr(model, i), Field)]
        return model.order


class Container:

    def __init__(self, size: dict, manager: Optional[object] = None):
        self._size = size
        self._contain = dict()
        self._hash = dict()
        self.item_count = dict()
        self._data_manager = manager
        self._logger = GlobalConstant().logger
        self.__db = None

    @property
    def _db(self):
        if self.__db is None:
            self.__db = GlobalConstant.database
        return self.__db

    @property
    def data_manager(self):
        if self._data_manager is None:
            self._data_manager = GlobalConstant().datamanager
        return self._data_manager

    def add_count(self, table: str, count: int):
        self.item_count[table] = self.item_count.get(table, 0) + count

    def get_count(self, table: str) -> int:
        return self.item_count.get(table, 0)

    def all_count(self) -> int:
        return sum(self.item_count.values())

    def add(self, sender: object):

        table = sender.__name__
        item = sender._make_item()
        item_copy = tools.deepcopy(item)
        field = sender._get_field()

        for i in tools.deepcopy(item_copy):
            if i in field:
                continue
            item_copy.pop(i)

        if self._contain.get(table) is None:
            self._contain[table] = list()

        if self._hash.get(table) is None:
            self._hash[table] = set()

        item_hash = tools.get_hash(item_copy)
        if item_hash not in self._hash[table] and not self.data_manager._dataloader.__contains__(item_hash, table):
            self._hash[table].add(item_hash)
            self._contain[table].append(item)

    def pop(self, table: str):
        self._contain[table].pop()

    def remove(self, item: dict, table: str):
        self._contain[table].remove(item)

    def clear(self, table: str):
        self._contain[table].clear()

    def sql_size(self, table: str) -> int:
        return self._contain[table].__len__()


class ABCCommit(metaclass=ABCMeta):

    # def __init__(self):
    #     self._logger = GlobalConstant().logger

    @abstractmethod
    async def commit(self, sender: object):
        pass


class ABCClose(metaclass=ABCMeta):

    def __init__(self):
        self._logger = GlobalConstant().logger
        self.__db = None

    @property
    def _db(self):
        if self.__db is None:
            self.__db = GlobalConstant.database
        return self.__db

    @abstractmethod
    async def close(self):
        pass


class SQLCommit(ABCCommit, Container):

    async def commit(self, sender: object):

        table = sender.__name__
        self.add(sender)

        if self.sql_size(table) >= self._size[table]:
            data = tools.deepcopy(self._contain[table])
            self.add_count(table, len(data))
            self.clear(table)
            await self._db[sender.db].insert_many(table=table, items=data)
            self._logger.info(f'本次已向{table}表提交{len(data)}条记录，总共已提交{self.get_count(table)}条')


class CSVCommit(ABCCommit, Container):

    def __init__(self, size: dict, manager: Optional[object] = None, encoding: Optional[dict] = None):
        super(CSVCommit, self).__init__(size=size, manager=manager)
        self.encoding = encoding

    async def commit(self, sender: object):

        table = sender.__name__
        self.add(sender)

        if self.sql_size(table) >= self._size[table]:
            data = tools.deepcopy(self._contain[table])
            self.add_count(table, len(data))
            self._logger.info(f'本次已向{table}表提交{len(data)}条记录，总共已提交{self.get_count(table)}条')
            self.clear(table)
            await self._db[self.db].insert_many(table=table, items=data, encoding=self.encoding[table])


class CloseContainer(ABCClose):

    async def close(self):
        for k in self._contain:
            item = self._contain[k]
            if not item:
                continue
            await self._db[item[0].db].insert_many(table=k, items=item)
            self.add_count(k, self.sql_size(k))
            self._logger.info(f'本次已向{k}表提交{self.sql_size(k)}条记录，总共已提交{self.get_count(k)}条记录')
            self.clear(k)

        if self.all_count():
            self._logger.info(
                f'爬虫即将关闭：总共保存 {self.all_count()} 条数据'
                f'（{"、".join([f"{k}表{v}条" for k, v in self.item_count.items()])}）'
            )


class SQLContainer(SQLCommit, CloseContainer):
    pass


class CSVContainer(CSVCommit, CloseContainer):
    pass
