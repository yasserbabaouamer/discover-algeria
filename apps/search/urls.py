from django.urls import path

from apps.search.views import QuickSearchView

APP_URL = 'search/'
urlpatterns = [
    path(APP_URL + 'quick', QuickSearchView.as_view())
]
