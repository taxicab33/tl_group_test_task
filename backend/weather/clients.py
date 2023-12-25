import requests
from django.core.cache import cache
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from backend.settings import YANDEX_GEOCODER_API_KEY, YANDEX_WEATHER_API_KEY
from weather.exceptions import CityNotFoundException


class YandexGeocoderClient:

    def __init__(
            self,
            geocoder_api_key
    ):
        self._geocoder_api_key = geocoder_api_key

    @staticmethod
    def _get_cached_city_cords(city_name: str) -> dict:
        return cache.get(f"{city_name}_cords")

    @staticmethod
    def _cache_city_cords(city_name, value: dict) -> None:
        cache.set(f"{city_name}_cords", value=value)

    def get_coordinates(self, city_name: str) -> dict:
        cached_cords = self._get_cached_city_cords(city_name)
        if cached_cords:
            return cached_cords
        base_url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": self._geocoder_api_key,
            "format": "json",
            "geocode": city_name,
        }

        response = requests.get(base_url, params=params)
        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise CityNotFoundException
        data = response.json()

        response = data.get("response", None)
        geo_object_collection = (
            response.get("GeoObjectCollection", None) if response else None
        )
        feature_member = (
            geo_object_collection.get("featureMember", None)
            if geo_object_collection
            else None
        )
        geo_object = (
            feature_member[0].get("GeoObject", None)
            if feature_member and isinstance(feature_member, list)
            else None
        )
        if not geo_object:
            raise CityNotFoundException
        point = geo_object.get("Point", None) if geo_object else None
        pos = point.get("pos", None) if point else None

        longitude, latitude = map(float, pos.split())
        data = {"lon": longitude, "lat": latitude}
        self._cache_city_cords(city_name=city_name, value=data)
        return data


class YandexWeatherClient:
    def __init__(
            self,
            weather_api_key
    ):
        self._weather_api_key = weather_api_key

    @staticmethod
    def _get_cached_city_weather(city_name: str) -> dict:
        return cache.get(f"{city_name}_weather")

    @staticmethod
    def _cache_city_weather(city_name, value: dict, timeout: int = None) -> None:
        """Кэшируем данные о погоде в городе на 30 минут"""
        if not timeout:
            timeout = 60 * 30
        cache.set(f"{city_name}_weather", value=value, timeout=timeout)

    def get_weather(self, city_name: str) -> dict:
        base_url = "https://api.weather.yandex.ru/v2/informers"
        headers = {
            "X-Yandex-API-Key": self._weather_api_key,
        }
        weather = self._get_cached_city_weather(city_name=city_name)
        if weather:
            return weather
        cords = yandex_geocoder_client.get_coordinates(city_name=city_name)
        lat = cords.get("lat", None)
        lon = cords.get("lon", None)
        response = requests.get(
            f"{base_url}?lat={lat}&lon={lon}&lang=ru_RU", headers=headers
        )
        match response.status_code:
            case status.HTTP_200_OK:
                data = response.json()
                fact = data.pop("fact", None)
                display_data = {
                    "temp": fact.get("temp", None),
                    "pressure_mm": fact.get("pressure_mm", None),
                    "wind_speed": fact.get("wind_speed", None),
                }
                self._cache_city_weather(value=display_data, city_name=city_name)
                return display_data
            case status.HTTP_403_FORBIDDEN:
                raise PermissionDenied


yandex_geocoder_client = YandexGeocoderClient(
    geocoder_api_key=YANDEX_GEOCODER_API_KEY,
)
yandex_weather_client = YandexWeatherClient(
    weather_api_key=YANDEX_WEATHER_API_KEY
)
