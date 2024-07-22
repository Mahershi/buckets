from django.db import models
import datetime
from django.utils.translation import gettext as _


class Bucket(models.Model):
    name = models.CharField(max_length=20, null=False, blank=False,)
    created_at = models.DateField(_("Date"), default=datetime.date.today)
    # Used to distinguish between Root Buckets and Sub Buckets.
    # Set False when creating Sub Buckets as a Field.
    is_root = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "buckets"
