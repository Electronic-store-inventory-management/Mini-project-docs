
import csv

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render

from inventory.models import Component


@login_required(login_url="/accounts/login/")
def availability_report(request):
    """US-10: Generate a filterable component availability report."""

    components = Component.objects.all()

    category = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()

    if category:
        components = components.filter(category=category)

    if status == "Available":
        components = components.filter(
            quantity__gt=F("minimum_stock_level")
        )
    elif status == "Low Stock":
        components = components.filter(
            quantity__gt=0,
            quantity__lte=F("minimum_stock_level"),
        )
    elif status == "Out of Stock":
        components = components.filter(quantity=0)

    if request.GET.get("export") == "csv":
        response = HttpResponse(
            content_type="text/csv; charset=utf-8"
        )
        response["Content-Disposition"] = (
            'attachment; filename="availability_report.csv"'
        )

        writer = csv.writer(response)
        writer.writerow([
            "Component ID",
            "Name",
            "Category",
            "Manufacturer",
            "Quantity",
            "Minimum Stock Level",
            "Availability Status",
            "Unit Price",
            "Supplier",
        ])

        for component in components:
            writer.writerow([
                component.component_id,
                component.name,
                component.category,
                component.manufacturer,
                component.quantity,
                component.minimum_stock_level,
                component.availability_status,
                component.unit_price,
                component.supplier,
            ])

        return response

    categories = (
        Component.objects.order_by("category")
        .values_list("category", flat=True)
        .distinct()
    )

    context = {
        "components": components,
        "categories": categories,
        "selected_category": category,
        "selected_status": status,
    }

    return render(
        request,
        "reports/availability_report.html",
        context,
    )
