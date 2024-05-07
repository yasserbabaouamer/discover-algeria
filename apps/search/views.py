from builtins import KeyError

from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers, services
from apps.destinations import services as destination_services
from .serializers import SearchItemSerializer
from .utils import SearchType


# Create your views here.


class QuickSearchView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Search'],
        responses={
            200: OpenApiResponse(response=serializers.SearchItemSerializer),
            400: 'Invalid parameters - either missing or invalid fields -'
        }
    )
    def get(self, request):
        keyword = self.request.query_params.get('q', None)
        search_type = self.request.query_params.get('type', None)
        if keyword is None or search_type is None:
            raise ValidationError({'detail': 'Missing query parameters: q or type'})
        if len(keyword) < 3:
            raise ValidationError({'detail': 'You have to provide at least a keyword with three characters'})
        if search_type not in iter(SearchType):
            raise ValidationError({'detail': 'Invalid search type, see the docs for more details'})
        result = []
        if search_type == SearchType.ALL:
            result = services.do_quick_search(keyword)[:10]
        elif search_type == SearchType.HOTELS:
            result = services.do_quick_search_hotels(keyword)[:10]
        elif search_type == SearchType.TOURS:
            result = services.do_quick_search_tours(keyword)[:10]
        elif search_type == SearchType.DESTINATIONS:
            result = services.do_quick_search_cities(keyword)[:10]
        response = serializers.SearchItemSerializer(result, many=True)
        return Response(data=response.data, status=status.HTTP_200_OK)
