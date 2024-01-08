from django.db import models


class FieldType(models.Model):
    type = models.CharField(max_length=10, null=False, blank=False)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'field_type'