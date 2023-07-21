from AioSpider import tools, logger
from AioSpider.constants import BackendEngine
from AioSpider.filter import AutoBloom, RedisBloomFilter, BloomFilter


class DataLoader:

    def __init__(self, connector, capacity: int, max_capacity: int, models: list):
        self.connector = connector
        self.capacity = capacity
        self.max_capacity = max_capacity
        self.bloom = AutoBloom(capacity=capacity, max_capacity=max_capacity)
        self._connector = self.connector
        self._models = models

    async def process_field(self, model):

        field = model.get_unique_field()
        table = model.Meta.tb_name

        desc = await self._connector[model.Meta.engine][model.Meta.db].desc(table)
        desc_field = [i.field for i in desc]

        return [f for f in field if f in desc_field]

    async def load_unique_data(self, model):

        table = model.Meta.tb_name
        unique_field = model.get_unique_field()

        if unique_field:
            data = await self._connector[model.Meta.engine][model.Meta.db].find_many(
                table=table, field=model.get_unique_field()
            )
        else:
            field = [i for i in model.fields.keys() if i != 'id']
            data = await self._connector[model.Meta.engine][model.Meta.db].find_many(
                table=table, field=field
            )

        self.bloom.add_many([tools.join([v for v in i.values()], on='-') for i in data])

        if len(data):
            logger.info(f'已加载到 {table} 表 {len(data)} 条数据')

        del data

    async def load_data(self, model):

        table = model.Meta.tb_name
        field = await self.process_field(model)

        if not field:
            return None

        logger.debug(f'正在加载{table}表的哈希值...')
        data = await self._connector[model.Meta.engine][model.Meta.db].find_many(
            table=table, field=tools.join(field, on=',')
        )
        logger.debug(f'{table}表的哈希值加载完成')

        self.bloom.add_many(data)

        if len(data):
            logger.info(f'已加载到 {table} 表 {len(data)} 条数据')

        del data

    async def load_sql_data(self, engine):
        for model in self._models:
            await self.load_unique_data(model)

    async def load_csv_data(self):
        for model in self._models:
            await self.load_data(model)

    async def contains(self, hash: str):
        return hash in self.bloom

    async def add_hash(self, hash):
        self.bloom.add(hash)


class RedisDataLoader:

    def __init__(self, settings, connector, capacity: int, models: list):
        self.settings = settings
        self.connector = connector
        self._capacity = capacity
        self._connector = self.connector
        self._models = models

    async def create_bloom(self, table):
        if self.settings.SystemConfig.BackendCacheEngine == BackendEngine.redis:
            return RedisBloomFilter(
                conn=self._connector.redis['DEFAULT'],
                name=table, capacity=self._capacity
            )
        else:
            return BloomFilter(capacity=self._capacity)

    async def process_field(self, model, engine=None):
        field = model.get_unique_field()
        table = model.Meta.tb_name

        if engine:
            if not await self._connector[engine][model.Meta.db].table_exist(table):
                return []

            desc = await self._connector[engine][model.Meta.db].desc(table)
            return [f for f in field if f in desc]
        else:
            return field

    async def load_data(self, model, engine=None):
        table = model.Meta.tb_name
        bloom = await self.create_bloom(table)

        field = await self.process_field(model, engine)
        if not field:
            return

        logger.debug(f'正在加载{table}表的哈希值...')
        if engine:
            data = await self._connector[engine][model.Meta.db].find_many(table=table, field=tools.join(field, on=','))

        await bloom.add_many(data)
        if len(data):
            logger.info(f'已加载到 {table} 表 {len(data)} 条数据')

        del data

    async def load_sql_data(self, engine):
        for model in self._models:
            if model._unique():
                continue
            await self.load_data(model, engine)

    async def load_csv_data(self):
        for model in self._models:
            await self.load_data(model)

    async def contains(self, item: str, table: str):
        return await item in self.bloom
