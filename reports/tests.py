import csv
from datetime import datetime, timedelta
from io import StringIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import DatabaseError
from django.test import TestCase, override_settings
from django.urls import reverse

from inventory.models import Component
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


User = get_user_model()

TEST_TZ = ZoneInfo("Asia/Kolkata")
FIXED_NOW = datetime(2026, 11, 2, 10, 0, tzinfo=TEST_TZ)


# ============================================================
# US-10: AVAILABILITY REPORT TESTS
# ============================================================

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


# ============================================================
# US-16: SYSTEM AVAILABILITY TESTS
# ============================================================

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
        monday = datetime(2026, 11, 2, 10, 0, tzinfo=TEST_TZ)
        sunday = datetime(2026, 11, 8, 10, 0, tzinfo=TEST_TZ)

        self.assertTrue(is_operating_time(monday))
        self.assertFalse(is_operating_time(sunday))

    def test_maintenance_period_is_excluded(self):
        start = datetime(2026, 11, 2, 9, 0, tzinfo=TEST_TZ)
        end = datetime(2026, 11, 2, 12, 0, tzinfo=TEST_TZ)

        MaintenanceWindow.objects.create(
            description="Planned maintenance",
            start_at=start + timedelta(hours=1),
            end_at=start + timedelta(hours=2),
        )

        result = calculate_availability(start, end)

        self.assertEqual(result["total_operating_seconds"], 10800)
        self.assertEqual(result["maintenance_seconds"], 3600)
        self.assertEqual(result["eligible_seconds"], 7200)

    def test_overlapping_maintenance_windows_are_not_double_counted(self):
        start = datetime(2026, 11, 2, 9, 0, tzinfo=TEST_TZ)
        end = datetime(2026, 11, 2, 12, 0, tzinfo=TEST_TZ)

        MaintenanceWindow.objects.create(
            description="Maintenance one",
            start_at=start + timedelta(minutes=30),
            end_at=start + timedelta(minutes=90),
        )

        MaintenanceWindow.objects.create(
            description="Maintenance two",
            start_at=start + timedelta(hours=1),
            end_at=start + timedelta(hours=2),
        )

        AvailabilityIncident.objects.create(
            started_at=start + timedelta(minutes=30),
            ended_at=start + timedelta(hours=2, minutes=30),
            failure_reason="Test downtime",
        )

        result = calculate_availability(start, end)

        self.assertEqual(result["maintenance_seconds"], 5400)
        self.assertEqual(result["eligible_seconds"], 5400)
        self.assertEqual(result["downtime_seconds"], 1800)

        self.assertAlmostEqual(
            result["availability_percentage"],
            66.67,
            places=2,
        )

    def test_failure_is_recorded(self):
        with patch(
            "reports.services.timezone.now",
            return_value=FIXED_NOW,
        ):
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
        self.assertEqual(incident.started_at, FIXED_NOW)

    def test_recovery_resolves_incident(self):
        incident = AvailabilityIncident.objects.create(
            started_at=FIXED_NOW - timedelta(minutes=5),
            failure_reason="Test failure",
        )

        with patch(
            "reports.services.timezone.now",
            return_value=FIXED_NOW,
        ):
            record_availability_check(is_available=True)

        incident.refresh_from_db()

        self.assertEqual(incident.ended_at, FIXED_NOW)

    def test_maintenance_failure_does_not_create_incident(self):
        MaintenanceWindow.objects.create(
            description="Current maintenance",
            start_at=FIXED_NOW - timedelta(minutes=5),
            end_at=FIXED_NOW + timedelta(minutes=5),
        )

        with patch(
            "reports.services.timezone.now",
            return_value=FIXED_NOW,
        ):
            record_availability_check(
                is_available=False,
                failure_reason="Maintenance test",
            )

        self.assertEqual(AvailabilityCheck.objects.count(), 1)
        self.assertEqual(AvailabilityIncident.objects.count(), 0)

    def test_availability_percentage(self):
        start = datetime(2026, 11, 2, 9, 0, tzinfo=TEST_TZ)
        end = datetime(2026, 11, 2, 11, 0, tzinfo=TEST_TZ)

        AvailabilityIncident.objects.create(
            started_at=start,
            ended_at=start + timedelta(minutes=30),
            failure_reason="Test downtime",
        )

        result = calculate_availability(start, end)

        self.assertEqual(
            result["availability_percentage"],
            75.0,
        )


