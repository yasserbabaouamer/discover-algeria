from django.urls import path

from .views import GetRecentlyAddedBlogs

APP_URL = 'blogs/'

urlpatterns = [
    path(APP_URL + 'recent/', GetRecentlyAddedBlogs.as_view())
]
