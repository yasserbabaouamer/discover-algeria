from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf.urls.static import static

BASE_URL = 'api/v1/'
urlpatterns = [
    path(BASE_URL, include('apps.users.urls')),
    path(BASE_URL, include('apps.guests.urls')),
    path(BASE_URL, include('apps.owners.urls')),
    path(BASE_URL, include('apps.destinations.urls')),
    path(BASE_URL, include('apps.hotels.urls')),
    path(BASE_URL, include('apps.touristicagencies.urls')),
    path(BASE_URL, include('apps.blogs.urls')),
    path(BASE_URL, include('apps.search.urls')),
    path(BASE_URL + "schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        BASE_URL + "docs/", SpectacularSwaggerView.as_view(),
        name="swagger-ui",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

