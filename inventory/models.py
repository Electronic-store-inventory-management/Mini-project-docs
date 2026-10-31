
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class ComponentQuerySet(models.QuerySet):
    """QuerySet methods that preserve Component validation."""

    def bulk_create(self, objs, **kwargs):
        objs = list(objs)

        for obj in objs:
            obj.full_clean()

        return super().bulk_create(objs, **kwargs)

    def bulk_update(self, objs, fields, batch_size=None):
        objs = list(objs)

        for obj in objs:
            obj.full_clean()

        return super().bulk_update(
            objs,
            fields,
            batch_size=batch_size,
        )

    def update(self, **kwargs):
        protected_fields = {
            "component_id",
            "name",
            "category",
            "manufacturer",
            "supplier",
        }

        modified_fields = protected_fields.intersection(kwargs)

        if modified_fields:
            raise ValidationError(
                "QuerySet.update() cannot modify validated text fields. "
                "Use normal model saves so validation is performed."
            )

        return super().update(**kwargs)


class Component(models.Model):
    component_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=150)
    minimum_stock_level = models.PositiveIntegerField(default=5)

    objects = ComponentQuerySet.as_manager()

    def clean(self):
        super().clean()

        text_fields = [
            "component_id",
            "name",
            "category",
            "manufacturer",
            "supplier",
        ]

        errors = {}

        for field in text_fields:
            value = getattr(self, field, None)

            if value is not None and not value.strip():
                errors[field] = (
                    "This field cannot be empty or contain only spaces."
                )

        if self.quantity is not None and self.quantity < 0:
            errors["quantity"] = "Quantity cannot be negative."

        if (
            self.minimum_stock_level is not None
            and self.minimum_stock_level < 0
        ):
            errors["minimum_stock_level"] = (
                "Minimum stock level cannot be negative."
            )

        if self.unit_price is not None and self.unit_price < 0:
            errors["unit_price"] = "Unit price cannot be negative."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Validate the model before performing a normal save."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_availability_status(self):
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
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gte=0),
                name="component_quantity_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(unit_price__gte=0),
                name="component_price_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(minimum_stock_level__gte=0),
                name="component_min_stock_nonnegative",
            ),
        ]
