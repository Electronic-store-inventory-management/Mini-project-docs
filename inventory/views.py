from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.apps import apps
from django.db.models import F


@login_required
def landing_page(request):
    """
    Minimal protected inventory landing page satisfying US-01 Acceptance Criteria.
    Restricted to authenticated store personnel (Staff, Manager, Admin).
    """
    context = {
        'page_title': 'Inventory Management',
        'user': request.user,
    }
    return render(request, 'inventory/landing.html', context)


# US-02 – Component list view (authentication protected)
@login_required
def component_list(request):
    """Render a table of all Component records.

    If the ``Component`` model is not yet available (e.g., US‑07/US‑08 not merged),
    we display a clear integration notice instead of an empty‑inventory message.
    """
    try:
        Component = apps.get_model('inventory', 'Component')
        model_missing = False
    except LookupError:
        Component = None
        model_missing = True

    components = Component.objects.all() if Component else []

    context = {
        'page_title': 'Component Inventory',
        'components': components,
        'model_missing': model_missing,
    }
    return render(request, 'inventory/component_list.html', context)

# US-07: View component availability
@login_required
def availability(request):
    components = apps.get_model('inventory', 'Component').objects.all()
    return render(
        request,
        'inventory/availability.html',
        {
            'page_title': 'Component Availability',
            'components': components,
        },
    )


# US-08: View low-stock components
@login_required
def low_stock(request):
    Component = apps.get_model('inventory', 'Component')
    components = Component.objects.filter(
        quantity__gt=0,
        quantity__lte=F('minimum_stock_level'),
    )
    return render(
        request,
        'inventory/low_stock.html',
        {
            'page_title': 'Low-Stock Components',
            'components': components,
        },
    )
