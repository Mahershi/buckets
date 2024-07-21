from django.db import models
from django.utils.translation import gettext as _
import datetime
from .User import User
from .Bucket import Bucket
from .Access import Access


class UserBucket(models.Model):
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateField(_("Date"), default=datetime.date.today)
    access = models.ForeignKey(Access, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.bucket.id) + "." + self.bucket.name + "|" + str(self.user.id) + "." + self.user.email

    class Meta:
        db_table = "user_buckets"
        # Added group indexing for (user, bucket)
        # Optimized get() for UB just by 'user' as well as by (user, bucket)
        indexes = [
            models.Index(fields=['user', 'bucket'])
        ]
