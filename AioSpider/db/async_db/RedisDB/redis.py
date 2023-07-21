from abc import ABCMeta, abstractmethod
from typing import Optional, Union, Any, Callable, Type, List as _List, Dict

from aioredis import Redis


class RedisDataType(metaclass=ABCMeta):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_isinstance'):
            setattr(cls, '_isinstance', super().__new__(cls))
        return getattr(cls, '_isinstance')

    def __init__(self, pool):
        self._pool: Redis = pool

    @classmethod
    def from_redis(cls, pool):
        return cls(pool)

    @abstractmethod
    async def insert_one(self, name: str, value: str, **kwargs):
        pass

    @abstractmethod
    async def insert_many(self, name: str, value: str, *args, **kwargs):
        pass

    @abstractmethod
    async def remove(self):
        pass

    @abstractmethod
    async def find_one(self):
        pass

    @abstractmethod
    async def find_many(self):
        pass


class String(RedisDataType):

    async def insert_one(
            self, name: str, value: str, ex: int = None, px: int = None, nx: bool = False, xx: bool = False,
            keepttl: bool = False
    ):
        """
        新增一条数据
        Args:
            name: 键
            value: 值
            ex: 过期时间（秒）
            px: 过期时间（毫秒）
            nx: 如果设置为True，则只有name不存在时，当前set操作才执行
            xx: 如果设置为True，则只有name存在时，当前set操作才执行
        """
        return await self._pool.set(name, value, ex=ex, px=px, nx=nx, xx=xx, keepttl=keepttl)

    async def insert_many(self, items: _List[dict]):
        """
        新增多条数据
        Args:
            items: 键值对列表
        """
        return await self._pool.mset(items)

    async def remove(self):
        pass

    async def find_one(self, name):
        """获取元素"""
        return await self._pool.get(name)

    async def find_many(self, name):
        """获取元素"""
        pass

    async def setnx(self, name, value):
        """设置值，只有name不存在时，执行设置操作"""
        return await self._pool.setnx(name, value)

    async def setex(self, name, time, value):
        """设置键值对和过期时间"""
        return await self._pool.setex(name, time, value)

    async def psetex(self, name, time_ms, value):
        """设置键值对和毫秒过期时间"""
        return await self._pool.psetex(name, time_ms, value)

    async def mget(self, keys, *args):
        """批量获取"""
        return await self._pool.mget(keys, *args)

    async def getset(self, name, value):
        """设置新值并获取原来的值"""
        return await self._pool.getset(name, value)

    async def getrange(self, name, start, end):
        """
        获取子序列（根据字节获取，非字符）
        Args:
            name: 键
            start: 起始位置（字节）
            end: 结束位置（字节）
        """
        return await self._pool.getrange(name, start, end)

    async def setrange(self, name, offset, value):
        """修改字符串内容，从指定字符串索引开始向后替换（新值太长时，则向后添加）"""
        return await self._pool.setrange(name, offset, value)

    async def setbit(self, name, offset, value):
        """对 name 对应值的二进制表示的位进行操作"""
        return await self._pool.setbit(name, offset, value)

    async def getbit(self, name, offset):
        """获取name对应的值的二进制表示中的某位的值 （0或1）"""
        return await self._pool.getbit(name, offset)

    async def bitcount(self, key, start=None, end=None):
        """获取name对应的值的二进制表示中 1 的个数"""
        return await self._pool.bitcount(key, start=start, end=end)

    async def bitop(self, operation, dest, *keys):
        """获取多个值，并将值做位运算，将最后的结果保存至新的name对应的值"""
        return await self._pool.bitop(operation, dest, *keys)

    async def strlen(self, name):
        """返回name对应值的字节长度（一个汉字3个字节）"""
        return await self._pool.strlen(name)

    async def incr(self, name, amount=1):
        """自增 name 对应的值，当 name 不存在时，则创建 name＝amount，否则，则自增"""
        return await self._pool.incr(name, amount=amount)

    async def incrbyfloat(self, name, amount=1.0):
        """自增 name对应的值，当name不存在时，则创建name＝amount，否则，则自增"""
        return await self._pool.incrbyfloat(name, amount=amount)

    async def decr(self, name, amount=1):
        """自减 name 对应的值，当 name 不存在时，则创建 name＝amount，否则，则自减"""
        return await self._pool.decr(name, amount=amount)

    async def append(self, key, value):
        """在redis name对应的值后面追加内容"""
        return await self._pool.append(key, value)


