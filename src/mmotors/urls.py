"""
URL configuration for mmotors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import index
from .views import test403

urlpatterns = [
    path('', index, name='index'),
    path("admin/", admin.site.urls),
    path('vehicles/', include('vehicles.urls')),
    path('accounts/', include('accounts.urls')),
    path('registration/', include('registration.urls')),
    path('client/', include('client.urls')),
    path('dashboard/', include('dashboard.urls')),
    path("test403/", test403),
]

handler404 = "mmotors.views.error_404"
handler500 = "mmotors.views.error_500"
handler403 = "mmotors.views.error_403"
handler400 = "mmotors.views.error_400"

# Media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)