import asyncio
from typing import List, Union, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from AioSpider.db.async_db.async_abc import AbcDB


class AsyncMongoAPI(AbcDB):
    """
    初始化
    Params:
        host: MongoDB的主机名，默认为localhost
        port: MongoDB的端口，默认为27017
        username: 用于连接的MongoDB用户名
        password: 对应的密码
        auth_db: 用于验证的数据库，默认是admin数据库
        max_size: 连接池的最大连接数，默认为100
        min_ize: 连接池的最小连接数，默认为0
        max_idle_time: 一个连接在连接池中空闲多久后会被关闭，默认为无限
    """
    def __init__(
            self, host: Optional[str] = None, port: Optional[int] = 27017, db: Optional[str] = None,
            username: Optional[str] = None, password: Optional[str] = None, max_connect_size: Optional[int] = 100,
            min_connect_size: Optional[int] = 0, max_idle_time: Optional[int] = 0
    ):
        client = AsyncIOMotorClient(
            host=host or 'localhost', port=port, username=username, password=password, authSource=db,
            maxPoolSize=max_connect_size, minPoolSize=min_connect_size, maxIdleTimeMS=max_idle_time
        )
        self.db = client[db]

    async def close(self):
        """
        关闭MongoDB数据库连接
        """
        await self.client.close()

    async def insert_one(self, collection: str, document: dict):
        """
        插入一条记录
        Params:
            collection: 要操作的集合名称
            document: 要插入的文档
        Return:
            插入文档的ID
        """
        col = self.db[collection]
        result = await col.insert_one(document)
        return result.inserted_id

    async def insert_many(self, collection: str, documents: List[dict]):
        """
        插入多条记录
        Params:
            collection: 要操作的集合名称
            documents: 要插入的文档列表
        Return:
            插入文档的ID列表
        """
        col = self.db[collection]
        result = await col.insert_many(documents)
        return result.inserted_ids

    async def find_one(self, collection: str, filter: dict):
        """
        查找一条记录
        Params:
            collection: 要操作的集合名称
            filter: 查询过滤器
        Return:
            返回找到的文档，如果没有找到，则返回None
        """
        col = self.db[collection]
        result = await col.find_one(filter)
        return result

    async def find_many(self, collection: str, filter: dict, sort: Optional[List[tuple]] = None, skip: int = 0, limit: int = 0):
        """
        查找多条记录
        Params:
            collection: 要操作的集合名称
            filter: 查询过滤器
            sort: 排序方式，例如[("field1", 1), ("field2", -1)]
            skip: 跳过的记录数
            limit: 限制返回的记录数
        Return:
            返回找到的文档列表，如果没有找到，则返回空列表
        """
        col = self.db[collection]
        cursor = col.find(filter).sort(sort).skip(skip).limit(limit)
        result = await cursor.to_list(length=100)
        return result

    async def update_one(self, collection: str, filter: dict, update: dict):
        """
        更新一条记录
        Params:
            collection: 要操作的集合名称
            filter: 查询过滤器
            update: 更新操作
        Return:
            返回被修改的文档数量
        """
        col = self.db[collection]
        result = await col.update_one(filter, update)
        return result.modified_count

    async def update_many(self, collection: str, filter: dict, update: dict):
        """
        更新多条记录
        Params:
            collection: 要操作的集合名称
            filter: 查询过滤器
            update: 更新操作
        Return:
            返回被修改的文档数量
        """
        col = self.db[collection]
        result = await col.update_many(filter, update)
        return result.modified_count

    async def delete_one(self, collection: str, filter: dict):
        """
        删除一条记录
        Params:
            collection: 要操作的集合名称
            filter: 查询过滤器
        Return:
            返回被删除的文档数量
        """
        col = self.db[collection]
        result = await col.delete_one(filter)
        return result.deleted_count

    async def delete_many(self, collection: str, filter: dict):
        """
        删除多条记录
        Params:
            collection: 要操作的集合名称
            filter: 查询过滤器
        Return:
            返回被删除的文档数量
        """
        col = self.db[collection]
        result = await col.delete_many(filter)
        return result.deleted_count

    async def upsert(self, collection: str, query: dict, new_data: dict):
        """
        插入新数据或更新已存在的数据。
        Params:
            collection (str): 操作的集合名称。
            query (dict): 用于查找数据的查询条件。
            new_data (dict): 要插入或更新的新数据。
        Return:
            UpdateResult: 包含了该操作的结果信息。

        例子:
            manager.upsert('my_collection', {'_id': 1}, {'name': 'John', 'age': 25})
        """
        coll = self.db[collection]
        result = await coll.update_one(query, {'$set': new_data}, upsert=True)
        return result


