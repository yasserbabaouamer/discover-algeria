from django.urls import path

from apps.hotels.views import GetMostVisitedHotelsView, FillDb

urlpatterns = [
    path('hotels/most-visited/', GetMostVisitedHotelsView.as_view()),
    path('hotels/fill/', FillDb.as_view())
]
