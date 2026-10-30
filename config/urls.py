"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Existing application routes
    path('accounts/', include('accounts.urls')),
    path('inventory/', include('inventory.urls')),

    # US-10: Generate Availability Report
    path('reports/', include('reports.urls')),

    # US-11: Display Inventory Dashboard
    path('dashboard/', include('dashboard.urls')),

    # Redirect root to inventory landing page
    path(
        '',
        RedirectView.as_view(
            pattern_name='inventory:landing',
            permanent=False
        ),
    ),
]