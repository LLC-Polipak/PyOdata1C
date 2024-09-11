class Base1cError(Exception):
    code: int | None = None
    text: str | None = None

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = self.text

    def __str__(self):
        return f'Код ошибки: {self.code}, описание: {self.message}'


class NotSupported(Base1cError):
    code = 0
    text = 'Возможность не поддерживается'


class CantParseString(Base1cError):
    code = 1
    text = 'Не удалось разобрать строку'


class InvalidRequestFormat(Base1cError):
    code = 2
    text = 'Неверный формат запроса'


class ViewTypeNotSupported(Base1cError):
    code = 3
    text = 'Запрошенный тип представления не поддерживается'


class InvalidPropertyValue(Base1cError):
    code = 4
    text = 'Неверное значение свойства'


class MissingRequiredField(Base1cError):
    code = 5
    text = 'Отсутствует обязательное значение свойства'


class InvalidUrl(Base1cError):
    code = 6
    text = 'Неверный URL'


class MissingEntityKey(Base1cError):
    code = 7
    text = 'Не хватает элемента ключа сущности'


class EntityTypeDoesNotExist(Base1cError):
    code = 8
    text = 'Тип сущности не найден'


class ObjectDoesNotExist(Base1cError):
    code = 9
    text = 'Экземпляр сущности не найден'


class PropertyDoesNotExist(Base1cError):
    code = 10
    text = 'Запрошенное свойство не найдено'


class MethodNotFound(Base1cError):
    code = 11
    text = 'Метод не найден'


class MissingRequiredArgument(Base1cError):
    code = 12
    text = 'Отсутствует обязательный аргумент метода'


class CreatingRowsDirectlyNotSupported(Base1cError):
    code = 13
    text = 'Создание строк табличных частей напрямую не поддерживается'


class ParseRequestOptionsError(Base1cError):
    code = 14
    text = 'Ошибка разбора опций запроса'


class EntityKeyError(Base1cError):
    code = 15
    text = 'Сущность с таким ключом уже существует'


class PropertyNotAssigned(Base1cError):
    code = 16
    text = 'Не удалось присвоить свойство'


class ObjectDoesNotSupportLoad(Base1cError):
    code = 17
    text = 'Объект не поддерживает режим загрузки данных'


class OdataInitializationFailed(Base1cError):
    code = 18
    text = ('Ошибка инициализации интерфейса OData:'
            'в объекте есть свойства с одинаковыми именами')


class HttpForbidden(Base1cError):
    code = 19
    text = 'Использованный HTTP-метод запрещен в данном контексте'


class PermissionDenied(Base1cError):
    code = 20
    text = '''
    Ошибка прав доступа. Может возникать:
    ● Когда у пользователя нет прав на запрошенное действие над данным объектом
    ● Когда в выборку попадает объект, недоступный в связи с ограничением
    доступа к данным и параметр allowedOnly не используется.
    '''


class FunctionNotImplemented(Base1cError):
    code = 21
    text = '''Вызов нереализованной функции.
Указание неверного количества аргументов функции.
Попытка передачи аргумента неверного типа.
Указание нереализованной лямбда-функции.
    '''


exception_mapper = {
    0: NotSupported,
    1: CantParseString,
    2: InvalidRequestFormat,
    3: ViewTypeNotSupported,
    4: InvalidPropertyValue,
    5: MissingRequiredField,
    6: InvalidUrl,
    7: MissingEntityKey,
    8: EntityTypeDoesNotExist,
    9: ObjectDoesNotExist,
    10: PropertyDoesNotExist,
    11: MethodNotFound,
    12: MissingRequiredArgument,
    13: CreatingRowsDirectlyNotSupported,
    14: ParseRequestOptionsError,
    15: EntityKeyError,
    16: PropertyNotAssigned,
    17: ObjectDoesNotSupportLoad,
    18: OdataInitializationFailed,
    19: HttpForbidden,
    20: PermissionDenied,
    21: FunctionNotImplemented
}


def throw_exception(data: dict):
    raise exception_mapper[data['odata.error']['code']]


class ValidationError(Exception):
    pass
