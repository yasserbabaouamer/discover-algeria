from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from . import services
from .models import ConfirmationCode
from .serializers import *


class IsEmailExistView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication'],
        summary='Check email existence',
        request=serializers.EmailSerializer,
        responses={
            200: OpenApiResponse(description="This email is already exist"),
            404: OpenApiResponse(description="This email does not exist"),
            403: OpenApiResponse(description="Invalid information")
        }
    )
    def post(self, request):
        email_request = serializers.EmailSerializer(data=self.request.data)
        if email_request.is_valid():
            if services.is_email_exists(email_request.data):
                return Response(data={'msg': 'This email already exists'}, status=status.HTTP_200_OK)
            else:
                return Response(data={'msg': 'This email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        raise ValidationError(email_request.errors)


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
            result = services.authenticate_guest(login_request.data)
            if isinstance(result, dict):
                tokens_serializer = TokensSerializer(result)
                return Response(data=tokens_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(data={'detail': 'Confirmation code sent successfully'}, status=status.HTTP_201_CREATED)

        raise ValidationError(login_request.errors)


class SignupGuestView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Guests'],
        request=GuestSignupRequestSerializer,
        responses={201: OpenApiResponse(description='Account Created , Confirmation code send to guest email')},
        summary='Signup for guests'
    )
    def post(self, request: Request):
        signup_request = GuestSignupRequestSerializer(data=request.data)
        if signup_request.is_valid():
            services.register_new_user(signup_request.validated_data)
            return Response(data={'detail': 'Confirmation code sent successfully'}, status=status.HTTP_201_CREATED)
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
        description='Post the confirmation code with the provided Token',
        request=serializers.ConfirmationCodeRequestSerializer,
        responses={200: TokensSerializer}
    )
    def post(self, request):
        confirmation_request = serializers.ConfirmationCodeRequestSerializer(data=self.request.data)
        if confirmation_request.is_valid():
            tokens = services.activate_user(confirmation_request.validated_data)
            serialized_tokens = TokensSerializer(tokens)
            return Response(data=serialized_tokens.data, status=status.HTTP_200_OK)
        raise ValidationError(detail=confirmation_request.errors)


class ResendConfirmationView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication'],
        summary='Resend Confirmation code',
        description='Use this endpoint to resend a confirmation code to the user again'
                    ', Provide the user email',
        request=EmailSerializer,
        responses={201: {
            "type": "object",
            "properties": {
                "detail": "confirmation code sent successfully",
            }
        }}
    )
    def post(self, _request):
        request = serializers.EmailSerializer(data=_request.data)
        if request.is_valid():
            services.resend_confirmation_code(request.validated_data)
            return Response(
                data={"detail": "confirmation code sent successfully"},
                status=status.HTTP_200_OK
            )
        raise ValidationError(detail=request.errors)


class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication'],
        summary='Reset Password 01',
        description='This endpoint is used ',
        request=serializers.EmailSerializer,
        responses={
            200: OpenApiResponse(description='Confirmation code sent successfully')
        }
    )
    def post(self, _request):
        request = serializers.EmailSerializer(data=_request.data)
        if request.is_valid():
            if not services.is_email_exists(request.validated_data):
                raise ValidationError({'detail': 'Invalid email address'})
            services.reset_password(request.validated_data)
            return Response(data={'detail': "Confirmation code was sent successfully"}, status=status.HTTP_200_OK)
        raise ValidationError(request.errors)


class VerifyResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication']
    )
    def post(self, _request):
        request = serializers.ConfirmationCodeRequestSerializer(data=_request.data)
        if request.is_valid():
            token = services.generate_token_for_password_reset(request.validated_data)
            return Response(data={'token': token}, status=status.HTTP_200_OK)
        raise ValidationError(request.errors)


class CompletePasswordResetView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication']
    )
    def post(self, _request):
        complete_request = serializers.CompletePasswordResetRequestSerializer(data=_request.data)
        if complete_request.is_valid():
            services.update_password(complete_request.validated_data)
            return Response(
                data={'detail': 'Your Password Has Been Changed Successfully'},
                status=status.HTTP_200_OK
            )
        raise ValidationError(complete_request.errors)
