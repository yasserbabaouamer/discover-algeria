from builtins import KeyError

from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers, services
from .serializers import SearchItemSerializer


# Create your views here.


class QuickSearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            keyword = self.request.query_params['keyword']
            result = services.do_quick_search(keyword)[:10]
            response = SearchItemSerializer(result, many=True)
            return Response(data=response.data, status=status.HTTP_200_OK)
        except KeyError as e:
            raise ValidationError({'detail': 'Keyword not found'})
