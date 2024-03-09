from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from . import serializers
from . import services
from .serializers import *


class LoginGuestView(APIView):
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        summary='Login for guests'
    )
    def post(self, request: Request):
        login_request = serializers.GuestLoginRequestSerializer(data=self.request.POST)
        if login_request.is_valid():
            tokens = services.authenticate_guest(login_request.data)
            if tokens is not None:
                tokens_serializer = TokensSerializer(tokens)
                return Response(data=tokens_serializer.data, status=status.HTTP_200_OK)
            else:
                raise AuthenticationFailed(detail="Authentication failed , invalid information")
        else:
            raise ValidationError(login_request.errors)


class SignupGuestView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(request=GuestSignupRequestSerializer,
                   responses={201: {
                       "type": "object",
                       "properties": {
                           "access": {"type": "string"},
                           "refresh": {"type": "string"},
                           "is_activated": {"type": "boolean"},
                       }
                   }},
                   summary='Signup for guests'
                   )
    def post(self, request: Request):
        signup_request = GuestSignupRequestSerializer(data=request.data)
        if signup_request.is_valid():
            tokens = services.register_new_guest(signup_request.data)
            return Response(data=tokens, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError(signup_request.errors)


class ConfirmationView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary='Account confirmation',
        description='Post the confirmation code with the JWT token in Headers',
        request=serializers.ConfirmationRequestSerializer,
        responses={200: None}
    )
    def post(self, request):
        try:
            jwt = self.request.META['HTTP_AUTHORIZATION'].split(' ')[1]
            access_token = AccessToken(jwt)
            user_id = access_token.payload['user_id']
            confirmation_request = serializers.ConfirmationRequestSerializer(self.request.POST)
            if confirmation_request.is_valid():
                services.activate_guest(user_id, **confirmation_request.validated_data)
                return Response(data={'detail': 'Your account has been activated'}, status=status.HTTP_200_OK)
            raise ValidationError(detail=confirmation_request.errors)
        except KeyError as e:
            raise ValidationError({'detail': 'You must provide an authentication token'})
        except TokenError as e:
            raise AuthenticationFailed(detail='Invalid authentication token')


class ResendConfirmationView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        responses={
            200: None,
        }
    )
    def post(self, request):
        try:
            jwt = self.request.META['HTTP_AUTHORIZATION'].split(' ')[1]
            access_token = AccessToken(jwt)
            user_id = access_token.payload['user_id']
            services.resend_confirmation_code(user_id)
            return Response(status=status.HTTP_200_OK)
        except (KeyError, TokenError) as e:
            raise AuthenticationFailed(detail='Invalid authentication token')
