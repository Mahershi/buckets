from rest_framework import serializers
from ..models import Access


class AccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Access
        fields = '__all__'
