from decimal import Decimal
from datetime import datetime, date
from typing import Optional, Union

from AioSpider import tools


class Field:

    def __init__(
            self, name: str, max_length: Optional[int] = None, unique: bool = False,
            blank: bool = True, null: bool = True, db_index: bool = False, db_column: Optional[str] = None,
            default: Union[str, int, float, None] = None, choices: Union[tuple, list, None] = None, validators=None,
            is_save: bool = True, dnt_filter: bool = False
    ):
        self.name = name
        self.max_length = max_length or 255
        self.unique = unique
        self.blank = blank
        self.null = null
        self.default = default
        self.choices = choices
        self.db_index = db_index
        self.db_column = db_column
        self.is_save = is_save
        self.dnt_filter = dnt_filter

        self._validators = validators or []
        self._message = []
        self._value = None

    def _check(self, field: str):

        if self._check_name() and self._check_max_length() and self._check_default() \
                and self._check_choices() and self._check_unique() and self._check_blank() \
                and self._check_null() and self._check_db_index() and self._check_is_save() \
                and self._check_db_column():
            return True
        else:
            raise Exception(field + '\n'.join(self._message))

    def _check_name(self):

        if not isinstance(self.name, str):
            self._message.append('name字段必须为str类型')
            return False

        if not self.name:
            self._message.append('name字段不能为空')
            return False

        return True

    def _check_max_length(self):
        return True

    def _check_default(self):
        return True

    def _check_choices(self):
        return True

    def _check_unique(self):

        if not isinstance(self.unique, bool):
            self._message.append('unique字段必须为True/False')
            return False

        return True

    def _check_blank(self):

        if not isinstance(self.blank, bool):
            self._message.append('blank字段必须为True/False')
            return False

        return True

    def _check_null(self):

        if not isinstance(self.null, bool):
            self._message.append('null字段必须为True/False')
            return float

        return True

    def _check_db_index(self):

        if not isinstance(self.db_index, bool):
            self._message.append('db_index字段必须为True/False')
            return False

        return True

    def _check_is_save(self):

        if not isinstance(self.is_save, bool):
            self._message.append('is_save字段必须为True/False')
            return False

        return True

    def _check_db_column(self):

        if self.db_column is None:
            return True

        if not isinstance(self.db_column, str):
            self._message.append('db_column字段必须为str类型')
            return False

        if not self.db_column:
            self._message.append('db_column字段不能为空')
            return False

        return True

    def _table_sql(self, cols=None):
        return ''

    def __str__(self):
        return f'<{self.name}: {self._value}>'

    def __repr__(self):
        return f'<{self.name}: {self._value}>'


class CharField(Field):

    def __init__(
            self, name, max_length=255, unique=False, blank=True, null=True, default=None,
            choices=None, validators=None, db_column=None, is_save=True, dnt_filter=False,
            is_truncate=False
    ):
        super(CharField, self).__init__(
            name=name, max_length=max_length, unique=unique, blank=blank, null=null,
            db_index=False, default=default, choices=choices, db_column=db_column,
            validators=validators, is_save=is_save, dnt_filter=dnt_filter
        )
        self.is_truncate = is_truncate
        self._value = ''
        self._check(f'{name}(CharField)')

    def _check(self, field='CharField'):
        return super(CharField, self)._check(field=field)

    def _check_max_length(self):

        if self.max_length is None:
            self.max_length = 255
            return True

        if not isinstance(self.max_length, int):
            self._message.append('max_length字段必须为int类型')
            return False

        if self.max_length < 0:
            self._message.append('max_length字段不能小于0')
            return False

        return True

    def _check_default(self):

        if self.default is None:
            self.default = ''
            return True

        if not isinstance(self.default, str):
            self._message.append('default字段必须为str类型')
            return False

        return True

    def _check_value(self):

        if self.choices is not None:
            if isinstance(self.choices, (tuple, list)):
                for i in self.choices:
                    if self._value != i[0]:
                        continue
                    self._value = i[1]
                    return
            else:
                raise TypeError(f'类型错误：choice 选项必须为元组或列表类型，当前类型为：{type(self.choices)}')

        if self._value is None and not self.null:
            self._value = self.default or ''

        if isinstance(self._value, (int, float)):
            self._value = str(self._value)

        if not isinstance(self._value, (str, type(None))):
            raise ValueError(f'{self.name}值错误，value={self._value}, value必须为str类型')

        if isinstance(self._value, str):
            self._value = self._value.replace(' ', '')

        if self._value and len(self._value) > self.max_length:
            if self.is_truncate:
                self._value = self._value[:self.max_length]
            else:
                raise ValueError(
                    f'{self.name}值错误，value={self._value}, max_length is {self.max_length}, value超出最大长度范围'
                )

    def _table_sql(self, cols=None):
        sql = f'{self.db_column or cols or self.name} VARCHAR({self.max_length})'
        if self.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if self.unique:
            sql += f' UNIQUE'

        if self.default is not None:
            sql += f' DEFAULT "{self.default}"'
        sql += f' COMMENT "{self.name}"'

        return sql


