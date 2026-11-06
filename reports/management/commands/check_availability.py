import time
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from reports.services import record_availability_check


class Command(BaseCommand):
    help = "Check system availability and record failures."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            default="http://127.0.0.1:8000/reports/health/",
        )
        parser.add_argument(
            "--loop",
            action="store_true",
            help="Keep checking continuously.",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=60,
            help="Seconds between checks.",
        )

    def handle(self, *args, **options):
        url = options["url"]
        interval = options["interval"]

        if interval < 1:
            self.stderr.write("Interval must be at least 1 second.")
            return

        while True:
            try:
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "InventoryAvailabilityMonitor"},
                )

                with urllib.request.urlopen(request, timeout=5) as response:
                    is_available = response.status == 200
                    reason = "" if is_available else (
                        f"HTTP status {response.status}"
                    )

            except (urllib.error.URLError, TimeoutError, OSError) as error:
                is_available = False
                reason = str(error)

            record_availability_check(
                is_available=is_available,
                failure_reason=reason,
            )

            if is_available:
                self.stdout.write(self.style.SUCCESS("System is available."))
            else:
                self.stderr.write(
                    self.style.ERROR(f"System failure: {reason}")
                )

            if not options["loop"]:
                break

            time.sleep(interval)