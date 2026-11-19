
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for the Electronics Store Inventory Management System.

    Implements role-based authorization for three application roles:
    Admin, Manager and Staff.
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
        """Returns True only for users assigned the Admin application role."""
        return self.role == self.Role.ADMIN

    @property
    def is_manager_role(self):
        """Returns True only for users assigned the Manager application role."""
        return self.role == self.Role.MANAGER

    @property
    def is_staff_role(self):
        """Returns True only for users assigned the Staff application role."""
        return self.role == self.Role.STAFF
