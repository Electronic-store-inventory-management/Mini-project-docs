
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F
from django.shortcuts import render

from inventory.models import Component


@login_required(login_url="/accounts/login/")
def dashboard_home(request):
    """US-11 and US-20: Display complete inventory dashboard statistics."""

    components = Component.objects.all()

    # Total number of components
    total_components = components.count()

    # Total units available in inventory
    total_stock = components.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    # Components with quantity greater than minimum stock level
    available_count = components.filter(
        quantity__gt=F("minimum_stock_level")
    ).count()

    # Components below or equal to minimum stock level, excluding zero
    low_stock_count = components.filter(
        quantity__gt=0,
        quantity__lte=F("minimum_stock_level"),
    ).count()

    # Components with zero quantity
    out_of_stock_count = components.filter(
        quantity=0
    ).count()

    # Inventory grouped by category
    category_summary = (
        components.values("category")
        .annotate(
            component_count=Count("id"),
            total_quantity=Sum("quantity"),
        )
        .order_by("category")
    )

    # Dashboard data
    context = {
        "total_components": total_components,
        "total_stock": total_stock,
        "available_count": available_count,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "category_summary": category_summary,
    }

    return render(request, "dashboard/dashboard.html", context)
