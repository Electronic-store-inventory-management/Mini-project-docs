
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import ComponentForm
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


class ComponentAvailabilityAndLowStockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="availability_staff",
            password="SecurePass123!",
        )

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

    def test_out_of_stock_page_requires_login(self):
        response = self.client.get(reverse("inventory:out_of_stock"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_out_of_stock_page_shows_only_zero_quantity_components(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("inventory:out_of_stock"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Out of Stock LED")
        self.assertContains(response, "Out of Stock")
        self.assertNotContains(response, "Available Capacitor")
        self.assertNotContains(response, "Low Stock Resistor")
        self.assertNotContains(response, "Minimum Stock Diode")


class ComponentDuplicateIdTests(TestCase):
    def test_duplicate_component_id_is_rejected(self):
        Component.objects.create(
            component_id="DUP001",
            name="Existing Resistor",
            category="Passive",
            manufacturer="Test Manufacturer",
            quantity=10,
            unit_price="2.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

        form = ComponentForm(
            data={
                "component_id": "DUP001",
                "name": "Another Resistor",
                "category": "Passive",
                "manufacturer": "Another Manufacturer",
                "quantity": 20,
                "unit_price": "3.00",
                "supplier": "Another Supplier",
                "minimum_stock_level": 5,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "A component with this Component ID already exists.",
            form.errors["component_id"],
        )

    def test_unique_component_id_is_accepted(self):
        form = ComponentForm(
            data={
                "component_id": "UNQ001",
                "name": "Unique Resistor",
                "category": "Passive",
                "manufacturer": "Test Manufacturer",
                "quantity": 10,
                "unit_price": "2.00",
                "supplier": "Test Supplier",
                "minimum_stock_level": 5,
            }
        )

        self.assertTrue(form.is_valid())

class DeleteComponentViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="delete_component_staff",
            password="SecurePass123!",
        )

        cls.component = Component.objects.create(
            component_id="DEL001",
            name="Delete Test Resistor",
            category="Passive",
            manufacturer="Test Manufacturer",
            quantity=10,
            unit_price="2.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

    def test_delete_component_requires_login(self):
        url = reverse(
            "inventory:delete_component",
            args=[self.component.pk],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertTrue(
            Component.objects.filter(pk=self.component.pk).exists()
        )

    def test_get_shows_confirmation_without_deleting(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "inventory:delete_component",
                args=[self.component.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete Test Resistor")
        self.assertContains(response, "DEL001")
        self.assertContains(response, "Confirm Delete")
        self.assertTrue(
            Component.objects.filter(pk=self.component.pk).exists()
        )

    def test_post_deletes_component_and_shows_success(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "inventory:delete_component",
                args=[self.component.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Component deleted successfully.")
        self.assertFalse(
            Component.objects.filter(pk=self.component.pk).exists()
        )

    def test_nonexistent_component_returns_404(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("inventory:delete_component", args=[999999])
        )

        self.assertEqual(response.status_code, 404)
