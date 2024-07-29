# TODO: Regarding indexes, need to create algo in Serializer where all new elements get the incremental index but also considers when deleting some element.
# Auto increment cannot be used because it does no decrease when deleted.
# Delete should be index specific -> user can pick and delete any index as required.
# Adding new element will strictly be sequential.

from django.db import models
from .FieldType import FieldType
from .BucketField import BucketField
from django.utils.translation import gettext as _
import datetime


class ArrayField(models.Model):
    # Instance of ARRAY field in BucketField tables to which this array element belongs to
    parent_field = models.ForeignKey(BucketField, on_delete=models.CASCADE, null=False, blank=False)
    # Index of this element in that array
    index = models.IntegerField(null=False, blank=False,)
    # Value, TODO: Currently max for value is 200, same as other, need to change later.
    value = models.CharField(max_length=200, null=False, default='', blank=False)
    type = models.ForeignKey(FieldType, on_delete=models.PROTECT, null=False, blank=False)
    created_at = models.DateTimeField(_("Date"), default=datetime.datetime.now)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        count = ArrayField.objects.filter(parent_field=self.parent_field).count()
        self.index = count
        print("Count: ", count)
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def __str__(self):
        return str(self.index)

    class Meta:
        db_table = 'array_field'
        # Composite index on (parent_field, index)
        # Will help get() based on 'parent_field' when collecting all elements belonging to an Array
        # Composite will help when updating or adding new index.
        indexes = [
            models.Index(fields=['parent_field', 'index'])
        ]