from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Component


User = get_user_model()


class ComponentListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="inventory_list_staff",
            password="SecurePass123!",
        )

    def test_component_list_requires_login(self):
        response = self.client.get(reverse("inventory:component-list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_component_list_empty_inventory(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("inventory:component-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No components found in the inventory.")

    def test_component_list_displays_component(self):
        component = Component.objects.create(
            component_id="C001",
            name="Test Resistor",
            category="Passive",
            manufacturer="Test Manufacturer",
            quantity=100,
            unit_price="0.10",
            supplier="Test Supplier",
            minimum_stock_level=10,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("inventory:component-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, component.component_id)
        self.assertContains(response, component.name)
        self.assertContains(response, str(component.quantity))


class ComponentAddTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="add_staff",
            password="SecurePass123!",
        )

        # Existing component for the duplicate-ID test
        cls.existing = Component.objects.create(
            component_id="DUP001",
            name="Existing Resistor",
            category="Passive",
            manufacturer="Existing Manufacturer",
            quantity=10,
            unit_price="0.20",
            supplier="Existing Supplier",
            minimum_stock_level=5,
        )

        # Component fixtures for availability and low-stock tests
        cls.available = Component.objects.create(
            component_id="AV001",
            name="Available Capacitor",
            category="Passive",
            manufacturer="Test Manufacturer",
            quantity=20,
            unit_price="5.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

        cls.low_stock = Component.objects.create(
            component_id="LS001",
            name="Low Stock Resistor",
            category="Passive",
            manufacturer="Test Manufacturer",
            quantity=3,
            unit_price="2.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

        cls.at_minimum = Component.objects.create(
            component_id="LS002",
            name="Minimum Stock Diode",
            category="Semiconductor",
            manufacturer="Test Manufacturer",
            quantity=5,
            unit_price="1.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

        cls.out_of_stock = Component.objects.create(
            component_id="OS001",
            name="Out of Stock LED",
            category="Optoelectronic",
            manufacturer="Test Manufacturer",
            quantity=0,
            unit_price="3.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

    def test_add_component_unauthenticated_redirect(self):
        response = self.client.get(reverse("inventory:component-add"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_add_component_get_shows_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("inventory:component-add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")
        self.assertContains(response, "name=\"component_id\"")

    def test_add_component_valid_post_creates(self):
        self.client.force_login(self.user)
        post_data = {
            "component_id": "NEW001",
            "name": "New Capacitor",
            "category": "Passive",
            "manufacturer": "New Manufacturer",
            "quantity": 50,
            "unit_price": "0.50",
            "supplier": "New Supplier",
            "minimum_stock_level": 5,
        }

        response = self.client.post(
            reverse("inventory:component-add"),
            post_data,
        )

        self.assertRedirects(
            response,
            reverse("inventory:component-list"),
            fetch_redirect_response=False,
        )
        self.assertTrue(
            Component.objects.filter(component_id="NEW001").exists()
        )

        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Component added successfully")

    def test_add_component_duplicate_id(self):
        self.client.force_login(self.user)
        post_data = {
            "component_id": "DUP001",  # same as existing
            "name": "Dup Capacitor",
            "category": "Passive",
            "manufacturer": "Dup Manufacturer",
            "quantity": 20,
            "unit_price": "0.30",
            "supplier": "Dup Supplier",
            "minimum_stock_level": 5,
        }
        response = self.client.post(reverse("inventory:component-add"), post_data)
        self.assertEqual(response.status_code, 200)
        # Should not create a second record
        self.assertEqual(Component.objects.filter(component_id="DUP001").count(), 1)
        self.assertContains(response, "Component with this Component Id already exists")

    def test_add_component_negative_minimum_stock_level(self):
        self.client.force_login(self.user)
        post_data = {
            "component_id": "NEGMIN",
            "name": "Negative Minimum Stock",
            "category": "Passive",
            "manufacturer": "Test Manufacturer",
            "quantity": 10,
            "unit_price": "1.00",
            "supplier": "Test Supplier",
            "minimum_stock_level": -1,
        }

        response = self.client.post(
            reverse("inventory:component-add"),
            post_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Component.objects.filter(component_id="NEGMIN").exists()
        )
        self.assertContains(response, "Minimum stock level cannot be negative")

    def test_add_component_negative_quantity(self):
        self.client.force_login(self.user)
        post_data = {
            "component_id": "NEG001",
            "name": "Neg Qty",
            "category": "Passive",
            "manufacturer": "Neg Manufacturer",
            "quantity": -5,
            "unit_price": "0.10",
            "supplier": "Neg Supplier",
            "minimum_stock_level": 1,
        }
        response = self.client.post(reverse("inventory:component-add"), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Component.objects.filter(component_id="NEG001").exists())
        self.assertContains(response, "Quantity cannot be negative")

    def test_add_component_negative_price(self):
        self.client.force_login(self.user)
        post_data = {
            "component_id": "NEGPRICE",
            "name": "Neg Price",
            "category": "Passive",
            "manufacturer": "Neg Manufacturer",
            "quantity": 10,
            "unit_price": "-0.10",
            "supplier": "Neg Supplier",
            "minimum_stock_level": 1,
        }
        response = self.client.post(reverse("inventory:component-add"), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Component.objects.filter(component_id="NEGPRICE").exists())
        self.assertContains(response, "Unit price cannot be negative")


    def test_availability_statuses(self):
        self.assertEqual(self.available.availability_status, "Available")
        self.assertEqual(self.low_stock.availability_status, "Low Stock")
        self.assertEqual(self.at_minimum.availability_status, "Low Stock")
        self.assertEqual(self.out_of_stock.availability_status, "Out of Stock")

    def test_availability_page_requires_login(self):
        url = reverse("inventory:availability")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_availability_page_shows_all_components_and_statuses(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("inventory:availability"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Available Capacitor")
        self.assertContains(response, "Low Stock Resistor")
        self.assertContains(response, "Minimum Stock Diode")
        self.assertContains(response, "Out of Stock LED")
        self.assertContains(response, "Available")
        self.assertContains(response, "Low Stock")
        self.assertContains(response, "Out of Stock")

    def test_low_stock_page_requires_login(self):
        url = reverse("inventory:low_stock")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_low_stock_page_shows_only_positive_low_stock(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("inventory:low_stock"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Low Stock Resistor")
        self.assertContains(response, "Minimum Stock Diode")
        self.assertNotContains(response, "Available Capacitor")
        self.assertNotContains(response, "Out of Stock LED")
