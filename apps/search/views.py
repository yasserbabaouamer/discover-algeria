from builtins import KeyError

from django.shortcuts import render
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

    def get(self, request):
        try:
            keyword = self.request.query_params['keyword']
            search_type = str(self.request.query_params['type'])
            if len(keyword) < 3:
                raise ValidationError({'detail': 'You have to provide at least a keyword with three characters'})
            print(search_type)
            if search_type not in iter(SearchType):
                raise ValidationError({'detail': 'Invalid search type , see the docs for more details'})
            result = []
            if search_type == SearchType.ALL:
                result = services.do_quick_search(keyword)[:10]
            elif search_type == SearchType.HOTELS:
                result = services.do_quick_search_hotels(keyword)[:10]
            elif search_type == SearchType.TOURS:
                result = services.do_quick_search_tours(keyword)[:10]
            response = serializers.SearchItemSerializer(result, many=True)
            return Response(data=response.data, status=status.HTTP_200_OK)
        except KeyError as e:
            raise ValidationError({'detail': 'Invalid URL parameters , '
                                             'follow this pattern : ?keyword=value&type=value '})


class DetailedSearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, _request):
        request = serializers.GeneralSearchSerializer(data=self.request.data)
        if request.is_valid():
            search_results = services.do_advanced_search(request.validated_data)
        raise ValidationError(request.errors)
