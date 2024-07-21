# TODO: Current max length for field value is 200.
# All primitive types (currently str, bool, int, double) will be stored as str
# Value is bucket id for Dict type, because dict is rep by a Sub-bucket.

from django.db import models
from .Bucket import Bucket
from .FieldType import FieldType
from django.utils.translation import gettext as _
import datetime


class BucketField(models.Model):

    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE, null=False, blank=False)
    key = models.CharField(max_length=20, null=False, blank=False)
    type = models.ForeignKey(FieldType, on_delete=models.PROTECT, null=False, blank=False)
    value = models.CharField(max_length=200, null=False, default='', blank=False)
    created_at = models.DateTimeField(_("Date"), default=datetime.datetime.now)

    def __str__(self):
        return self.key

    class Meta:
        db_table = 'bucket_field'
        # Indexing bucket field. Optmizes getting all Fields for a given bucket.
        # Optimized get for (bucket, key)
        indexes = [
            models.Index(fields=['bucket', 'key'])
        ]
