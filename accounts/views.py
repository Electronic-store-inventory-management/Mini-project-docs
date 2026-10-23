from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .forms import LoginForm


class UserLoginView(LoginView):
    """
    Handles staff user authentication using Django's built-in session framework.
    Redirects authenticated users to the protected inventory landing page.
    """
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        # Redirect to 'next' parameter if present, otherwise default to inventory landing
        redirect_to = self.get_redirect_url()
        return redirect_to or reverse_lazy('inventory:landing')


class UserLogoutView(LogoutView):
    """
    Handles staff logout via Django's secure POST flow.
    Flushes user session and redirects to login page.
    """
    next_page = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You have been successfully logged out.")
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # If user directly visits logout URL via GET, redirect safely to login page
        return redirect(reverse_lazy('login'))
