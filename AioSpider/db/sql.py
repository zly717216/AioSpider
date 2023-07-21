import re
from abc import abstractmethod
from pathlib import Path
from datetime import datetime, date
from typing import Union, Optional

from pymysql.converters import escape_string

from AioSpider import tools
from AioSpider.field import (
    UniqueUnionIndexField, NormalIndexField, UniqueIndexField, UnionIndexField, TextField
)


def escape_strings(value):
    """转移数据类型"""

    if isinstance(value, str):
        escaped_value = escape_string(value)
        return f'"{escaped_value}"'
    elif isinstance(value, Path):
        return '"' + escape_string(str(value)).replace('"', '""') + '"'
    elif isinstance(value, (datetime, date)):
        return '"' + str(value) + '"'
    elif isinstance(value, (int, float, bool)):
        return str(value)
    elif value is None:
        return 'NULL'
    elif isinstance(value, (list, tuple)):
        return ','.join(escape_strings(item) for item in value)
    else:
        return escape_string(str(value))


def compare(k, v):
    return [
        f'`{k}`{op}{escape_strings(val)}'
        for op, val in v.items() if op in ('>=', '<=', '=', '>', '<')
    ]


class SelectBase:
    """
        生成查询语句
        @params:
            table: 表名
            field: 查询字段约束
            where: 查询条件，dict -> {字段名1: 字段值1, 字段名2: 字段值2}
            group: 分组
            having: 筛选分组后的各组数据
            order: 排序
            desc: 是否倒序
            limit: 数量
            offset: 偏移量
            join: 多表连接查询,
            subquery: 子查询,
            union: 联合查询,
            union_all: 联合查询,
            distinct: 去重行,
    """

    def __init__(
            self,
            table: str,
            field: Union[list, tuple, str, None] = None,
            where: Optional[dict] = None,
            group: Union[list, tuple] = None,
            having: Optional[dict] = None,
            order: Union[list, tuple] = None,
            desc: bool = False,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            join: Optional[list] = None,
            subquery: Optional[str] = None,
            union: Optional[str] = None,
            union_all: Optional[str] = None,
            distinct: bool = False
    ):
        self._table = table
        self._field = field
        self._where = where
        self._group = group
        self._having = having
        self._order = order
        self._limit = limit
        self._offset = offset
        self._desc = desc
        self._join = join
        self._subquery = subquery
        self._union = union
        self._union_all = union_all
        self._distinct = distinct

    def __str__(self):
        pass

    __repr__ = __str__

    def build_field(self):
        pass

    def build_where(self):

        if not self._where:
            return None

        if not isinstance(self._where, dict):
            raise TypeError(f'where 参数类型错误，当前类型为：{type(self._where)}，必须为 dict 类型')

        where_list = [
            compare(k, v) if isinstance(v, dict) else [f'`{k}`={escape_strings(v)}']
            for k, v in self._where.items()
        ]
        where_list = [j for i in where_list for j in i if j]
        return ' WHERE ' + tools.join(where_list, on=' AND ')

    def build_group(self):
        if self._group is None:
            return None
        elif isinstance(self._group, str):
            return f' GROUP BY {self._group}'
        elif isinstance(self._group, (list, tuple)):
            return f' GROUP BY {tools.join(self._group, on=",")}'
        else:
            raise TypeError(f'order 参数类型错误，当前类型为：{type(self._group)}，必须为 str、list 类型')

    def build_having(self):

        if self._having is None:
            return None

        if not isinstance(self._having, dict):
            raise TypeError(f'having 参数类型错误，当前类型为：{type(self._having)}，必须为 dict 类型')

        having_list = [
            compare(k, v) if isinstance(v, dict) else [f'`{k}`={escape_strings(v)}']
            for k, v in self._having.items()
        ]
        having_list = [j for i in having_list for j in i if j]

        return ' HAVING ' + tools.join(having_list, on=' AND ')

    def build_order(self):
        pass

    def build_limit(self):

        if self._limit is None:
            return None

        return f' LIMIT {self._limit}'

    def build_offset(self):

        if self._offset is None:
            return None

        return f' OFFSET {self._offset}'

    def build_desc(self):
        return ' DESC' if self._desc else None

    def build_distinct(self):
        return 'DISTINCT' if self._distinct else ''

    def build_join(self):

        if not self._join:
            return None

        join_str = ''
        for join_clause in self._join:
            join_type = join_clause.get('type', 'INNER').upper()
            join_table = join_clause['table']
            join_on = join_clause['on']
            join_str += f' {join_type} JOIN `{join_table}` ON {join_on}'

        return join_str

    def build_union(self):
        return f' UNION {self._union}' if self._union else None

    def build_union_all(self):
        return f' UNION ALL {self._union_all}' if self._union_all else None


class InsertBase:

    def __init__(self, table: str, field: Union[list, tuple], values: Union[list, tuple], auto_update: bool = False):
        self._table = table
        self._field = field
        self._values = values
        self._auto_update = auto_update

    def build_insert_sql(self):
        """插入数据"""

        field = tools.join([f'`{i}`' for i in self._field], on=',')
        value = tools.join([
            (
                '(' + tools.join([escape_strings(i) for i in item], ',') + ')'
            ) for item in self._values
        ], ',\n')

        return f'INSERT INTO `{self._table}` ({field}) VALUES {value}'

    @abstractmethod
    def build_insert_update_sql(self): ...

    def __str__(self):

        if self._auto_update:
            return self.build_insert_update_sql()
        else:
            return self.build_insert_sql()

    __repr__ = __str__


