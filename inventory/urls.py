from django.urls import path
from .views import landing_page, component_list, availability, low_stock

app_name = 'inventory'

urlpatterns = [
    path('', landing_page, name='landing'),
    path('components/', component_list, name='component-list'),
    path('availability/', availability, name='availability'),
    path('low-stock/', low_stock, name='low_stock'),
]