__all__ = [
    'StampField', 'DateField', 'DateTimeField', 'TimeField'
]

from datetime import datetime, date, time
from typing import Union, Optional, List

from AioSpider import tools
from AioSpider.field.field import Field, return_value
from AioSpider.field.intfield import BigIntField
from AioSpider.field.validators import *


class StampField(BigIntField):

    mapping = {
        'ftype': bool, 'stype': 'TIMESTAMP', 'mtype': 'TIMESTAMP', 'bit': None
    }
    error_messages = {
        **BigIntField.error_messages,
        'timestamp': '字段值必须为int类型，兼容可转换的datetime、date、float、str类型'
    }

    def __init__(
            self, name: str, *, auto_add: bool = False, auto_update: bool = False, db_column: Optional[str] = None,
            primary: bool = False, unique: bool = False, db_index: bool = False, default: Optional[int] = None,
            null: bool = True, validators: Union[List[Validator], Validator] = None,
            is_save: bool = True, error_messages: Optional[dict] = None
    ):

        self.auto_add = auto_add
        self.auto_update = auto_update

        super(StampField, self).__init__(
            name=name, db_column=db_column, primary=primary, max_length=None, unique=unique, null=null,
            db_index=db_index, default=default, validators=validators, is_save=is_save,
            error_messages=error_messages
        )

    def clean(self):
        
        super().clean()

        self.auto_add = BoolValidator(self.error_messages['auto_add_type'])(self.auto_add)
        self.auto_update = BoolValidator(self.error_messages['auto_update_type'])(self.auto_update)

        if self.auto_add:
            self.default = None
        elif self.default is None and not self.null:
            self.default = None
        elif self.default is None and not self.null:
            self.default = int(time.time())
        else:
            self.default = self.default

    @return_value
    def __set__(self, instance, value):

        if value is None:
            return self.default

        value = UniumTpyeValidator(self.error_messages['timestamp'])(value, (int, datetime, date, float, str))

        if isinstance(value, (datetime, date)):
            return value

        try:
            return tools.stamp_to_time(value)
        except:
            raise Validator(self.error_messages['timestamp'])


class DateField(Field):

    mapping = {
        'ftype': date, 'stype': 'DATE', 'mtype': 'DATE', 'bit': None
    }
    error_messages = {
        **Field.error_messages,
        'date': '字段值必须为date类型，兼容可转换的str类型'
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, primary: bool = False, unique: bool = False,
            db_index: bool = False, default: Optional[date] = None, null: bool = True,
            validators: Union[List[Validator], Validator] = None, is_save: bool = True,
            error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, db_column=db_column, primary=primary, max_length=None, unique=unique, null=null,
            db_index=db_index, default=default, validators=validators, is_save=is_save,
            error_messages=error_messages
        )

    def clean(self):

        if self.default is None and not self.null:
            self.default = None
        elif self.default is None and not self.null:
            self.default = datetime.now().date()
        else:
            self.default = self.default

        super().clean()

    @return_value
    def __set__(self, instance, value):

        if value is None:
            return self.default

        value = UniumTpyeValidator(self.error_messages['date'])(value, (date, datetime, str))

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        try:
            return tools.strtime_to_time(value, is_date=True)
        except:
            raise Validator(self.error_messages['date'])


class TimeField(Field):

    mapping = {
        'ftype': time, 'stype': 'TIME', 'mtype': 'TIME', 'bit': None
    }
    error_messages = {
        **Field.error_messages,
        'time': '字段值必须为time类型，兼容可转换的str类型'
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, primary: bool = False, unique: bool = False,
            db_index: bool = False, default: Optional[date] = None, null: bool = True,
            validators: Union[List[Validator], Validator] = None, is_save: bool = True,
            error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, db_column=db_column, primary=primary, max_length=None, unique=unique, null=null,
            db_index=db_index, default=default, validators=validators, is_save=is_save,
            error_messages=error_messages
        )

    def clean(self):

        if self.default is None and not self.null:
            self.default = None
        elif self.default is None and not self.null:
            self.default = datetime.now().time()
        else:
            self.default = self.default

        super().clean()

    @return_value
    def __set__(self, instance, value):

        if value is None:
            return self.default

        value = UniumTpyeValidator(self.error_messages['date'])(value, (time, datetime, str))

        if isinstance(value, datetime):
            return value.time()

        if isinstance(value, time):
            return value

        try:
            return tools.strtime_to_time(value).time()
        except:
            raise Validator(self.error_messages['time'])


class DateTimeField(DateField):

    mapping = {
        'ftype': datetime, 'stype': 'DATETIME', 'mtype': 'DATETIME', 'bit': None
    }
    error_messages = {
        **Field.error_messages,
        'datetime': '字段值必须为datetime类型，兼容可转换的date、int、float、str类型'
    }

    def __init__(
            self, name: str, *, auto_add: bool = False, auto_update: bool = False, db_column: Optional[str] = None,
            primary: bool = False, unique: bool = False, db_index: bool = False, default: Optional[datetime] = None,
            null: bool = True, validators: Union[List[Validator], Validator] = None,
            is_save: bool = True, error_messages: Optional[dict] = None
    ):

        self.auto_add = auto_add
        self.auto_update = auto_update

        super().__init__(
            name=name, db_column=db_column, primary=primary, unique=unique, null=null, db_index=db_index,
            default=default, validators=validators, is_save=is_save,
            error_messages=error_messages
        )

    def clean(self):

        self.auto_add = BoolValidator(self.error_messages['auto_add_type'])(self.auto_add)
        self.auto_update = BoolValidator(self.error_messages['auto_update_type'])(self.auto_update)

        if self.auto_add:
            self.default = 'CURRENT_TIMESTAMP'
        elif self.default is None and not self.null:
            self.default = None
        elif self.default is None and not self.null:
            self.default = datetime.now()
        else:
            self.default = self.default

        super().clean()

    @return_value
    def __set__(self, instance, value):

        if value is None:
            return self.default

        value = UniumTpyeValidator(self.error_messages['datetime'])(value, (date, datetime, int, float, str))

        if isinstance(value, datetime):
            return value

        if isinstance(value, date):
            return tools.strtime_to_time(str(value))

        try:
            return tools.strtime_to_time(value)
        except:
            raise ValueError(self.error_messages['datetime'])
