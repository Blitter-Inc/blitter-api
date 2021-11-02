from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('', views.UserViewSet, basename='user')

urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view())
]

urlpatterns += router.urls
