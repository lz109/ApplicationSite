from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("officer", "Admission Officer"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="officer")

    class Meta:
        app_label = "base"

    groups = models.ManyToManyField(
        Group,
        related_name="base_user_groups",  
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="base_user_permissions",  
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
