__all__ = [
    'Field', 'CharField', 'HashField', 'PathField', 'ExtensionNameField', 'BytesContentField',
    'JSONField', 'IPAddressField', 'UUIDField'
]

import ipaddress
from uuid import UUID
from pathlib import Path

from typing import Optional, Union, Any, List, Iterable

from AioSpider import tools
from AioSpider.field.indexfield import IndexMeta
from AioSpider.field.validators import *


def return_value(func):

    def inner(cls: Any, instance: Any, value: Any, *args, **kwargs):

        value = func(cls, instance, value, *args, **kwargs)

        if all(i(value) for i in cls.validators):
            instance.__dict__[cls.db_column] = value

    return inner


class Field:

    mapping = {
        'ftype': None, 'stype': None, 'mtype': None, 'bit': None
    }
    error_messages = {
        'name_type': '字段名参数类型错误',
        'value_type': '字段值参数类型错误',
        'default_type': '默认值参数类型错误',
        'column_type': '列名参数类型错误',
        'max_length_type': '最大长度参数类型错误',
        'min_length_type': '最小长度参数类型错误',
        'primary_type': '主键参数类型错误',
        'unique_type': '唯一键参数类型错误',
        'null_type': 'null参数类型错误',
        'is_save_type': 'is_save参数类型错误',
        'db_index_type': '索引参数类型错误',
        'regex_type': 'regex参数类型错误',
        'str': '%s字段的值必须为str类型，当前类型为：%s，当前值：%s',
        'int': '字段值必须为int类型',
        'float': '字段值必须为float类型',
        'regex': '正则匹配错误',
        'max_length': '%s 字段值超出最大长度，字段长度：%s，当前字段值长度：%s，当前字段值：%s',
        'min_length': '字段值小于最小长度',
        'auto_update_type': 'auto_update参数类型错误',
        'auto_add_type': 'auto_add参数类型错误',
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, min_length=None, max_length: Optional[int] = None,
            primary: bool = False, unique: bool = False, db_index: Union[bool, IndexMeta] = False, null: bool = True,
            default: Any = None, is_save: bool = True, validators: Union[List[Validator], Validator] = None,
            error_messages: Optional[dict] = None
    ):

        self.name = name
        self.db_column = db_column
        self.max_length = max_length
        self.min_length = min_length
        self.primary = primary
        self.unique = unique
        self.db_index = db_index
        self.null = null
        self.default = default
        self.is_save = is_save
        self.validators = validators

        if error_messages is not None:
            self.error_messages.update(error_messages)

        self._value = None

        self.clean()

    def clean(self):

        self.name = StrValidator(self.error_messages['name_type'])(self.name)
        self.db_column = StrValidator(self.error_messages['column_type'])(self.db_column)
        self.max_length = IntValidator(self.error_messages['max_length_type'])(self.max_length)
        self.min_length = IntValidator(self.error_messages['min_length_type'])(self.min_length)
        self.primary = BoolValidator(self.error_messages['primary_type'])(self.primary)
        self.unique = BoolValidator(self.error_messages['unique_type'])(self.unique)
        self.db_index = IndexValidator(self.error_messages['db_index_type'])(self.db_index)
        self.null = BoolValidator(self.error_messages['null_type'])(self.null)
        self.is_save = BoolValidator(self.error_messages['is_save_type'])(self.is_save)

        if self.validators is None:
            self.validators = []

        if self.primary:
            self.unique = True

        if self.unique:
            self.db_index = True

        return True

    def __set_name__(self, owner, name):
        self.db_column = name

    def __get__(self, instance, owner):

        if self._value is None:
            self._value = self.default

        if instance is not None:
            return instance.__dict__.get(self.db_column, self._value)
        else:
            return self._value

    def __eq__(self, other):
        return self._value == other

    def __str__(self):
        return f'<{self.name}: {self._value}>'

    __repr__ = __str__


