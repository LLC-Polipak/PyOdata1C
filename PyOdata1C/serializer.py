from typing import List

from PyOdata1C.fields import Field, DELIMITER


class Serializer:
    path: str | None = None
    _data: dict = {}
    _fields: list = []

    def __init__(self, **kwargs):
        self.__dict__['_fields'] = self._get_fields_for_props()
        for kwarg in kwargs.keys():
            if kwarg not in self._fields:
                raise AttributeError(
                    f"'{self.__class__.__name__}' object has no attribute '{kwarg}'")
        self.__dict__['_data'] = kwargs

    def __setattr__(self, key, value):
        if key in self._fields:
            self._data[key] = value
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __getattribute__(self, item):
        if item in object.__getattribute__(self, '_fields') and item != 'data':
            return self.__getattr__(item)
        return super().__getattribute__(item)

    def __getattr__(self, item):
        if item in self._fields:
            return self._data[item]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __delattr__(self, item):
        if item in self._fields:
            del self._data[item]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __iter__(self):
        for key in self._data:
            yield key, self._data[key]

    @property
    def data(self):
        return self._data

    @classmethod
    def _get_fields_for_props(cls):
        return list(filter(lambda x: not x.startswith('_'), dir(cls)))

    @classmethod
    def _get_selected_fields_str(cls) -> List[str]:
        return list(filter(lambda x: getattr(cls, x).select, dict(filter(
            lambda x: issubclass(type(x[1]), Field),
            cls.__dict__.items())).keys()))

    @classmethod
    def _get_fields(cls) -> list[Field]:
        return [getattr(cls, field) for field in dict(filter(
            lambda x: issubclass(type(x[1]), Field),
            cls.__dict__.items())).keys()]

    @classmethod
    def get_expand(cls) -> list[str]:
        return [field.expand for field in cls._get_fields()
                if field.expand is not None]

    @classmethod
    def get_select(cls) -> list[str]:
        return [field.source for field in cls._get_fields() if field.select]

    @classmethod
    def validate(cls, data: dict):
        new_data = {}
        for str_field in cls._get_selected_fields_str():
            field = getattr(cls, str_field)
            if field.expand:
                obj = data
                for x in field.source.split(DELIMITER):
                    try:
                        obj = obj.get(x)
                    except AttributeError:
                        break
            else:
                obj = data[field.source]
            new_data[str_field] = field.deserialize(obj)
            field.validate(new_data[str_field])
        return cls(**new_data)

    @classmethod
    def deserialize(cls, data, many=False):
        if cls._fields is None:
            cls._fields = cls._get_fields_for_props()
        validated_data = []
        if many:
            for obj in data:
                validated_data.append(cls.validate(obj))
        else:
            return cls.validate(data)
        return validated_data

    @classmethod
    def serialize(cls, obj) -> dict:
        if cls._fields is None:
            cls._fields = cls._get_fields_for_props()
        data = {}
        for str_field in cls._get_selected_fields_str():
            field = getattr(cls, str_field)
            data[field.source] = field.serialize(getattr(obj, str_field))
        return data



