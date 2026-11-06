from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import models
from django.utils import timezone

from .models import (
    AvailabilityCheck,
    AvailabilityIncident,
    MaintenanceWindow,
)


def get_availability_timezone():
    """Return the configured system availability timezone."""
    return ZoneInfo(
        getattr(
            settings,
            "SYSTEM_AVAILABILITY_TIME_ZONE",
            "Asia/Kolkata",
        )
    )


def is_operating_time(moment):
    """Check whether the given time falls within store operating hours."""

    local_time = moment.astimezone(get_availability_timezone())
    hours = settings.SYSTEM_OPERATING_HOURS.get(
        local_time.weekday()
    )

    if hours is None:
        return False

    opening, closing = hours
    current_time = local_time.time().replace(tzinfo=None)

    return (
        time.fromisoformat(opening)
        <= current_time
        < time.fromisoformat(closing)
    )


def is_maintenance_time(moment):
    """Check whether the given time falls within planned maintenance."""

    return MaintenanceWindow.objects.filter(
        is_active=True,
        start_at__lte=moment,
        end_at__gt=moment,
    ).exists()


def record_availability_check(is_available, failure_reason=""):
    """Record health checks and track system failures."""

    checked_at = timezone.now()

    check = AvailabilityCheck.objects.create(
        is_available=is_available,
        failure_reason=failure_reason,
    )

    # Ignore failures outside operating hours.
    if not is_operating_time(checked_at):
        return check

    # Planned maintenance is excluded from failure tracking.
    if is_maintenance_time(checked_at):
        return check

    open_incident = AvailabilityIncident.objects.filter(
        ended_at__isnull=True
    ).first()

    if not is_available:
        if not open_incident:
            AvailabilityIncident.objects.create(
                started_at=checked_at,
                failure_reason=(
                    failure_reason or "System unavailable"
                ),
            )

    elif open_incident:
        open_incident.ended_at = checked_at
        open_incident.save(update_fields=["ended_at"])

    return check


def calculate_availability(start_at, end_at):
    """
    Calculate system availability during operating hours.

    Planned maintenance is excluded from eligible operating time
    and from downtime.
    """

    if start_at >= end_at:
        raise ValueError("End time must be after start time.")

    tz = get_availability_timezone()

    start_local = start_at.astimezone(tz)
    end_local = end_at.astimezone(tz)

    total_seconds = 0
    maintenance_seconds = 0
    downtime_seconds = 0
    downtime_during_maintenance_seconds = 0

    current_date = start_local.date()

    while current_date <= end_local.date():

        hours = settings.SYSTEM_OPERATING_HOURS.get(
            current_date.weekday()
        )

        if hours:

            opening = time.fromisoformat(hours[0])
            closing = time.fromisoformat(hours[1])

            window_start = datetime.combine(
                current_date,
                opening,
                tzinfo=tz,
            )

            window_end = datetime.combine(
                current_date,
                closing,
                tzinfo=tz,
            )

            period_start = max(
                start_local,
                window_start,
            )

            period_end = min(
                end_local,
                window_end,
            )

            if period_start < period_end:

                total_seconds += (
                    period_end - period_start
                ).total_seconds()

                maintenance_windows = list(
                    MaintenanceWindow.objects.filter(
                        is_active=True,
                        start_at__lt=period_end,
                        end_at__gt=period_start,
                    )
                )

                # Calculate planned maintenance overlap.
                for maintenance in maintenance_windows:

                    overlap_start = max(
                        period_start,
                        maintenance.start_at.astimezone(tz),
                    )

                    overlap_end = min(
                        period_end,
                        maintenance.end_at.astimezone(tz),
                    )

                    if overlap_start < overlap_end:

                        maintenance_seconds += (
                            overlap_end - overlap_start
                        ).total_seconds()

                # Find incidents overlapping this operating period.
                incidents = AvailabilityIncident.objects.filter(
                    started_at__lt=period_end,
                ).filter(
                    models.Q(ended_at__isnull=True)
                    | models.Q(ended_at__gt=period_start)
                )

                for incident in incidents:

                    incident_start = max(
                        period_start,
                        incident.started_at.astimezone(tz),
                    )

                    incident_end = min(
                        period_end,
                        (
                            incident.ended_at.astimezone(tz)
                            if incident.ended_at
                            else end_local
                        ),
                    )

                    if incident_start < incident_end:

                        downtime_seconds += (
                            incident_end - incident_start
                        ).total_seconds()

                        # Exclude only the downtime that overlaps
                        # planned maintenance.
                        for maintenance in maintenance_windows:

                            excluded_start = max(
                                incident_start,
                                maintenance.start_at.astimezone(tz),
                            )

                            excluded_end = min(
                                incident_end,
                                maintenance.end_at.astimezone(tz),
                            )

                            if excluded_start < excluded_end:

                                downtime_during_maintenance_seconds += (
                                    excluded_end - excluded_start
                                ).total_seconds()

        current_date += timedelta(days=1)

    eligible_seconds = max(
        total_seconds - maintenance_seconds,
        0,
    )

    actual_downtime = max(
        downtime_seconds
        - downtime_during_maintenance_seconds,
        0,
    )

    actual_downtime = min(
        actual_downtime,
        eligible_seconds,
    )

    uptime_seconds = eligible_seconds - actual_downtime

    availability_percentage = (
        uptime_seconds / eligible_seconds * 100
        if eligible_seconds > 0
        else 100.0
    )

    return {
        "total_operating_seconds": total_seconds,
        "maintenance_seconds": maintenance_seconds,
        "eligible_seconds": eligible_seconds,
        "downtime_seconds": actual_downtime,
        "uptime_seconds": uptime_seconds,
        "availability_percentage": round(
            availability_percentage,
            2,
        ),
    }