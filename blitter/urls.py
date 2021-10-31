from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


handler500 = 'rest_framework.exceptions.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bill-manager/', include('blitter.bill.urls')),
    path('user/', include('blitter.user.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
