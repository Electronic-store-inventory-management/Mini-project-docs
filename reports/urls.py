from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path(
        "availability/",
        views.availability_report,
        name="availability",
    ),
]