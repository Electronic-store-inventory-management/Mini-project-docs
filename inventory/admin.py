
from django.contrib import admin
from .models import Component


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = (
        "component_id",
        "name",
        "category",
        "manufacturer",
        "quantity",
        "minimum_stock_level",
        "unit_price",
        "supplier",
    )

    search_fields = (
        "component_id",
        "name",
        "category",
        "manufacturer",
        "supplier",
    )

    list_filter = ("category", "manufacturer")

    ordering = ("name",)
