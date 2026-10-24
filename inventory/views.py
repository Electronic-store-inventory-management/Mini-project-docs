from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render

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
    # Clear any leftover messages from previous requests
    list(messages.get_messages(request))
    if request.method == "POST":
        form = ComponentForm(request.POST)
        if form.is_valid():
            # Check for duplicate component_id to provide clear error
            component_id = form.cleaned_data.get('component_id')
            if Component.objects.filter(component_id=component_id).exists():
                form.add_error('component_id', 'Component with this Component Id already exists')
            else:
                try:
                    form.save()
                    messages.success(request, "Component added successfully.")
                    return render(request, "inventory/component_list.html", {
                        "page_title": "Component Inventory",
                        "components": Component.objects.all(),
                        "model_missing": False,
                    })
                except IntegrityError:
                    form.add_error('component_id', 'Component with this Component Id already exists')
            # fall through to render form with errors
    else:
        form = ComponentForm()
    # Clear any leftover success messages before re‑rendering the form with errors
    list(messages.get_messages(request))
    return render(request, "inventory/component_form.html", {
        "page_title": "Add Component",
        "form": form,
    })


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