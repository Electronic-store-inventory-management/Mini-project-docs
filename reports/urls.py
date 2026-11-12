
from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path(
        "availability/",
        views.availability_report,
        name="availability",
    ),
    path(
        "health/",
        views.health_check,
        name="health",
    ),
    path(
    "system-availability/monthly/",
    views.monthly_availability_report,
    name="monthly_availability",
    ),
]