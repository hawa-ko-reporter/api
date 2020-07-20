from django.urls import include, path
from . import views

urlpatterns = [

    path('', views.welcome),
    path('api/hawa/', views.AirQualityIndexAPI.as_view(), name='Air Quality Index API'),
]
