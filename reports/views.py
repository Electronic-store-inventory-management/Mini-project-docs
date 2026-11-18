
import csv

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from datetime import datetime
from reports.services import generate_monthly_availability_report

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
def health_check(request):
    """Check whether the application and database are responding."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse({
            "status": "available",
            "database": "connected",
        }, status=200)

    except Exception:
        return JsonResponse({
            "status": "unavailable",
            "database": "disconnected",
        }, status=503)
@login_required(login_url="/accounts/login/")
def monthly_availability_report(request):
    """US-22: Display the monthly system availability report."""

    from django.utils import timezone
    from reports.services import get_availability_timezone

    local_now = timezone.now().astimezone(get_availability_timezone())

    year_value = request.GET.get("year", str(local_now.year))
    month_value = request.GET.get("month", str(local_now.month))

    report = None
    error_message = ""

    try:
        year = int(year_value)
        month = int(month_value)
        report = generate_monthly_availability_report(year, month)
    except ValueError as error:
        error_message = str(error)

    return render(
        request,
        "reports/monthly_availability_report.html",
        {
            "report": report,
            "selected_year": year_value,
            "selected_month": month_value,
            "error_message": error_message,
            "current_year": local_now.year,
        },
    )