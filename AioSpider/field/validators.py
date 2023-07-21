from AioSpider.field.indexfield import *


class Validator:

    def __init__(self, message):
        self.message = message

    def __call__(self, value):
        raise NotImplementedError


class MaxLengthValidator(Validator):

    def __init__(self, message, max_length=None):
        super().__init__(message)
        self.max_length = max_length

    def __call__(self, value):

        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(self.message)

        if self.max_length is None:
            return value

        if len(value) > self.max_length:
            raise ValueError(self.message)

        return value


class MinLengthValidator(Validator):

    def __init__(self, message, min_length=None):
        super().__init__(message)
        self.min_length = min_length

    def __call__(self, value):

        if not isinstance(value, str):
            raise ValueError(self.message)

        if self.min_length is None:
            return value

        if len(value) < self.min_length:
            raise ValueError(self.message)

        return value


class BitSizeValidator(Validator):

    def __init__(self, message, max_value: int, min_value: int):
        super().__init__(message)
        self.max_value = max_value
        self.min_value = min_value

    def __call__(self, value):

        if value is None:
            return None

        if self.min_value <= value <= self.max_value:
            return value
        else:
            raise ValueError(self.message)


class RangeValidator(Validator):

    def __init__(self, message, min_value=None, max_value=None):
        super().__init__(message)
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Value must be a number.")

        if (self.min_value is not None and value < self.min_value) or (
                self.max_value is not None and value > self.max_value
        ):
            raise ValueError(self.message or f"Value must be between {self.min_value} and {self.max_value}.")


class RegexValidator(Validator):

    def __init__(self, message, regex):
        super().__init__(message)
        self.regex = regex

    def __call__(self, value):
        
        if value is None:
            return None

        if self.regex is None:
            return value
        
        if not isinstance(value, str):
            raise TypeError(self.message)

        if not self.regex.match(value):
            raise ValueError(self.message)
        
        return value


class EmailValidator(RegexValidator):

    def __init__(self, message):
        super().__init__(message, regex=r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


class TypeValidator(Validator):

    def __call__(self, value, type, *args, **kwargs):

        if value is None:
            return None

        if not isinstance(value, type):
            raise TypeError(self.message)

        return value


class StrValidator(TypeValidator):

    def __call__(self, value, *args, **kwargs):
        return super().__call__(value, type=str, *args, **kwargs)
    

class BytesValidator(TypeValidator):

    def __call__(self, value, *args, **kwargs):
        return super().__call__(value, type=bytes, *args, **kwargs)


class IntValidator(TypeValidator):

    def __call__(self, value, *args, **kwargs):
        return super().__call__(value, type=int, *args, **kwargs)


class BoolValidator(TypeValidator):

    def __call__(self, value, *args, **kwargs):
        return super().__call__(value, type=bool, *args, **kwargs)


class UniumTpyeValidator(Validator):

    def __call__(self, value, types):

        if value is None:
            return None

        if not isinstance(value, types):
            raise TypeError(self.message)

        return value


class DefaultTypeValidator(UniumTpyeValidator):
    pass


class IndexValidator(Validator):

    def __call__(self, value, *args, **kwargs):

        if value is False:
            return False

        if value is True:
            return NormalIndexField

        if issubclass(value, IndexMeta):
            return value

        raise TypeError(self.message)
