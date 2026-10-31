
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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


class ComponentAddTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="add_staff",
            password="SecurePass123!",
        )

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
        self.assertContains(response, 'name="component_id"')

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
            "component_id": "DUP001",
            "name": "Dup Capacitor",
            "category": "Passive",
            "manufacturer": "Dup Manufacturer",
            "quantity": 20,
            "unit_price": "0.30",
            "supplier": "Dup Supplier",
            "minimum_stock_level": 5,
        }

        response = self.client.post(
            reverse("inventory:component-add"),
            post_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Component.objects.filter(component_id="DUP001").count(),
            1,
        )
        self.assertContains(
            response,
            "Component with this Component Id already exists",
        )

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
        self.assertContains(
            response,
            "Minimum stock level cannot be negative",
        )

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

        response = self.client.post(
            reverse("inventory:component-add"),
            post_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Component.objects.filter(component_id="NEG001").exists()
        )
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

        response = self.client.post(
            reverse("inventory:component-add"),
            post_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Component.objects.filter(component_id="NEGPRICE").exists()
        )
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


class ComponentIntegrityTests(TestCase):
    def create_component(self, component_id="TEST001", **overrides):
        data = {
            "component_id": component_id,
            "name": "Test Component",
            "category": "Electronics",
            "manufacturer": "Test Manufacturer",
            "quantity": 10,
            "unit_price": "10.00",
            "supplier": "Test Supplier",
            "minimum_stock_level": 5,
        }
        data.update(overrides)
        return Component.objects.create(**data)

    def test_whitespace_only_text_fields_are_rejected(self):
        text_fields = [
            "component_id",
            "name",
            "category",
            "manufacturer",
            "supplier",
        ]

        for field in text_fields:
            with self.subTest(field=field):
                data = {
                    "component_id": "SPACE001",
                    "name": "Valid Component",
                    "category": "Electronics",
                    "manufacturer": "Test Manufacturer",
                    "supplier": "Test Supplier",
                    "quantity": 10,
                    "unit_price": "10.00",
                    "minimum_stock_level": 5,
                }
                data[field] = "   "
                component = Component(**data)

                with self.assertRaises(ValidationError):
                    component.save()

                self.assertFalse(
                    Component.objects.filter(
                        component_id="SPACE001"
                    ).exists()
                )

    def test_negative_values_are_rejected_by_model(self):
        invalid_values = [
            {"quantity": -1},
            {"unit_price": "-1.00"},
            {"minimum_stock_level": -1},
        ]

        for index, values in enumerate(invalid_values):
            with self.subTest(values=values):
                component = Component(
                    component_id=f"INVALID{index}",
                    name="Valid Component",
                    category="Electronics",
                    manufacturer="Test Manufacturer",
                    quantity=10,
                    unit_price="10.00",
                    supplier="Test Supplier",
                    minimum_stock_level=5,
                )

                for field, value in values.items():
                    setattr(component, field, value)

                with self.assertRaises(ValidationError):
                    component.save()

    def test_existing_record_remains_unchanged_after_other_record_operations(self):
        original = self.create_component(
            component_id="KEEP001",
            name="Original Component",
            quantity=25,
        )

        self.create_component(
            component_id="NEW002",
            name="New Component",
        )

        new_component = Component.objects.get(component_id="NEW002")
        new_component.delete()
        original.refresh_from_db()

        self.assertEqual(original.name, "Original Component")
        self.assertEqual(original.quantity, 25)
        self.assertTrue(
            Component.objects.filter(component_id="KEEP001").exists()
        )

    def test_bulk_create_inserts_100_inventory_records(self):
        components = [
            Component(
                component_id=f"BULK{i:04d}",
                name=f"Component {i}",
                category="Electronics",
                manufacturer="Test Manufacturer",
                quantity=100,
                unit_price="5.00",
                supplier="Test Supplier",
                minimum_stock_level=10,
            )
            for i in range(100)
        ]

        Component.objects.bulk_create(components)

        self.assertEqual(
            Component.objects.filter(
                component_id__startswith="BULK"
            ).count(),
            100,
        )

    def test_bulk_create_rejects_whitespace_only_fields(self):
        component = Component(
            component_id="BULK001",
            name="   ",
            category="Electronics",
            manufacturer="Test Manufacturer",
            quantity=10,
            unit_price="5.00",
            supplier="Test Supplier",
            minimum_stock_level=5,
        )

        with self.assertRaises(ValidationError):
            Component.objects.bulk_create([component])

        self.assertFalse(
            Component.objects.filter(component_id="BULK001").exists()
        )

    def test_bulk_update_rejects_whitespace_only_fields(self):
        component = self.create_component(
            component_id="BULK002",
            name="Valid Component",
        )
        component.name = "   "

        with self.assertRaises(ValidationError):
            Component.objects.bulk_update([component], ["name"])

        component.refresh_from_db()
        self.assertEqual(component.name, "Valid Component")

    def test_queryset_update_rejects_whitespace_only_fields(self):
        component = self.create_component(
            component_id="BULK003",
            name="Valid Component",
        )

        with self.assertRaises(ValidationError):
            Component.objects.filter(pk=component.pk).update(name="   ")

        component.refresh_from_db()
        self.assertEqual(component.name, "Valid Component")

    def test_bulk_update_accepts_valid_data(self):
        component = self.create_component(
            component_id="BULK004",
            quantity=10,
        )
        component.quantity = 25

        updated_count = Component.objects.bulk_update(
            [component],
            ["quantity"],
        )

        component.refresh_from_db()
        self.assertEqual(updated_count, 1)
        self.assertEqual(component.quantity, 25)