class Set(RedisDataType):

    async def insert_one(self, name: str, value: str):
        """添加一条数据"""
        await self.sadd(name, value)

    async def insert_many(self, name: str, value: str, *args):
        """添加多条数据"""
        await self.sadd(name, value, *args)

    async def remove(self, name: str, count: Optional[int] = None, *values, way=1):
        """
        删除数据，默认随机删除1个
        Args:
            name: 键名
            count: 随机删除个数
            values: 指定删除方式的值
            way: 删除方式，1: 随机删除；2: 指定元素删除
        """
        if way == 1:
            await self.spop(name, count=count)
        else:
            await self.srem(name, *values)

    async def find_one(self, name: str):
        pass

    async def find_many(self, name: str):
        await self.smembers(name)

    async def sadd(self, name, *values):
        """添加元素"""
        return await self._pool.sadd(name, *values)

    async def scard(self, name):
        """获取元素个数"""
        return await self._pool.scard(name)

    async def smembers(self, name):
        """获取集合中所有的成员"""
        return await self._pool.smembers(name)

    async def sscan(self, name, cursor=0, match=None, count=None):
        """获取集合中所有的成员--元组形式"""
        return await self._pool.sscan(name, cursor=cursor, match=match, count=count)

    async def sscan_iter(self, name, match=None, count=None):
        """获取集合中所有的成员--迭代器的方式"""
        return await self._pool.sscan_iter(name, match=match, count=count)

    async def sdiff(self, keys, *args):
        """差集"""
        return await self._pool.sdiff(keys, *args)

    async def sdiffstore(self, dest, keys, *args):
        """获取keys对应集合的差集，再将其新加入到dest对应的集合中"""
        return await self._pool.sdiffstore(dest, keys, *args)

    async def sinter(self, keys, *args):
        """交集"""
        return await self._pool.sinter(keys, *args)

    async def sinterstore(self, dest, keys, *args):
        """获取keys对应集合的并集，再将其加入到dest对应的集合中"""
        return await self._pool.sinterstore(dest, keys, *args)

    async def sunion(self, keys, *args):
        """并集"""
        return await self._pool.sunion(keys, *args)

    async def sunionstore(self, dest, keys, *args):
        """获取keys对应的集合的并集，并将结果保存到dest对应的集合中"""
        return await self._pool.sunionstore(dest, keys, *args)

    async def sismember(self, name, value):
        """判断是否是集合的成员"""
        return await self._pool.sismember(name, value)

    async def smove(self, src, dst, value):
        """将某个成员从一个集合中移动到另外一个集合"""
        return await self._pool.smove(src, dst, value)

    async def spop(self, name, count: int = None):
        """随机删除并且返回被删除值"""
        return await self._pool.spop(name, count)

    async def srem(self, name, *values):
        """指定值删除"""
        return await self._pool.srem(name, *values)


