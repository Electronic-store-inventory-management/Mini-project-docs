
from django.db.models import F
from django.shortcuts import render

from .models import Component


def availability(request):
    """
    US-07: Display component availability status.
    Shows all components with their calculated stock status.
    """
    components = Component.objects.all()

    return render(
        request,
        "inventory/availability.html",
        {"components": components},
    )


def low_stock(request):
    """
    US-08: Identify components that need restocking.
    Excludes out-of-stock components, which have their own status.
    """
    components = Component.objects.filter(
        quantity__gt=0,
        quantity__lte=F("minimum_stock_level"),
    )

    return render(
        request,
        "inventory/low_stock.html",
        {"components": components},
    )
