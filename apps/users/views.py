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

    def post(self, request):
        try:
            jwt = self.request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            access_token = AccessToken(jwt)
            user_id = access_token.payload['user_id']
            confirmation_code = self.request.data['confirmation_code']
            services.activate_guest(user_id, confirmation_code)
            return Response(data={'detail': 'Your account has been activated'}, status=status.HTTP_200_OK)
        except KeyError as e:
            raise ValidationError({'detail': 'No confirmation code provided'})
        except TokenError as e:
            raise AuthenticationFailed(detail='Invalid authentication token')


class ResendConfirmationView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            jwt = self.request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            access_token = AccessToken(jwt)
            user_id = access_token.payload['user_id']
            services.resend_confirmation_code(user_id)
            return Response(status=status.HTTP_200_OK)
        except (KeyError, TokenError) as e:
            raise AuthenticationFailed(detail='Invalid authentication token')
