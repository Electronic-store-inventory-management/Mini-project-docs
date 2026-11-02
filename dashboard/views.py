

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F
from django.shortcuts import render

from inventory.models import Component


@login_required(login_url="/accounts/login/")
def dashboard_home(request):
    """US-11: Display inventory dashboard statistics."""

    components = Component.objects.all()

    total_components = components.count()

    total_stock = components.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    low_stock_count = components.filter(
        quantity__gt=0,
        quantity__lte=F("minimum_stock_level"),
    ).count()

    out_of_stock_count = components.filter(
        quantity=0
    ).count()

    category_summary = (
        components.values("category")
        .annotate(
            component_count=Count("id"),
            total_quantity=Sum("quantity"),
        )
        .order_by("category")
    )

    context = {
        "total_components": total_components,
        "total_stock": total_stock,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "category_summary": category_summary,
    }

    return render(request, "dashboard/dashboard.html", context)