from .settings import *

# Force all performance tests to use the isolated database.
DATABASES = {
    "default": {
        **DATABASES["default"],
        "NAME": "electronics_inventory_perf",
    }
}