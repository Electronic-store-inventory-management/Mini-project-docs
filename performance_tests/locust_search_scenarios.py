
import os
import re

from locust import HttpUser, between, task


USERNAME = os.getenv("PERF_TEST_USERNAME", "perf_staff")
PASSWORD = os.getenv("PERF_TEST_PASSWORD")

SCENARIOS = {
    "id": {
        "query": "PERFLOAD05000",
        "label": "Component ID",
    },
    "name": {
        "query": "Performance Test Component 05000",
        "label": "Component Name",
    },
    "category": {
        "query": "Passive Components",
        "label": "Category",
    },
}

SCENARIO_KEY = os.getenv("PERF_SEARCH_SCENARIO", "id").lower()

if SCENARIO_KEY not in SCENARIOS:
    raise ValueError("PERF_SEARCH_SCENARIO must be id, name, or category")

SCENARIO = SCENARIOS[SCENARIO_KEY]


class ComponentSearchUser(HttpUser):
    wait_time = between(1, 2)

    login_url = "/accounts/login/"
    search_url = "/inventory/components/"

    def on_start(self):
        if not PASSWORD:
            raise RuntimeError("PERF_TEST_PASSWORD is not set.")

        response = self.client.get(
            self.login_url,
            name="Authentication - Login page",
        )

        csrf_token = self.client.cookies.get("csrftoken")

        if not csrf_token:
            match = re.search(
                r"""name=["']csrfmiddlewaretoken["'][^>]*value=["']([^"']+)["']""",
                response.text,
            )

            if match:
                csrf_token = match.group(1)

        if not csrf_token:
            raise RuntimeError("Could not obtain Django CSRF token.")

        with self.client.post(
            self.login_url,
            data={
                "username": USERNAME,
                "password": PASSWORD,
                "csrfmiddlewaretoken": csrf_token,
            },
            headers={"Referer": self.host + self.login_url},
            name="Authentication - Login",
            catch_response=True,
            allow_redirects=False,
        ) as login_response:

            location = login_response.headers.get("Location", "")

            if (
                login_response.status_code in (301, 302, 303)
                and "/accounts/login" not in location
            ):
                login_response.success()
            else:
                login_response.failure(
                    f"Login unsuccessful: HTTP {login_response.status_code}"
                )
                raise RuntimeError("Performance-test login failed.")

    @task
    def search_component(self):
        with self.client.get(
            self.search_url,
            params={"q": SCENARIO["query"]},
            name=f"Search - {SCENARIO['label']}",
            catch_response=True,
            allow_redirects=False,
        ) as search_response:

            if search_response.status_code != 200:
                search_response.failure(
                    f"Unexpected HTTP status: {search_response.status_code}"
                )
            elif SCENARIO["query"] not in search_response.text:
                search_response.failure(
                    "Search response did not contain the requested query."
                )
            else:
                search_response.success()