class IntField(Field):

    def __init__(
            self, name, blank=True, default=0, null=True, validators=None,
            db_column=None, is_save=True, db_index=False, unique=False, dnt_filter=False
    ):
        super(IntField, self).__init__(
            name=name, max_length=None, unique=unique, blank=blank, null=null,
            db_index=db_index, default=default, choices=None, db_column=db_column,
            validators=validators, is_save=is_save, dnt_filter=dnt_filter
        )
        self._value = 0
        self._check(f'{name}(IntField)')

    def _check(self, field='IntField'):
        super(IntField, self)._check(field=field)

    def _check_value(self):
        
        if isinstance(self._value, float):
            self._value = int(self._value)

        if self._value is None:
            if not self.null:
                self._value = self.default or 0
            else:
                self._value = self.default or 0

        if not isinstance(self._value, (int, type(None))):
            raise ValueError(f'{self.name}值错误，value={self._value}, value必须为int类型')

    def _table_sql(self, cols=None):
        sql = f'{self.db_column or cols or self.name} INTEGER '
        if self.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if self.default is not None:
            sql += f' DEFAULT {self.default}'
        sql += f' COMMENT "{self.name}"'

        return sql


class FloatField(Field):

    def __init__(
            self, name, blank=True, null=True, default=0.0, validators=None,
            db_column=None, is_save=True, dnt_filter=False
    ):
        super(FloatField, self).__init__(
            name=name, max_length=None, unique=False, blank=blank, null=null,
            db_index=False, default=default, choices=None, db_column=db_column,
            validators=validators, is_save=is_save, dnt_filter=dnt_filter
        )
        self._value = 0
        self._check(f'{name}(FloatField)')

    def _check(self, field='FloatField'):
        super(FloatField, self)._check(field=field)

    def _check_value(self):

        if self._value is None and not self.null:
            self._value = self.default or float()
            
        if isinstance(self._value, int):
            self._value = int(self._value)

        if not isinstance(self._value, (float, type(None))):
            if isinstance(self._value, int):
                self._value = float(self._value)
            else:
                raise ValueError(f'{self.name}值错误，value={self._value}, value必须为float类型')

        if self._value is not None:
            self._value = float(Decimal(self._value).quantize(Decimal('0.000')))

    def _table_sql(self, cols=None):

        sql = f'{self.db_column or cols or self.name} FLOAT'
        if self.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if self.default is not None:
            sql += f' DEFAULT {self.default}'
        sql += f' COMMENT "{self.name}"'

        return sql


class BoolField(Field):

    def __init__(self, name, default=False, db_column=None, is_save=True, dnt_filter=False):

        super(BoolField, self).__init__(
            name=name, max_length=None, unique=False, blank=False, null=False,
            db_index=False, default=default, choices=None, db_column=db_column,
            validators=None, is_save=is_save, dnt_filter=dnt_filter
        )
        self._value = default
        self._check(f'{name}(BoolField)')

    def _check(self, field='BoolField'):
        super(BoolField, self)._check(field=field)

    def _check_value(self):

        if self._value is None:
            self._value = self.default

        # 转换, 0 False 1 True
        self._value = 1 if self._value else 0

    def _table_sql(self, cols=None):

        sql = f'{self.db_column or cols or self.name} BOOLEAN '
        if self.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if self.default is not None:
            sql += f' DEFAULT {1 if self.default else 0}'
        sql += f' COMMENT "{self.name}"'

        return sql


class AutoIntField(IntField):

    def __init__(
            self, name, sep=1, validators=None, db_column=None, is_save=True, db_index=False,
            auto_field='AUTOINCREMENT', dnt_filter=True
    ):
        super(AutoIntField, self).__init__(
            name=name, blank=False, default=1, null=False, validators=validators,
            db_column=db_column, is_save=is_save, db_index=db_index, unique=True,
            dnt_filter=dnt_filter
        )
        self.sep = sep
        self.auto_field = auto_field
        self._value = 1
        self._check(f'{name}(AutoIntField)')

    def _check(self, field='AutoIntField'):
        super(AutoIntField, self)._check(field=field)

    def _check_value(self):

        if self._value is None:
            self._value = self.default
            self._auto_increase()

        if not isinstance(self._value, int):
            raise ValueError(f'{self.name}值错误，value={self._value}, value必须为int类型')

    def _auto_increase(self):
        self.default += self.sep

    def _table_sql(self, cols=None):

        sql = f'{self.db_column or cols or self.name} INTEGER NOT NULL PRIMARY KEY {self.auto_field}'
        return sql


