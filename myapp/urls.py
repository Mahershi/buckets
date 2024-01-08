from django.urls import path
from rest_framework import routers
from .views import UserView, BucketView, UBView


router = routers.DefaultRouter()

router.register('user', UserView)
router.register('bucket', BucketView)
router.register('user-buckets', UBView)

urlpatterns = []

urlpatterns += router.urls