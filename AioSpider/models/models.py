import re
import copy
import asyncio
from pathlib import Path
from importlib import import_module

import AioSpider
from .field import Field, AutoIntField
from AioSpider import tools, GlobalConstant
from AioSpider.filter import BloomFilter


class DataLoader:

    def __init__(self, capacity):
        self._capacity = capacity
        self._data_contain = dict()

    async def _load_data(self):

        sts = GlobalConstant().settings
        db = GlobalConstant().database

        if db.engine == 'mysql':
            for p in GlobalConstant().pipelines:

                _model = import_module('models')
                model = getattr(_model, p.model, None)
                if model is None:
                    continue

                field = self._get_field(model)
                table = self._handler_name(p.model)

                data = await db.find_many(sql=f'SELECT {field} FROM {table}')
                bloom = BloomFilter(capacity=self._capacity)
                bloom.add_many(data, is_hash=True)
                self._data_contain[table] = bloom

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
            name = re.findall('[A-Z][^A-Z]*', name)
            name = [i.lower() for i in  name]
            return '_'.join(name)

    def __contains__(self, item, table):
        return item in self._data_contain[table]

    def _get_field(self, model):

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


class Container:

    def __init__(self, size=1000):
        self._size = size
        self._contain = dict()
        self._hash = dict()
        self.item_count = dict()
        self._data_loader = None

    @property
    def data_loader(self):
        if self._data_loader is None:
            self._data_loader = GlobalConstant().dataloader
        return self._data_loader

    def add_count(self, table, count):
        self.item_count[table] = self.item_count.get(table, 0) + count

    def get_count(self, table):
        return self.item_count.get(table, 0)

    def all_count(self):
        return sum(self.item_count.values())

    def add(self, sender):

        table = sender.__name__
        item = sender.make_item()
        field = self.data_loader._get_field(sender)
        for i in copy.deepcopy(item):
            if i in field:
                continue
            item.pop(i)

        if self._contain.get(table) is None:
            self._contain[table] = list()

        if self._hash.get(table) is None:
            self._hash[table] = set()

        item_hash = tools.get_hash(item)
        if item_hash not in self._hash[table] and not self.data_loader.__contains__(item_hash, table):
            self._hash[table].add(item_hash)
            self._contain[table].append(item)

    def pop(self, table):
        self._contain[table].pop()

    def remove(self, item, table):
        self._contain[table].remove(item)

    def clear(self, table):
        self._contain[table].clear()

    def sql_size(self, table):
        return self._contain[table].__len__()


class SQLContainer(Container):

    async def commit(self, sender):

        table = sender.__name__
        self.add(sender)

        if self.sql_size(table) >= self._size:
            data = copy.deepcopy(self._contain[table])
            self.add_count(table, len(data))
            AioSpider.logger.info(f'本次已向{table}表提交{len(data)}条记录，总共已提交{self.get_count(table)}条')
            self.clear(table)
            await GlobalConstant().database.insert_many(table=table, items=data)

    async def close(self, table):
        for k in self._contain:
            if not self._contain[k] or k != table:
                continue

            await GlobalConstant().database.insert_many(table=k, items=self._contain[k])
            self.add_count(table, self.sql_size(table))
            AioSpider.logger.info(f'本次已向{k}表提交{self.sql_size(table)}条记录，总共已提交{self.get_count(table)}条记录')
            self.clear(k)

        if self.all_count():
            AioSpider.logger.info(
                f'爬虫即将关闭：总共保存 {self.all_count()} 条数据'
                f'（{"、".join([f"{k}表{v}条" for k, v in self.item_count.items()])}）'
            )


class CSVContainer(Container):

    async def commit(self, sender, encoding=None):

        table = sender.__name__
        self.add(sender)

        if self.sql_size(table) >= self._size:
            data = copy.deepcopy(self._contain[table])
            self.add_count(table, len(data))
            AioSpider.logger.info(f'本次已向{table}表提交{len(data)}条记录，总共已提交{self.get_count(table)}条')
            self.clear(table)
            await GlobalConstant().database.insert_many(table=table, items=data, encoding=encoding)

    async def close(self, table, encoding=None):
        for k in self._contain:
            if not self._contain[k] or k != table:
                continue

            await GlobalConstant().database.insert_many(table=k, items=self._contain[k], encoding=encoding)
            self.add_count(table, self.sql_size(table))
            AioSpider.logger.info(f'本次已向{k}表提交{self.sql_size(table)}条记录，总共已提交{self.get_count(table)}条')
            self.clear(k)

        AioSpider.logger.info(
            f'爬虫即将关闭：总共保存 {self.all_count()} 条数据'
            f'（{"、".join([f"{k}表{v}条" for k, v in self.item_count.items()])}）'
        )


