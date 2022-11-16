from typing import Optional
import pymongo

from AioSpider.aio_db.abc_db import ABCDB


class MongoAPI(ABCDB):

    engine = 'mongo'

    def __init__(
            self, host: str = '127.0.0.1', port: int = 27017, db: Optional[str] = None,
            username: Optional[str] = None, password: Optional[str] = None
    ):

        client = pymongo.MongoClient(host=host, port=port, username=username, password=password)
        self.db = client[db]

    def insert_one(self, col, data=None):
        if data is None:
            print('数据为空，数据写入失败')
            return

        self.db[col].insert_one(data)

    def insert_many(self, col, data=None):
        if data is None:
            print('数据为空，数据写入失败')
            return

        self.db[col].insert_many(data)

    def update_one(self, col, query=None, data=None):
        if query is None:
            print('条件语句为空，数据更改失败')
            return

        if data is None:
            print('数据为空，数据更改失败')
            return

        self.db[col].update_one(query, data)

    def update_many(self, col, query=None, data=None):
        if query is None:
            print('条件语句为空，数据更改失败')
            return

        if data is None:
            print('数据为空，数据更改失败')
            return

        self.db[col].update_many(query, data)

    def find_one(self, col, query=None):
        if query is None:
            return self.db[col].find_one()

        return self.db[col].find_one(query)

    def find_many(self, col, query=None, limit=10):
        if query is None:
            return self.db[col].find({}, {'_id': 0})

        return self.db[col].find(query, {'_id': 0}).limit(limit)

    def exist(self, col):
        return True if self.db[col].find_one() else False
