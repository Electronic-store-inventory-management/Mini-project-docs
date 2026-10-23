
from django.db import models


class Component(models.Model):
    component_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=150)
    minimum_stock_level = models.PositiveIntegerField(default=5)

    def get_availability_status(self):
        """Return the stock status according to the project SRS."""
        if self.quantity == 0:
            return "Out of Stock"
        elif self.quantity <= self.minimum_stock_level:
            return "Low Stock"
        return "Available"

    @property
    def availability_status(self):
        return self.get_availability_status()

    @property
    def is_low_stock(self):
        return 0 < self.quantity <= self.minimum_stock_level

    @property
    def is_out_of_stock(self):
        return self.quantity == 0

    def __str__(self):
        return f"{self.component_id} - {self.name}"

    class Meta:
        ordering = ["name"]
