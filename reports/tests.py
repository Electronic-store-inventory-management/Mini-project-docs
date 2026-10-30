
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
