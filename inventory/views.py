from django.contrib.auth.decorators import login_required
from django.shortcuts import render


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
