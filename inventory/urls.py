
from django.urls import path

from .views import (
    landing_page,
    component_list,
    availability,
    low_stock,
    add_component,
    out_of_stock,
    delete_component,
)

app_name = "inventory"

urlpatterns = [
    path("", landing_page, name="landing"),
    path("components/", component_list, name="component-list"),
    path("availability/", availability, name="availability"),
    path("low-stock/", low_stock, name="low_stock"),
    path("add/", add_component, name="component-add"),
    path("out-of-stock/", out_of_stock, name="out_of_stock"),
    path(
        "components/delete/<int:component_id>/",
        delete_component,
        name="delete_component",
    ),
]
