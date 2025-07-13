from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),  # include all API routes from the app
    path('accounts/', include('allauth.urls')),  # for django-allauth if used
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
