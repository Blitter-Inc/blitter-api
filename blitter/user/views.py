from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, DestroyModelMixin
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework_simplejwt.views import TokenViewBase

from . import models
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


class UPIAddressViewSet(GenericViewSet, ListModelMixin, DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UPIAddressSerializer

    def get_queryset(self):
        return models.UPIAddress.objects.filter(user=self.request.user)

    @staticmethod
    def get_object_query(pk):
        query = models.UPIAddress.objects.filter(pk=pk)
        if not query.exists():
            raise NotFound()
        return query

    @action(methods=['POST'], detail=False)
    def add(self, request):
        print(type(request.data), request.data)
        serializer = serializers.UPIAddressSerializer(
            data={**request.data, 'user': request.user.pk, 'is_primary': not request.user.upi_addresses.exists()})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({**serializer.validated_data, 'user': request.user.pk})

    @action(methods=['PATCH'], detail=True, url_name='set-primary', url_path='set-primary')
    def set_primary(self, request, pk):
        query = self.get_object_query(pk)
        models.UPIAddress.objects.filter(user=request.user).exclude(
            pk=pk).update(is_primary=False)
        query.update(is_primary=True)
        return Response({'message': 'success'})
