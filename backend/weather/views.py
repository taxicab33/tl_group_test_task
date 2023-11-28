from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from weather.exceptions import CityWasNotProvidedException
from weather.utils import CityWeatherGetter


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='city',
            type=str,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Название города'
        )
    ],
)
class CityWeatherRetrieveAPIView(GenericAPIView):

    def get(self, *args, **kwargs):
        city_name = self.request.query_params.get('city', None)
        if not city_name:
            raise CityWasNotProvidedException
        city = CityWeatherGetter(city_name)
        weather = city.get_weather()
        return Response(data=weather)
