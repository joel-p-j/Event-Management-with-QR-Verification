from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import RegisterView,ProfileView
from django.urls import path


urlpatterns=[
    path('register/',RegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/',TokenRefreshView.as_view()),
    path('user/', ProfileView.as_view()),
]