from rest_framework.exceptions import NotFound, ValidationError


class CityNotFoundException(NotFound):
    default_detail = 'Такого города не существует'


class CityWasNotProvidedException(ValidationError):
    default_detail = 'Название города не было предоставлено'
