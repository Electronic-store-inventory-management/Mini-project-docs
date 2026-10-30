
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from inventory.models import Component


User = get_user_model()


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="dashboard_test_user",
            password="SecurePass123!",
            role=User.Role.STAFF,
        )

        Component.objects.create(
            component_id="DASH001",
            name="Dashboard Capacitor",
            category="Passive Components",
            manufacturer="Test Manufacturer",
            quantity=20,
            unit_price="5.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

        Component.objects.create(
            component_id="DASH002",
            name="Dashboard Resistor",
            category="Passive Components",
            manufacturer="Test Manufacturer",
            quantity=4,
            unit_price="2.50",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

        Component.objects.create(
            component_id="DASH003",
            name="Dashboard LED",
            category="Optoelectronic Components",
            manufacturer="Test Manufacturer",
            quantity=0,
            unit_price="3.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_dashboard_displays_correct_statistics(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(
            response.status_code,
            200,
            f"Dashboard redirected to: {response.get('Location')}",
        )

        self.assertEqual(response.context["total_components"], 3)
        self.assertEqual(response.context["total_stock"], 24)
        self.assertEqual(response.context["low_stock_count"], 1)
        self.assertEqual(response.context["out_of_stock_count"], 1)

    def test_dashboard_shows_categories(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(
            response.status_code,
            200,
            f"Dashboard redirected to: {response.get('Location')}",
        )

        self.assertContains(response, "Passive Components")
        self.assertContains(
            response,
            "Optoelectronic Components",
        )

    def test_unauthenticated_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_all_authenticated_roles_can_access_dashboard(self):
        for role in (
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.STAFF,
        ):
            with self.subTest(role=role):
                user = User.objects.create_user(
                    username=f"dashboard_{role.value.lower()}",
                    password="SecurePass123!",
                    role=role,
                )

                self.client.force_login(user)

                response = self.client.get(
                    reverse("dashboard:home")
                )

                self.assertEqual(
                    response.status_code,
                    200,
                    f"{role} should be allowed to access the dashboard.",
                )
