from rest_framework.serializers import ModelSerializer, CurrentUserDefault
from ..models import User


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def to_representation(self, instance):
        # removes password field from responses.
        instance = super(ModelSerializer, self).to_representation(instance)
        instance.pop('password')
        return instance