class CharField(Field):

    mapping = {
        'ftype': str, 'stype': 'VARCHAR', 'mtype': 'VARCHAR', 'bit': None
    }
    error_messages = {
        **Field.error_messages,
        'truncate_type': 'is_truncate参数字段类型错误',
        'choices_type': 'choice参数字段类型错误',
        'strip_type': 'strip_spaces参数字段类型错误',
    }

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, min_length=None, max_length: Optional[int] = None,
            primary: bool = False, unique: bool = False, db_index: bool = False, null: bool = True,
            default: Optional[str] = None, choices: Union[Iterable, None] = None, is_truncate: bool = False,
            is_save: bool = True, validators: Union[List[Validator], Validator] = None, strip: bool = True,
            regex: Optional[str] = None, error_messages: Optional[dict] = None
    ):

        self.choices = choices
        self.regex = regex
        self.is_truncate = is_truncate
        self.strip = strip

        super(CharField, self).__init__(
            name=name, db_column=db_column, max_length=max_length or 255, min_length=min_length,
            primary=primary, unique=unique, db_index=db_index, null=null, default=default,
            validators=validators, is_save=is_save, error_messages=error_messages
        )

    def clean(self):

        self.default = DefaultTypeValidator(self.error_messages['default_type'])(self.default, (str, ))
        self.is_truncate = BoolValidator(self.error_messages['truncate_type'])(self.is_truncate)
        self.strip = BoolValidator(self.error_messages['strip_type'])(self.strip)

        if self.choices is not None:
            self.choices = dict(self.choices)

        regex = StrValidator(self.error_messages['regex_type'])(self.regex)
        self.regex = re.compile(regex) if regex else None

        if self.default is None and self.null:
            self.default = None
        elif self.default is None and not self.null:
            self.default = ""
        else:
            self.default = self.default

        super(CharField, self).clean()

    @return_value
    def __set__(self, instance, value):

        if value is None:
            return self.default

        # 处理choice
        if self.choices:
            value = self.choices.get(value, value)

        value = StrValidator(
            self.error_messages['str'] % (self.db_column, type(value), value)
        )(value)
        
        if self.strip:
            value = value.strip()

        if not self.is_truncate:
            value = MaxLengthValidator(
                self.error_messages['max_length'] % (self.db_column, self.max_length, len(value), value),
                self.max_length
            )(value)
        else:
            value = value[:self.max_length]

        value = MinLengthValidator(self.error_messages['min_length'], self.min_length)(value)
        value = RegexValidator(self.error_messages, self.regex)(value)

        return value


class HashField(CharField):

    error_messages = {
        **CharField.error_messages,
        'make_hash_field_type_error': 'make_hash_field 字段参数类型错误',
        'exclude_field_type_error': 'exclude_field 字段参数类型错误',
        'make_hash_field_value_error': 'make_hash_field 字段为空',
    }

    def __init__(
            self, name: str, *, make_hash_field: Union[str, list, tuple] = None,
            exclude_field: Union[str, list, tuple] = None, db_column: Optional[str] = None,
            primary: bool = False, unique: bool = True, db_index: bool = True, is_save: bool = True,
            validators: Union[List[Validator], Validator] = None, error_messages: Optional[dict] = None
    ):

        self.make_hash_field = make_hash_field
        self.exclude_field = exclude_field

        super().__init__(
            name=name, db_column=db_column, max_length=32, primary=primary, unique=unique, db_index=db_index,
            null=False, default=None, validators=validators, is_save=is_save,
            error_messages=error_messages
        )

    def clean(self):
        self.make_hash_field = UniumTpyeValidator(self.error_messages['make_hash_field_type_error'])(
            self.make_hash_field, (str, list, tuple, Field)
        )
        self.exclude_field = UniumTpyeValidator(self.error_messages['make_hash_field_type_error'])(
            self.exclude_field, (str, list, tuple, Field)
        )
        super(HashField, self).clean()

    def __get__(self, instance, owner):
        self.__set__(instance, value=None)
        return super(HashField, self).__get__(instance, owner)

    @return_value
    def __set__(self, instance, value):
        
        if value is not None:
            return super(HashField, self).__set__(instance, value)

        if self.exclude_field:
            fields = [
                k for k, v in instance.fields.items()
                if k not in self.exclude_field and not isinstance(v, self.__class__)
            ]
        else:
            fields = [k for k, v in instance.fields.items() if not isinstance(v, self.__class__)]

        if isinstance(self.make_hash_field, str) and self.make_hash_field in fields:
            return tools.make_md5(getattr(instance, self.make_hash_field))

        if isinstance(self.make_hash_field, (list, tuple)):
            value_list = [getattr(instance, field) for field in self.make_hash_field if field in fields]
            return tools.make_md5(tools.join(value_list, on='-'))

        if self.make_hash_field is None:
            value_list = [getattr(instance, field) for field in fields]
            return tools.make_md5(tools.join(value_list, on='-'))

        raise ValueError(self.error_messages['make_hash_field_value_error'])


