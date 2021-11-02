from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.views import TokenViewBase

from . import serializers


UserModel = get_user_model()


class CustomTokenObtainPairView(TokenViewBase):
    serializer_class = serializers.CustomTokenObtainPairSerializer


class UserViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(methods=['PATCH'], detail=False, url_name='update-profile', url_path='update-profile')
    def update_profile(self, request):
        serializer = serializers.UserSerializer(
            request.user, data=request.data, partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['POST'], detail=False, url_name='fetch-profiles', url_path='fetch-profiles')
    def fetch_profiles(self, request):
        serializer = serializers.FetchProfilesSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
