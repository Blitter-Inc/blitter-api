from django.contrib.auth import get_user_model
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenViewBase

from .serializers import CustomTokenObtainPairSerializer, UserSerializer


UserModel = get_user_model()


class CustomTokenObtainPairView(TokenViewBase):
    serializer_class = CustomTokenObtainPairSerializer


class UserUpdateView(GenericViewSet, UpdateModelMixin):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_object(self):
        return self.request.user
