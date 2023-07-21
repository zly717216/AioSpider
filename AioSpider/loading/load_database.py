import subprocess
from pprint import pformat
from pathlib import Path

from AioSpider import logger
from AioSpider import tools
from AioSpider.exceptions import NoRedisServerError
from AioSpider.db import Connector
from AioSpider.db.async_db import (
    AsyncSQLiteAPI, AsyncCSVFile, AsyncMySQLAPI, AsyncRdisAPI, AsyncMongoAPI
)


class LoadDatabase:
    
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.init_database()

    def __init__(self, settings):
        self.settings = settings

    async def _init_sqlite_database(self, db_engine):

        sqlite_config = db_engine.Sqlite['CONNECT']
        sqlite_conn = Connector()

        for name, config in sqlite_config.items():
            sqlite_path = config['SQLITE_PATH']
            sqlite_db = config['SQLITE_DB']
            path = sqlite_path / sqlite_db
            sqlite_timeout = config['SQLITE_TIMEOUT']
            chunk_size = config['CHUNK_SIZE']

            if not sqlite_path.exists():
                tools.mkdir(sqlite_path)

            sqlite_conn[name] = await AsyncSQLiteAPI(path, chunk_size, sqlite_timeout)

        logger.info(f"SQLite数据库已启动：\n{pformat(sqlite_config)}")
        return sqlite_conn

    async def _init_csv_database(self, db_engine):

        csv_conf = db_engine.Csv['CONNECT']
        csv_conn = Connector()
        csv_sync_conn = Connector()

        for name, config in csv_conf.items():

            csv_path = config['CSV_PATH']
            encoding = config['ENCODING']

            if not csv_path.exists():
                tools.mkdir(csv_path)

            csv_conn[name] = AsyncCSVFile(path=csv_path, encoding=encoding)

        logger.info(f"CSVFile数据库已启动：\n{pformat(db_engine.Csv)}")
        return csv_conn

    async def _init_mysql_database(self, db_engine):

        mysql_conf = db_engine.Mysql['CONNECT']
        mysql_conn = Connector()
        mysql_sync_conn = Connector()

        for name, config in mysql_conf.items():
            host = config['MYSQL_HOST']
            port = config['MYSQL_PORT']
            db = config['MYSQL_DB']
            user = config['MYSQL_USER_NAME']
            pwd = config['MYSQL_USER_PWD']
            charset = config['MYSQL_CHARSET']
            timeout = config['MYSQL_CONNECT_TIMEOUT']
            time_zone = config['MYSQL_TIME_ZONE']
            max_size = config['MYSQL_MAX_CONNECT_SIZE']
            min_size = config['MYSQL_MIN_CONNECT_SIZE']

            mysql_conn[name] = await AsyncMySQLAPI(
                host=host, port=port, db=db, user=user, password=pwd, max_size=max_size, min_size=min_size,
                connect_timeout=timeout, charset=charset, time_zone=time_zone
            )

        logger.info(f"MySql数据库已启动：\n{pformat(db_engine.Mysql)}")
        return mysql_conn

    async def _init_mongo_database(self, db_engine):

        mongo_conf = db_engine.Mongodb['CONNECT']
        mongo_conn = Connector()
        mongo_sync_conn = Connector()

        for name, config in mongo_conf.items():
            mo_host = config['MONGO_HOST']
            mo_port = config['MONGO_PORT']
            mo_db = config['MONGO_DB']
            mo_user = config['MONGO_USERNAME']
            mo_pwd = config['MONGO_USER_PWD']
            mo_max_size = config['MONGO_MIN_CONNECT_SIZE']
            mo_min_size = config['MONGO_MAX_CONNECT_SIZE']
            mo_max_idle = config['MONGO_MAX_IDLE_TIME']

            mongo_conn[name] = AsyncMongoAPI(
                host=mo_host, port=mo_port, db=mo_db, username=mo_user, password=mo_pwd,
                max_connect_size=mo_max_size, min_connect_size=mo_min_size, max_idle_time=mo_max_idle
            )

        logger.info(f"MongoDB数据库已启动：\n{pformat(db_engine.Mongodb)}")
        return mongo_conn

    async def _init_file_database(self, db_engine):

        file_conf = db_engine.File['CONNECT']
        file_conn = Connector()
        file_sync_conn = Connector()

        for name, config in file_conf.items():

            file_path = config['FILE_PATH']
            file_encoding = config['ENCODING']
            file_mode = config['WRITE_MODE']

            if not file_path.exists():
                tools.mkdir(file_path)

        logger.info(f"File数据库已启动：\n{pformat(db_engine.File)}")
        return file_conn

    async def _init_redis_database(self, db_engine):

        redis_conf = db_engine.Redis['CONNECT']
        redis_conn = Connector()
        redis_sync_conn = Connector()

        for name, config in redis_conf.items():
            redis_conn[name] = AsyncRdisAPI(**config)
            # 如果host为127.0.0.1或localhost启动redis服务
            if config['host'] in ['127.0.0.1', 'localhost', tools.get_ipv4()] and \
                    not tools.redis_running(port=config['port']):
                self._open_redis()

        logger.info(f"redis 数据库已启动：\n{pformat(db_engine.Redis)}")
        return redis_conn

    def _open_redis(self):
        if (Path(__file__).parent.parent / 'tools/Redis-x64/redis-server.exe').exists():
            # 使用 subprocess.Popen 在后台运行程序
            process = subprocess.Popen(
                Path(__file__).parent.parent / 'tools/Redis-x64/redis-server.exe',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        raise NoRedisServerError()

    async def init_database(self):

        db_engine = self.settings.DataBaseConfig
        conn_dict = dict()

        if hasattr(db_engine, 'Sqlite') and db_engine.Sqlite['enabled']:
            conn_dict['sqlite'] = await self._init_sqlite_database(db_engine)
        if hasattr(db_engine, 'Csv') and db_engine.Csv['enabled']:
            conn_dict['csv'] = await self._init_csv_database(db_engine)
        if hasattr(db_engine, 'Mysql') and db_engine.Mysql['enabled']:
            conn_dict['mysql'] = await self._init_mysql_database(db_engine)
        if hasattr(db_engine, 'Mongodb') and db_engine.Mongodb['enabled']:
            conn_dict['mongo'] = await self._init_mongo_database(db_engine)
        if hasattr(db_engine, 'File') and db_engine.File['enabled']:
            conn_dict['file'] = await self._init_file_database(db_engine)
        if hasattr(db_engine, 'Redis') and db_engine.Redis['enabled']:
            conn_dict['redis'] = await self._init_redis_database(db_engine)

        return conn_dict
