import re
import copy
import asyncio

import AioSpider
from .field import Field, AutoIntField
from AioSpider import tools


class Container:

    def __init__(self, size=1000):
        self._size = size
        self._contain = dict()
        self._hash = dict()
        self.item_count = dict()

    def add_count(self, table, count):
        self.item_count[table] = self.item_count.get(table, 0) + count

    def get_count(self, table):
        return self.item_count.get(table, 0)

    def all_count(self):
        return sum(self.item_count.values())

    def add(self, item, table):

        if self._contain.get(table) is None:
            self._contain[table] = list()

        if self._hash.get(table) is None:
            self._hash[table] = set()

        item_hash = tools.get_hash(item)
        if item_hash not in self._hash[table]:
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

    async def commit(self, sender, item):

        table = sender.__name__
        self.add(item, table)

        if self.sql_size(table) >= self._size:
            data = copy.deepcopy(self._contain[table])
            self.add_count(table, len(data))
            AioSpider.logger.info(f'本次已向{table}表提交{len(data)}条记录，总共已提交{self.get_count(table)}条')
            self.clear(table)
            await AioSpider.db.insert_many(table=table, items=data)

    async def close(self, table):
        for k in self._contain:
            if not self._contain[k] or k != table:
                continue

            await AioSpider.db.insert_many(table=k, items=self._contain[k])
            self.add_count(table, self.sql_size(table))
            AioSpider.logger.info(f'本次已向{k}表提交{self.sql_size(table)}条记录，总共已提交{self.get_count(table)}条')
            self.clear(k)

        AioSpider.logger.info(
            f'爬虫即将关闭：总共保存 {self.all_count()} 条数据'
            f'（{"、".join([f"{k}表{v}条" for k, v in self.item_count.items()])}）'
        )


class CSVContainer(Container):

    async def commit(self, sender, item, encoding=None):

        table = sender.__name__
        self.add(item, table)

        if self.sql_size(table) >= self._size:
            data = copy.deepcopy(self._contain[table])
            self.add_count(table, len(data))
            AioSpider.logger.info(f'本次已向{table}表提交{len(data)}条记录，总共已提交{self.get_count(table)}条')
            self.clear(table)
            await AioSpider.db.insert_many(table=table, items=data, encoding=encoding)

    async def close(self, table, encoding=None):
        for k in self._contain:
            if not self._contain[k] or k != table:
                continue

            await AioSpider.db.insert_many(table=k, items=self._contain[k], encoding=encoding)
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
        name = self.__class__.__name__.replace('model', '').replace('Model', '')
        name = re.findall('[A-Z][^A-Z]*', name)
        name = [i.lower() for i in  name]
        return '_'.join(name)

    def _check_attr_(self):

        attr = [i for i in dir(self) if isinstance(getattr(self, i), Field)]

        if self.order and isinstance(self.order, list):
            order = self.order
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

    def _save_mysql(self):
        pass

    def _save_mongo(self):
        pass

    async def save(self):

        if AioSpider.db is None:
            raise Exception('未在settings中配置数据库引擎')

        if AioSpider.db is False:
            return

        if AioSpider.db.engine == 'sqlite':
            await self._save_sqlite()

        elif AioSpider.db.engine == 'csv':
            await self._save_csv()

        elif AioSpider.db.engine == 'mysql':
            self._save_mysql()

        elif AioSpider.db.engine == 'mongo':
            self._save_mongo()

    @classmethod
    async def close(cls):
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

        await AioSpider.db.create_table(sql=sql)


class SQLiteModel(SQLModel):

    container = SQLContainer()

    async def _save_sqlite(self):

        item = self.make_item()

        await self.container.commit(self, item)
        await self._create_table()

    @classmethod
    async def close(cls):
        name = cls.__name__.replace('model', '').replace('Model', '')
        name = re.findall('[A-Z][^A-Z]*', name)
        name = [i.lower() for i in name]
        await cls.container.close('_'.join(name))


class CSVModel(Model):

    encoding = None
    container = CSVContainer()

    async def _save_csv(self):

        item = self.make_item()
        await self.container.commit(self, item, encoding=self.encoding)

    @classmethod
    async def close(cls):
        name = cls.__name__.replace('model', '').replace('Model', '')
        name = re.findall('[A-Z][^A-Z]*', name)
        name = [i.lower() for i in name]
        await cls.container.close('_'.join(name), encoding=cls.encoding)

