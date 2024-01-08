from rest_framework import serializers
from ..models import Bucket


class BucketSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Bucket