class OrderSet(RedisDataType):

    async def insert_one(self, name, item: Union[str, dict, tuple, list]):
        """
        添加一条数据
        Args:
            name: 键
            value: 值
            nx: 使 ZADD 命令只创建新元素而不更新已存在元素的分数。
            xx: 使 ZADD 命令只更新已经存在的元素的分数，不会添加新元素。
            ch: 将返回值修改为更改的元素数。更改的元素包括添加的新元素和分数发生了变化的元素
            incr: 将 ZADD 修改为类似 ZINCRBY 的行为。在此模式下，只有可以指定单个元素/分数对，
                分数是数字时将会自增。使用此模式时 ZADD 的返回值将是元素的新得分。
        Return：
            ZADD 的返回值根据指定的模式而变化。没有选项时，ZADD 返回添加到有序集合中的新元素的分数
        """

        if isinstance(item, str):
            value = (item, 0)
        elif isinstance(item, dict):
            value = list(item.values())[0] if item else tuple()
        else:
            value = item

        return await self._pool.zadd(name, *value)

    async def insert_many(self, name: str, item: Union[list, Dict[str, int]]):
        """
        添加多条数据
        Args:
            name: 键
            value: 值
            nx: 使 ZADD 命令只创建新元素而不更新已存在元素的分数。
            xx: 使 ZADD 命令只更新已经存在的元素的分数，不会添加新元素。
            ch: 将返回值修改为更改的元素数。更改的元素包括添加的新元素和分数发生了变化的元素
            incr: 将 ZADD 修改为类似 ZINCRBY 的行为。在此模式下，只有可以指定单个元素/分数对，
                分数是数字时将会自增。使用此模式时 ZADD 的返回值将是元素的新得分。
        Return：
            ZADD 的返回值根据指定的模式而变化。没有选项时，ZADD 返回添加到有序集合中的新元素的分数
        """

        if isinstance(item, list):
            item = dict(zip(item, [0] * len(item)))

        return await self._pool.zadd(name, item)

    async def remove(self, name, *values):
        """删除--指定值删除"""
        return await self._pool.zrem(name, *values)

    async def find_one(
            self, name, start: int, end: int, desc: bool = False, withscores: bool = False,
            score_cast_func: Union[Type, Callable] = float
    ):
        pass

    async def find_many(
            self, name, start: int, end: int, desc: bool = False, withscores: bool = False,
            score_cast_func: Union[Type, Callable] = float
    ):
        """
        获取有序集合的所有元素
        Args:
            name: 键
            start: 有序集合索引起始位置（非分数）
            end: 有序集合索引结束位置（非分数）
            desc: 排序规则，默认按照分数从小到大排序
            withscores: 是否获取元素的分数，默认只获取元素的值
            score_cast_func: 对分数进行数据转换的函数
        """
        return await self._pool.zrange(
            name, start, end, desc=desc, withscores=withscores, score_cast_func=score_cast_func
        )
    
    async def zrange(
            self, name, start: int, end: int, desc: bool = False, withscores: bool = False,
            score_cast_func: Union[Type, Callable] = float
    ):
        return await self._pool.zrange(
            name, start, end, desc=desc, withscores=withscores, score_cast_func=score_cast_func
        )
    
    async def zadd(self, name, mapping, **kwargs):
        return await self._pool.zadd(name, mapping, **kwargs)

    async def zcard(self, name):
        """获取有序集合元素个数 类似于len"""
        return await self._pool.zcard(name)

    async def zcount(self, name, min, max):
        """获取name对应的有序集合中分数 在 [min,max] 之间的个数"""
        return await self._pool.zcount(name, min, max)

    async def zincrby(self, name, amount: float, value):
        """自增"""
        return await self._pool.zincrby(name, amount, value)

    async def zrank(self, name, value):
        """获取值的索引号"""
        return await self._pool.zrank(name, value)
    
    async def zrem(self, name, *value):
        """获取值的索引号"""
        return await self._pool.zrem(name, *value)

    async def zremrangebyrank(self, name, min: int, max: int):
        """删除--根据排行范围删除，按照索引号来删除"""
        return await self._pool.zremrangebyrank(name, min, max)

    async def zremrangebyscore(self, name, min, max):
        """删除--根据分数范围删除"""
        return await self._pool.zremrangebyscore(name, min, max)

    async def zscore(self, name, value):
        """获取值对应的分数"""
        return await self._pool.zscore(name, value)


