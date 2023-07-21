from AioSpider import logger, pretty_table
from AioSpider.constants import WriteMode
from AioSpider.db.sql import MysqlCreateTable, SqliteCreateTable, MysqlAlterTable, SqliteAlterTable
from AioSpider.models.models import SQLiteModel, MySQLModel, CSVModel


class CreateTable:

    def __init__(self, connector, models: list):
        self._connector = connector
        self._models = models

    async def create_sql_table(self):

        table_list = []

        for m in self._models:
            table = m.Meta.tb_name

            if not table:
                continue

            if issubclass(m, SQLiteModel):
                table_list.append(await self._handle_sqlite_table(m))
            elif issubclass(m, MySQLModel):
                table_list.extend(await self._handle_mysql_table(m))
            else:
                continue

        table_list = [i for i in table_list if i]
        if table_list:
            logger.info(f'已自动创建{len(table_list)}张表: \n{pretty_table(table_list)}')

    async def create_csv_table(self):
        for model in self._models:
            table = model.Meta.tb_name
            if not issubclass(model, CSVModel):
                continue
            if not await self._connector[model.Meta.engine][model.Meta.db].table_exist(table):
                await self._connector['csv'][model.Meta.db].create_table(
                    table=table, headers=[i for i in model.fields], encoding=model.Meta.encoding
                )
            else:
                if model.Meta.write_mode == WriteMode.W or model.Meta.write_mode == WriteMode.WB:
                    await self._connector['csv'][model.Meta.db].clear_table(table=table)

    async def _handle_sqlite_table(self, model):

        table = model.Meta.tb_name

        # 如果表不存在，新建表；如果表存在，修改表结构
        if not await self._connector[model.Meta.engine][model.Meta.db].table_exist(table):
            sql = str(SqliteCreateTable(model))
            await self._connector['sqlite'][model.Meta.db].create_table(sql=sql)
            return {'库名': model.Meta.db, '表名': table}

        if not model.Meta.read_only:
            # 修改表结构
            desc = await self._connector['sqlite'][model.Meta.db].desc(table)

            add_cols_sql = SqliteAlterTable(model).build_add_cols_sql(desc)
            modify_cols_sql = SqliteAlterTable(model).build_modify_cols_type_sql(desc)
            modify_primary_sql = SqliteAlterTable(model).build_modify_cols_primary_sql(desc)
            modify_unique_sql = SqliteAlterTable(model).build_modify_cols_unique_sql(desc)
            modify_index_sql = SqliteAlterTable(model).build_modify_cols_index_sql(desc)

            await self._execute_sqlite_alter_sql(
                model, add_cols_sql, modify_cols_sql, modify_primary_sql, modify_unique_sql, modify_index_sql
            )

        return {}

    async def _handle_mysql_table(self, model):

        table = model.Meta.tb_name

        if not await self._connector[model.Meta.engine][model.Meta.db].table_exist(table):
            sql = str(MysqlCreateTable(model))
            await self._connector['mysql'][model.Meta.db].create_table(sql=sql)
            return {'库名': model.Meta.db, '表名': table}
            
        if not model.Meta.read_only:
            desc = await self._connector['mysql'][model.Meta.db].desc(table)
            add_cols_sql = MysqlAlterTable(model).build_add_cols_sql(desc)
            modify_cols_sql = MysqlAlterTable(model).build_modify_cols_type_sql(desc)
            modify_primary_sql = MysqlAlterTable(model).build_modify_cols_primary_sql(desc)
            modify_unique_sql = MysqlAlterTable(model).build_modify_cols_unique_sql(desc)
            modify_index_sql = MysqlAlterTable(model).build_modify_cols_index_sql(desc)

            await self._execute_mysql_alter_sql(
                model, add_cols_sql, modify_cols_sql, modify_primary_sql, modify_unique_sql, modify_index_sql
            )

        return {}

    async def _execute_sqlite_alter_sql(
        self, model, add_cols_sql, modify_cols_sql, modify_primary_sql, modify_unique_sql, modify_index_sql
    ):

        async def recreate_table_with_data(self, model, table):
            data = await self._connector[model.Meta.engine][model.Meta.db].find_many(table=table)
            await self._connector[model.Meta.engine][model.Meta.db].drop_table(table=table)
            await self._connector[model.Meta.engine][model.Meta.db].create_table(sql=str(SqliteCreateTable(model)))
            await self._connector[model.Meta.engine][model.Meta.db].insert(
                table=table, items=data, auto_update=model.Meta.auto_update
            )

        table = model.Meta.tb_name

        # 添加字段
        if add_cols_sql:
            await recreate_table_with_data(self, model, table)
            logger.info(f"{table}表字段添加成功")

        # 修改字段类型
        if modify_cols_sql:
            await recreate_table_with_data(self, model, table)
            logger.info(f'{table}表字段类型修改成功')

        # 添加主键
        if modify_primary_sql:
            await recreate_table_with_data(self, model, table)
            logger.info(f'{table}表主键添加或修改成功')

        # 修改唯一索引
        if modify_unique_sql:
            await recreate_table_with_data(self, model, table)
            logger.info(f'{table}表唯一索引添加或修改成功')

        # 修改普通索引
        if modify_index_sql:
            await recreate_table_with_data(self, model, table)
            logger.info(f'{table}表索引添加或修改成功')

    async def _execute_mysql_alter_sql(
        self, model, add_cols_sql, modify_cols_sql, modify_primary_sql, modify_unique_sql, modify_index_sql
    ):

        table = model.Meta.tb_name

        # 添加字段
        if add_cols_sql:
            await self._connector['mysql'][model.Meta.db]._execute(add_cols_sql)
            logger.info(f"{table}表字段添加成功")

        # 修改字段类型
        if modify_cols_sql:
            await self._connector['mysql'][model.Meta.db]._execute(modify_cols_sql)
            logger.info(f'{table}表字段类型修改成功')

        # 修改主键
        if modify_primary_sql:
            await self._connector['mysql'][model.Meta.db]._execute(modify_primary_sql)
            logger.info(f'{table}表主键添加或修改成功')

        # 修改唯一索引
        if modify_unique_sql:
            await self._connector['mysql'][model.Meta.db]._execute(modify_unique_sql)
            logger.info(f'{table}表唯一索引添加或修改成功')

        # 修改普通索引
        if modify_index_sql:
            await self._connector['mysql'][model.Meta.db]._execute(modify_index_sql)
            logger.info(f'{table}表索引添加或修改成功')

    def create_mongo_doc(self):
        pass
