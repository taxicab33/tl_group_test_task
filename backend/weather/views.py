from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from weather.exceptions import CityWasNotProvidedException
from weather.clients import yandex_weather_client


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="city",
            type=str,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Название города",
        )
    ],
)
class CityWeatherRetrieveAPIView(GenericAPIView):
    permission_classes = (AllowAny, )

    def get(self, *args, **kwargs):
        city_name = self.request.query_params.get("city", None)
        if not city_name:
            raise CityWasNotProvidedException
        weather = yandex_weather_client.get_weather(city_name=city_name)
        return Response(data=weather)
