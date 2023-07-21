__all__ = [
    'TinyIntField', 'SmallIntField', 'MediumIntField', 'IntField', 'BigIntField', 'AutoIntField',
    'BoolField'
]

from typing import Optional, Union, Iterable, List

import numpy as np
from AioSpider.field.field import Field, return_value
from AioSpider.field.validators import *


class TinyIntField(Field):
    mapping = {
        'ftype': int, 'stype': 'TINYINTEGER', 'mtype': 'TINYINT', 'bit': 8
    }
    error_messages = {
        **Field.error_messages,
        'int': '%s字段值必须为int类型，或兼容可转换的float和str类型，当前类型为：%s，字段值：%s',
        'bit_size': '%s字段值超出范围，字段范围：%s，当前字段值：%s',
        'unsigned_type': 'unsigned_type参数类型错误'
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, primary: bool = False, max_length: int = 4,
            unsigned: bool = False, default: Optional[int] = None, null: bool = True, unique: bool = False,
            db_index: bool = False, choices: Union[Iterable, None] = None,
            validators: Union[List[Validator], Validator] = None, is_save: bool = True,
            error_messages: Optional[dict] = None
    ):

        self.choices = choices
        self.unsigned = unsigned

        super().__init__(
            name=name, primary=primary, default=default, unique=unique, null=null, max_length=max_length,
            db_index=db_index, db_column=db_column, validators=validators, is_save=is_save,
            error_messages=error_messages
        )

    def clean(self):

        self.default = DefaultTypeValidator(self.error_messages['default_type'])(
            self.default, (int, float, str)
        )
        self.unsigned = BoolValidator(self.error_messages['unsigned_type'])(self.unsigned)

        if self.choices is not None:
            self.choices = dict(self.choices)

        if self.default is None and self.null is None:
            self.default = None
        elif self.default is None and self.null is not None:
            self.default = 0
        else:
            self.default = self.default

        super().clean()

    @return_value
    def __set__(self, instance, value):

        if value is None:
            return self.default

        # 处理choice
        if self.choices:
            value = self.choices.get(value, value)

        value = UniumTpyeValidator(
            self.error_messages['int'] % (self.db_column, type(value), value)
        )(value, (int, float, str, np.integer, np.float_))
        min_value, max_value = (0, 2 ** self.mapping['bit'] - 1) if self.unsigned else (
            2 ** (self.mapping['bit'] - 1) * (-1), 2 ** (self.mapping['bit'] - 1) - 1
        )

        if isinstance(value, int):
            return BitSizeValidator(
                self.error_messages['bit_size'] % (self.db_column, f'{min_value}~{max_value}', value),
                max_value, min_value
            )(value)

        try:
            return int(value)
        except ValueError:
            raise ValueError(self.error_messages['int'] % (self.db_column, type(value), value))


class SmallIntField(TinyIntField):
    mapping = {
        'ftype': int, 'stype': 'SMALLINTEGER', 'mtype': 'SMALLINT', 'bit': 16
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, primary: bool = False, max_length: int = 6,
            unsigned: bool = False, default: Optional[int] = None, null: bool = True, unique: bool = False,
            db_index: bool = False, validators: Union[List[Validator], Validator] = None,
            is_save: bool = True, error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, primary=primary, default=default, unique=unique, null=null, max_length=max_length,
            unsigned=unsigned, db_index=db_index, db_column=db_column, validators=validators, is_save=is_save,
            error_messages=error_messages
        )


class MediumIntField(TinyIntField):
    mapping = {
        'ftype': int, 'stype': 'MEDIUMINTEGER', 'mtype': 'MEDIUMINT', 'bit': 24
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, primary: bool = False, max_length: int = 9,
            unsigned: bool = False, default: Optional[int] = None, null: bool = True, unique: bool = False,
            db_index: bool = False, validators: Union[List[Validator], Validator] = None,
            is_save: bool = True, error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, primary=primary, default=default, unique=unique, null=null, max_length=max_length,
            db_index=db_index, db_column=db_column, validators=validators, is_save=is_save,
            unsigned=unsigned, error_messages=error_messages
        )


class IntField(TinyIntField):
    mapping = {
        'ftype': int, 'stype': 'INTEGER', 'mtype': 'INT', 'bit': 32
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, primary: bool = False, max_length: int = 11,
            unsigned: bool = False, default: Optional[int] = None, null: bool = True, unique: bool = False,
            db_index: bool = False, validators: Union[List[Validator], Validator] = None,
            is_save: bool = True, error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, primary=primary, default=default, unique=unique, null=null, max_length=max_length,
            db_index=db_index, db_column=db_column, validators=validators, is_save=is_save,
            unsigned=unsigned, error_messages=error_messages
        )


class BigIntField(TinyIntField):
    mapping = {
        'ftype': int, 'stype': 'BIGINTEGER', 'mtype': 'BIGINT', 'bit': 64
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, primary: bool = False, max_length: int = 20,
            unsigned: bool = False, default: Optional[int] = None, null: bool = True, unique: bool = False,
            db_index: bool = False, validators: Union[List[Validator], Validator] = None,
            is_save: bool = True, error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, primary=primary, default=default, unique=unique, null=null, max_length=max_length,
            db_index=db_index, db_column=db_column, validators=validators, is_save=is_save,
            unsigned=unsigned, error_messages=error_messages
        )


class AutoIntField(IntField):
    factor = None

    def __init__(
            self, name: str, *, sep: int = 1, max_length: int = 11, db_column: Optional[str] = None,
            is_save: bool = True, primary: bool = False, db_index: bool = False,
            validators: Union[List[Validator], Validator] = None, error_messages: Optional[dict] = None
    ):
        self.sep = sep
        super().__init__(
            name=name, max_length=max_length, default=None, null=False, validators=validators, db_column=db_column,
            is_save=is_save, db_index=db_index, unique=True, primary=primary,
            unsigned=False, error_messages=error_messages
        )

    @return_value
    def __set__(self, instance, value):

        if self.factor is None:
            self.factor = {}

        class_name = instance.__class__.__name__

        if isinstance(value, int) and value > self.factor.get(class_name, 0):
            self.factor[class_name] = value
        else:
            self.factor[class_name] = self.factor.get(class_name, 0) + self.sep

        return self.factor[class_name]


class BoolField(TinyIntField):
    mapping = {
        'ftype': bool, 'stype': 'BOOLEAN', 'mtype': 'TINYINT', 'bit': None
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, db_index: bool = False,
            default: Optional[int] = False, is_save: bool = True,
            validators: Union[List[Validator], Validator] = None, error_messages: Optional[dict] = None
    ):
        super(BoolField, self).__init__(
            name=name, db_column=db_column, primary=False, unique=False, null=False, db_index=db_index,
            unsigned=False, default=default, validators=validators, is_save=is_save,
            error_messages=error_messages
        )

    def clean(self):

        self.default = DefaultTypeValidator(self.error_messages['default_type'])(
            self.default, (bool, int, float, str, list, set, tuple)
        )

        if self.default is None and self.null:
            self.default = None
        elif self.default is None and not self.null:
            self.default = 0
        else:
            self.default = int(self.default)

        super(BoolField, self).clean()

    @return_value
    def __set__(self, instance, value):
        return bool(value)