class CreateTableBase:

    def __init__(self, model):
        self.model = model
        self.type = 'mtype' if model.Meta.engine == 'mysql' else 'stype'
        self.tb_name = self.model.Meta.tb_name

    def __str__(self):
        pass

    __repr__ = __str__
    
    @abstractmethod
    def build_common_sql(self, field, cname, sql, default_format=None):
        pass

    @abstractmethod
    def build_auto_sql(self, field, cname): ...

    @abstractmethod
    def build_stamp_sql(self, field, cname): ...

    @abstractmethod
    def build_time_sql(self, field, cname): ...

    @abstractmethod
    def build_date_sql(self, field, cname): ...

    @abstractmethod
    def build_datetime_sql(self, field, cname): ...

    def build_column_sql(self, field, cname):

        build_method_mapping = {
            'AutoIntField': self.build_auto_sql,
            'VARCHAR': self.build_varchar_sql,
            'TINYINT': self.build_int_sql,
            'SMALLINT': self.build_int_sql,
            'INT': self.build_int_sql,
            'BIGINT': self.build_int_sql,
            'MEDIUMINT': self.build_int_sql,
            'TINYINTEGER': self.build_int_sql,
            'SMALLINTEGER': self.build_int_sql,
            'INTEGER': self.build_int_sql,
            'MEDIUMINTEGER': self.build_int_sql,
            'BIGINTEGER': self.build_int_sql,
            'FLOAT': self.build_float_sql,
            'DOUBLE': self.build_float_sql,
            'BOOLEAN': self.build_boolean_sql,
            'TIMESTAMP': self.build_stamp_sql,
            'TIME': self.build_time_sql,
            'DATE': self.build_date_sql,
            'DATETIME': self.build_datetime_sql,
            'TEXT': self.build_text_sql,
            'MEDIUMTEXT': self.build_text_sql,
            'LONGTEXT': self.build_text_sql,
            'DECIMAL': self.build_decimal_sql,
            'ENUM': self.build_enum_sql,
            'FOREIGN KEY': self.build_foreign_key_sql
        }

        key = field.__class__.__name__ if field.__class__.__name__ == 'AutoIntField' else field.mapping[self.type]
        build_method = build_method_mapping.get(key)

        if build_method:
            return build_method(field, cname)

        return None

    def build_varchar_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}({field.max_length})'
        return self.build_common_sql(field, cname, sql)

    def build_int_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        if hasattr(field, 'unsigned') and field.unsigned:
            sql += f' UNSIGNED'
        return self.build_common_sql(field, cname, sql)

    def build_float_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        return self.build_common_sql(field, cname, sql)

    def build_boolean_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        return self.build_common_sql(field, cname, sql)

    def build_text_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        return self.build_common_sql(field, cname, sql)

    def build_decimal_sql(self, field, cname):

        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}({field.precision}, {field.scale})'

        if field.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if field.primary:
            sql += f' PRIMARY KEY'
        elif field.unique:
            sql += f' UNIQUE'

        if field.default is not None:
            sql += f' DEFAULT {field.default}'

        sql += f' COMMENT "{field.name}"'

        return sql

    def build_enum_sql(self, field, cname):

        enum_values = ','.join([f'"{value}"' for value in field.choices])
        sql = f'`{field.db_column or cname or field.name}` ENUM({enum_values})'

        if field.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if field.primary:
            sql += f' PRIMARY KEY'
        elif field.unique:
            sql += f' UNIQUE'

        if field.default:
            sql += f' DEFAULT "{field.default}"'

        sql += f' COMMENT "{field.name}"'

        return sql

    def build_foreign_key_sql(self, field, cname):

        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql += f' REFERENCES {field.reference_table}({field.reference_column})'

        if field.on_delete:
            sql += f' ON DELETE {field.on_delete}'
        if field.on_update:
            sql += f' ON UPDATE {field.on_update}'

        return sql

    def build_index_sql(self, field, cname):

        if not field.db_index:
            return None

        if field.db_index is True:
            if field.primary:
                return None
            elif field.unique:
                index = UniqueIndexField
            else:
                index = NormalIndexField
        else:
            index = field.db_index

        if self.model.Meta.engine == 'mysql':
            return index(self.tb_name, cname).index_mysql()
        elif self.model.Meta.engine == 'sqlite':
            return index(self.tb_name, cname).index_sqlite()
        else:
            return None

    def build_cols_sql_list(self):
        return [
            self.build_column_sql(field=field, cname=f)
            for f, field in self.model.fields.items() if field
        ]

    def build_index_sql_list(self):

        index_sql = []

        for f, field in self.model.fields.items():
            if not field or field.unique:
                continue
            index_sql.append(self.build_index_sql(field=field, cname=f))
            
        # 联合索引
        if self.model.Meta.union_index is not None:
            index_fields = [i for i in self.model.Meta.union_index if i in self.model.fields]
            if index_fields:
                index = UnionIndexField(self.tb_name, index_fields)
                if self.model.Meta.engine == 'mysql':
                    index_sql.append(index.index_mysql())
                elif self.model.Meta.engine == 'sqlite':
                    index_sql.append(index.index_sqlite())
                
        # 联合唯一索引
        if self.model.Meta.union_unique_index is not None:
            index_fields = [i for i in self.model.Meta.union_unique_index if i in self.model.fields]
            if index_fields:
                index = UniqueUnionIndexField(self.tb_name, index_fields)
                if self.model.Meta.engine == 'mysql':
                    index_sql.append(index.index_mysql())
                elif self.model.Meta.engine == 'sqlite':
                    index_sql.append(index.index_sqlite())

        return (i for i in index_sql if i)


