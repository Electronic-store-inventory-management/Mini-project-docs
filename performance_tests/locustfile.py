
import os
import re

from locust import HttpUser, between, task
from locust.exception import StopUser


USERNAME = os.environ.get("PERF_TEST_USERNAME", "perf_staff")
PASSWORD = os.environ.get("PERF_TEST_PASSWORD")


class InventoryUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        if not PASSWORD:
            raise StopUser("PERF_TEST_PASSWORD is not configured.")

        # Open login page and obtain the CSRF token.
        login_page = self.client.get(
            "/accounts/login/",
            name="Authentication - Login page",
        )

        if login_page.status_code != 200:
            raise StopUser("Could not open the login page.")

        match = re.search(
            r'<input[^>]*name=["\']csrfmiddlewaretoken["\']'
            r'[^>]*value=["\']([^"\']+)["\']',
            login_page.text,
            re.IGNORECASE,
        )

        if not match:
            raise StopUser("Could not obtain the login CSRF token.")

        csrf_token = match.group(1)

        # Log in. Each virtual user maintains its own session.
        with self.client.post(
            "/accounts/login/",
            data={
                "username": USERNAME,
                "password": PASSWORD,
                "csrfmiddlewaretoken": csrf_token,
            },
            headers={"Referer": self.host + "/accounts/login/"},
            name="Authentication - Login",
            catch_response=True,
        ) as response:

            if (
                response.status_code != 200
                or "/accounts/login/" in response.url
            ):
                response.failure("Login failed.")
                raise StopUser("Authentication unsuccessful.")

            response.success()

    def visit_page(self, path, label):
        with self.client.get(
            path,
            name=label,
            catch_response=True,
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"Unexpected HTTP status: {response.status_code}"
                )
            else:
                response.success()

    @task(5)
    def view_components(self):
        self.visit_page(
            "/inventory/components/",
            "Inventory - Component list",
        )

    @task(3)
    def view_availability(self):
        self.visit_page(
            "/inventory/availability/",
            "Inventory - Availability",
        )

    @task(2)
    def view_low_stock(self):
        self.visit_page(
            "/inventory/low-stock/",
            "Inventory - Low stock",
        )

    @task(2)
    def view_out_of_stock(self):
        self.visit_page(
            "/inventory/out-of-stock/",
            "Inventory - Out of stock",
        )

    @task(3)
    def search_components(self):
        self.visit_page(
            "/inventory/components/?q=PERFLOAD05000",
            "Inventory - Component search",
        )

    @task(1)
    def view_dashboard(self):
        self.visit_page(
            "/dashboard/",
            "Dashboard - Statistics",
        )
