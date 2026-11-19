
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.exceptions import ValidationError

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900  # 15 minutes per SRS AC-SR-006


class LoginForm(AuthenticationForm):
    """
    Staff Authentication Form with rate limiting per SAD Section 3.9
    and SRS AC-SR-006.

    After five consecutive failed attempts, further login attempts
    are blocked for a full 15 minutes from the fifth failed attempt.
    """

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autofocus': True,
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)

        self.error_messages['invalid_login'] = (
            "Invalid username or password. Please check your credentials and try again."
        )

    def _get_rate_limit_key(self, username):
        ip = self.request.META.get('REMOTE_ADDR', '127.0.0.1') if self.request else '127.0.0.1'
        normalized_user = (username or '').strip().lower()
        return f"login_fails_{ip}_{normalized_user}"

    def _get_lockout_key(self, username):
        return f"{self._get_rate_limit_key(username)}_lockout"

    def _get_rate_limit_error(self):
        return ValidationError(
            "Too many failed login attempts. For security reasons, please try again after 15 minutes.",
            code='rate_limited'
        )

    def clean(self):
        username = self.cleaned_data.get('username')

        if username:
            cache_key = self._get_rate_limit_key(username)
            lockout_key = self._get_lockout_key(username)

            # The separate lockout timer starts on the fifth failed attempt.
            if cache.get(lockout_key):
                raise self._get_rate_limit_error()

        try:
            cleaned = super().clean()

            # Successful authentication resets the failed-attempt counter.
            if username:
                cache.delete(cache_key)

            return cleaned

        except ValidationError as e:
            if username and 'invalid_login' in [
                getattr(err, 'code', None) for err in e.error_list
            ]:
                # Preserve the original atomic counter implementation.
                cache.add(
                    cache_key,
                    0,
                    timeout=LOCKOUT_DURATION_SECONDS
                )

                failed_attempts = cache.incr(cache_key)

                if failed_attempts >= MAX_FAILED_ATTEMPTS:
                    # Start a separate full 15-minute lockout now.
                    # cache.add prevents resetting an existing lockout timer.
                    cache.add(
                        lockout_key,
                        True,
                        timeout=LOCKOUT_DURATION_SECONDS
                    )

                    raise self._get_rate_limit_error()

            raise
