
from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("availability/", views.availability, name="availability"),
    path("low-stock/", views.low_stock, name="low_stock"),
]
