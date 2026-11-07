from django.db import models


class MaintenanceWindow(models.Model):
    description = models.CharField(max_length=255)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.description


class AvailabilityCheck(models.Model):
    checked_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    failure_reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.checked_at} - {'Up' if self.is_available else 'Down'}"


class AvailabilityIncident(models.Model):
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField()

    @property
    def is_resolved(self):
        return self.ended_at is not None

    def __str__(self):
        return f"Incident starting {self.started_at}"