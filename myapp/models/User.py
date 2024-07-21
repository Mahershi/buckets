from django.utils.translation import gettext as _
import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from ..managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    # Unique fields are indexed by default.
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
        error_messages={
            'unique': "Email already exists!"
        }
    )

    name = models.CharField(
        max_length=40,
        null=False,
        blank=False,
    )

    password = models.CharField(max_length=200, null=False, blank=False)

    created_at = models.DateField(_("Date"), default=datetime.date.today)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.name + " (" + self.email + ")"

    def has_module_perms(self, app_label):
        return self.is_superuser

    class Meta:
        db_table = "users"