class AlterTableBase:

    def __init__(self, model):
        self.model = model
        self.type = 'mtype' if model.Meta.engine == 'mysql' else 'stype'
        self.tb_name = self.model.Meta.tb_name

    def __str__(self):
        pass

    __repr__ = __str__

    def build_sql_list(self, method_name: str, condition: callable) -> str:
        cols_sql = []

        for f, field in self.model.fields.items():
            if not field or not condition(f, field):
                continue
            cols_sql.append(method_name(f, field))

        return tools.join(cols_sql, on=';\n')


class Select(SelectBase):

    MysqlFunc = (
        'ABS', 'ACOS', 'ASIN', 'ATAN', 'ATAN2', 'AVG', 'CEIL', 'CEILING',
        'COS', 'COT', 'COUNT', 'DEGREES', 'DIV', 'EXP', 'FLOOR', 'GREATEST',
        'LEAST', 'LN', 'LOG', 'LOG10', 'LOG2', 'MAX', 'MIN', 'MOD',
        'PI', 'POW', 'POWER', 'RADIANS', 'RAND', 'ROUND', 'SIGN', 'SIN',
        'SQRT', 'SUM', 'TAN', 'TRUNCATE', 'ASCII', 'CHAR_LENGTH', 'CHARACTER_LENGTH', 'CONCAT',
        'CONCAT_WS', 'FIELD', 'FIND_IN_SET', 'FORMAT', 'INSERT', 'LOCATE', 'LCASE', 'LEFT',
        'LOWER', 'LPAD', 'LTRIM', 'MID', 'POSITION', 'REPEAT', 'REPLACE', 'REVERSE',
        'RIGHT', 'RPAD', 'RTRIM', 'SPACE', 'STRCMP', 'SUBSTR', 'SUBSTRING', 'SUBSTRING_INDEX',
        'TRIM', 'UCASE', 'UPPER', 'ADDDATE', 'ADDTIME', 'CURDATE', 'CURRENT_DATE', 'CURRENT_TIME',
        'CURRENT_TIMESTAMP', 'CURTIME', 'DATE', 'DATEDIFF', 'DATE_ADD', 'DATE_FORMAT', 'DATE_SUB', 'DAY',
        'DAYNAME', 'DAYOFMONTH', 'DAYOFWEEK', 'DAYOFYEAR', 'EXTRACT', 'HOUR', 'LAST_DAY', 'LOCALTIME',
        'LOCALTIMESTAMP', 'MAKEDATE', 'MAKETIME', 'MICROSECOND', 'MINUTE', 'MONTHNAME', 'MONTH', 'NOW',
        'PERIOD_ADD', 'PERIOD_DIFF', 'QUARTER', 'SECOND', 'SEC_TO_TIME', 'STR_TO_DATE', 'SUBDATE', 'SUBTIME',
        'SYSDATE', 'TIME', 'TIME_FORMAT', 'TIME_TO_SEC', 'TIMEDIFF', 'TIMESTAMP', 'TIMESTAMPDIFF', 'TO_DAYS',
        'WEEK', 'WEEKDAY', 'WEEKOFYEAR', 'YEAR', 'YEARWEEK', 'BINARY', 'CAST',
        'COALESCE', 'CONNECTION_ID', 'CONV', 'CURRENT_USER', 'DATABASE', 'IF', 'IFNULL', 'ISNULL',
        'LAST_INSERT_ID', 'NULLIF', 'SESSION_USER', 'SYSTEM_USER', 'USER', 'VERSION'
    )

    def __str__(self):
        sql = f'SELECT {self.build_distinct()} {self.build_field()} FROM `{self._table}`'

        join = self.build_join()
        if join:
            sql += join

        where = self.build_where()
        if where:
            sql += where

        group = self.build_group()
        if group:
            sql += group

        having = self.build_having()
        if having:
            sql += having

        order = self.build_order()
        if order:
            sql += order

        limit = self.build_limit()
        if limit:
            sql += limit

        if self._subquery:
            sql = f'SELECT {self.build_field()} FROM ({sql}) AS {self._subquery}'

        union = self.build_union()
        if union:
            sql += union

        union_all = self.build_union_all()
        if union_all:
            sql += union_all

        return sql

    def build_field(self):
        if self._field is None:
            return '*'
        elif isinstance(self._field, str):
            return self._field
        elif isinstance(self._field, (list, tuple)):
            field = [
                i if re.match(r'^(.+)\(.*\).*$', i) and re.match(r'^(.+)\(.*\).*$', i).group(
                    1).upper() in self.MysqlFunc
                else f"`{i}`"
                for i in self._field
            ]
            return tools.join(field, on=",")
        else:
            raise TypeError(f'field 参数类型错误，当前类型为：{type(self._field)}，必须为 str、list 类型')

    def build_order(self):
        if self._order is None:
            return None
        elif isinstance(self._order, str):
            return f' ORDER BY {self._order}'
        elif isinstance(self._order, (list, tuple)):
            return f' ORDER BY {tools.join(self._order, on=",")}'
        else:
            raise TypeError(f'order 参数类型错误，当前类型为：{type(self._order)}，必须为 str、list 类型')


