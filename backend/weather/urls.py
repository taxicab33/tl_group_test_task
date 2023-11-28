from django.urls import path

from weather.views import CityWeatherRetrieveAPIView

CITY_WEATHER_URL = 'get-city-weather'

urlpatterns = [
    path(
        'weather',
        CityWeatherRetrieveAPIView.as_view(),
        name=CITY_WEATHER_URL
    )
]
