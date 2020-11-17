from django.urls import include, path
from . import views

urlpatterns = [

    path('', views.welcome),
    path('api/hawa/', views.AirQualityIndexAPI.as_view(), name='Air Quality Index API'),
    path('message/new/', views.message_new, name='message_new'),
    path('aqi/', views.aqi_detail, name='aqi_detail'),
]
