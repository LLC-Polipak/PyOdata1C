from datetime import datetime


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

    def __str__(self):
        return self.result


class Field:
    source: str
    expand: str | None = None
    cast: bool = False
    cast_on: str | None = None

    def __init__(self, source: str, cast: bool = False, cast_on: str | None = None):
        self.source = source
        if DELIMITER in source:
            self.expand = '/'.join(source.split(DELIMITER)[:-1])
        if cast:
            if cast_on is None:
                raise TypeError("If cast == True then cast_on can't be None")
            self.cast = cast
            self.cast_on = cast_on

    def _build_result_field(self, other, operand) -> FilterResultField:
        if self.cast:
            return FilterResultField(f"cast({self.source}, '{self.cast_on}') {operand} {other}")
        else:
            return FilterResultField(f"{self.source} {operand} {other}")

    def __eq__(self, other: int) -> FilterResultField:
        return self._build_result_field(other, 'eq')

    def __ne__(self, other: int) -> FilterResultField:
        return self._build_result_field(other, 'ne')

    def __lt__(self, other: int) -> FilterResultField:
        return self._build_result_field(other, 'lt')

    def __le__(self, other: int) -> FilterResultField:
        return self._build_result_field(other, 'le')

    def __ge__(self, other: int) -> FilterResultField:
        return self._build_result_field(other, 'ge')

    def __gt__(self, other: int) -> FilterResultField:
        return self._build_result_field(other, 'gt')

    def __str__(self):
        return self.source


a = Field('a', True, cast_on='da')
print(a.cast_on)


class IntegerField(Field):
    pass


class StringField(Field):

    def _build_result_field(self, other, operand) -> FilterResultField:
        if self.cast:
            return FilterResultField(f"cast({self.source}, '{self.cast_on}') {operand} '{other}'")
        else:
            return FilterResultField(f"{self.source} {operand} '{other}'")

    def __getitem__(self, item: int | slice):
        """1c analog of substring"""
        if isinstance(item, int):
            return StringField(f"substring({self.source}, {item}, {item})", self.cast, self.cast_on)
        elif isinstance(item, slice):
            if item.start:
                start = item.start
            else:
                start = 0
            if item.stop:
                return StringField(f"substring({self.source}, {start+1}, {item.stop})", self.cast, self.cast_on)
            else:
                return StringField(f"substring({self.source}, {start+1})", self.cast, self.cast_on)
        else:
            raise TypeError(f'item in block quotes should be int or slice, not {type(item)}')

    def __add__(self, other: str | Field):
        if isinstance(other, str):
            return StringField(f"concat({self.source}, '{other}')", self.cast, self.cast_on)
        if issubclass(type(other), Field):
            return StringField(f"concat({self.source}, {other})", self.cast, self.cast_on)
        else:
            raise TypeError(f"cant concatenate {type(other)} with StringField, use FieldType or str")

    def __radd__(self, other: str | Field):
        if isinstance(other, str):
            return StringField(f"concat('{other}', {self.source})", self.cast, self.cast_on)
        if issubclass(type(other), Field):
            return StringField(f"concat({other}, {self.source})", self.cast, self.cast_on)
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

    def __init__(self, source: str, cast: bool = False, cast_on: str | None = None, dt_format: str = DATETIME_FORMAT):
        super().__init__(source, cast, cast_on)
        self.dt_format = dt_format

    @staticmethod
    def __validate_compare_value(other: str):
        datetime.strptime(other, DATETIME_FORMAT)
        return True

    def __cast_compare_value_to_string(self, other: str | float | datetime) -> str:
        if isinstance(other, str):
            if self.__validate_compare_value(other):
                return other
        elif isinstance(other, datetime):
            return datetime.strftime(other, self.dt_format)
        elif isinstance(other, float):
            dt = datetime.fromtimestamp(other)
            return datetime.strftime(dt, self.dt_format)
        else:
            raise TypeError('value to compare should be formatted str, float timestamp or datetime object')

    def _build_result_field(self, other, operand) -> FilterResultField:
        if self.cast:
            return FilterResultField(f"cast({self.source}) {operand} datetime'{other}'")
        else:
            return FilterResultField(f"{self.source} {operand} datetime'{other}'")

    def __eq__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'eq')

    def __ne__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'eq')

    def __lt__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'eq')

    def __le__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'eq')

    def __ge__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'eq')

    def __gt__(self, other: str | float | datetime) -> FilterResultField:
        value = self.__cast_compare_value_to_string(other)
        return self._build_result_field(value, 'eq')

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
        if self.cast:
            return FilterResultField(f"cast({self.source}) {operand} guid'{other}'")
        else:
            return FilterResultField(f"{self.source} {operand} guid'{other}'")
