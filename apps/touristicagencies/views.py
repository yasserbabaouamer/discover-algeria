from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from . import services, serializers


class GetTopTours(ListAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = services.get_top_tours()
    serializer_class = serializers.TourSerializer

    @extend_schema(
        tags=['Touristic Agencies'],
        summary='Get top tours in Algeria',
        responses=serializers.TourSerializer
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
