from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.exceptions import ValidationError

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900  # 15 minutes per SRS AC-SR-006


class LoginForm(AuthenticationForm):
    """
    Staff Authentication Form with built-in rate limiting per SAD Section 3.9
    and SRS AC-SR-006 (blocks user after 5 consecutive failed attempts for 15 minutes).
    Generic error messages prevent account enumeration and credential leakage.
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
        # Non-sensitive error message per SAD 3.9 Information disclosure mitigation
        self.error_messages['invalid_login'] = (
            "Invalid username or password. Please check your credentials and try again."
        )

    def _get_rate_limit_key(self, username):
        ip = self.request.META.get('REMOTE_ADDR', '127.0.0.1') if self.request else '127.0.0.1'
        normalized_user = (username or '').strip().lower()
        return f"login_fails_{ip}_{normalized_user}"

    def clean(self):
        username = self.cleaned_data.get('username')

        if username:
            cache_key = self._get_rate_limit_key(username)
            # Check current count (may be missing)
            failed_attempts = cache.get(cache_key, 0)
            if failed_attempts >= MAX_FAILED_ATTEMPTS:
                raise ValidationError(
                    "Too many failed login attempts. For security reasons, please try again after 15 minutes.",
                    code='rate_limited'
                )

        try:
            cleaned = super().clean()
            # Successful authentication -> reset counter
            if username:
                cache.delete(cache_key)
            return cleaned
        except ValidationError as e:
            # Increment only on invalid credentials
            if username and 'invalid_login' in [getattr(err, 'code', None) for err in e.error_list]:
                cache_key = self._get_rate_limit_key(username)
                # Ensure the key exists with the correct expiry. `add` only sets if missing.
                cache.add(cache_key, 0, timeout=LOCKOUT_DURATION_SECONDS)
                failed_attempts = cache.incr(cache_key)
                if failed_attempts >= MAX_FAILED_ATTEMPTS:
                    raise ValidationError(
                        "Too many failed login attempts. For security reasons, please try again after 15 minutes.",
                        code='rate_limited'
                    )
            raise e

