from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from .views import CustomTokenObtainPairView, UserUpdateView


router = DefaultRouter()
router.register('update', UserUpdateView, basename='update_user')

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view())
]

urlpatterns += router.urls
