from django.urls import path
from .views import CustomAuthToken, logout

urlpatterns = [
    path('login/', CustomAuthToken.as_view(), name='api-login'),
    path('logout/', logout, name='api-logout'),
]
