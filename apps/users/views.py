from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from . import services
from .models import Activation
from .serializers import *


class IsEmailExistView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication'],
        summary='Check email existence',
        request=serializers.EmailSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "msg": "This email is already exist",
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "msg": "This email does not exist",
                }
            },
            403: {
                "type": "object",
                "properties": {
                    "msg": "Invalid information",
                }
            }
        }
    )
    def post(self, request):
        email_request = serializers.EmailSerializer(data=self.request.data)
        if email_request.is_valid():
            if services.is_email_exists(email_request.data):
                return Response(data={'msg': 'This email already exists'}, status=status.HTTP_200_OK)
            else:
                return Response(data={'msg': 'This email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        raise ValidationError(email_request.errors)


class LoginGuestView(APIView):
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        tags=['Guests'],
        summary='Login a guest',
        request=GuestLoginRequestSerializer
    )
    def post(self, request: Request):
        login_request = serializers.GuestLoginRequestSerializer(data=self.request.data)
        if login_request.is_valid():
            result = services.authenticate_guest(login_request.data)
            if isinstance(result, dict):
                tokens_serializer = TokensSerializer(result)
                return Response(data=tokens_serializer.data, status=status.HTTP_200_OK)
            elif isinstance(result, int):
                return Response(data={'token': result}, status=status.HTTP_201_CREATED)
            else:
                raise AuthenticationFailed(detail="Authentication failed , invalid information")
        else:
            raise ValidationError(login_request.errors)


class SignupGuestView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Guests'],
        request=GuestSignupRequestSerializer,
        responses={201: {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
            }
        }},
        summary='Signup for guests'
    )
    def post(self, request: Request):
        signup_request = GuestSignupRequestSerializer(data=request.data)
        if signup_request.is_valid():
            token = services.register_new_user(signup_request.validated_data)
            return Response(data={'token': token}, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError(signup_request.errors)


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
            created = services.setup_guest_profile_for_existing_user(self.request.user, profile_request.validated_data)
            if created:
                return Response(data={'detail': 'Your profile has been created successfully'},
                                status=status.HTTP_200_OK)
            else:
                raise ValidationError({'detail': 'You have already an existing profile *__*'})
        raise ValidationError(profile_request.errors)


class ConfirmationView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication'],
        summary='Account confirmation',
        description='Post the confirmation code with the provided UUID Token',
        request=serializers.ConfirmationRequestSerializer,
        responses={200: TokensSerializer}
    )
    def post(self, request):
        confirmation_request = ConfirmationRequestSerializer(data=self.request.data)
        if confirmation_request.is_valid():
            tokens = services.activate_user(confirmation_request.validated_data)
            serialized_tokens = TokensSerializer(tokens)
            return Response(data=serialized_tokens.data, status=status.HTTP_200_OK)
        raise ValidationError(detail=confirmation_request.errors)


class ResendConfirmationView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Guests'],
        summary='Resend Confirmation code',
        description='Use this endpoint to resend a confirmation code to the user again , provide the last UUID Token '
                    'which comes lastly',
        request=ResendConfirmationRequestSerializer,
        responses={201: {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
            }
        }}
    )
    def post(self, request):
        resend_request = ResendConfirmationRequestSerializer(data=request.data)
        if resend_request.is_valid():
            token = services.resend_confirmation_code(resend_request.validated_data)
            return Response(data={'token': token}, status=status.HTTP_200_OK)
        raise ValidationError(detail=resend_request.errors)
