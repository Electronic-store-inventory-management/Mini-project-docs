
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import F
from django.shortcuts import get_object_or_404, render

from .forms import ComponentForm
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


@login_required
def add_component(request):
    if request.method == "POST":
        form = ComponentForm(request.POST)

        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error(
                    "component_id",
                    "A component with this Component ID already exists.",
                )
            else:
                return render(
                    request,
                    "inventory/add_component.html",
                    {
                        "page_title": "Add Component",
                        "form": ComponentForm(),
                        "success_message": "Component added successfully.",
                    },
                )
    else:
        form = ComponentForm()

    return render(
        request,
        "inventory/add_component.html",
        {
            "page_title": "Add Component",
            "form": form,
        },
    )


@login_required
def out_of_stock(request):
    """US-09: Identify components with zero available quantity."""
    components = Component.objects.filter(quantity=0)

    return render(
        request,
        "inventory/out_of_stock.html",
        {
            "page_title": "Out-of-Stock Components",
            "components": components,
        },
    )


@login_required
def delete_component(request, component_id):
    component = get_object_or_404(Component, id=component_id)

    if request.method == "POST":
        component.delete()
        return render(
            request,
            "inventory/delete_component.html",
            {
                "page_title": "Delete Component",
                "success_message": "Component deleted successfully.",
            },
        )

    return render(
        request,
        "inventory/delete_component.html",
        {
            "page_title": "Delete Component",
            "component": component,
        },
    )