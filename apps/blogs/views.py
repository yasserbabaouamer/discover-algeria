from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from . import serializers, services


class GetRecentlyAddedBlogs(ListAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = services.get_some_blogs()
    serializer_class = serializers.BlogSerializer

    @extend_schema(
        tags=['Blogs'],
        summary='Get Recently Added Blogs',
        responses=serializers.BlogSerializer
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