class SQLiteSelect(SelectBase):

    SqliteFunc = (
        'ABS', 'LENGTH', 'LOWER', 'RANDOM', 'ROUND', 'UPPER', 'COUNT', 'MAX', 'MIN', 'SUM', 'AVG', 'TOTAL',
        'COALESCE', 'NULLIF', 'CAST', 'DATE', 'TIME', 'DATETIME', 'JULIANDAY', 'STRFTIME', 'LIKE', 'GLOB',
        'REGEXP', 'MATCH', 'SOUNDEX', 'LAST_INSERT_ROWID', 'CHANGES', 'TOTAL_CHANGES', 'REPLACE', 'LTRIM',
        'RTRIM', 'TRIM', 'SUBSTR', 'SUBSTRING', 'INSTR'
    )

    def build_field(self):
        if self._field is None:
            return '*'
        elif isinstance(self._field, str):
            return self._field
        elif isinstance(self._field, (list, tuple)):
            field = []
            for i in self._field:
                x = re.findall(r'^(.*)\(.*\)$', i) or re.findall(r'^(.*)\(.*\) ', i) or \
                    re.findall(r'^(.*)\(.*\)as', i)
                if x and x[0].upper() in self.SqliteFunc:
                    field.append(i)
                else:
                    field.append(f'"{i}"')
            return tools.join(field, on=",")
        else:
            raise TypeError(f'field 参数类型错误，当前类型为：{type(self._field)}，必须为 str、list 类型')

    def build_order(self):
        if not self._order:
            return None

        if not isinstance(self._order, (list, tuple)):
            raise TypeError(f'order 参数类型错误，当前类型为：{type(self._order)}，必须为 list、tuple 类型')

        order_list = [f'"{k}" {v}' for k, v in self._order]
        return ' ORDER BY ' + tools.join(order_list, on=',')

    def __str__(self):
        sql = f'SELECT {self.build_distinct()} {self.build_field()} FROM "{self._table}"'

        join = self.build_join()
        if join:
            sql += join

        where = self.build_where()
        if where:
            sql += where

        group = self.build_group()
        if group:
            sql += group

        having = self.build_having()
        if having:
            sql += having

        order = self.build_order()
        if order:
            sql += order

        limit = self.build_limit()
        if limit:
            sql += limit

        if self._subquery:
            sql = f'SELECT {self.build_field()} FROM ({sql}) AS "{self._subquery}"'

        union = self.build_union()
        if union:
            sql += union

        union_all = self.build_union_all()
        if union_all:
            sql += union_all

        return sql


