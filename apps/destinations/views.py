from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from . import services, serializers


# Create your views here.


class TopDestinationsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self,request):
        cities = services.get_top_destinations()
        cities_serializer = serializers.DestinationSerializer(cities, many=True)
        return Response(data=cities_serializer.data, status=status.HTTP_200_OK)
