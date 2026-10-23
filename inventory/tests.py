from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()

def component_model_exists():
    try:
        apps.get_model('inventory', 'Component')
        return True
    except LookupError:
        return False

class ComponentListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = 'TestPass123!'
        cls.user = User.objects.create_user(username='teststaff', password=cls.password, email='staff@example.com')
        if hasattr(cls.user, 'role'):
            # Assign staff role if the custom user model defines it
            cls.user.role = getattr(User.Role, 'STAFF', None)
            cls.user.save()

    def setUp(self):
        self.client = Client()
        self.url = reverse('inventory:component-list')

    def test_unauthenticated_redirect(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_authenticated_missing_model_notice(self):
        """Show an integration notice when the Component model is absent."""
        if component_model_exists():
            self.skipTest(
                'Component model is present; missing-model case does not apply'
            )

        self.client.login(
            username='teststaff',
            password=self.password,
        )
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Component inventory is not available yet.',
        )

    def test_authenticated_empty_inventory(self):
        """Show the empty-state message when no components exist."""
        if not component_model_exists():
            self.skipTest('Component model not available in this branch')

        Component = apps.get_model('inventory', 'Component')
        Component.objects.all().delete()

        self.client.login(
            username='teststaff',
            password=self.password,
        )
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No components found in the inventory.',
        )

    def test_authenticated_with_components(self):
        """Create a Component record if the model exists and verify rendering.
        The test is skipped when the Component model is not present in this branch.
        """
        if not component_model_exists():
            self.skipTest('Component model not available in this branch')
        Component = apps.get_model('inventory', 'Component')
        # Minimal required fields – adjust if model signature differs.
        comp = Component.objects.create(
            component_id='C001',
            name='Resistor',
            category='Passive',
            manufacturer='Acme Corp',
            quantity=100,
            unit_price=0.10,
            supplier='ElectroSupply',
            minimum_stock_level=10,
        )
        self.client.login(username='teststaff', password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, comp.component_id)
        self.assertContains(response, comp.name)
        self.assertContains(response, str(comp.quantity))


class ComponentAvailabilityAndLowStockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="availability_staff",
            password="SecurePass123!",
        )

        Component = apps.get_model("inventory", "Component")

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

    def test_availability_page_requires_login(self):
        url = reverse("inventory:availability")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_availability_page_shows_all_statuses(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("inventory:availability"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Available Capacitor")
        self.assertContains(response, "Low Stock Resistor")
        self.assertContains(response, "Out of Stock LED")
        self.assertContains(response, "Available")
        self.assertContains(response, "Low Stock")
        self.assertContains(response, "Out of Stock")

    def test_low_stock_page_requires_login(self):
        url = reverse("inventory:low_stock")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_low_stock_page_includes_only_positive_low_stock(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("inventory:low_stock"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Low Stock Resistor")
        self.assertContains(response, "Minimum Stock Diode")
        self.assertNotContains(response, "Available Capacitor")
        self.assertNotContains(response, "Out of Stock LED")
