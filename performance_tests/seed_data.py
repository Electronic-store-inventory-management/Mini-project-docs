
import os
import sys
from pathlib import Path
from decimal import Decimal

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Always force the isolated performance settings.
# Do not allow an inherited DJANGO_SETTINGS_MODULE to select
# the normal application database.
os.environ["DJANGO_SETTINGS_MODULE"] = "config.performance_settings"

import django
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.db.models.query import QuerySet

from inventory.models import Component


DATABASE_NAME = "electronics_inventory_perf"
PREFIX = "PERFLOAD"
TOTAL_RECORDS = 10_000

PERF_USERNAME = os.environ.get("PERF_TEST_USERNAME", "perf_staff")
PERF_PASSWORD = os.environ.get("PERF_TEST_PASSWORD")

CATEGORIES = [
    "Passive Components",
    "Active Components",
    "Optoelectronic Components",
    "Semiconductors",
]


def seed_database():
    if not PERF_PASSWORD:
        raise SystemExit(
            "Set PERF_TEST_PASSWORD before running this script."
        )

    # Safety check 1: verify the Django database configuration.
    configured_database = settings.DATABASES["default"]["NAME"]

    if configured_database != DATABASE_NAME:
        raise SystemExit(
            f"STOP: Django is configured for {configured_database}, "
            f"not {DATABASE_NAME}."
        )

    # Safety check 2: verify the actual MySQL connection.
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE()")
        current_database = cursor.fetchone()[0]

    if current_database != DATABASE_NAME:
        raise SystemExit(
            f"STOP: Connected to {current_database}, "
            f"not {DATABASE_NAME}."
        )

    unexpected = Component.objects.exclude(
        component_id__startswith=PREFIX
    ).count()

    if unexpected:
        raise SystemExit(
            "Unexpected component records found. "
            "Refusing to modify the database."
        )

    records = []

    for i in range(1, TOTAL_RECORDS + 1):
        quantity = 0 if i % 10 == 0 else i % 50

        records.append(
            Component(
                component_id=f"{PREFIX}{i:05d}",
                name=f"Performance Test Component {i:05d}",
                category=CATEGORIES[i % len(CATEGORIES)],
                manufacturer="Performance Test Manufacturer",
                quantity=quantity,
                unit_price=Decimal(f"{(i % 500) + 1}.00"),
                supplier="Performance Test Supplier",
                minimum_stock_level=5,
            )
        )

    User = get_user_model()

    with transaction.atomic():
        # Remove only previous performance-test records.
        Component.objects.filter(
            component_id__startswith=PREFIX
        ).delete()

        # Bulk insert without invoking per-object validation.
        QuerySet.bulk_create(
            Component.objects.all(),
            records,
            batch_size=1000,
        )

        user, created = User.objects.get_or_create(
            username=PERF_USERNAME,
            defaults={"role": User.Role.STAFF},
        )

        user.set_password(PERF_PASSWORD)
        user.role = User.Role.STAFF
        user.save(update_fields=["password", "role"])

    actual_count = Component.objects.filter(
        component_id__startswith=PREFIX
    ).count()

    if actual_count != TOTAL_RECORDS:
        raise RuntimeError(
            f"Expected {TOTAL_RECORDS} records, "
            f"but found {actual_count}."
        )

    print("\nPerformance data created successfully!")
    print(f"Database: {current_database}")
    print(f"Component records: {actual_count}")
    print(f"Test username: {PERF_USERNAME}")
    print(f"Test account created: {created}")


if __name__ == "__main__":
    seed_database()
