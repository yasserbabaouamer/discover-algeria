from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from . import services as guest_services
from .serializers import *


class LoginGuestView(APIView):
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        tags=['Guests'],
        summary='Login a guest',
        request=GuestLoginRequestSerializer,
        responses={
            200: OpenApiResponse(response=TokensSerializer),
            201: OpenApiResponse(description='Inactivated account , Confirmation code sent to the user email')
        }
    )
    def post(self, request: Request):
        login_request = serializers.GuestLoginRequestSerializer(data=self.request.data)
        if login_request.is_valid():
            result = guest_services.authenticate_guest(login_request.validated_data)
            if isinstance(result, dict):
                tokens_serializer = TokensSerializer(result)
                return Response(data=tokens_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(data={'detail': 'Confirmation code sent successfully'}, status=status.HTTP_201_CREATED)

        raise ValidationError(login_request.errors)


class SetupGuestProfileForExistingUser(APIView):
    parser_classes = [MultiPartParser]

    @extend_schema(
        tags=['Guests'],
        summary='Quick profile setup',
        request=QuickProfileRequestSerializer
    )
    def post(self, request):
        profile_request = serializers.QuickProfileRequestSerializer(data=self.request.data)
        if profile_request.is_valid():
            created = guest_services.setup_guest_profile(self.request.user,
                                                         profile_request.validated_data)
            if created:
                return Response(data={'detail': 'Your profile has been created successfully'},
                                status=status.HTTP_200_OK)
            else:
                raise ValidationError({'detail': 'You have already an existing profile *__*'})
        raise ValidationError(profile_request.errors)
