from datetime import datetime
from typing import Callable, List
from errors import ValidationError


DELIMITER = '/'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


class FilterResultField:
    result: str

    def __init__(self, result):
        self.result = result

    def __and__(self, other):
        return FilterResultField(f"{self.result} and {other}")

    def __or__(self, other):
        return FilterResultField(f"{self.result} or {other}")

    def __rand__(self, other):
        return FilterResultField(f"{other} and {self.result}")

    def __ror__(self, other):
        return FilterResultField(f"{other} or {self.result}")

    def __str__(self):
        return self.result


class Field:
    source: str
    expand: str | None = None
    cast_on: str | None = None
    select: bool = True
    validate_function: Callable | None = None
    validators: List[Callable] | None = None
    null: bool = False

    def __init__(
            self,
            source: str,
            cast_on: str | None = None,
            select=True,
            validators: List[Callable] | None = None,
            null: bool = False
    ):
        self.source = source
        self.select = select
        self.validators = validators
        self.cast_on = cast_on
        self.null = null
        if DELIMITER in source:
            self.expand = '/'.join(source.split(DELIMITER)[:-1])

    def _build_result_field(self, other, operand) -> FilterResultField:
        return FilterResultField(f"cast({self.source}, '{self.cast_on}') {operand} {other}") if self.cast_on else FilterResultField(f"{self.source} {operand} {other}")

    def field_mapper(self, *args, **kwargs):
        if args[0] is None and not self.null:
            raise ValidationError
        return self.validate_function(*args, **kwargs)

    def __eq__(self, other) -> FilterResultField:
        return self._build_result_field(other, 'eq')

    def __ne__(self, other) -> FilterResultField:
        return self._build_result_field(other, 'ne')

    def __lt__(self, other) -> FilterResultField:
        return self._build_result_field(other, 'lt')

    def __le__(self, other) -> FilterResultField:
        return self._build_result_field(other, 'le')

    def __ge__(self, other) -> FilterResultField:
        return self._build_result_field(other, 'ge')

    def __gt__(self, other) -> FilterResultField:
        return self._build_result_field(other, 'gt')

    def __str__(self):
        return self.source


class BoolField(Field):
    validate_function = bool


class IntegerField(Field):
    validate_function = int


class FloatField(IntegerField):
    validate_function = float


class StringField(Field):
    validate_function = str

    def _build_result_field(self, other, operand) -> FilterResultField:
        if self.cast_on:
            return FilterResultField(f"cast({self.source}, '{self.cast_on}') {operand} '{other}'")
        else:
            return FilterResultField(f"{self.source} {operand} '{other}'")

    def __getitem__(self, item: int | slice):
        """1c analog of substring"""
        if isinstance(item, int):
            return StringField(f"substring({self.source}, {item}, {item})", self.cast_on)
        elif isinstance(item, slice):
            if item.start:
                start = item.start
            else:
                start = 0
            if item.stop:
                return StringField(f"substring({self.source}, {start+1}, {item.stop})", self.cast_on)
            else:
                return StringField(f"substring({self.source}, {start+1})", self.cast_on)
        else:
            raise TypeError(f'item in block quotes should be int or slice, not {type(item)}')

    def __add__(self, other: str | Field):
        if isinstance(other, str):
            return StringField(f"concat({self.source}, '{other}')", self.cast_on)
        if issubclass(type(other), Field):
            return StringField(f"concat({self.source}, {other})", self.cast_on)
        else:
            raise TypeError(f"cant concatenate {type(other)} with StringField, use FieldType or str")

    def __radd__(self, other: str | Field):
        if isinstance(other, str):
            return StringField(f"concat('{other}', {self.source})", self.cast_on)
        if issubclass(type(other), Field):
            return StringField(f"concat({other}, {self.source})", self.cast_on)
        else:
            raise TypeError(f"cant concatenate {type(other)} with StringField, use FieldType or str")

    # ref
    def substringof(self, item: str) -> FilterResultField:
        """1c analog of substringof"""
        return FilterResultField(f"substringof('{item}', {self.source})")

    # ref
    def startswith(self, item: str) -> FilterResultField:
        return FilterResultField(f"startswith({self.source}, '{item}')")

    # ref
    def endswith(self, item: str) -> FilterResultField:
        return FilterResultField(f"endswith({self.source}, '{item}')")

    def like(self, template: str):
        return FilterResultField(f"like({self.source}, '{template}')")


class DateTimeField(Field):
    validate_function = datetime.strptime

    def __init__(
            self,
            source: str,
            cast_on: str | None = None,
            dt_format: str = DATETIME_FORMAT,
            select: bool = True,
            validators: List[Callable] | None = None,
            null: bool = False
    ):
        super().__init__(source, cast_on, select, validators, null)
        self.dt_format = dt_format

    def __cast_compare_value_to_string(self, other: str | float | datetime) -> str:
        if isinstance(other, str):
            datetime.strptime(other, self.dt_format)
            return other
        elif isinstance(other, datetime):
            return datetime.strftime(other, self.dt_format)
        elif isinstance(other, float):
            dt = datetime.fromtimestamp(other)
            return datetime.strftime(dt, self.dt_format)
        else:
            raise TypeError('value to compare should be formatted str, float timestamp or datetime object')

    def _build_result_field(self, other, operand) -> FilterResultField:
        if self.cast_on:
            return FilterResultField(f"cast({self.source}) {operand} datetime'{other}'")
        else:
            return FilterResultField(f"{self.source} {operand} datetime'{other}'")

    def field_mapper(self, date_string):
        return self.validate_function(date_string, self.dt_format)

    def __eq__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'eq')

    def __ne__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'ne')

    def __lt__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'lt')

    def __le__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'le')

    def __ge__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'ge')

    def __gt__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'gt')

    def year(self) -> IntegerField:
        return IntegerField(f"year({self.source})")

    def quarter(self) -> IntegerField:
        return IntegerField(f"quarter({self.source})")

    def month(self) -> IntegerField:
        return IntegerField(f"month({self.source})")

    def day(self) -> IntegerField:
        return IntegerField(f"day({self.source})")

    def hour(self) -> IntegerField:
        return IntegerField(f"hour({self.source})")

    def minute(self) -> IntegerField:
        return IntegerField(f"minute({self.source})")

    def second(self) -> IntegerField:
        return IntegerField(f"second({self.source})")

    def date_difference(self, other, dt_type: str) -> StringField:
        return StringField(f"datedifference({self.source}, {other}, '{dt_type}')")

    def date_add(self, other: int, dt_type) -> StringField:
        return StringField(f"datedifference({self.source}, {dt_type}, '{other}')")

    def day_of_week(self) -> StringField:
        return StringField(f"dayofweek({self.source})")

    def day_of_year(self) -> StringField:
        return StringField(f"dayofyear({self.source})")


class GUIDField(StringField):

    def _build_result_field(self, other, operand) -> FilterResultField:
        if self.cast_on:
            return FilterResultField(f"cast({self.source}) {operand} guid'{other}'")
        else:
            return FilterResultField(f"{self.source} {operand} guid'{other}'")
