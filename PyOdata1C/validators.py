class BaseValidator:

    def __init__(self, message=None, ):
        if message is None:
            message = 'Ошибка валидации'
        self.message = message


class MaxValueValidator(BaseValidator):

    def compare(self, a, b):
        return a > b


class MinValueValidator(BaseValidator):

    def compare(self, a, b):
        return a < b
