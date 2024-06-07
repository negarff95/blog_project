from django.urls import path
from .views import PostView, RateView

urlpatterns = [
    path("posts/", PostView.as_view(), name='post_list'),
    path("submit-rate/", RateView.as_view(), name='submit_rate')
]