from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import redirect,render

from django.db import IntegrityError
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


from django.contrib import messages
from .forms import ComponentForm

@login_required
def add_component(request):
    if request.method == "POST":
        form = ComponentForm(request.POST)

        if form.is_valid():
            component_id = form.cleaned_data.get("component_id")

            if Component.objects.filter(component_id=component_id).exists():
                form.add_error(
                    "component_id",
                    "Component with this Component Id already exists",
                )
            else:
                try:
                    form.save()
                    messages.success(
                        request,
                        "Component added successfully.",
                    )
                    return redirect("inventory:component-list")
                except IntegrityError:
                    form.add_error(
                        "component_id",
                        "Component with this Component Id already exists",
                    )
    else:
        form = ComponentForm()

    return render(
        request,
        "inventory/component_form.html",
        {
            "page_title": "Add Component",
            "form": form,
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