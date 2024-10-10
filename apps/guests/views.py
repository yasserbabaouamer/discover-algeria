import stripe
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import CustomException
from . import serializers
from . import services
from .dtos import GuestTokens
from .models import Guest
from ..hotels.permissions import IsGuestOrAdmin
from ..users.permissions import IsAdmin


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
        if not login_request.is_valid():
            raise ValidationError(login_request.errors)
        result = services.authenticate_guest(login_request.validated_data)
        if isinstance(result, GuestTokens):
            tokens_serializer = serializers.GuestTokensSerializer(result)
            return Response(data=tokens_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data={'detail': 'Confirmation code sent successfully'}, status=status.HTTP_201_CREATED)



class SetupGuestProfileForExistingUser(APIView):
    parser_classes = [MultiPartParser]

    @extend_schema(
        tags=['Guests'],
        summary='Quick profile setup',
        request=serializers.QuickProfileRequestSerializer,
        responses={
            201: OpenApiResponse(description='Your account has been created successfully'),
            400: OpenApiResponse(description='Invalid information'),
            409: OpenApiResponse(description='You have already a guest account'),
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
                raise CustomException({'detail': 'You have already an existing profile *__*'},
                                      status=status.HTTP_409_CONFLICT)
        raise ValidationError(profile_request.errors)


class GetEssentialGuestInfo(APIView):
    permission_classes = [IsGuestOrAdmin]

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
    permission_classes = [IsGuestOrAdmin]
    parser_classes = [MultiPartParser, JSONParser]

    @extend_schema(
        tags=['Guests', 'Admin'],
        summary='Get Guest Profile Information',
        responses={
            200: OpenApiResponse(response=serializers.ProfileSerializer,
                                 description='Send request to see the real response structure')
        }
    )
    def get(self, request, *args, **kwargs):
        guest_id = kwargs.pop('guest_id', None)
        if guest_id is None:
            raise ValidationError({'detail': 'Provide a guest_id'})
        guest = get_object_or_404(Guest, id=guest_id)
        self.check_object_permissions(request, guest)
        profile = services.find_guest_profile(guest_id)
        response = serializers.ProfileSerializer(profile)
        return Response(response.data)

    @extend_schema(
        tags=['Guests', 'Admin'],
        summary='Update Guest Profile Information',
        request=serializers.UpdateGuestFormSerializer,
        responses={
            100: OpenApiResponse(description="This is what to send in the request body",
                                 response=serializers.BaseGuestInfoSerializer),
            200: OpenApiResponse(description='The account has been updated successfully'),
            400: OpenApiResponse(description='Invalid arguments')
        }
    )
    def put(self, request, *args, **kwargs):
        guest_id = kwargs.pop('guest_id', None)
        if guest_id is None:
            raise ValidationError({'detail': 'Provide a guest_id'})
        update_guest_form = serializers.UpdateGuestFormSerializer(data=request.data)
        if not update_guest_form.is_valid():
            raise ValidationError(update_guest_form.errors)
        services.update_guest(guest_id, update_guest_form.validated_data)
        return Response({'detail': 'The account has been updated successfully'})


class ListCreateGuests(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=['Admin'],
        summary='Get list of guests',
        responses=serializers.GuestSerializer
    )
    def get(self, request, *args, **kwargs):
        guests = services.find_all_guests()
        response = serializers.GuestSerializer(guests, many=True)
        return Response(response.data)

    @extend_schema(
        tags=['Admin'],
        summary='Create new guest',
        responses={
            200: serializers.CreateGuestRequestSerializer,
            400: OpenApiResponse(description='Invalid or missing information'),
            409: OpenApiResponse(description='This email is already used by a guest account')
        })
    def post(self, _request, *args, **kwargs):
        request = serializers.CreateGuestRequestSerializer(data=self.request.data)
        if not request.is_valid():
            raise ValidationError(request.errors)
        services.create_guest(request.validated_data)
        return Response({'detail': "Guest has been created successfully"}, status=status.HTTP_201_CREATED)


class ManageGuestsView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=['Admin'],
        summary='Delete a guest',
    )
    def delete(self, request, *args, **kwargs):
        guest_id = kwargs.pop('guest_id', None)
        if guest_id is None:
            raise ValidationError({'detail': 'provide a guest id'})
        services.delete_guest(guest_id)
        return Response({'detail': 'The account has been deleted successfully'},
                        status=status.HTTP_204_NO_CONTENT)
