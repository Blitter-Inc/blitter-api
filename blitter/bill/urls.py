from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('bill', views.BillViewSet, 'bill')

urlpatterns = router.urls
