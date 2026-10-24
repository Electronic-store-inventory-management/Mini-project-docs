from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render

from .models import Component


@login_required
def landing_page(request):
    return render(
        request,
        "inventory/landing.html",
        {
            "page_title": "Inventory Management",
            "user": request.user,
        },
    )


@login_required
def component_list(request):
    components = Component.objects.all()
    return render(
        request,
        "inventory/component_list.html",
        {
            "page_title": "Component Inventory",
            "components": components,
            "model_missing": False,
        },
    )


@login_required
def availability(request):
    components = Component.objects.all()
    return render(
        request,
        "inventory/availability.html",
        {
            "page_title": "Component Availability",
            "components": components,
        },
    )


@login_required
def low_stock(request):
    components = Component.objects.filter(
        quantity__gt=0,
        quantity__lte=F("minimum_stock_level"),
    )
    return render(
        request,
        "inventory/low_stock.html",
        {
            "page_title": "Low-Stock Components",
            "components": components,
        },
    )