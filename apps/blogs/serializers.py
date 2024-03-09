from rest_framework import serializers as rest_serializers

from .models import Blog


class BlogSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'