class Model:

    id = AutoIntField(name='id', db_index=True)
    order = None
    container = Container()

    def __init__(self, item=None):
        if item is not None:
            for f in self._check_attr_():
                setattr(self, f, item.get(f))

    def __setattr__(self, key, value):

        if key.startswith('_') or key.endswith('_'):
            return

        o = getattr(self, key, Field)
        o._value = value
        o.db_column = key
        o._check_value()

    @property
    def __name__(self):

        name_type = getattr(GlobalConstant().settings, 'MODEL_NAME_TYPE', None)
        if name_type == 'lower':
            name = self.__class__.__name__.replace('model', '').replace('Model', '')
            return name.lower()
        elif name_type == 'upper':
            name = self.__class__.__name__.replace('model', '').replace('Model', '')
            return name.upper()
        else:
            name = self.__class__.__name__.replace('model', '').replace('Model', '')
            name = re.findall('[A-Z][^A-Z]*', name)
            name = [i.lower() for i in  name]
            return '_'.join(name)

    def _order(self):
        if self.order is None:
            self.order = [i for i in dir(self) if isinstance(getattr(self, i), Field)]
        return self.order

    def _check_attr_(self):

        attr = [i for i in dir(self) if isinstance(getattr(self, i), Field)]

        if self._order and isinstance(self._order, list):
            order = self._order
            for i in attr:
                if i not in order:
                    order.append(i)
            attr = order

        if 'id' in attr:
            attr.remove('id')
            attr.insert(0, 'id')

        return attr

    def make_item(self):

        value_dic = {}

        for f in self._check_attr_():
            field_obj = getattr(self, f, None)
            if isinstance(field_obj, Field) and field_obj.is_save:
                value_dic[f] = getattr(self, f, None)._value
            else:
                value_dic[f] = None

        if 'id' in value_dic:
            value_dic.pop('id')

        return value_dic

    async def _save_sqlite(self):
        pass

    async def _save_csv(self):
        pass

    async def _save_mysql(self):
        pass

    def _save_mongo(self):
        pass

    async def save(self):
        
        db = GlobalConstant().database
        if db is None:
            return None

        if db.engine == 'sqlite':
            await self._save_sqlite()

        elif db.engine == 'csv':
            await self._save_csv()

        elif db.engine == 'mysql':
            await self._save_mysql()

        elif db.engine == 'mongo':
            self._save_mongo()

    @classmethod
    async def _close(cls):
        pass


class SQLModel(Model):

    class TableCreate:

        create = False
        table = []

        def __new__(cls, table_name, *args, **kwargs):
            if table_name not in cls.table:
                cls.table.append(table_name)
                cls.instance = object.__new__(cls)

            return cls.instance

        @property
        def is_create(self):
            return self.create

        def set_create(self):
            self.create = True

        def clear_create(self):
            self.create = False

    def _table_sql(self):

        sql = f'CREATE TABLE {self.__name__} (\n'
        for f in self._check_attr_():
            sql += getattr(self, f)._table_sql() + ',\n'
        sql = sql[:-2] + '\n)'

        return sql

    async def _create_table(self):

        t = self.TableCreate(self.__name__)
        if t.is_create:
            return

        t.set_create()
        sql = self._table_sql()

        await GlobalConstant().database.create_table(sql=sql)


class SQLiteModel(SQLModel):

    container = SQLContainer()

    async def _save_sqlite(self):
        await self.container.commit(self)
        await self._create_table()

    @classmethod
    async def _close(cls):

        name_type = getattr(GlobalConstant().settings, 'MODEL_NAME_TYPE', None)
        if name_type == 'lower':
            name = cls.__name__.replace('model', '').replace('Model', '')
            await cls.container.close(name.lower())
        elif name_type == 'upper':
            name = cls.__name__.replace('model', '').replace('Model', '')
            await cls.container.close(name.upper())
        else:
            name = cls.__name__.replace('model', '').replace('Model', '')
            name = re.findall('[A-Z][^A-Z]*', name)
            name = [i.lower() for i in name]
            await cls.container.close('_'.join(name))


class MySQLModel(SQLModel):

    id = AutoIntField(name='id', db_index=True, auto_field='AUTO_INCREMENT')
    container = SQLContainer()

    async def _save_mysql(self):
        await self.container.commit(self)
        await self._create_table()

    @classmethod
    async def _close(cls):

        name_type = getattr(GlobalConstant().settings, 'MODEL_NAME_TYPE', None)
        if name_type == 'lower':
            name = cls.__name__.replace('model', '').replace('Model', '')
            await cls.container.close(name.lower())
        elif name_type == 'upper':
            name = cls.__name__.replace('model', '').replace('Model', '')
            await cls.container.close(name.upper())
        else:
            name = cls.__name__.replace('model', '').replace('Model', '')
            name = re.findall('[A-Z][^A-Z]*', name)
            name = [i.lower() for i in name]
            await cls.container.close('_'.join(name))


class CSVModel(Model):

    encoding = None
    container = CSVContainer()

    async def _save_csv(self):
        await self.container.commit(self, encoding=self.encoding)

    @classmethod
    async def _close(cls):

        name_type = getattr(GlobalConstant().settings, 'MODEL_NAME_TYPE', None)
        if name_type == 'lower':
            name = cls.__name__.replace('model', '').replace('Model', '')
            await cls.container.close(name.lower(), encoding=cls.encoding)
        elif name_type == 'upper':
            name = cls.__name__.replace('model', '').replace('Model', '')
            await cls.container.close(name.upper(), encoding=cls.encoding)
        else:
            name = cls.__name__.replace('model', '').replace('Model', '')
            name = re.findall('[A-Z][^A-Z]*', name)
            name = [i.lower() for i in name]
            await cls.container.close('_'.join(name), encoding=cls.encoding)