# ============================================================
# US-16: HEALTH ENDPOINT TESTS
# ============================================================

class HealthCheckTests(TestCase):

    def test_health_endpoint_returns_200_when_database_is_available(self):
        response = self.client.get(reverse("reports:health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "available")
        self.assertEqual(response.json()["database"], "connected")

    @patch("reports.views.connection.cursor")
    def test_health_endpoint_returns_503_when_database_fails(
        self,
        mock_cursor,
    ):
        mock_cursor.side_effect = DatabaseError(
            "Database unavailable"
        )

        response = self.client.get(reverse("reports:health"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "unavailable")
        self.assertEqual(response.json()["database"], "disconnected")


# ============================================================
# US-16: AVAILABILITY MANAGEMENT COMMAND TESTS
# ============================================================

class AvailabilityCommandTests(TestCase):

    @patch(
        "reports.management.commands.check_availability.record_availability_check"
    )
    @patch(
        "reports.management.commands.check_availability.urllib.request.urlopen"
    )
    def test_successful_availability_check(
        self,
        mock_urlopen,
        mock_record,
    ):
        response = MagicMock()
        response.status = 200

        mock_urlopen.return_value.__enter__.return_value = response

        output = StringIO()

        call_command(
            "check_availability",
            stdout=output,
        )

        mock_record.assert_called_once_with(
            is_available=True,
            failure_reason="",
        )

        self.assertIn("System is available", output.getvalue())

    @patch(
        "reports.management.commands.check_availability.record_availability_check"
    )
    @patch(
        "reports.management.commands.check_availability.urllib.request.urlopen"
    )
    def test_http_failure_is_recorded(
        self,
        mock_urlopen,
        mock_record,
    ):
        mock_urlopen.side_effect = HTTPError(
            "http://127.0.0.1:8000/reports/health/",
            503,
            "Service Unavailable",
            None,
            None,
        )

        output = StringIO()

        call_command(
            "check_availability",
            stdout=StringIO(),
            stderr=output,
        )

        mock_record.assert_called_once()

        recorded_arguments = mock_record.call_args.kwargs

        self.assertFalse(recorded_arguments["is_available"])
        self.assertIn("503", recorded_arguments["failure_reason"])
        self.assertIn("System failure", output.getvalue())

    @patch(
        "reports.management.commands.check_availability.record_availability_check"
    )
    @patch(
        "reports.management.commands.check_availability.urllib.request.urlopen"
    )
    def test_connection_error_is_recorded(
        self,
        mock_urlopen,
        mock_record,
    ):
        mock_urlopen.side_effect = URLError("Connection refused")

        call_command(
            "check_availability",
            stdout=StringIO(),
            stderr=StringIO(),
        )

        mock_record.assert_called_once()

        recorded_arguments = mock_record.call_args.kwargs

        self.assertFalse(recorded_arguments["is_available"])
        self.assertIn(
            "Connection refused",
            recorded_arguments["failure_reason"],
        )

    @patch(
        "reports.management.commands.check_availability.record_availability_check"
    )
    @patch(
        "reports.management.commands.check_availability.urllib.request.urlopen"
    )
    def test_timeout_error_is_recorded(
        self,
        mock_urlopen,
        mock_record,
    ):
        mock_urlopen.side_effect = TimeoutError("Request timed out")

        call_command(
            "check_availability",
            stdout=StringIO(),
            stderr=StringIO(),
        )

        mock_record.assert_called_once()

        recorded_arguments = mock_record.call_args.kwargs

        self.assertFalse(recorded_arguments["is_available"])
        self.assertIn(
            "timed out",
            recorded_arguments["failure_reason"].lower(),
        )

    @patch(
        "reports.management.commands.check_availability.record_availability_check"
    )
    @patch(
        "reports.management.commands.check_availability.urllib.request.urlopen"
    )
    def test_invalid_interval_is_rejected(
        self,
        mock_urlopen,
        mock_record,
    ):
        output = StringIO()

        call_command(
            "check_availability",
            interval=0,
            stdout=StringIO(),
            stderr=output,
        )

        mock_urlopen.assert_not_called()
        mock_record.assert_not_called()

        self.assertIn(
            "Interval must be at least 1 second",
            output.getvalue(),
        )