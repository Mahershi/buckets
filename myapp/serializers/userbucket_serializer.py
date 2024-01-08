from rest_framework import serializers
from ..models import UserBucket
from .bucket_serializer import BucketSerializer
from .access_serializer import AccessSerializer


class UBSerializer(serializers.ModelSerializer):
    bucket = BucketSerializer(many=False)
    access = AccessSerializer(many=False)

    class Meta:
        model = UserBucket
        fields = '__all__'




