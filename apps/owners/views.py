from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers, services
from .dtos import OwnerTokens
from .permissions import *


class LoginOwnerView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        login_request = serializers.OwnerLoginRequestSerializer(data=self.request.data)
        if login_request.is_valid():
            if login_request.is_valid():
                result = services.authenticate_owner(login_request.validated_data)
                if isinstance(result, OwnerTokens):
                    response = serializers.OwnerTokensSerializer(result)
                    return Response(data=response.data, status=status.HTTP_200_OK)
                else:
                    return Response(data={'detail': 'Confirmation code sent successfully'},
                                    status=status.HTTP_201_CREATED)
        raise ValidationError(login_request.errors)


class SetupOwnerProfileView(APIView):

    def post(self, _request, *args, **kwargs):
        request_body = serializers.SetupOwnerProfileRequestSerializer(data=self.request.data)
        if request_body.is_valid():
            services.setup_owner_profile(self.request.user, request_body.validated_data)
            return Response({'details': "Your account has been created successfully"})
        raise ValidationError(detail=request_body.errors)


class ManageProfileView(APIView):
    permission_classes = [IsProfileOwner]

    @extend_schema(
        summary='Get owner profile information',
        tags=['Owner']
    )
    def get(self, request, *args, **kwargs):

        pass


    @extend_schema(
        summary='Update profile information',
        tags=['Owner']
    )
    def put(self, request, *args, **kwargs):
        pass