class StampField(IntField):

    def __init__(
            self, name, blank=True, null=True, validators=None, db_column=None,
            is_save=True, db_index=False, unique=False, dnt_filter=True
    ):
        super(StampField, self).__init__(
            name=name, unique=unique, blank=blank, null=null,
            db_index=db_index, default=None, db_column=db_column,
            validators=validators, is_save=is_save, dnt_filter=dnt_filter
        )
        self._value = 0
        self._check(f'{name}(IntField)')

    def _check_value(self):

        if not self._value:
            self._value = datetime.now()

        if isinstance(self._value, (float, int)):
            self._value = tools.stamp_to_time(self._value)

        elif isinstance(self._value, str):
            try:
                self._value = tools.stamp_to_time(self._value)
            except:
                raise ValueError(f'{self.name}值错误，字段值与预期值不匹配：{self._value}，值必须为可识别的字符串时间或数字')

        else:
            if not isinstance(self._value, datetime):
                raise TypeError(f'{self.name}值类型错误，value={self._value}, value必须为{type(self._value)}类型')

    def _table_sql(self, cols=None):

        sql = f'{self.db_column or cols or self.name} TIMESTAMP '

        if self.null:
            sql += f' NULL'
        else:
            sql += f' NOT NULL'

        if self.default:
            sql += f' DEFAULT {self.default}'
        else:
            sql += f' DEFAULT CURRENT_TIMESTAMP'

        sql += f' COMMENT "{self.name}"'

        return sql


class DateField(Field):

    def __init__(self, name, db_column=None, dnt_filter=True):
        super(DateField, self).__init__(
            name=name, max_length=None, unique=False, blank=True, null=True,
            db_index=False, default=None, choices=None, db_column=db_column,
            validators=None, is_save=True, dnt_filter=dnt_filter
        )
        self._value = datetime.now()
        self._check(f'{name}(DateField)')

    def _check(self, field='DateTimeField'):
        return super(DateField, self)._check(field=field)

    def _check_value(self):

        if self._value is None:
            self._value = datetime.now().date()

        if isinstance(self._value, str):
            try:
                self._value = tools.TimeConverter.strtime_to_time(self._value)
                if self._value is not None:
                    self._value = self._value.date()
            except:
                raise ValueError(f'值错误：{self.name} 必须为可识别的时间字符串，当前值为：{self._value}')

        if isinstance(self._value, int):
            try:
                self._value = tools.TimeConverter.stamp_to_time(self._value)
                if self._value is not None:
                    self._value = self._value.date()
            except:
                raise ValueError(f'值错误：{self.name} 必须秒级或毫秒级时间戳，当前值为：{self._value}')

        if not self.null and not isinstance(self._value, date):
            raise TypeError(f'类型错误：{self.name} 必须为时间类型，当前类型为：{type(self._value)}')

    def _table_sql(self, cols=None):

        sql = f'{self.db_column or cols or self.name} DATE NOT NULL COMMENT "{self.name}"'

        return sql


class DateTimeField(Field):

    def __init__(self, name, db_column=None, dnt_filter=True):
        super(DateTimeField, self).__init__(
            name=name, max_length=None, unique=False, blank=True, null=True,
            db_index=False, default=None, choices=None, db_column=db_column,
            validators=None, is_save=True, dnt_filter=dnt_filter
        )
        self._value = datetime.now()
        self._check(f'{name}(DateTimeField)')

    def _check(self, field='DateTimeField'):
        return super(DateTimeField, self)._check(field=field)

    def _check_value(self):

        if self._value is None:
            self._value = datetime.now()

        if isinstance(self._value, str):
            try:
                self._value = tools.TimeConverter.strtime_to_time(self._value)
            except:
                raise ValueError(f'值错误：{self.name} 必须为可识别的时间字符串，当前值为：{self._value}')

        if isinstance(self._value, int):
            try:
                self._value = tools.TimeConverter.stamp_to_time(self._value)
            except:
                raise ValueError(f'值错误：{self.name} 必须秒级（10位）或毫秒级（13位）时间戳，当前值为：{self._value}')

        if not self.null and not isinstance(self._value, datetime):
            raise TypeError(f'类型错误：{self.name} 必须为时间类型，当前类型为：{type(self._value)}')

    def _table_sql(self, cols=None):

        sql = f'{self.db_column or cols or self.name} DATETIME NOT NULL COMMENT "{self.name}"'

        return sql


class TextField(Field):

    def __init__(
            self, name, default=None, validators=None, db_column=None, is_save=True, dnt_filter=False
    ):
        super(TextField, self).__init__(
            name=name, max_length=None, unique=False, blank=True, null=True,
            db_index=False, default=default, choices=None, db_column=db_column,
            validators=validators, is_save=is_save, dnt_filter=dnt_filter
        )
        self._value = ''
        self._check(f'{name}(TextField)')

    def _check(self, field='TextField'):
        return super(TextField, self)._check(field=field)

    def _check_default(self):

        if self.default is None:
            self.default = ''
            return True

        if not isinstance(self.default, str):
            self._message.append('default字段必须为str类型')
            return False

        return True

    def _check_value(self):

        if self._value is None:
            self._value = self.default or ''

        if not isinstance(self._value, str):
            raise ValueError(f'{self.name}值错误，value={self._value}, value必须为str类型')

    def _table_sql(self, cols=None):

        sql = f'{self.db_column or cols or self.name} TEXT NULL'

        # if self.default is not None:
        #     sql += f' DEFAULT "{self.default}"'

        sql += f' COMMENT "{self.name}"'

        return sql
