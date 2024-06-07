from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import SignUpView


urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('signup/', SignUpView.as_view(), name='signup')
]