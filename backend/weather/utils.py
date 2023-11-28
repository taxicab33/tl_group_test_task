import requests
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from weather.exceptions import CityNotFoundException
from django.core.cache import cache
from backend.settings import (
    YANDEX_GEOCODER_API_KEY,
    YANDEX_WEATHER_API_KEY
)


class CityWeatherGetter:

    def __init__(self, city):
        self.city = city

    def __str__(self):
        return self.city

    def __get_cached_city_cords(self) -> dict:
        return cache.get(f'{self.city}_cords')

    def __cache_city_cords(self, value: dict) -> None:
        cache.set(f'{self.city}_cords', value=value)

    def _get_coordinates(self) -> dict:
        cached_cords = self.__get_cached_city_cords()
        if cached_cords:
            return cached_cords
        base_url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": YANDEX_GEOCODER_API_KEY,
            "format": "json",
            "geocode": self.city,
        }

        response = requests.get(base_url, params=params)
        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise CityNotFoundException
        data = response.json()

        response = data.pop('response', None)
        geo_object_collection = response.pop('GeoObjectCollection', None) if response else None
        feature_member = geo_object_collection.pop('featureMember', None) if geo_object_collection else None
        geo_object = feature_member[0].pop('GeoObject', None) \
            if feature_member and isinstance(feature_member, list) else None
        if not geo_object:
            raise CityNotFoundException
        point = geo_object.pop('Point', None) if geo_object else None
        pos = point.pop('pos', None) if point else None

        longitude, latitude = map(float, pos.split())
        data = {
            'lon': longitude,
            'lat': latitude
        }
        self.__cache_city_cords(data)
        return data

    def __get_cached_city_weather(self) -> dict:
        return cache.get(f'{self.city}_weather')

    def __cache_city_weather(self, value: dict, timeout: int = None) -> None:
        """Кэшируем данные о погоде в городе на 30 минут"""
        if not timeout:
            timeout = 60 * 30
        cache.set(f'{self.city}_weather', value=value, timeout=timeout)

    def get_weather(self) -> dict:
        base_url = "https://api.weather.yandex.ru/v2/informers"
        headers = {
            "X-Yandex-API-Key": YANDEX_WEATHER_API_KEY,
        }
        weather = self.__get_cached_city_weather()
        if weather:
            return weather
        cords = self._get_coordinates()
        lat = cords.get('lat', None)
        lon = cords.get('lon', None)
        response = requests.get(
            f"{base_url}?lat={lat}&lon={lon}&lang=ru_RU",
            headers=headers
        )
        match response.status_code:
            case status.HTTP_200_OK:
                data = response.json()
                fact = data.pop('fact', None)
                display_data = {
                    'temp': fact.get('temp', None),
                    'pressure_mm': fact.get('pressure_mm', None),
                    'wind_speed': fact.get('wind_speed', None)
                }
                self.__cache_city_weather(value=display_data)
                return display_data
            case status.HTTP_403_FORBIDDEN:
                raise PermissionDenied