class PathField(CharField):

    def __init__(
            self, name: str, *, db_column: Optional[str] = None, max_length: Optional[int] = None,
            min_length: Optional[int] = None, default: Optional[str] = None, null: bool = True,
            validators: Union[List[Validator], Validator] = None, is_save: bool = True,
            regex: Optional[str] = None, error_messages: Optional[dict] = None
    ):
        super(PathField, self).__init__(
            name=name, db_column=db_column, max_length=max_length, min_length=min_length, primary=False,
            unique=False, null=null,  db_index=False, default=default, choices=None, validators=validators,
            is_save=is_save, regex=regex, error_messages=error_messages
        )
        
    def clean(self):
        super(PathField, self).clean()
        if self.regex is None:
            self.regex = r'^(?:[a-zA-Z]:\\|/)?(?:[^\\\r\n]+[\\/]?)*$'

    def exists(self):
        return self._value.exists()

    @return_value
    def __set__(self, instance, value):

        if value is None or isinstance(value, Path):
            return value

        value = str(value)
        value = super(PathField, self).__set__(instance, value)
        
        return Path(value)

    def __truediv__(self, other: Union[Field, str]):
        new_instance = self.__class__(
            name=self.name, max_length=self.max_length, default=self.default,
            null=self.null, validators=self.validators
        )

        if isinstance(other, Field):
            new_value = str(self._value / other._value)
        else:
            new_value = str(self._value / other)

        new_instance.__set__(new_instance, new_value)
        return new_instance

    def __str__(self):
        return str(self._value)

    __repr__ = __str__


class ExtensionNameField(Field):

    mapping = {
        'ftype': str, 'stype': 'VARCHAR', 'mtype': 'VARCHAR', 'length': None
    }

    def __init__(
            self, name: str, *, db_column: str = None, db_index: bool = False, default: str = None,
            is_save: bool = True, validators: Union[List[Validator], Validator] = None,
            error_messages: Optional[dict] = None
    ):
        super(ExtensionNameField, self).__init__(
            name=name, db_column=db_column, primary=False, unique=False, max_length=None, min_length=None,
            null=False, db_index=db_index, default=default, validators=validators, is_save=is_save,
            error_messages=error_messages
        )

    def clean(self):
        
        self.default = DefaultTypeValidator(self.error_messages['default_type'])(self.default, (str, ))
        
        if self.default is None:
            self.default = ".txt"
        
        super().clean()

    @return_value
    def __set__(self, instance, value):

        if value is None:
            return self.default

        value = StrValidator(self.error_messages['str'] % (self.db_column, type(value), value))(value)
        value = '.' + value if value and value[0] != '.' else value

        return value