class List(RedisDataType):

    async def insert_one(self, name: str, value: str, way: str = 'r'):
        """
        添加一条数据
        Args:
            name: 键名
            value: 值
            way: 添加方式，r: 右侧插入；l: 左侧插入
        """
        if way == 'r':
            await self.rpush(name, value)
        else:
            await self.lpush(name, value)

    async def insert_many(self, name: str, value: str, *args, **kwargs):
        """
        添加多条数据
        Args:
            name: 键名
            value: 值
            way: 添加方式，r: 右侧插入；l: 左侧插入
        """
        if way == 'r':
            await self.rpush(name, value, *args)
        else:
            await self.lpush(name, value, *args)

    async def remove(self, name: str, start: Optional[int] = None, end: Optional[int] = None):
        """
        删除数据，默认随机删除
        Args:
            name: 键名
            start: 开始位置
            end: 结束位置
        """
        if start is None or end is None:
            await self.lpop(name)
        else:
            await self.ltrim(name, start, end)

    async def find_one(self, name: str, index: int):
        await self.lindex(name, index)

    async def find_many(self, name: str, index: int):
        pass

    async def lpush(self, name, *values):
        """从左边新增加元素--没有就新建"""
        return await self._pool.lpush(name, *values)

    async def rpush(self, name, *values):
        """从右边新增加元素--没有就新建"""
        return await self._pool.rpush(name, *values)

    async def lpushx(self, name, value):
        """往已经有的name的列表的左边添加元素，没有的话无法创建"""
        return await self._pool.lpushx(name, value)

    async def rpushx(self, name, *value):
        """往已经有的name的列表的右边添加元素，没有的话无法创建"""
        return await self._pool.rpushx(name, *value)

    async def linsert(self, name, where, refvalue, value):
        """固定索引号位置插入元素"""
        return await self._pool.linsert(name, where, refvalue, value)

    async def lset(self, keys, index: int, value):
        """指定索引号进行修改"""
        return await self._pool.lset(keys, index, value)

    async def lrem(self, name, count: int, value):
        """指定值进行删除"""
        return await self._pool.lrem(name, count, value)

    async def lpop(self, name):
        """在name对应的列表的左侧获取第一个元素并在列表中移除，返回值则是第一个元素"""
        return await self._pool.lpop(name)

    async def ltrim(self, name, start: int, end: int):
        """在name对应的列表中移除没有在start-end索引之间的值"""
        return await self._pool.ltrim(name, start, end)

    async def lindex(self,  name, index):
        """根据索引号取值"""
        return await self._pool.lindex(name, index)

    async def rpoplpush(self, src, dst):
        """从一个列表取出最右边的元素，同时将其添加至另一个列表的最左边"""
        return await self._pool.rpoplpush(src, dst)

    async def brpoplpush(self, src, dst, timeout: int = 0):
        """从一个列表的右侧移除一个元素并将其添加到另一个列表的左侧"""
        return await self._pool.brpoplpush(src, dst, timeout)

    async def blpop(self, keys, timeout: int = 0):
        """一次移除多个列表，将多个列表排列，按照从左到右去pop对应列表的元素"""
        return await self._pool.blpop(keys, timeout)

    async def brpop(self, keys, timeout: int = 0):
        """一次移除多个列表，将多个列表排列,按照从右像左去移除各个列表内的元素"""
        return await self._pool.brpop(keys, timeout)

    async def llen(self, name):
        """获取列表长度"""
        return await self._pool.llen(name)

    async def list_iter(self, name):
        """列表增量迭代"""
        for index in range(await self.llen(name)):
            yield await self.lindex(name, index)


