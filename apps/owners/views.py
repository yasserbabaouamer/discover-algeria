from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import CustomException
from . import serializers, services
from .dtos import OwnerTokens
from .permissions import *
from ..users.permissions import IsAdmin


class LoginOwnerView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=['Owner'],
        summary='Login an owner',
        request=serializers.OwnerLoginRequestSerializer,
        responses={
            200: OpenApiResponse(response=serializers.OwnerTokensSerializer),
            201: OpenApiResponse(description='Confirmation code sent to owner email'),
            400: OpenApiResponse(description='Invalid information'),
        }
    )
    def post(self, request, *args, **kwargs):
        login_request = serializers.OwnerLoginRequestSerializer(data=self.request.data)
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
    parser_classes = [MultiPartParser, JSONParser]

    @extend_schema(
        tags=['Owner'],
        summary='Quick setup for owner profile',
        request=serializers.SetupOwnerProfileFormSerializer,
        responses={
            201: OpenApiResponse(description='Profile has been created successfully'),
            400: OpenApiResponse(description='Invalid information'),
            409: OpenApiResponse(description='You have already an owner account'),
        }
    )
    def post(self, _request, *args, **kwargs):
        request_body = serializers.SetupOwnerProfileFormSerializer(data=self.request.data)
        if request_body.is_valid():
            services.setup_owner_profile(self.request.user, request_body.validated_data)
            return Response({'details': "Your account has been created successfully"}
                            , status=status.HTTP_201_CREATED)
        raise ValidationError(detail=request_body.errors)


class GetOwnerEssentials(APIView):
    permission_classes = [IsOwnerOrAdmin]

    @extend_schema(
        summary='Get Owner essential information',
        tags=['Owner'],
        responses=serializers.OwnerEssentialInfoSerializer
    )
    def get(self, request, *args, **kwargs):
        owner_info = services.find_owner_essentials_info(request.user.owner.id)
        self.check_object_permissions(request, owner_info)
        return Response(serializers.OwnerEssentialInfoSerializer(owner_info).data)


class ManageProfileView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    @extend_schema(
        summary='Get owner profile - Owner',
        tags=['Owner', 'Admin'],
        responses=serializers.OwnerProfileSerializer
    )
    def get(self, request, *args, **kwargs):
        owner_id = kwargs.pop('owner_id', None)
        if owner_id is None:
            raise ValidationError({'detail': 'Provide an owner_id'})
        profile = services.find_owner_profile(owner_id)
        response = serializers.OwnerProfileSerializer(profile)
        return Response(response.data)

    @extend_schema(
        summary='Update owner profile',
        tags=['Owner', 'Admin'],
        request=serializers.UpdateOwnerFormSerializer,
        responses={
            100: OpenApiResponse(description="This is what to send in the form body attr",
                                 response=serializers.BaseOwnerSerializer),
            200: OpenApiResponse(description="Successful update")
        }
    )
    def put(self, request, *args, **kwargs):
        owner_id = kwargs.pop('owner_id', None)
        if owner_id is None:
            raise ValidationError({'detail': 'Provide an owner_id'})
        update_form = serializers.UpdateOwnerFormSerializer(data=request.data)
        if not update_form.is_valid():
            raise ValidationError(update_form.errors)
        services.update_owner(owner_id, update_form.validated_data)
        return Response({'detail': 'The account has been updated successfully'})


class GetOwnerProfileForAnyone(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary='Get Owner profile for anyone',
        tags=['Owner'],
        responses={
            200: OpenApiResponse(response=serializers.OwnerProfileForAnyoneSerializer),
            400: OpenApiResponse(description="Provide an owner id"),
            404: OpenApiResponse(description="No such owner with this id")
        }
    )
    def get(self, request, *args, **kwargs):
        owner_id = kwargs.pop('owner_id', None)
        if owner_id is None:
            raise ValidationError({'detail': 'Provide an owner id'})
        profile = services.find_owner_profile(owner_id)
        response = serializers.OwnerProfileForAnyoneSerializer(profile)
        return Response(response.data)


class ListCreateOwners(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=['Admin'],
        summary='Get list of owners',
        responses=serializers.OwnerSerializer
    )
    def get(self, request, *args, **kwargs):
        owners = services.find_all_owners()
        response = serializers.OwnerSerializer(owners, many=True)
        return Response(response.data)

    @extend_schema(
        tags=['Admin'],
        summary='Create new owner',
        request=serializers.CreateOwnerRequestSerializer,
        responses={
            201: OpenApiResponse(description="Account created successfully"),
            400: OpenApiResponse(description="Invalid arguments")
        }
    )
    def post(self, request, *args, **kwargs):
        create_request = serializers.CreateOwnerRequestSerializer(data=request.data)
        if not create_request.is_valid():
            raise ValidationError(create_request.errors)
        services.create_owner(create_request.validated_data)
        return Response({'detail': 'The account has been created successfully'},
                        status=status.HTTP_201_CREATED)


class ManageOwnersView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=['Admin'],
        summary='Delete an owner',
    )
    def delete(self, request, *args, **kwargs):
        owner_id = kwargs.pop('owner_id', None)
        if owner_id is None:
            raise ValidationError({'detail': 'provide an owner id'})
        services.delete_owner(owner_id)
        return Response({'detail': 'The account has been deleted successfully'},
                        status=status.HTTP_204_NO_CONTENT)