class BytesContentField(Field):
    
    mapping = {
        'ftype': bytes, 'stype': 'VARCHAR', 'mtype': 'VARCHAR', 'length': None
    }
    error_messages = {
        **Field.error_messages,
        'bytes': '字段值必须为bytes类型',
    }

    def __init__(
            self, name: str, *, encoding: str = 'utf-8', db_column: str = None, null: bool = True,
            default: bytes = None, is_save: bool = True, regex: Optional[str] = None,
            validators: Union[List[Validator], Validator] = None, error_messages: Optional[dict] = None
    ):

        self.encoding = encoding
        self.regex = regex

        super(BytesContentField, self).__init__(
            name=name, db_column=db_column, primary=False, unique=False, null=null, db_index=False,
            max_length=None, min_length=None, default=default, is_save=is_save, validators=validators,
            error_messages=error_messages
        )

    def clean(self):

        self.default = DefaultTypeValidator(self.error_messages['default_type'])(self.default, (bytes,))
        self.encoding = DefaultTypeValidator(self.error_messages['default_type'])(self.encoding, (str,))
        regex = StrValidator(self.error_messages['regex_type'])(self.regex)
        self.regex = re.compile(regex) if regex else None

        if self.default is None and self.null:
            self.default = None
        elif self.default is None and not self.null:
            self.default = b""
        else:
            self.default = self.default

        super().clean()

    @return_value
    def __set__(self, instance, value):

        if value is None:
            return self.default

        if isinstance(value, str):
            value = value.encode(self.encoding)

        value = BytesValidator(self.error_messages['bytes'])(value)
        value = RegexValidator(self.error_messages, self.regex)(value)

        return value


class JSONField(Field):

    mapping = {
        'ftype': dict, 'stype': 'JSON', 'mtype': 'JSON', 'bit': None
    }

    def __init__(
            self, name: str, *, null: bool = True, default: dict = None, db_column: str = None, is_save: bool = True,
            validators: Union[List[Validator], Validator] = None, primary: bool = False
    ):
        super(JSONField, self).__init__(
            name=name, max_length=None, unique=False, null=null, db_index=False, default=default, db_column=db_column,
            validators=validators, is_save=is_save, primary=primary,
            min_length=None, error_messages=None,
        )

    def clean(self):
        self.default = DefaultTypeValidator(self.error_messages['default_type'])(
            self.default, (str, )
        )
        super().clean()


class IPAddressField(Field):
    mapping = {
        'ftype': ipaddress.IPv4Address, 'stype': 'VARCHAR', 'mtype': 'VARCHAR', 'length': None
    }

    def __init__(
            self, name: str, *, null: bool = True, default: str = None, db_column: str = None, is_save: bool = True,
            validators: Union[List[Validator], Validator] = None, primary: bool = False
    ):
        super(IPAddressField, self).__init__(
            name=name, max_length=None, unique=False, null=null, db_index=False, default=default, db_column=db_column,
            validators=validators, is_save=is_save, primary=primary, error_messages=None
        )

    def clean(self):
        self.default = DefaultTypeValidator(self.error_messages['default_type'])(
            self.default, (str, )
        )
        super().clean()


class UUIDField(Field):

    mapping = {
        'ftype': UUID, 'stype': 'UUID', 'mtype': 'UUID', 'bit': None
    }

    def __init__(
            self, name: str, *, null: bool = True, default: UUID = None, db_column: str = None, is_save: bool = True,
            validators: Union[List[Validator], Validator] = None, primary: bool = False
    ):
        super(UUIDField, self).__init__(
            name=name, max_length=None, unique=False, null=null, db_index=False, default=default, db_column=db_column,
            validators=validators, is_save=is_save, primary=primary
        )

    def clean(self):
        self.default = DefaultTypeValidator(self.error_messages['default_type'])(
            self.default, (str, )
        )
        super().clean()


class RelationshipField(Field):

    def __init__(self, related_model, *args, **kwargs):
        self.related_model = related_model
        super().__init__(*args, **kwargs)


class ForeignKeyField(RelationshipField):

    def __init__(self, related_model, *args, **kwargs):
        super().__init__(related_model, *args, **kwargs)


class ManyToManyField(RelationshipField):

    def __init__(self, related_model, *args, **kwargs):
        super().__init__(related_model, *args, **kwargs)
