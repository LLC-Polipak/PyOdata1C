from typing import List

from PyOdata1C.fields import Field, DELIMITER


class Serializer:
    path: str | None = None
    _data: dict = {}

    def __init__(self, **kwargs):
        for kwarg in kwargs.keys():
            if kwarg not in self._get_fields_for_props():
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{kwarg}'")
        self._data = kwargs

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        elif key in self._get_fields_for_props():
            self._data[key] = value
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __getattribute__(self, item):
        if item in object.__getattribute__(self, '_get_fields_for_props')() and item != 'data':
            return self.__getattr__(item)
        return super().__getattribute__(item)

    def __getattr__(self, item):
        if item in self._get_fields_for_props():
            return self._data[item]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __delattr__(self, item):
        if item in self._get_fields_for_props():
            del self._data[item]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

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
            # тут нужно подкинуть валидатор
            if field.expand:
                obj = data
                for x in field.source.split(DELIMITER):
                    try:
                        obj = obj.get(x)
                    except AttributeError:
                        break
            else:
                obj = data[field.source]
            new_data[str_field] = field.field_mapper(obj)
        return cls(**new_data)
        # return Model(**new_data)

    @classmethod
    def deserialize(cls, data):
        validated_data = []
        for obj in data:
            validated_data.append(cls.validate(obj))
        return validated_data

    @classmethod
    def serialize(cls, obj) -> dict:
        data = {}
        for str_field in cls._get_selected_fields_str():
            field = getattr(obj, str_field)
            data[str_field] = field
        return data