class Hash(RedisDataType):

    async def insert_one(self, name, item: dict):
        """添加一条数据"""
        key, value = list(item.items())[0]
        return await self._pool.hset(name, key, value, mapping)

    async def insert_many(self, name: str, items: _List):
        """添加多条数据"""
        return await self._pool.hmset(name, items)

    async def remove(self, name, keys):
        """删除键值对"""
        return await self._pool.hdel(name, keys)

    async def find_one(self, name, keys, *args):
        pass

    async def find_many(self, name, keys, *args):
        """批量取出"""
        return await self._pool.hmget(name, keys, *args)
    
    async def hset(self, name, key=None, value=None):
        return await self._pool.hset(name, key, value)

    async def hmset(self, name, mapping):
        return await self._pool.hmset(name, mapping)

    async def hgetall(self, name):
        """取出所有的键值对"""
        return await self._pool.hgetall(name)

    async def hlen(self, name):
        """得到所有键值对的格式 hash长度"""
        return await self._pool.hlen(name)

    async def hkeys(self, name):
        """得到所有的keys（类似字典的取所有keys）"""
        return await self._pool.hkeys(name)

    async def hvals(self, name):
        """得到所有的value（类似字典的取所有value）"""
        return await self._pool.hvals(name)

    async def hexists(self, name, key):
        """断成员是否存在（类似字典的in）"""
        return await self._pool.hexists(name, key)

    async def hincrbyfloat(self, name, key, amount: float = 1.0):
        """自增自减浮点数(将key对应的value--浮点数 自增1.0或者2.0，或者别的浮点数 负数就是自减)"""
        return await self._pool.hincrbyfloat(name, key, amount=amount)

    async def hscan(self, name, cursor: int = 0, match=None, count: Optional[int] = None):
        """取值查看--分片读取"""
        return await self._pool.hscan(name, cursor=cursor, match=match, count=count)

    async def hscan_iter(self, name, match=None, count: Optional[int] = None):
        """利用yield封装hscan创建生成器，实现分批去redis中获取数据"""
        return await self._pool.hscan_iter(name, match=match, count=count)


class AsyncRdisAPI:

    def __init__(
            self, *, host: str, port: int = 6379, username: Optional[str] = None, password: Optional[str] = None,
            db: [int, str] = 0, encoding: str = "utf-8", max_connections: Optional[int] = None
    ):
        self._conn_kwargs = {
            'host': host, 'port': port, 'username': username, 'password': password, 'db': db,
            'encoding': encoding, 'decode_responses': True, 'retry_on_timeout': True,
            'max_connections': max_connections,
        }
        self._pool = Redis(**self._conn_kwargs)

    @property
    def string(self) -> String:
        return String.from_redis(self._pool)

    @property
    def set(self) -> Set:
        return Set.from_redis(self._pool)

    @property
    def order_set(self) -> OrderSet:
        return OrderSet.from_redis(self._pool)

    @property
    def list(self) -> List:
        return List.from_redis(self._pool)

    @property
    def hash(self) -> Hash:
        return Hash.from_redis(self._pool)

    async def delete(self):
        """删除"""
        await self._pool.delete()

    async def exists(self):
        """检查名字是否存在"""
        await self._pool.exists()

    async def keys(self):
        """模糊匹配"""
        return await self._pool.keys()

    async def expire(self):
        """设置超时时间"""
        await self._pool.expire()

    async def rename(self):
        """重命名"""
        await self._pool.rename()

    async def randomkey(self):
        """随机获取name"""
        await self._pool.randomkey()

    async def type(self):
        """获取类型"""
        await self._pool.type()

    async def scan(self):
        """查看所有元素"""
        await self._pool.scan()

    async def scan_iter(self):
        """查看所有元素--迭代器"""
        await self._pool.scan()

    async def dbsize(self):
        """前redis包含多少条数据"""
        await self._pool.dbsize()

    async def save(self):
        """执行"检查点"操作，将数据写回磁盘。保存时阻塞"""
        await self._pool.save()

    async def flushdb(self):
        """清空所有数据"""
        await self._pool.flushdb()

    async def close(self):
        """关闭数据库连接"""
        await self._pool.connection_pool.disconnect()

    async def ping(self):
        await self._pool.ping()