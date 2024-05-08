from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from . import services
from .dtos import GuestTokens
from ..hotels.permissions import IsGuest


class LoginGuestView(APIView):
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        tags=['Guests'],
        summary='Login a guest',
        request=serializers.GuestLoginRequestSerializer,
        responses={
            200: OpenApiResponse(response=serializers.GuestTokensSerializer),
            201: OpenApiResponse(description='Confirmation code sent to the user email'),
            400: OpenApiResponse(description='Invalid information')
        }
    )
    def post(self, request: Request):
        login_request = serializers.GuestLoginRequestSerializer(data=self.request.data)
        if login_request.is_valid():
            result = services.authenticate_guest(login_request.validated_data)
            if isinstance(result, GuestTokens):
                tokens_serializer = serializers.GuestTokensSerializer(result)
                return Response(data=tokens_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(data={'detail': 'Confirmation code sent successfully'}, status=status.HTTP_201_CREATED)

        raise ValidationError(login_request.errors)


class SetupGuestProfileForExistingUser(APIView):
    parser_classes = [MultiPartParser]

    @extend_schema(
        tags=['Guests'],
        summary='Quick profile setup',
        request=serializers.QuickProfileRequestSerializer,
        responses={
            201: OpenApiResponse(description='Your account has been created successfully'),
            400: OpenApiResponse(description='Invalid information')
        }
    )
    def post(self, request):
        profile_request = serializers.QuickProfileRequestSerializer(data=self.request.data)
        if profile_request.is_valid():
            created = services.setup_guest_profile(self.request.user,
                                                   profile_request.validated_data)
            if created:
                return Response(data={'detail': 'Your profile has been created successfully'},
                                status=status.HTTP_201_CREATED)
            else:
                raise ValidationError({'detail': 'You have already an existing profile *__*'})
        raise ValidationError(profile_request.errors)


class GetEssentialGuestInfo(APIView):
    permission_classes = [IsGuest]

    @extend_schema(
        tags=['Guests'],
        summary='Get Essential Guest Information',
        responses={
            200: OpenApiResponse(response=serializers.EssentialGuestInfoSerializer),
            403: OpenApiResponse(description="You don't have the permission because you don't have a guest account")
        }
    )
    def get(self, request, *args, **kwargs):
        guest = services.find_guest_by_id(self.request.user.guest.id)
        response = serializers.EssentialGuestInfoSerializer(guest)
        return Response(response.data, status=status.HTTP_200_OK)


class ManageMyGuestProfile(APIView):
    permission_classes = [IsGuest]

    @extend_schema(
        tags=['Guests'],
        summary='Get Guest Profile Information',
    )
    def get(self, request, *args, **kwargs):
        pass

    @extend_schema(
        tags=['Guests'],
        summary='Update Profile Information'
    )
    def put(self, request, *args, **kwargs):
        pass
