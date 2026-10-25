from django import forms
from .models import Component


class ComponentForm(forms.ModelForm):
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

    def clean_component_id(self):
        component_id = self.cleaned_data["component_id"]

        if Component.objects.filter(component_id=component_id).exists():
            raise forms.ValidationError(
                "A component with this Component ID already exists."
            )

        return component_id