__all__ = [
    'DecimalField', 'FloatField', 'DoubleField'
]

from decimal import Decimal
from typing import Optional, Union, List

import numpy as np
from AioSpider.field.field import Field, return_value
from AioSpider.field.validators import *


class DecimalField(Field):

    mapping = {
        'ftype': Decimal, 'stype': 'DECIMAL', 'mtype': 'DECIMAL', 'bit': None
    }
    error_messages = {
        **Field.error_messages,
        'float': '字段值必须为float类型'
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, primary: bool = False, unique: bool = False,
            db_index: bool = False, max_length: Optional[int] = None, default: Optional[float] = None,
            null: bool = True, validators: Union[List[Validator], Validator] = None,
            is_save: bool = True, error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, max_length=max_length, unique=unique, null=null, db_index=db_index, default=default,
            primary=primary, db_column=db_column, validators=validators, is_save=is_save,
            error_messages=error_messages
        )

    def clean(self):

        self.default = DefaultTypeValidator(self.error_messages['default_type'])(
            self.default, (float, int, str)
        )

        if self.default is None and self.null:
            self.default = None
        elif self.default is None and not self.null:
            self.default = float()
        else:
            self.default = self.default

        super().clean()

    @return_value
    def __set__(self, instance, value):

        if value is None:
            return self.default

        value = UniumTpyeValidator(self.error_messages['int'])(value, (float, int, str, np.float_))
        
        try:
            if self.max_length is not None:
                return Decimal(float(value)).quantize(Decimal('0.' + '0' * (self.max_length - 2)))
            else:
                return Decimal(float(value)).quantize(Decimal('0.00000'))
        except (ValueError, TypeError):
            raise ValueError(self.error_messages['float'])


class FloatField(DecimalField):

    mapping = {
        'ftype': float, 'stype': 'FLOAT', 'mtype': 'FLOAT', 'bit': None
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, primary: bool = False, unique: bool = False,
            db_index: bool = False, max_length: Optional[int] = None, default: Optional[float] = None,
            null: bool = True, validators: Union[List[Validator], Validator] = None,
            is_save: bool = True, error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, max_length=max_length, unique=unique, null=null, db_index=db_index, default=default,
            primary=primary, db_column=db_column, validators=validators, is_save=is_save,
            error_messages=error_messages
        )


class DoubleField(FloatField):

    mapping = {
        'ftype': float, 'stype': 'DOUBLE', 'mtype': 'DOUBLE', 'bit': None
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, primary: bool = False, unique: bool = False,
            db_index: bool = False, max_length: Optional[int] = None, default: Optional[float] = None,
            null: bool = True, validators: Union[List[Validator], Validator] = None,
            is_save: bool = True, error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, max_length=max_length, unique=unique, null=null, db_index=db_index, default=default,
            primary=primary, db_column=db_column, validators=validators, is_save=is_save,
            error_messages=error_messages
        )
        