
from django.contrib import admin
from .models import Component, AuditLog


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
        "availability_status",
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


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "component_id",
        "timestamp",
    )

    search_fields = ("component_id", "user__username")
    list_filter = ("action", "timestamp")
    ordering = ("-timestamp",)

    readonly_fields = (
        "user",
        "action",
        "component_id",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