class MysqlCreateTable(CreateTableBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_common_sql(self, field, cname, sql, default_format=None):
        if field.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if field.primary:
            sql += f' PRIMARY KEY'
        elif field.unique:
            sql += f' UNIQUE'

        if field.default is not None:
            if default_format:
                sql += f' DEFAULT {default_format(field.default)}'
            else:
                sql += f' DEFAULT ' + (
                    '""' if isinstance(field.default, str) and not field.default else str(field.default)
                )

        sql += f' COMMENT "{field.name}"'
        return sql

    def build_auto_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        if field.primary:
            sql += f' NOT NULL PRIMARY KEY AUTO_INCREMENT'
        else:
            sql += f' NOT NULL AUTO_INCREMENT'
        return sql

    def build_stamp_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(field, cname, sql)
        if field.auto_update:
            sql += ' ON UPDATE CURRENT_TIMESTAMP'
        return sql

    def build_time_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(
            field, cname, sql,
            default_format=lambda x: f'"{x}"' if isinstance(x, (date, datetime)) or (
                isinstance(x, str) and ' ' in x.strip()
            ) else x
        )
        return sql

    def build_date_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(
            field, cname, sql,
            default_format=lambda x: f'"{x}"' if isinstance(x, (date, datetime)) or (
                isinstance(x, str) and ' ' in x.strip()
            ) else x
        )
        return sql

    def build_datetime_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(
            field, cname, sql,
            default_format=lambda x: f'"{x}"' if isinstance(x, (date, datetime)) or (
                isinstance(x, str) and ' ' in x.strip()
            ) else x
        )
        if field.auto_update:
            sql += ' ON UPDATE CURRENT_TIMESTAMP'
        return sql

    def __str__(self):

        cols_sql_list = self.build_cols_sql_list()
        index_sql_list = self.build_index_sql_list()
        charset = self.model.Meta.encoding if self.model.Meta.encoding else "utf8mb4"

        sql = f'CREATE TABLE {self.tb_name} (\n'
        sql += tools.join(cols_sql_list, on=',\n')

        index = tools.join([i for i in index_sql_list], on=",\n")
        if index:
            sql += f',\n{index}\n) ENGINE=InnoDB DEFAULT CHARSET={charset} COMMENT="{self.model.__doc__}"'
        else:
            sql += f'\n) ENGINE=InnoDB DEFAULT CHARSET={charset} COMMENT="{self.model.__doc__ or ""}"'

        return sql


class SqliteCreateTable(CreateTableBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_common_sql(self, field, cname, sql, default_format=None):

        if field.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if field.primary:
            sql += f' PRIMARY KEY'

        if field.default is not None:
            if default_format:
                sql += f' DEFAULT {default_format(field.default)}'
            else:
                sql += f' DEFAULT "{field.default}"'

        return sql

    def build_auto_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        if field.primary:
            sql += f' NOT NULL PRIMARY KEY AUTOINCREMENT'
        else:
            sql += f' NOT NULL AUTOINCREMENT'
        return sql

    def build_stamp_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(field, cname, sql)
        return sql

    def build_time_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(
            field, cname, sql,
            default_format=lambda x: f'"{x}"' if isinstance(x, (date, datetime)) or (
                isinstance(x, str) and ' ' in x.strip()
            ) else x
        )
        return sql

    def build_date_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(
            field, cname, sql,
            default_format=lambda x: f'"{x}"' if isinstance(x, (date, datetime)) or (
                isinstance(x, str) and ' ' in x.strip()
            ) else x
        )
        return sql

    def build_datetime_sql(self, field, cname):
        sql = f'`{field.db_column or cname or field.name}` {field.mapping[self.type]}'
        sql = self.build_common_sql(
            field, cname, sql,
            default_format=lambda x: f'"{x}"' if isinstance(x, (date, datetime)) or (
                isinstance(x, str) and ' ' in x.strip()
            ) else x
        )
        return sql

    def __str__(self):

        cols_sql_list = self.build_cols_sql_list()

        sql = f'CREATE TABLE {self.tb_name} (\n'
        sql += tools.join(cols_sql_list, on=',\n')
        sql += f'\n);'

        index = tools.join([i for i in self.build_index_sql_list() if i], on=";\n")

        return f'{sql}\n{index}'


class MysqlAlterTable(AlterTableBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = MysqlAlterAPI(self.tb_name)

    def build_add_cols_sql(self, desc):

        index = 0
        fields = list(self.model.fields.keys())
        condition = lambda cname, *args, **kwargs: cname not in [i.field for i in desc]

        def add_column_method(cname, field):
            nonlocal index
            after = fields[index - 1] if index else None
            index += 1
            return self.api.build_add_column_sql(field=field, cname=cname, after=after)

        return self.build_sql_list(add_column_method, condition)
    
    def build_modify_cols_primary_sql(self, desc) -> str:
        condition = lambda cname, field: field.primary and not any(
            cname == i.field and i.key == 'PRI' for i in desc
        )
        return self.build_sql_list(self.api.build_modify_primary_sql, condition)

    def build_modify_cols_unique_sql(self, desc) -> str:
        condition = lambda cname, field: (
                not field.primary and field.unique and
                all(cname != des.field or des.key != 'UNI' for des in desc)
        )
        return self.build_sql_list(self.api.build_modify_unique_sql, condition)

    def build_modify_cols_index_sql(self, desc) -> str:
        condition = lambda cname, field: cname in [
            i.field for i in desc
            if not field.primary and not field.unique and field.db_index and i.key != 'MUL'
        ]
        return self.build_sql_list(self.api.build_modify_index_sql, condition)

    def build_modify_cols_type_sql(self, desc):

        def condition(cname, field):
            for des in desc:
                if cname == des.field:
                    if field.max_length != des.length and not issubclass(field.__class__, TextField):
                        return True
                    if hasattr(field, 'unsigned'):
                        if field.unsigned and (field.mapping[self.type] + ' UNSIGNED') != des.type:
                            return True
                        if not field.unsigned and field.mapping[self.type] != des.type:
                            return True
                    else:
                        if field.mapping[self.type] != des.type:
                            return True
                    return False
            return False

        return self.build_sql_list(self.api.build_modify_column_type_sql, condition)

    def build_drop_column_sql(self, cname: str) -> str:
        """删除列"""
        return f'ALTER TABLE `{self.tb_name}` DROP COLUMN `{cname}`'

    def build_rename_column_sql(self, old_cname: str, new_cname: str) -> str:
        """重命名列"""
        field = self.model.fields[old_cname]
        sql = f'ALTER TABLE `{self.tb_name}` CHANGE `{old_cname}` `{new_cname}` {field.mapping["mtype"]}'
        if field.max_length is not None:
            sql += f'({field.max_length})'
        if field.default is not None:
            sql += f' DEFAULT {escape_strings(field.default)}'
        return sql

    def build_drop_primary_key_sql(self) -> str:
        """删除主键"""
        return f'ALTER TABLE `{self.tb_name}` DROP PRIMARY KEY'

    def build_drop_unique_key_sql(self, cname: str) -> str:
        """删除唯一键"""
        return f'ALTER TABLE `{self.tb_name}` DROP INDEX `{cname}`'

    def build_drop_index_sql(self, cname: str) -> str:
        """删除索引"""
        return f'ALTER TABLE `{self.tb_name}` DROP INDEX `{cname}`'

    def build_rename_table_sql(self, new_name: str) -> str:
        """重命名表"""
        return f'ALTER TABLE `{self.tb_name}` RENAME TO `{new_name}`'

    def build_add_foreign_key_sql(
            self, cname: str, ref_table: str, ref_cname: str, on_delete: str = 'CASCADE',
            on_update: str = 'CASCADE'
    ) -> str:
        """添加外键约束"""
        return f'ALTER TABLE `{self.tb_name}` ADD FOREIGN KEY (`{cname}`) REFERENCES `{ref_table}`(`' \
               f'{ref_cname}`) ON DELETE {on_delete} ON UPDATE {on_update}'

    def build_drop_foreign_key_sql(self, constraint_name: str) -> str:
        """删除外键约束"""
        return f'ALTER TABLE `{self.tb_name}` DROP FOREIGN KEY `{constraint_name}`'

    def build_change_column_default_sql(self, cname: str, default_value: Union[str, int, float]) -> str:
        """更改列的默认值"""

        field = self.model.fields[cname]
        sql = f'ALTER TABLE `{self.tb_name}` ALTER COLUMN `{cname}` {field.mapping["mtype"]}'
        if field.max_length is not None:
            sql += f'({field.max_length})'
        if default_value is not None:
            sql += f' DEFAULT {escape_strings(default_value)}'
        return sql

    def build_change_column_null_sql(self, cname: str, nullable: bool) -> str:
        """更改列的可空属性"""

        field = self.model.fields[cname]
        sql = f'ALTER TABLE `{self.tb_name}` MODIFY COLUMN `{cname}` {field.mapping["mtype"]}'
        if field.max_length is not None:
            sql += f'({field.max_length})'
        if not nullable:
            sql += f' NOT NULL'
        if field.default is not None:
            sql += f' DEFAULT {escape_strings(field.default)}'
        return sql

    def build_change_column_charset_sql(self, cname: str, charset: str, collation: str) -> str:
        """更改列的字符集"""

        field = self.model.fields[cname]
        if field.mapping["mtype"] not in ["CHAR", "VARCHAR", "TEXT"]:
            raise ValueError("This method can only be used for character-based columns")
        sql = f'ALTER TABLE `{self.tb_name}` MODIFY COLUMN `{cname}` {field.mapping["mtype"]}'
        if field.max_length is not None:
            sql += f'({field.max_length})'
        sql += f' CHARACTER SET {charset} COLLATE {collation}'
        if field.default is not None:
            sql += f' DEFAULT {escape_strings(field.default)}'
        return sql

    def build_change_table_storage_engine_sql(self, engine: str) -> str:
        """更改表的存储引擎"""
        return f'ALTER TABLE `{self.tb_name}` ENGINE={engine}'

    def build_change_table_charset_collation_sql(self, charset: str, collation: str) -> str:
        """更改表的字符集和排序规则"""
        return f'ALTER TABLE `{self.tb_name}` CONVERT TO CHARACTER SET {charset} COLLATE {collation}'

    def build_change_table_comment_sql(self, comment: str) -> str:
        """更改表的注释"""
        return f'ALTER TABLE `{self.tb_name}` COMMENT="{comment}"'


class SqliteAlterTable(AlterTableBase):

    def __init__(self, *args, **kwargs):
        super(SqliteAlterTable, self).__init__(*args, **kwargs)
        self.api = SqliteAlterAPI(self.tb_name)

    def build_add_cols_sql(self, desc):

        condition = lambda cname, *args, **kwargs: cname not in [i.field for i in desc]
        return self.build_sql_list(self.api.build_add_column_sql, condition)

    def build_modify_cols_primary_sql(self, desc) -> str:
        condition = lambda cname, field: field.primary and not any(
            cname == i.field and i.key == 'PRI' for i in desc
        )
        return self.build_sql_list(self.api.build_modify_primary_sql, condition)

    def build_modify_cols_unique_sql(self, desc) -> str:
        condition = lambda cname, field: (
                not field.primary and field.unique and
                all(cname != des.field or des.key != 'UNI' for des in desc)
        )
        return self.build_sql_list(self.api.build_modify_unique_sql, condition)

    def build_modify_cols_index_sql(self, desc) -> str:
        condition = lambda cname, field: cname in [
            i.field for i in desc
            if not field.primary and not field.unique and field.db_index and i.key != 'MUL'
        ]
        return self.build_sql_list(self.api.build_modify_index_sql, condition)

    def build_modify_cols_type_sql(self, desc):

        def condition(cname, field):
            for des in desc:
                if cname != des.field:
                    continue
                if hasattr(field, 'unsigned'):
                    if field.unsigned and (field.mapping[self.type] + ' UNSIGNED') != des.type:
                        return True
                    if not field.unsigned and field.mapping[self.type] != des.type:
                        return True
                else:
                    if field.mapping[self.type] != des.type:
                        return True
                return False

            return False

        return self.build_sql_list(self.api.build_modify_column_type_sql, condition)

    def build_change_column_type_sql(self, cname: str, new_type: str, max_length: int = None) -> str:
        """更改列类型 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support changing column types directly. Consider using other workarounds."
        )

    def build_change_column_default_sql(self, cname: str, default_value: Union[str, int, float]) -> str:
        """更改列的默认值 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support changing column default values directly. Consider using other workarounds."
        )

    def build_change_column_null_sql(self, cname: str, nullable: bool) -> str:
        """更改列的可空属性 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support changing column nullability directly. Consider using other workarounds."
        )

    def build_drop_column_sql(self, cname: str) -> str:
        """删除列 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support dropping columns directly. Consider using other workarounds."
        )

    def build_rename_column_sql(self, old_cname: str, new_cname: str) -> str:
        """重命名列 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise 'ALTER TABLE old_table_name RENAME TO new_table_name;'

    def build_add_index_sql(self, cname: str, index_name: str, unique: bool = False) -> str:
        """添加索引"""
        sql = f'CREATE {"UNIQUE" if unique else ""} INDEX `{index_name}` ON `{self.tb_name}`(`{cname}`);'
        return sql

    def build_drop_index_sql(self, index_name: str) -> str:
        """删除索引"""
        return f'DROP INDEX `{index_name}`;'

    def build_add_foreign_key_sql(self, cname: str, ref_table: str, ref_cname: str, constraint_name: str,
                                   on_delete: str = 'CASCADE', on_update: str = 'CASCADE') -> str:
        """添加外键约束 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support adding foreign keys directly. Consider using other workarounds."
        )

    def build_drop_foreign_key_sql(self, constraint_name: str) -> str:
        """删除外键约束 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support dropping foreign keys directly. Consider using other workarounds."
        )

    def build_change_table_collation_sql(self, collation: str) -> str:
        """更改表的排序规则 - SQLite 不支持更改表的排序规则"""
        raise NotImplementedError("SQLite does not support changing table collation.")

    def build_change_column_collation_sql(self, cname: str, collation: str) -> str:
        """更改列的排序规则 - 不直接支持，需要借助其他方式实现，例如创建一个新表并拷贝数据"""
        raise NotImplementedError(
            "SQLite does not support changing column collation directly. Consider using other workarounds."
        )

    def build_rename_table_sql(self, new_name: str) -> str:
        """重命名表"""
        return self.api.build_rename_table_sql(new_name)


class MysqlAlterAPI:

    def __init__(self, tb_name):
        self.tb_name = tb_name

    def build_add_column_sql(self, cname: str, field, after: str = None, *args, **kwargs) -> str:

        sql = f'ALTER TABLE `{self.tb_name}` ADD COLUMN `{cname}` {field.mapping["mtype"]}'

        if field.max_length is not None:
            sql += f'({field.max_length})'

        if hasattr(field, 'unsigned') and field.unsigned:
            sql += f' UNSIGNED'

        if field.primary:
            sql += f' primary key auto_increment' if field.__class__.__name__ == 'AutoIntField' else f' primary key'
        elif field.unique:
            sql += f' unique key'

        if field.mapping["mtype"] not in ['TEXT', 'BLOB', 'GEOMETRY', 'JSON'] and field.default is not None:
            if isinstance(field.default, (str, date, datetime)):
                if field.default == 'CURRENT_TIMESTAMP':
                    sql += f' DEFAULT {field.default}'
                else:
                    sql += f' DEFAULT {escape_strings(field.default)}'
            else:
                sql += f' DEFAULT {field.default}'
        else:
            sql += f' DEFAULT NULL'

        if field.name is not None:
            sql += f' COMMENT "{field.name}"'

        if after is not None:
            sql += f' AFTER {after}'

        return sql

    def build_modify_column_type_sql(self, cname: str, field, *args, **kwargs) -> str:

        sql = f'ALTER TABLE `{self.tb_name}` MODIFY COLUMN `{cname}` {field.mapping["mtype"]}'

        if field.max_length is not None and not issubclass(field.__class__, TextField):
            sql += f'({field.max_length})'

        if hasattr(field, 'unsigned') and field.unsigned:
            sql += f' UNSIGNED'

        if field.__class__.__name__ == 'AutoIntField' and field.primary:
            sql = f'ALTER TABLE `{self.tb_name}` DROP PRIMARY KEY;\n' + sql
            sql += f' AUTO_INCREMENT PRIMARY KEY'
        elif field.default is not None:
            sql += f' DEFAULT {escape_strings(field.default)}'
        else:
            sql += f' DEFAULT NULL'

        if field.name is not None:
            sql += f' COMMENT "{field.name}"'

        return sql

    def build_modify_primary_sql(self, cname: str, is_primary: bool = False, *args, **kwargs) -> str:
        if is_primary:
            return f'ALTER TABLE `{self.tb_name}` DROP PRIMARY KEY;\nALTER TABLE `{self.tb_name}` ADD PRIMARY' \
                   f' KEY(`{cname}`);'
        else:
            return f'ALTER TABLE `{self.tb_name}` ADD PRIMARY KEY (`{cname}`);'

    def build_modify_unique_sql(self, cname: str, *args, **kwargs) -> str:
        return f'ALTER TABLE `{self.tb_name}` ADD UNIQUE (`{cname}`);'

    def build_modify_index_sql(self, cname: str, *args, **kwargs) -> str:
        return f'ALTER TABLE `{self.tb_name}` ADD INDEX (`{cname}`)'


class SqliteAlterAPI:

    def __init__(self, tb_name):
        self.tb_name = tb_name

    def build_rename_table_sql(self, new_name: str) -> str:
        """重命名表"""
        return f'ALTER TABLE `{self.tb_name}` RENAME TO `{new_name}`'

    def build_add_column_sql(self, cname: str, field, *args, **kwargs) -> str:
        """添加列"""

        sql = f'ALTER TABLE "{self.tb_name}" ADD COLUMN "{cname}" {field.mapping["stype"]}'

        if field.max_length is not None:
            sql += f'({field.max_length})'

        if hasattr(field, 'unsigned') and field.unsigned:
            sql += ' UNSIGNED'

        if field.default is not None:
            if isinstance(field.default, (str, date, datetime)):
                if field.default == 'CURRENT_TIMESTAMP':
                    sql += f' DEFAULT {field.default}'
                else:
                    sql += f' DEFAULT {escape_strings(field.default)}'
            else:
                sql += f' DEFAULT {field.default}'

        if not field.null:
            sql += f' NOT NULL'

        return sql

    def build_modify_column_type_sql(self, cname: str, field, *args, **kwargs) -> str:
        """修改字段类型"""
        return 'True'

    def build_modify_primary_sql(self, cname: str, field, *args, **kwargs) -> str:
        return 'True'

    def build_modify_unique_sql(self, cname: str, *args, **kwargs) -> str:
        return 'True'

    def build_modify_index_sql(self, cname: str, *args, **kwargs) -> str:
        return 'True'


class MysqlInsert(InsertBase):

    def build_insert_update_sql(self):

        sql = f'{self.build_insert_sql()} ON DUPLICATE KEY UPDATE '
        sql += tools.join([f"`{i}`=values(`{i}`)" for i in self._field], on=',')

        return sql


class SqliteInsert(InsertBase):

    def build_insert_sql(self):
        """插入数据"""

        field = tools.join([f'`{i}`' for i in self._field], on=',')
        value = tools.join([
            (
                '(' + tools.join([f"'{escape_strings(i)}'" for i in item], ',') + ')'
            ) for item in self._values
        ], ',\n')
        value = value.replace('\'\"', "'").replace('\"\'', "'")

        return f"INSERT INTO `{self._table}` ({field}) VALUES {value}"

    def build_insert_update_sql(self):

        field = tools.join([f'`{i}`' for i in self._field], on=',')
        sql = f'{self.build_insert_sql()} on conflict do update set ({field}) = (' \
              f'{tools.join([f"EXCLUDED.`{i}`" for i in self._field], on=",")})'

        return sql


class MysqlUpdate:

    def __init__(
            self, table: str, items: Union[list, tuple], where: Optional[dict] = None
    ):
        self._table = table
        self._items = items
        self._where = where

    def build_update_sql(self):

        if not self._items:
            return ''

        fields = list(self._items[0].keys())

        update_values = tools.join(
            [
                '\tSELECT\n\t\t' + tools.join(
                    [f'{escape_strings(item[field])} AS `{field}`' for field in fields],
                    on=',\n\t\t'
                )
                for item in self._items
            ],
            on="\n"
        )

        conditions = ' ON ' + tools.join(
            [f't1.`{field}` = t2.`{field}`' for field in self._where],
            on=' AND '
        ) if self._where else ""

        set_field = tools.join(
            [f't1.`{field}` = t2.`{field}`' for field in fields if field not in self._where],
            on=',\n\t'
        )

        return f"UPDATE `{self._table}` AS t1\nJOIN (\n{update_values}\n\t) AS t2{conditions}\nSET\t {set_field};"

    def __str__(self):
        return self.build_update_sql()

    __repr__ = __str__


class SQLiteUpdate:

    def __init__(
            self, table: str, items: Union[list, tuple], where: Optional[dict] = None
    ):
        self._table = table
        self._items = items
        self._where = where

    def build_update_sql(self):

        if not self._items:
            return ''

        sql = f"UPDATE `{self._table}`\nSET "

        for field in self._items[0].keys():
            if field in self._where:
                continue
            sql += f"`{field}` = CASE\n\t"
            sql += tools.join(
                [
                    f"WHEN {' AND '.join([f'`{x}` = {item[x]}' for x in self._where])} "
                    f"THEN {escape_strings(item[field])}"
                    for item in self._items
                ],
                on="\n\t"
            )
            sql += f"\n\tELSE `{field}`\n\tEND,\n"

        return sql[:-2]

    def __str__(self):
        return self.build_update_sql()

    __repr__ = __str__
