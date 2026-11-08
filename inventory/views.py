from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import F, Q
from django.shortcuts import redirect, render

from .forms import ComponentForm
from .models import Component


PAGE_SIZE = 50


def paginate_components(request, queryset):
    paginator = Paginator(queryset, PAGE_SIZE)
    return paginator.get_page(request.GET.get("page"))


def admin_required(view_func):
    """Allow only users with the ADMIN role or superuser status."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin_role:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


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
    # Search by component ID, name, or category.
    query = request.GET.get("q", "").strip()

    components = Component.objects.all()

    if query:
        components = components.filter(
            Q(component_id__icontains=query)
            | Q(name__icontains=query)
            | Q(category__icontains=query)
        )

    # Paginate the filtered queryset.
    page_obj = paginate_components(request, components)

    return render(
        request,
        "inventory/component_list.html",
        {
            "page_title": "Component Inventory",
            "components": page_obj,
            "page_obj": page_obj,
            "search_query": query,
            "model_missing": False,
        },
    )


@login_required
@admin_required
def add_component(request):
    if request.method == "POST":
        form = ComponentForm(request.POST)

        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error(
                    "component_id",
                    "Component with this Component Id already exists",
                )
            else:
                messages.success(
                    request,
                    "Component added successfully.",
                )
                return redirect("inventory:component-list")

        elif "component_id" in form.errors:
            if Component.objects.filter(
                component_id=request.POST.get("component_id")
            ).exists():
                form.errors["component_id"] = [
                    "Component with this Component Id already exists"
                ]

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
def availability(request):
    page_obj = paginate_components(
        request,
        Component.objects.all(),
    )

    return render(
        request,
        "inventory/availability.html",
        {
            "page_title": "Component Availability",
            "components": page_obj,
            "page_obj": page_obj,
        },
    )


@login_required
def low_stock(request):
    components = Component.objects.filter(
        quantity__gt=0,
        quantity__lte=F("minimum_stock_level"),
    )

    page_obj = paginate_components(request, components)

    return render(
        request,
        "inventory/low_stock.html",
        {
            "page_title": "Low-Stock Components",
            "components": page_obj,
            "page_obj": page_obj,
        },
    )


@login_required
def out_of_stock(request):
    """US-09: Identify components with zero available quantity."""
    components = Component.objects.filter(quantity=0)

    page_obj = paginate_components(request, components)

    return render(
        request,
        "inventory/out_of_stock.html",
        {
            "page_title": "Out-of-Stock Components",
            "components": page_obj,
            "page_obj": page_obj,
        },
    )


@login_required
@admin_required
def delete_component(request, component_id):
    try:
        component = Component.objects.get(id=component_id)

    except Component.DoesNotExist:
        return render(
            request,
            "inventory/delete_component.html",
            {
                "page_title": "Delete Component",
                "error_message": (
                    "Component could not be found. "
                    "The component was not deleted."
                ),
            },
            status=404,
        )

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