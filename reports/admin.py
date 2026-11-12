from django.contrib import admin

from .models import (
    AvailabilityCheck,
    AvailabilityIncident,
    MaintenanceWindow,
)


@admin.register(MaintenanceWindow)
class MaintenanceWindowAdmin(admin.ModelAdmin):
    list_display = ("description", "start_at", "end_at", "is_active")
    list_filter = ("is_active",)
    search_fields = ("description",)


@admin.register(AvailabilityCheck)
class AvailabilityCheckAdmin(admin.ModelAdmin):
    list_display = ("checked_at", "is_available", "failure_reason")
    list_filter = ("is_available",)
    readonly_fields = ("checked_at",)


@admin.register(AvailabilityIncident)
class AvailabilityIncidentAdmin(admin.ModelAdmin):
    list_display = ("started_at", "ended_at", "is_resolved")
    list_filter = ("ended_at",)
    search_fields = ("failure_reason",)