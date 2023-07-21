__all__ = [
    'TextField', 'MediumTextField', 'ListField', 'LongTextField'
]

from typing import Optional, Union, List

from AioSpider import tools
from AioSpider.field.field import CharField, return_value
from AioSpider.field.validators import *


class TextField(CharField):

    mapping = {
        'ftype': str, 'stype': 'TEXT', 'mtype': 'TEXT', 'bit': None
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, min_length: Optional[int] = None,
            max_length: Optional[int] = None, null: bool = True, default: Optional[str] = None,
            is_save: bool = True, validators: Union[List[Validator], Validator] = None, strip: bool = True,
            regex: Optional[str] = None, error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, db_column=db_column, max_length=max_length or (2 ** 16 - 1), min_length=min_length, regex=regex,
            primary=False, unique=False, db_index=False, null=null, default=default, choices=None, is_truncate=False,
            validators=validators, strip=strip, is_save=is_save, error_messages=error_messages
        )

    @return_value
    def __set__(self, instance, value):

        if value is None:
            return self.default

        value = StrValidator(
            self.error_messages['str'] % (self.db_column, type(value), value)
        )(value)

        if self.strip:
            value = value.strip()

        value = MaxLengthValidator(
            self.error_messages['max_length'] % (self.db_column, self.max_length, len(value), value),
            self.max_length
        )(value)
        value = MinLengthValidator(self.error_messages['min_length'], self.min_length)(value)
        value = RegexValidator(self.error_messages, self.regex)(value)

        return value


class MediumTextField(TextField):

    mapping = {
        'ftype': str, 'stype': 'MEDIUMTEXT', 'mtype': 'MEDIUMTEXT', 'bit': None
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, min_length: Optional[int] = None,
            max_length: Optional[int] = None, null: bool = True, default: Optional[str] = None,
            is_save: bool = True, validators: Union[List[Validator], Validator] = None, strip: bool = True,
            regex: Optional[str] = None, error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, db_column=db_column, max_length=max_length or (2 ** 24 - 1), min_length=min_length,
            null=null, regex=regex, default=default, validators=validators, strip=strip, is_save=is_save,
            error_messages=error_messages
        )
        
        
class LongTextField(TextField):

    mapping = {
        'ftype': str, 'stype': 'LONGTEXT', 'mtype': 'LONGTEXT', 'bit': None
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, min_length: Optional[int] = None,
            max_length: Optional[int] = None, null: bool = True, default: Optional[str] = None,
            is_save: bool = True, validators: Union[List[Validator], Validator] = None, strip: bool = True,
            regex: Optional[str] = None, error_messages: Optional[dict] = None
    ):
        super().__init__(
            name=name, db_column=db_column, max_length=max_length or (2 ** 32 - 1), min_length=min_length,
            null=null, regex=regex, default=default, validators=validators, strip=strip, is_save=is_save,
            error_messages=error_messages
        )
    

class ListField(TextField):

    error_messages = {
        **TextField.error_messages,
        'origin_type': 'origin_type参数字段类型错误',
        'join_type': 'join_type参数字段类型错误',
    }

    def __init__(
            self, name: str, *, origin: bool = False, join: str = None, db_column: str = None, null: bool = True,
            max_length: Optional[int] = None, min_length: Optional[int] = None, is_save: bool = True,
            validators: Union[List[Validator], Validator] = None, regex: Optional[str] = None,
            error_messages: Optional[dict] = None
    ):
        self.origin = origin
        self.join = join

        super(ListField, self).__init__(
            name=name, db_column=db_column, max_length=max_length, min_length=min_length, validators=validators,
            null=null, regex=regex, is_save=is_save, error_messages=error_messages
        )

    def clean(self):

        self.origin = BoolValidator(self.error_messages['origin_type'])(self.origin)
        self.join = StrValidator(self.error_messages['join_type'])(self.join)

        super().clean()

    @return_value
    def __set__(self, instance, value):

        if isinstance(value, Iterable):

            if self.origin:
                value = str(value)
            elif self.join:
                value = tools.join(value, self.join)
            else:
                value = tools.join(value)

            return value

        return super(ListField, self).__set__(instance, value)
