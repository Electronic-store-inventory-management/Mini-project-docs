from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for the Electronics Store Inventory Management System.
    Implements SAD Section 3.6 data store specification:
      User: id, username, password hash, role
    and Section 3.4 component specification:
      Auth Service checks role (Admin, Manager, Staff) before actions are allowed.
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        STAFF = 'STAFF', 'Staff'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STAFF,
        help_text="Role determining user authorization (Admin, Manager, Staff)."
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        """Returns True if user has Admin role or superuser status."""
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_manager_role(self):
        """Returns True if user has Manager role."""
        return self.role == self.Role.MANAGER

    @property
    def is_staff_role(self):
        """Returns True if user has Staff role."""
        return self.role == self.Role.STAFF
