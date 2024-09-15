import re

from PyOdata1C.errors import ValidationError


class BaseValidator:
    message = None

    def __init__(self, limit_value, message=None, ):
        if message:
            self.message = message
        self.limit_value = limit_value

    def __call__(self, *args, **kwargs):
        if not self.compare(self.limit_value, *args, **kwargs):
            raise ValidationError(self.__class__.message % self.limit_value)

    @classmethod
    def compare(cls, a, b):
        return a is not b


class MaxValueValidator(BaseValidator):
    message = 'Значение больше или равно максимальному - %d'

    @classmethod
    def compare(cls, a, b):
        return a > b


class MinValueValidator(BaseValidator):
    message = 'Значение меньше или равно минимальному - %d'

    @classmethod
    def compare(cls, a, b):
        return a < b


class BaseStringValidator:
    message = None

    def __init__(self, string_pattern, message=None, ):
        if message:
            self.message = message
        self.string_pattern = string_pattern

    def __call__(self, *args, **kwargs):
        if not self.compare(self.string_pattern, *args, **kwargs):
            raise ValidationError(self.__class__.message % str(self.string_pattern))

    @staticmethod
    def compare(pattern, value):
        return pattern == value


class RegexValidator(BaseStringValidator):
    message = 'Значение не соответствует шаблону - %s'

    @staticmethod
    def compare(pattern, value):
        return bool(re.search(pattern, str(value)))


class ReadyRegexValidator(RegexValidator):
    message = None
    str_pattern = None

    def __init__(self):
        super().__init__(self.str_pattern)


class EmailValidator(ReadyRegexValidator):
    message = 'Поле не является email'
    str_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


class PhoneNumberValidator(ReadyRegexValidator):
    message = 'Поле не является номером телефона %s'
    str_pattern = r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'
