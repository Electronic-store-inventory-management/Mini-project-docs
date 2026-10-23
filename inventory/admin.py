
from django.contrib import admin

from .models import Component


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = (
        "component_id",
        "name",
        "category",
        "quantity",
        "minimum_stock_level",
        "availability_status",
    )
    search_fields = ("component_id", "name", "manufacturer")
    list_filter = ("category",)
