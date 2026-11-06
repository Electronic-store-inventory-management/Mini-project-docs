
import csv

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from inventory.models import Component


User = get_user_model()


class AvailabilityReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="report_test_user",
            password="SecurePass123!",
            role=User.Role.STAFF,
        )

        Component.objects.create(
            component_id="REP001",
            name="Report Capacitor",
            category="Passive Components",
            manufacturer="Test Manufacturer",
            quantity=20,
            unit_price="5.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

        Component.objects.create(
            component_id="REP002",
            name="Report Resistor",
            category="Passive Components",
            manufacturer="Test Manufacturer",
            quantity=4,
            unit_price="2.50",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

        Component.objects.create(
            component_id="REP003",
            name="Report LED",
            category="Optoelectronic Components",
            manufacturer="Test Manufacturer",
            quantity=0,
            unit_price="3.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.report_url = reverse("reports:availability")

    def test_report_page_loads(self):
        response = self.client.get(self.report_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Report Capacitor")
        self.assertContains(response, "Report Resistor")
        self.assertContains(response, "Report LED")

    def test_available_filter(self):
        response = self.client.get(
            self.report_url,
            {"status": "Available"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Report Capacitor")
        self.assertNotContains(response, "Report Resistor")
        self.assertNotContains(response, "Report LED")

    def test_low_stock_filter(self):
        response = self.client.get(
            self.report_url,
            {"status": "Low Stock"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Report Resistor")
        self.assertNotContains(response, "Report Capacitor")
        self.assertNotContains(response, "Report LED")

    def test_out_of_stock_filter(self):
        response = self.client.get(
            self.report_url,
            {"status": "Out of Stock"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Report LED")
        self.assertNotContains(response, "Report Capacitor")
        self.assertNotContains(response, "Report Resistor")

    def test_category_filter(self):
        response = self.client.get(
            self.report_url,
            {"category": "Passive Components"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Report Capacitor")
        self.assertContains(response, "Report Resistor")
        self.assertNotContains(response, "Report LED")

    def test_csv_export(self):
        response = self.client.get(
            self.report_url,
            {"export": "csv"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn(
            'attachment; filename="availability_report.csv"',
            response["Content-Disposition"],
        )

        rows = list(
            csv.reader(
                response.content.decode("utf-8").splitlines()
            )
        )

        self.assertEqual(rows[0][0], "Component ID")
        self.assertEqual(len(rows), 4)

    def test_filtered_csv_export(self):
        response = self.client.get(
            self.report_url,
            {
                "status": "Low Stock",
                "export": "csv",
            },
        )

        self.assertEqual(response.status_code, 200)

        rows = list(
            csv.reader(
                response.content.decode("utf-8").splitlines()
            )
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][0], "REP002")

    def test_unauthenticated_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(self.report_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_all_authenticated_roles_can_access_report_and_csv(self):
        for role in (
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.STAFF,
        ):
            with self.subTest(role=role):
                user = User.objects.create_user(
                    username=f"report_{role.value.lower()}",
                    password="SecurePass123!",
                    role=role,
                )

                self.client.force_login(user)

                report_response = self.client.get(self.report_url)

                self.assertEqual(
                    report_response.status_code,
                    200,
                    f"{role} should access the availability report.",
                )

                csv_response = self.client.get(
                    self.report_url,
                    {"export": "csv"},
                )

                self.assertEqual(
                    csv_response.status_code,
                    200,
                    f"{role} should be allowed to export CSV.",
                )
                self.assertIn(
                    "text/csv",
                    csv_response["Content-Type"],
                )

    def test_unauthenticated_user_cannot_export_csv(self):
        self.client.logout()

        response = self.client.get(
            self.report_url,
            {"export": "csv"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.test import override_settings
from django.utils import timezone

from reports.models import (
    AvailabilityCheck,
    AvailabilityIncident,
    MaintenanceWindow,
)

from reports.services import (
    calculate_availability,
    is_operating_time,
    record_availability_check,
)


@override_settings(
    SYSTEM_AVAILABILITY_TIME_ZONE="Asia/Kolkata",
    SYSTEM_OPERATING_HOURS={
        0: ("09:00", "21:00"),
        1: ("09:00", "21:00"),
        2: ("09:00", "21:00"),
        3: ("09:00", "21:00"),
        4: ("09:00", "21:00"),
        5: ("09:00", "21:00"),
        6: None,
    },
)
class SystemAvailabilityTests(TestCase):

    def test_operating_hours(self):
        tz = ZoneInfo("Asia/Kolkata")

        monday = datetime(2026, 11, 2, 10, 0, tzinfo=tz)
        sunday = datetime(2026, 11, 8, 10, 0, tzinfo=tz)

        self.assertTrue(is_operating_time(monday))
        self.assertFalse(is_operating_time(sunday))

    def test_maintenance_period_is_excluded(self):
        tz = ZoneInfo("Asia/Kolkata")

        start = datetime(2026, 11, 2, 9, 0, tzinfo=tz)
        end = datetime(2026, 11, 2, 12, 0, tzinfo=tz)

        MaintenanceWindow.objects.create(
            description="Planned maintenance",
            start_at=start + timedelta(hours=1),
            end_at=start + timedelta(hours=2),
        )

        result = calculate_availability(start, end)

        self.assertEqual(
            result["total_operating_seconds"], 10800
        )
        self.assertEqual(
            result["maintenance_seconds"], 3600
        )
        self.assertEqual(
            result["eligible_seconds"], 7200
        )

    def test_failure_is_recorded(self):
        record_availability_check(
            is_available=False,
            failure_reason="Test server failure",
        )

        self.assertEqual(AvailabilityCheck.objects.count(), 1)
        self.assertEqual(AvailabilityIncident.objects.count(), 1)

        incident = AvailabilityIncident.objects.first()

        self.assertEqual(
            incident.failure_reason,
            "Test server failure",
        )
        self.assertIsNone(incident.ended_at)

    def test_recovery_resolves_incident(self):
        now = timezone.now()

        incident = AvailabilityIncident.objects.create(
            started_at=now - timedelta(minutes=5),
            failure_reason="Test failure",
        )

        record_availability_check(is_available=True)

        incident.refresh_from_db()

        self.assertIsNotNone(incident.ended_at)

    def test_maintenance_failure_does_not_create_incident(self):
        now = timezone.now()

        MaintenanceWindow.objects.create(
            description="Current maintenance",
            start_at=now - timedelta(minutes=5),
            end_at=now + timedelta(minutes=5),
        )

        record_availability_check(
            is_available=False,
            failure_reason="Maintenance test",
        )

        self.assertEqual(AvailabilityCheck.objects.count(), 1)
        self.assertEqual(AvailabilityIncident.objects.count(), 0)

    def test_availability_percentage(self):
        tz = ZoneInfo("Asia/Kolkata")

        start = datetime(2026, 11, 2, 9, 0, tzinfo=tz)
        end = datetime(2026, 11, 2, 11, 0, tzinfo=tz)

        AvailabilityIncident.objects.create(
            started_at=start,
            ended_at=start + timedelta(minutes=30),
            failure_reason="Test downtime",
        )

        result = calculate_availability(start, end)

        self.assertEqual(
            result["availability_percentage"], 75.0
        )
