
import os
import re
from html.parser import HTMLParser

from locust import HttpUser, between, task
from locust.exception import StopUser


USERNAME = os.getenv("PERF_TEST_USERNAME", "perf_staff")
PASSWORD = os.getenv("PERF_TEST_PASSWORD")


SCENARIOS = {
    "id": {
        "query": "PERFLOAD05000",
        "label": "Component ID",
        "expected_column": 0,
        "expected_value": "PERFLOAD05000",
        "expected_field": "Component ID",
    },
    "name": {
        "query": "Performance Test Component 05000",
        "label": "Component Name",
        "expected_column": 1,
        "expected_value": "Performance Test Component 05000",
        "expected_field": "Component Name",
    },
    "category": {
        "query": "Passive Components",
        "label": "Category",
        "expected_column": 2,
        "expected_value": "Passive Components",
        "expected_field": "Category",
    },
}


SCENARIO_KEY = os.getenv("PERF_SEARCH_SCENARIO", "id").lower()

if SCENARIO_KEY not in SCENARIOS:
    raise ValueError(
        "PERF_SEARCH_SCENARIO must be id, name, or category"
    )

SCENARIO = SCENARIOS[SCENARIO_KEY]


class ComponentResultsParser(HTMLParser):
    """Extract actual component rows from the inventory results table."""

    def __init__(self):
        super().__init__(convert_charrefs=True)

        self.in_results_table = False
        self.in_tbody = False
        self.in_row = False
        self.in_cell = False

        self.current_cell = []
        self.current_row = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if (
            tag == "table"
            and "table" in attributes.get("class", "").split()
        ):
            self.in_results_table = True

        elif self.in_results_table and tag == "tbody":
            self.in_tbody = True

        elif self.in_tbody and tag == "tr":
            self.in_row = True
            self.current_row = []

        elif self.in_row and tag == "td":
            self.in_cell = True
            self.current_cell = []

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell.append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self.in_cell:
            cell_text = " ".join(
                "".join(self.current_cell).split()
            )
            self.current_row.append(cell_text)
            self.in_cell = False

        elif tag == "tr" and self.in_row:
            if self.current_row:
                self.rows.append(self.current_row)
            self.in_row = False

        elif tag == "tbody" and self.in_tbody:
            self.in_tbody = False

        elif tag == "table" and self.in_results_table:
            self.in_results_table = False


class ComponentSearchUser(HttpUser):
    wait_time = between(1, 2)

    login_url = "/accounts/login/"
    search_url = "/inventory/components/"

    def on_start(self):
        if not PASSWORD:
            raise StopUser("PERF_TEST_PASSWORD is not set.")

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
            raise StopUser("Could not obtain Django CSRF token.")

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
                raise StopUser("Performance-test login failed.")

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
                return

            parser = ComponentResultsParser()
            parser.feed(search_response.text)

            expected_column = SCENARIO["expected_column"]
            expected_value = SCENARIO["expected_value"]

            component_found = any(
                len(row) > expected_column
                and row[expected_column] == expected_value
                for row in parser.rows
            )

            if not component_found:
                search_response.failure(
                    f"Expected {SCENARIO['expected_field']} "
                    f"'{expected_value}' was not found in the "
                    "actual component results table."
                )
            else:
                search_response.success()
