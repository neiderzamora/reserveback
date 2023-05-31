from django.urls import path
from .views import ReserveList, ReserveDetail, ReservePost

urlpatterns = [
    path('reserves/', ReserveList.as_view(), name='reserve-list'),
    path('reservespost/', ReservePost.as_view(), name='reserve-post'),
    path('reserves/<uuid:pk>/', ReserveDetail.as_view(), name='reserve-detail'),
]
