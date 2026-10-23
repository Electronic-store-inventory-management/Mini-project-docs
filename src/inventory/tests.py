
from django.test import TestCase
from django.urls import reverse

from .models import Component


class ComponentAvailabilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
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

    def test_availability_statuses(self):
        self.assertEqual(
            self.available.availability_status, "Available"
        )
        self.assertEqual(
            self.low_stock.availability_status, "Low Stock"
        )
        self.assertEqual(
            self.out_of_stock.availability_status, "Out of Stock"
        )

    def test_availability_page(self):
        response = self.client.get(
            reverse("inventory:availability")
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Capacitor")
        self.assertContains(response, "Test Resistor")
        self.assertContains(response, "Test LED")

    def test_low_stock_page_only_shows_low_stock(self):
        response = self.client.get(
            reverse("inventory:low_stock")
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Resistor")
        self.assertNotContains(response, "Test Capacitor")
        self.assertNotContains(response, "Test LED")
