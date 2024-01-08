from django.db import models


class Access(models.Model):
    type = models.CharField(max_length=15, null=False, blank=False)

    def __str__(self):
        return self.type

    class Meta:
        db_table = "user_access"
