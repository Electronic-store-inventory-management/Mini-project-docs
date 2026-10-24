'''Forms for the inventory app.

Provides a ModelForm for adding a Component with validation.
'''

from django import forms
from django.core.exceptions import ValidationError
from .models import Component


class ComponentForm(forms.ModelForm):
    """Form for creating a new Component.

    Validation rules:
    * ``component_id`` must be unique (enforced by model).
    * ``quantity`` and ``minimum_stock_level`` must be non‑negative integers.
    * ``unit_price`` must be a non‑negative decimal.
    """


    quantity = forms.IntegerField(
        min_value=0,
        error_messages={"min_value": "Quantity cannot be negative"},
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0}),
    )
    unit_price = forms.DecimalField(
        min_value=0,
        error_messages={"min_value": "Unit price cannot be negative"},
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
    )
    minimum_stock_level = forms.IntegerField(
        min_value=0,
        error_messages={"min_value": "Minimum stock level cannot be negative"},
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0}),
    )

    class Meta:
        model = Component
        fields = [
            "component_id",
            "name",
            "category",
            "manufacturer",
            "quantity",
            "unit_price",
            "supplier",
            "minimum_stock_level",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "manufacturer": forms.TextInput(attrs={"class": "form-control"}),
            "supplier": forms.TextInput(attrs={"class": "form-control"}),
        }
        error_messages = {
            "component_id": {
                "unique": "Component with this Component Id already exists",
            },
        }

    def clean_quantity(self):
        qty = self.cleaned_data.get("quantity")
        if qty is not None and qty < 0:
            raise ValidationError("Quantity cannot be negative.")
        return qty

    def clean_minimum_stock_level(self):
        lvl = self.cleaned_data.get("minimum_stock_level")
        if lvl is not None and lvl < 0:
            raise ValidationError("Minimum stock level cannot be negative.")
        return lvl

    def clean_unit_price(self):
        price = self.cleaned_data.get("unit_price")
        if price is not None and price < 0:
            raise ValidationError("Unit price cannot be negative.")
        return price
