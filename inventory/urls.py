from django.urls import path
from .views import landing_page

app_name = 'inventory'

urlpatterns = [
    path('', landing_page, name='landing'),
]

