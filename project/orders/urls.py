from django.urls import path, include
from django.contrib import admin
from .views import OrderListView

app_name = "orders"

urlpatterns = [
    path("", OrderListView.as_view(), name="list"),
    path("admin/", admin.site.urls),
    path("api/", include("subscriptions.urls")),
]
