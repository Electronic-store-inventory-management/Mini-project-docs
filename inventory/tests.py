
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Component


User = get_user_model()


class ComponentAvailabilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="inventory_staff",
            password="SecurePass123!",
        )

        cls.available = Component.objects.create(
            component_id="TEST001",
            name="Test Capacitor",
            category="Passive Components",
            manufacturer="Test Manufacturer",
            quantity=20,
            unit_price="5.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

        cls.low_stock = Component.objects.create(
            component_id="TEST002",
            name="Test Resistor",
            category="Passive Components",
            manufacturer="Test Manufacturer",
            quantity=4,
            unit_price="2.50",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

        cls.out_of_stock = Component.objects.create(
            component_id="TEST003",
            name="Test LED",
            category="Optoelectronic Components",
            manufacturer="Test Manufacturer",
            quantity=0,
            unit_price="3.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

    def setUp(self):
        self.availability_url = reverse("inventory:availability")
        self.low_stock_url = reverse("inventory:low_stock")

    def test_availability_statuses(self):
        self.assertEqual(self.available.availability_status, "Available")
        self.assertEqual(self.low_stock.availability_status, "Low Stock")
        self.assertEqual(
            self.out_of_stock.availability_status,
            "Out of Stock",
        )

    def test_availability_page_requires_login(self):
        response = self.client.get(self.availability_url)
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self.availability_url}",
        )

    def test_availability_page_shows_all_components(self):
        self.client.force_login(self.user)

        response = self.client.get(self.availability_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Capacitor")
        self.assertContains(response, "Test Resistor")
        self.assertContains(response, "Test LED")
        self.assertContains(response, "Available")
        self.assertContains(response, "Low Stock")
        self.assertContains(response, "Out of Stock")

    def test_low_stock_page_requires_login(self):
        response = self.client.get(self.low_stock_url)
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self.low_stock_url}",
        )

    def test_low_stock_page_shows_only_positive_low_stock(self):
        self.client.force_login(self.user)

        response = self.client.get(self.low_stock_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Resistor")
        self.assertNotContains(response, "Test Capacitor")
        self.assertNotContains(response, "Test LED")
